#!/usr/bin/env python3
"""Parse a RAID: Shadow Legends roster export (artifacts.json) into facts the skill can reason on.

Stdlib only. Reads the open `artifacts.json` written by RaidExtractor (Gen 1, no
`fileVersion`) or the Raid Toolkit extractor (Gen 2, `"fileVersion": "1.3"`), or a .zip
holding that file. The schema was read from both extractors' C# source; see
references/roster-file.md for the field table and what the file does not contain.

Usage:
  python3 -I raid_roster.py FILE summary
  python3 -I raid_roster.py FILE heroes [--min-stars N] [--include-food]
  python3 -I raid_roster.py FILE hero NAME
  python3 -I raid_roster.py FILE gear [--top N]
  python3 -I raid_roster.py FILE factions

Output is JSON on stdout. Errors are JSON on stdout with exit code 2.

Privacy: the account-level `id` and `name` are never printed. Hero and artifact ids are
in-game instance ids and are kept so outputs can cross-reference each other.
"""

import argparse
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

# --- Encodings -----------------------------------------------------------------------------

# Stat kind -> short label. Gen 1/2 C# enum (1-9) plus the Node client's IgnoreDefense.
STAT_LABEL = {
    "Health": "HP",
    "Attack": "ATK",
    "Defense": "DEF",
    "Speed": "SPD",
    "Resistance": "RES",
    "Accuracy": "ACC",
    "CriticalChance": "C.RATE",
    "CriticalDamage": "C.DMG",
    "CriticalHeal": "C.HEAL",
    "IgnoreDefense": "IGNORE DEF",
}
# Stats that exist as both a flat and a percent bonus; the percent form gets a "%" label.
DUAL_STATS = {"Health", "Attack", "Defense"}

SLOT_LABEL = {
    "Helmet": "Helmet",
    "Chest": "Chest",
    "Gloves": "Gloves",
    "Boots": "Boots",
    "Weapon": "Weapon",
    "Shield": "Shield",
    "Ring": "Ring",
    "Cloak": "Amulet",  # the game's internal name for the amulet slot
    "Banner": "Banner",
}
ARTIFACT_SLOTS = ["Weapon", "Helmet", "Shield", "Gloves", "Chest", "Boots"]
ACCESSORY_SLOTS = ["Ring", "Amulet", "Banner"]
BOTTOM_ROW = {"Gloves", "Chest", "Boots"}

RANK = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6}
RARITY_ORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythical"]
RARITY_ALIASES = {"Mythic": "Mythical"}  # C# says Mythical, the TypeScript client says Mythic

ROLE_LABEL = {
    "Attack": "ATK",
    "Defense": "DEF",
    "Health": "HP",
    "Support": "Support",
    "Evolve": "Evolve (fodder)",
    "Xp": "Food",
}
FODDER_ROLES = {"Evolve", "Xp"}

FACTION_LABEL = {
    "BannerLords": "Banner Lords",
    "HighElves": "High Elves",
    "SacredOrder": "The Sacred Order",
    "CovenOfMagi": "Coven of Magi",
    "OgrynTribes": "Ogryn Tribes",
    "LizardMen": "Lizardmen",
    "Skinwalkers": "Skinwalkers",
    "Orcs": "Orcs",
    "Demonspawn": "Demonspawn",
    "UndeadHordes": "Undead Hordes",
    "DarkElves": "Dark Elves",
    "KnightsRevenant": "Knights Revenant",
    "Barbarians": "Barbarians",
    "NyresanElves": "Sylvan Watchers",
    "Samurai": "Shadowkin",
    "Dwarves": "Dwarves",
}
# These two pairings are inferred (newer factions under older internal names), not read
# from source. The output marks them so the skill can say so.
FACTION_INFERRED = {"NyresanElves", "Samurai"}

# Internal set name -> (in-game name, confidence). No public file pairs these; every entry
# is inferred. "high" = classic sets whose internal name describes the bonus unambiguously,
# "medium" = plausible but disputed or hybrid. Anything absent is shown raw as "unmapped".
SET_NAMES = {
    "Hp": ("Life", "high"),
    "AttackPower": ("Offense", "high"),
    "Defense": ("Defense", "high"),
    "AttackSpeed": ("Speed", "high"),
    "CriticalChance": ("Critical Rate", "high"),
    "CriticalDamage": ("Critical Damage", "high"),
    "Accuracy": ("Accuracy", "high"),
    "Resistance": ("Resistance", "high"),
    "LifeDrain": ("Lifesteal", "high"),
    "DamageIncreaseOnHpDecrease": ("Fury", "high"),
    "SleepChance": ("Daze", "high"),
    "BlockHealChance": ("Cursed", "high"),
    "FreezeRateOnDamageReceived": ("Frost", "high"),
    "Stamina": ("Frenzy", "high"),
    "Heal": ("Regeneration", "high"),
    "BlockDebuff": ("Immunity", "high"),
    "Shield": ("Shield", "high"),
    "GetExtraTurn": ("Relentless", "high"),
    "DecreaseMaxHp": ("Destroy", "high"),
    "StunChance": ("Stun", "high"),
    "DotRate": ("Toxic", "high"),
    "ProvokeChance": ("Taunting", "high"),
    "Counterattack": ("Retaliation", "high"),
    "CounterattackOnCrit": ("Avenging", "high"),
    "AoeDamageDecrease": ("Stalwart", "high"),
    "CooldownReductionChance": ("Reflex", "high"),
    "CriticalHealMultiplier": ("Curing", "high"),
    "HpAndHeal": ("Immortal", "high"),
    "ShieldAndAttackPower": ("Divine Offense", "high"),
    "ShieldAndCriticalChance": ("Divine Critical Rate", "high"),
    "ShieldAndHp": ("Divine Life", "high"),
    "ShieldAndSpeed": ("Divine Speed", "high"),
    "IgnoreDefense": ("Savage", "medium"),
    "AttackPowerAndIgnoreDefense": ("Cruel", "medium"),
    "StoneSkinHpResDef": ("Stoneskin", "medium"),
    "AccuracyAndSpeed": ("Perception", "medium"),
    "FreezeResistAndRate": ("Frostbite", "medium"),
    "CritRateAndLifeDrain": ("Bloodthirst", "medium"),
}

# Mastery ids from Raid Toolkit's MasteryKindId enum (account-extension, MIT). The id
# itself encodes tree and tier: 500<tree><tier><n>, tree 1 Offense / 2 Defense / 3 Support.
MASTERY_NAMES = {
    500112: "Blade Disciple", 500113: "Deadly Precision", 500121: "Heart of Glory",
    500122: "Keen Strike", 500123: "Shield Breaker", 500124: "Grim Resolve",
    500131: "Single Out", 500132: "Life Drinker", 500133: "Whirlwind of Death",
    500134: "Ruthless Ambush", 500141: "Bring It Down", 500142: "Wrath of the Slain",
    500143: "Cycle of Violence", 500144: "Opportunist", 500151: "Methodical",
    500152: "Kill Streak", 500153: "Blood Shield", 500154: "Stoked to Fury",
    500161: "Warmaster", 500162: "Helmsmasher", 500163: "Giant Slayer",
    500164: "Flawless Execution",
    500212: "Tough Skin", 500213: "Defiant", 500221: "Blastproof", 500222: "Rejuvenation",
    500223: "Mighty Endurance", 500224: "Improved Parry", 500231: "Shadow Heal",
    500232: "Resurgent", 500233: "Bloodthirst", 500234: "Wisdom of Battle",
    500241: "Solidarity", 500242: "Delay Death", 500243: "Harvest Despair",
    500244: "Stubbornness", 500251: "Selfless Defender", 500252: "Cycle of Revenge",
    500253: "Retribution", 500254: "Deterrence", 500261: "Iron Skin", 500262: "Bulwark",
    500263: "Fearsome Presence", 500264: "Unshakeable",
    500312: "Steadfast", 500313: "Pinpoint Accuracy", 500321: "Lay on Hands",
    500322: "Shieldbearer", 500323: "Exalt in Death", 500324: "Charged Focus",
    500331: "Healing Savior", 500332: "Rapid Response", 500333: "Swarm Smiter",
    500334: "Arcane Celerity", 500341: "Merciful Aid", 500342: "Cycle of Magic",
    500343: "Lore of Steel", 500344: "Evil Eye", 500351: "Lasting Gifts",
    500352: "Spirit Haste", 500353: "Sniper", 500354: "Master Hexer",
    500361: "Elixir of Life", 500362: "Timely Intervention", 500363: "Oppressor",
    500364: "Eagle-Eye",
}
MASTERY_TREES = {1: "Offense", 2: "Defense", 3: "Support"}
MAX_MASTERIES = 15

BLIND_SPOTS = [
    "Hero stats in the file are base stats for rank and level only: no gear, masteries, "
    "Great Hall, ascension, blessings or empowerment.",
    "Blessings, Awakening (double ascension), artifact ascension and relics are not exported.",
    "Silver, gems, energy, books and potions are not exported; only shard counts are.",
    "Percent values are rounded to 2 decimals by the extractor, so a 4.6% roll reads as 5%.",
    "Skill max levels are not in the file, so book gaps need a lookup.",
]


class RosterError(Exception):
    pass


# --- Loading -------------------------------------------------------------------------------

def load(path):
    """Read artifacts.json or a .zip containing it. Returns the parsed JSON object."""
    p = Path(path)
    if not p.is_file():
        raise RosterError(f"file not found: {path}")
    raw = None
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as zf:
            names = [n for n in zf.namelist() if n.lower().endswith(".json")]
            preferred = [n for n in names if Path(n).name.lower() == "artifacts.json"]
            pick = preferred or names
            if not pick:
                raise RosterError("zip contains no .json file")
            if len(pick) > 1:
                raise RosterError(f"zip has several JSON files, expected one: {pick}")
            raw = zf.read(pick[0])
    else:
        raw = p.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise RosterError(f"not valid JSON: {e}") from e
    if not isinstance(data, dict) or not (
        isinstance(data.get("heroes"), list) or isinstance(data.get("artifacts"), list)
    ):
        raise RosterError(
            "not an artifacts.json roster: no top-level `heroes` or `artifacts` list. "
            "If this came from the HellHades extractor, its format is undocumented."
        )
    return data


def generation(data):
    fv = data.get("fileVersion")
    if fv is None:
        return {"generation": 1, "fileVersion": None, "tool": "RaidExtractor (Gen 1)"}
    if str(fv) == "1.3":
        return {"generation": 2, "fileVersion": "1.3", "tool": "Raid Toolkit extractor (Gen 2)"}
    return {"generation": None, "fileVersion": str(fv), "tool": "unknown version; parsed as Gen 2"}


# --- Normalisation -------------------------------------------------------------------------

def norm_name(name):
    """Name key for joining with outside ratings: lowercase alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def norm_rarity(r):
    return RARITY_ALIASES.get(r, r)


def stars(grade):
    m = re.match(r"Stars(\d)", grade or "")
    return int(m.group(1)) if m else None


def set_info(set_kind):
    if not set_kind or set_kind == "None":
        return {"set": None, "setKind": set_kind, "mapping": None}
    name, conf = SET_NAMES.get(set_kind, (set_kind, "unmapped"))
    return {"set": name, "setKind": set_kind, "mapping": conf}


def bonus(b, warnings):
    """Normalise one ArtifactBonus. Percent stats come as fractions (0.15 = 15%)."""
    kind = b.get("kind")
    absolute = bool(b.get("isAbsolute", True))
    value = float(b.get("value") or 0)
    glyph = float(b.get("enhancement") or 0)
    label = STAT_LABEL.get(kind, kind or "?")
    if kind not in STAT_LABEL:
        warnings.add(f"unknown stat kind passed through: {kind!r}")
    percent = not absolute
    if percent:
        if abs(value) > 1.0 or abs(glyph) > 1.0:
            warnings.add(
                f"{label} percent value above 1 ({value}); assumed already a percent"
            )
        else:
            value, glyph = value * 100, glyph * 100
        if kind in DUAL_STATS:
            label += "%"
    return {
        "stat": label,
        "kind": kind,
        "percent": percent,
        "value": round(value, 2),
        "glyph": round(glyph, 2),
        "total": round(value + glyph, 2),
        "rolls": b.get("level", 0),
    }


def artifact(a, warnings, owner=None):
    slot = SLOT_LABEL.get(a.get("kind"), a.get("kind") or "?")
    if a.get("kind") not in SLOT_LABEL:
        warnings.add(f"unknown slot kind passed through: {a.get('kind')!r}")
    s = set_info(a.get("setKind"))
    if s["mapping"] == "unmapped":
        warnings.add(f"unmapped set name shown raw: {s['setKind']!r}")
    out = {
        "id": a.get("id"),
        "slot": slot,
        "rank": RANK.get(a.get("rank"), a.get("rank")),
        "rarity": norm_rarity(a.get("rarity")),
        "level": a.get("level", 0),
        **s,
        "main": bonus(a["primaryBonus"], warnings) if a.get("primaryBonus") else None,
        "subs": [bonus(b, warnings) for b in a.get("secondaryBonuses") or []],
        "owner": owner,
    }
    if a.get("requiredFraction"):
        out["factionLock"] = FACTION_LABEL.get(a["requiredFraction"], a["requiredFraction"])
    if "sellPrice" in a:
        out["sellPrice"] = a["sellPrice"]
    return out


def mastery(mid):
    tree = MASTERY_TREES.get((mid // 100) % 10)
    tier = (mid // 10) % 10
    return {"id": mid, "name": MASTERY_NAMES.get(mid, f"unknown mastery {mid}"),
            "tree": tree, "tier": tier}


class Roster:
    def __init__(self, data):
        self.data = data
        self.gen = generation(data)
        self.warnings = set()
        if self.gen["generation"] is None:
            self.warnings.add(f"unrecognised fileVersion {self.gen['fileVersion']!r}")
        heroes = data.get("heroes") or []
        self.owner_of = {}
        hero_names = {}
        for h in heroes:
            hero_names[h.get("id")] = h.get("name")
            for aid in h.get("artifacts") or []:
                self.owner_of[aid] = h.get("id")
        self.artifacts = {}
        for a in data.get("artifacts") or []:
            if "id" not in a:
                self.warnings.add("artifact without id skipped")
                continue
            owner = self.owner_of.get(a["id"])
            art = artifact(a, self.warnings, owner)
            art["ownerName"] = hero_names.get(owner) if owner is not None else None
            self.artifacts[a["id"]] = art
        missing = [aid for aid in self.owner_of if aid not in self.artifacts]
        if missing:
            self.warnings.add(f"{len(missing)} equipped artifact id(s) not in the artifacts list")
        self.heroes = [self.hero(h) for h in heroes]

    # -- heroes --
    def hero(self, h):
        type_id = h.get("typeId")
        ascension = type_id % 10 if isinstance(type_id, int) else h.get("awakenLevel")
        fraction = h.get("fraction")
        if fraction and fraction not in FACTION_LABEL:
            self.warnings.add(f"unknown faction passed through: {fraction!r}")
        masteries = [mastery(m) for m in h.get("masteries") or [] if isinstance(m, int)]
        gear = [self.artifacts[i] for i in h.get("artifacts") or [] if i in self.artifacts]
        filled = {g["slot"] for g in gear}
        sets = Counter(g["set"] for g in gear if g["set"])
        out = {
            "id": h.get("id"),
            "name": h.get("name"),
            "nameKey": norm_name(h.get("name")),
            "typeId": type_id,
            "baseTypeId": type_id // 10 * 10 if isinstance(type_id, int) else None,
            "rarity": norm_rarity(h.get("rarity")),
            "faction": FACTION_LABEL.get(fraction, fraction),
            "affinity": h.get("element"),
            "role": ROLE_LABEL.get(h.get("role"), h.get("role")),
            "fodder": h.get("role") in FODDER_ROLES,
            "stars": stars(h.get("grade")),
            "level": h.get("level"),
            "ascension": ascension,
            "empower": h.get("empowerLevel"),
            "inVault": bool(h.get("inStorage", False)),
            "isGuardian": h.get("isGuardian"),
            "masteryCount": len(masteries),
            "masteries": masteries,
            "skills": [
                {"typeId": s.get("typeId"), "level": s.get("level")}
                for s in h.get("skills") or []
            ],
            "gear": {
                "equipped": len(gear),
                "emptyArtifactSlots": [s for s in ARTIFACT_SLOTS if s not in filled],
                "emptyAccessorySlots": [s for s in ACCESSORY_SLOTS if s not in filled],
                "sets": dict(sets.most_common()),
                "pieceIds": [g["id"] for g in gear],
            },
            "approxStats": self.approx_stats(h, gear),
        }
        if fraction in FACTION_INFERRED:
            out["factionMapping"] = "inferred"
        scrolls = h.get("unassignedMasteryScrolls")
        if isinstance(scrolls, dict):
            out["unassignedMasteryScrolls"] = scrolls
        return out

    @staticmethod
    def approx_stats(h, gear):
        """Base + gear main/sub stats + glyphs. Excludes set bonuses, masteries, Great Hall,
        ascension, blessings, empowerment and area bonuses, so it undercounts on purpose."""
        flat = defaultdict(float)
        pct = defaultdict(float)
        for g in gear:
            for b in ([g["main"]] if g["main"] else []) + g["subs"]:
                (pct if b["percent"] else flat)[b["kind"]] += b["total"]

        def crit(v):
            v = float(v or 0)
            return v * 100 if v <= 1.5 else v  # base crit may be stored as a fraction

        stats = {}
        for kind, label in (("Health", "HP"), ("Attack", "ATK"), ("Defense", "DEF")):
            base = float(h.get(kind[0].lower() + kind[1:]) or 0)
            stats[label] = round(base * (1 + pct[kind] / 100) + flat[kind])
        base_spd = float(h.get("speed") or 0)
        stats["SPD"] = round(base_spd * (1 + pct["Speed"] / 100) + flat["Speed"], 1)
        stats["ACC"] = round(float(h.get("accuracy") or 0) + flat["Accuracy"])
        stats["RES"] = round(float(h.get("resistance") or 0) + flat["Resistance"])
        stats["C.RATE"] = round(crit(h.get("criticalChance")) + pct["CriticalChance"], 1)
        stats["C.DMG"] = round(crit(h.get("criticalDamage")) + pct["CriticalDamage"], 1)
        stats["label"] = ("approximate: base + gear + glyphs only; set bonuses, masteries, "
                          "Great Hall, ascension and blessings excluded. Check in-game.")
        return stats

    def real_heroes(self):
        return [h for h in self.heroes if not h["fodder"]]

    # -- reports --
    def summary(self):
        heroes = self.real_heroes()
        built = [h for h in heroes if h["stars"] == 6 and h["level"] == 60]
        great_hall = self.data.get("greatHall") or {}
        gh_total = sum(
            v for stats_ in great_hall.values() if isinstance(stats_, dict)
            for v in stats_.values() if isinstance(v, (int, float))
        )
        shards = {
            k: (v.get("count") if isinstance(v, dict) else v)
            for k, v in (self.data.get("shards") or {}).items()
        }
        gaps = {
            "sixStarLevel60WithoutAllMasteries": [
                {"name": h["name"], "masteries": h["masteryCount"]}
                for h in built if h["masteryCount"] < MAX_MASTERIES
            ],
            "ascensionBelowRank": [
                {"name": h["name"], "stars": h["stars"], "ascension": h["ascension"]}
                for h in heroes
                if h["stars"] and h["level"] and h["level"] >= 50
                and isinstance(h["ascension"], int) and h["ascension"] < h["stars"]
            ],
            "builtWithEmptySlots": [
                {"name": h["name"], "empty": h["gear"]["emptyArtifactSlots"]}
                for h in built if h["gear"]["emptyArtifactSlots"]
            ],
        }
        unassigned = sum(
            v for h in heroes for v in (h.get("unassignedMasteryScrolls") or {}).values()
            if isinstance(v, (int, float))
        )
        return {
            "source": self.gen,
            "lastUpdated": self.data.get("lastUpdated"),
            "redacted": [k for k in ("id", "name") if k in self.data],
            "counts": {
                "champions": len(heroes),
                "fodderAndFood": len(self.heroes) - len(heroes),
                "byRarity": dict(Counter(h["rarity"] for h in heroes)),
                "byStars": {str(k): v for k, v in sorted(
                    Counter(h["stars"] for h in heroes).items(), key=lambda kv: kv[0] or 0)},
                "sixStarLevel60": len(built),
                "level60": sum(1 for h in heroes if h["level"] == 60),
                "artifacts": len(self.artifacts),
                "unequippedArtifacts": sum(1 for a in self.artifacts.values() if a["owner"] is None),
            },
            "stageSignal": stage_signal(len(built), gh_total),
            "arenaLeague": self.data.get("arenaLeague"),
            "greatHall": {"levels": great_hall, "totalLevels": gh_total,
                          "note": "24 tracks x 10 levels = 240 max [CHECK IN-GAME]"},
            "factionGuardians": self.data.get("factionGuardians"),
            "shards": shards,
            "unassignedMasteryScrolls": unassigned or None,
            "investmentGaps": gaps,
            "builtChampions": sorted(h["name"] for h in built),
            "blindSpots": BLIND_SPOTS,
            "warnings": sorted(self.warnings),
        }

    def hero_rows(self, min_stars=0, include_food=False):
        pool = self.heroes if include_food else self.real_heroes()
        rows = [
            {k: h[k] for k in ("id", "name", "rarity", "faction", "affinity", "role", "stars",
                               "level", "ascension", "empower", "masteryCount", "inVault")}
            | {"sets": h["gear"]["sets"], "emptySlots": h["gear"]["emptyArtifactSlots"],
               "SPD~": h["approxStats"]["SPD"], "ACC~": h["approxStats"]["ACC"]}
            for h in pool if (h["stars"] or 0) >= min_stars
        ]
        rows.sort(key=lambda r: (-(r["stars"] or 0), -(r["level"] or 0), r["name"] or ""))
        return {"heroes": rows, "warnings": sorted(self.warnings)}

    def hero_detail(self, name):
        key = norm_name(name)
        matches = [h for h in self.heroes if h["nameKey"] == key]
        if not matches:
            matches = [h for h in self.heroes if key and key in h["nameKey"]]
        if not matches:
            raise RosterError(f"no champion named {name!r} in this roster")
        out = []
        for h in matches:
            d = dict(h)
            d["gear"] = dict(h["gear"], pieces=[self.artifacts[i] for i in h["gear"]["pieceIds"]])
            out.append(d)
        return {"matches": out, "blindSpots": BLIND_SPOTS, "warnings": sorted(self.warnings)}

    def gear(self, top=25):
        arts = list(self.artifacts.values())

        def spd_sub(a):
            return sum(b["total"] for b in a["subs"] if b["kind"] == "Speed")

        def spd_rolls(a):
            return sum(b["rolls"] or 0 for b in a["subs"] if b["kind"] == "Speed")

        speed_pieces = sorted(
            (a for a in arts if spd_sub(a) > 0),
            key=lambda a: (-spd_sub(a), -(a["rank"] or 0)),
        )
        compact = lambda a: {  # noqa: E731
            "id": a["id"], "slot": a["slot"], "set": a["set"], "rank": a["rank"],
            "rarity": a["rarity"], "level": a["level"],
            "main": a["main"]["stat"] if a["main"] else None,
            "spdSub": round(spd_sub(a), 1), "spdRolls": spd_rolls(a),
            "owner": a["ownerName"],
        }
        upgrade = [
            compact(a) for a in speed_pieces
            if (a["level"] or 0) < 16 and (a["rank"] or 0) >= 5
        ]
        spd_boots = [compact(a) for a in arts
                     if a["slot"] == "Boots" and a["main"] and a["main"]["kind"] == "Speed"]
        spd_boots.sort(key=lambda a: (a["owner"] is not None, -(a["rank"] or 0)))
        sell = []
        for a in arts:
            if a["owner"] is not None or a["rarity"] == "Mythical":
                continue
            reasons = []
            if (a["rank"] or 0) < 5:
                reasons.append("under 5 stars")
            if a["rarity"] in ("Epic", "Legendary") and spd_sub(a) == 0 \
                    and not (a["main"] and a["main"]["kind"] == "Speed"):
                reasons.append("Epic/Legendary with no SPD substat")
            if a["slot"] in BOTTOM_ROW and a["main"] and not a["main"]["percent"] \
                    and a["main"]["kind"] in DUAL_STATS:
                reasons.append(f"flat {a['main']['stat']} main on {a['slot']}")
            if reasons:
                sell.append(compact(a) | {"reasons": reasons})
        sell.sort(key=lambda a: (-len(a["reasons"]), a["rank"] or 0))
        by_set = Counter(a["set"] or "none" for a in arts)
        return {
            "totals": {"artifacts": len(arts),
                       "equipped": sum(1 for a in arts if a["owner"] is not None),
                       "bySet": dict(by_set.most_common())},
            "topSpeedSubstatPieces": [compact(a) for a in speed_pieces[:top]],
            "speedUpgradeCandidates": upgrade[:top],
            "speedBoots": spd_boots[:top],
            "sellCandidates": {
                "rule": ("2021 community heuristics (HellHades, MurderInc, Chosen via "
                         "RaidExtractor Discussion #42); a starting point only, predates "
                         "variable sets and gear ascension. Unequipped, non-Mythical only."),
                "count": len(sell),
                "pieces": sell[:top],
            },
            "warnings": sorted(self.warnings),
        }

    def factions(self):
        groups = defaultdict(list)
        for h in self.real_heroes():
            groups[h["faction"] or "unknown"].append(h)
        out = {}
        for fac, hs in sorted(groups.items()):
            ready = [h for h in hs if (h["stars"] or 0) >= 5 and (h["level"] or 0) >= 50]
            out[fac] = {
                "owned": len(hs),
                "ready": len(ready),
                "canField5": len(ready) >= 5,
                "readyChampions": sorted(
                    (f"{h['name']} ({h['stars']}*{h['level']}, {h['role']})" for h in ready)),
                "others": sorted(h["name"] for h in hs if h not in ready),
            }
        return {
            "readyMeans": "5+ stars and level 50+ (a rough bar for Faction Wars, not a clear guarantee)",
            "factions": out,
            "warnings": sorted(self.warnings),
        }


def stage_signal(six_star_60, gh_total):
    """Roster-only stage hint from HellHades' 2020 stage definitions. Clears decide the
    real stage; the skill must ask what the player has beaten."""
    if six_star_60 <= 2:
        stage = "Early"
    elif six_star_60 <= 4:
        stage = "Early to Mid"
    elif six_star_60 <= 10:
        stage = "Mid"
    else:
        stage = "Late or End (End needs Great Hall 180+ and one-key UNM)"
    return {
        "stage": stage,
        "sixStarLevel60": six_star_60,
        "greatHallTotal": gh_total,
        "basis": "HellHades stage definitions (2020), roster count only; confirm with the "
                 "player's clears",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Summarise a RAID artifacts.json roster export.")
    ap.add_argument("file")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("summary")
    p_heroes = sub.add_parser("heroes")
    p_heroes.add_argument("--min-stars", type=int, default=0)
    p_heroes.add_argument("--include-food", action="store_true")
    p_hero = sub.add_parser("hero")
    p_hero.add_argument("name")
    p_gear = sub.add_parser("gear")
    p_gear.add_argument("--top", type=int, default=25)
    sub.add_parser("factions")
    args = ap.parse_args(argv)
    try:
        roster = Roster(load(args.file))
        if args.cmd == "summary":
            out = roster.summary()
        elif args.cmd == "heroes":
            out = roster.hero_rows(args.min_stars, args.include_food)
        elif args.cmd == "hero":
            out = roster.hero_detail(args.name)
        elif args.cmd == "gear":
            out = roster.gear(args.top)
        else:
            out = roster.factions()
    except RosterError as e:
        print(json.dumps({"error": str(e)}))
        return 2
    if args.cmd == "heroes":
        # One compact row per line: a real roster has hundreds of champions.
        rows = ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in out["heroes"])
        print('{"heroes": [\n' + rows + '\n], "warnings": '
              + json.dumps(out["warnings"], ensure_ascii=False) + "}")
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
