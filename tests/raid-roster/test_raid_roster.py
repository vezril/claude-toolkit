#!/usr/bin/env python3
"""Tests for skills/raid-shadow-legends/scripts/raid_roster.py.

The fixtures are synthetic rosters built in this file: the artifacts.json shape the two
extractors write (field names from their C# source), and the HellHades optimiser's account
shape (integer enums, defaults omitted). No real account data is used.

Run: python3 tests/raid-roster/test_raid_roster.py
"""

import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "raid-shadow-legends" / "scripts" / "raid_roster.py"
sys.path.insert(0, str(SCRIPT.parent))

import raid_roster as rr  # noqa: E402

ACCOUNT_ID = "acct-7f3e-secret"
ACCOUNT_NAME = "PlayerNameShouldNotLeak"


def bonus(kind, value, absolute=True, glyph=0.0, rolls=0):
    return {"kind": kind, "isAbsolute": absolute, "value": value, "enhancement": glyph,
            "level": rolls}


def art(aid, kind, set_kind, main, subs, rank="Six", rarity="Legendary", level=16, **extra):
    return {"id": aid, "kind": kind, "rank": rank, "rarity": rarity, "setKind": set_kind,
            "level": level, "sellPrice": 1000, "isActivated": True, "isSeen": True,
            "failedUpgrades": 0, "primaryBonus": main, "secondaryBonuses": subs, **extra}


def hero(hid, name, type_id, grade="Stars6", level=60, artifacts=None, masteries=None,
         fraction="BannerLords", role="Support", rarity="Epic", **extra):
    h = {"id": hid, "typeId": type_id, "name": name, "grade": grade, "level": level,
         "fraction": fraction, "rarity": rarity, "role": role, "element": "Magic",
         "awakenLevel": type_id % 10, "health": 15000, "attack": 900, "defense": 1000,
         "speed": 100, "resistance": 30, "accuracy": 10, "criticalChance": 0.15,
         "criticalDamage": 0.5, "criticalHeal": 0, "masteries": masteries or [],
         "skills": [{"id": 1, "typeId": 2011, "level": 3}], "locked": False,
         "inStorage": False, "marker": "None", **extra}
    if artifacts is not None:
        h["artifacts"] = artifacts
    return h


def gen1_roster():
    artifacts = [
        art(1, "Boots", "AttackSpeed", bonus("Speed", 45),
            [bonus("Accuracy", 20, rolls=1), bonus("Speed", 11, glyph=3, rolls=2),
             bonus("Health", 0.06, absolute=False)]),
        art(2, "Chest", "AttackSpeed", bonus("Accuracy", 96),
            [bonus("Speed", 5, rolls=0)]),
        art(3, "Gloves", "AccuracyAndSpeed", bonus("Health", 0.6, absolute=False),
            [bonus("Speed", 4)]),
        # unequipped: a sell candidate on three counts
        art(4, "Gloves", "Hp", bonus("Attack", 80), [bonus("Defense", 0.05, absolute=False)],
            rank="Four", rarity="Epic", level=4),
        # unequipped good speed piece below +16
        art(5, "Helmet", "AttackSpeed", bonus("Health", 2000),
            [bonus("Speed", 16, rolls=3)], rank="Six", rarity="Legendary", level=12),
        # a post-2024 set the enum does not know
        art(6, "Ring", "MercurialSomething", bonus("Health", 1500), [], rarity="Mythic",
            requiredFraction="BannerLords"),
    ]
    heroes = [
        hero(100, "Arbiter", 1236, artifacts=[1, 2, 3], rarity="Legendary",
             masteries=[500161, 500343, 500364]),
        hero(101, "Kael", 30, grade="Stars5", level=50, fraction="DarkElves", role="Attack",
             rarity="Rare"),
        hero(102, "Chicken", 5, grade="Stars1", level=1, role="Xp", rarity="Common"),
    ]
    return {"artifacts": artifacts, "heroes": heroes, "arenaLeague": "GoldIV",
            "greatHall": {"magic": {"accuracy": 10, "health": 5}, "force": {"accuracy": 3}},
            "shards": {"ancient": {"count": 12, "summonData": []},
                       "sacred": {"count": 2, "summonData": []}},
            "stagePresets": {"1001": [100, 101]}}


def gen2_roster():
    data = gen1_roster()
    data.update({"fileVersion": "1.3", "id": ACCOUNT_ID, "name": ACCOUNT_NAME,
                 "lastUpdated": "2026-11-01T10:00:00.0000000Z",
                 "factionGuardians": {"BannerLords": {"Epic": 1}}})
    data["heroes"][0]["empowerLevel"] = 2
    data["heroes"][0]["isGuardian"] = False
    data["heroes"][0]["unassignedMasteryScrolls"] = {"Basic": 40, "Advanced": 0}
    return data


HH_USER_ID = 987654321
HH_CLAN = "ClanNameShouldNotLeak"


def hh_roster():
    """The HellHades optimiser's account shape: integer enums, defaults omitted (no
    isAbsolute = percent, no level = 0), its own heroTypes table, account identifiers."""
    artifacts = [
        # boots, Speed set, SPD main, SPD sub with 2 rolls and a glyph, gear ascension
        {"id": 1, "level": 16, "isActivated": True, "set": 4, "rank": 6, "rarity": 5,
         "kind": 4, "primaryBonus": {"kind": 4, "isAbsolute": True, "value": 45.0},
         "secondaryBonuses": [
             {"kind": 4, "isAbsolute": True, "value": 11.0, "enhancement": 3.0, "level": 2},
             {"kind": 1, "value": 0.06}],
         "ascendLevel": 2, "ascendBonus": {"kind": 4, "isAbsolute": True, "value": 2.0}},
        # gloves, Perception (38), C.RATE% main
        {"id": 2, "level": 12, "set": 38, "rank": 5, "rarity": 4, "kind": 3,
         "primaryBonus": {"kind": 7, "value": 0.5},
         "secondaryBonuses": [{"kind": 6, "isAbsolute": True, "value": 20.0, "level": 1}]},
        # unequipped amulet (Cloak = 8), faction-locked to Argonites (17), no set
        {"id": 3, "set": 0, "rank": 4, "rarity": 3, "kind": 8, "requiredFraction": 17,
         "primaryBonus": {"kind": 8, "value": 0.2}, "secondaryBonuses": []},
        # a set id no published enum names
        {"id": 4, "set": 60, "rank": 6, "rarity": 5, "kind": 7,
         "primaryBonus": {"kind": 1, "isAbsolute": True, "value": 1500.0},
         "secondaryBonuses": []},
    ]
    hero_types = [
        {"id": 2016, "name": "Arbiter", "fraction": 3, "rarity": 5,
         "forms": [{"role": 3, "element": 1, "skillTypeIds": [20161, 20162],
                    "baseStats": {"health": 76.0, "attack": 87.0, "defence": 82.0,
                                  "speed": 110.0, "resistance": 30.0, "accuracy": 10.0,
                                  "criticalChance": 15.0, "criticalDamage": 50.0}}]},
        {"id": 6620, "name": "Horned Viper", "fraction": 17, "rarity": 3,
         "forms": [{"role": 0, "element": 2, "skillTypeIds": [66201],
                    "baseStats": {"health": 60.0, "attack": 100.0, "defence": 70.0,
                                  "speed": 99.0, "resistance": 30.0, "accuracy": 0.0,
                                  "criticalChance": 15.0, "criticalDamage": 50.0}}]},
    ]
    heroes = [
        {"id": 100, "typeId": 2016, "grade": 6, "level": 60, "empowerLevel": 0,
         "locked": False, "inStorage": False, "artifacts": [1, 2], "relics": [7],
         "masteries": [500161, 500343], "skillLevels": {"20161": 5, "20162": 3},
         "awakenedGrade": 2, "blessingId": 1102},
        {"id": 101, "typeId": 6620, "grade": 4, "level": 40, "empowerLevel": 0,
         "locked": False, "inStorage": True, "artifacts": None, "relics": None,
         "masteries": [], "skillLevels": {}, "awakenedGrade": 0, "blessingId": None},
    ]
    return {
        "createdOn": "2026-11-08T00:00:00Z", "userId": HH_USER_ID, "name": ACCOUNT_NAME,
        "userName": None, "clanId": 4242, "clanName": HH_CLAN,
        "accountCreatedOn": "2020-01-01T00:00:00Z",
        "artifacts": artifacts, "heroes": heroes, "heroTypes": hero_types,
        "relics": [{"id": 7, "typeId": 1, "rank": 2, "level": 3, "sockets": []}],
        "relicStones": [], "greatHall": {"Magic": {"Accuracy": 4, "Health": 1}},
        "arenaLeague": 14, "arenaPoints": 1840, "liveArenaLeague": 0, "liveArenaPoints": 950,
        "shards": {"Ancient": 9, "Void": 1},
        "guardians": {"Argonites": {"Rare": [{"firstHero": 101, "secondHero": None},
                                             {"firstHero": None, "secondHero": None}]}},
        "resources": {"Silver": 17633693.08, "Gem": 197.0, "Energy": 123.0,
                      "Orb_MagicLow": 37.0, "Orb_VoidHigh": 12.0, "CursedCity_Key": 8.0},
        "blackMarketItems": {"SkillUpgradeItemEpic": 12, "SkillUpgradeItemLegendary": 1},
        "doubleAscendSoulCount": {"15300100": 1, "11301510": 2},
        "accountStatistics": {"factionWars": {"stars": 127}},
    }


def relic_data():
    return {"relicTypes": [{"id": 1, "name": "Unholy Grail", "rarity": 3}],
            "relicStoneTypes": []}


def run_cli(path, *args):
    proc = subprocess.run([sys.executable, "-I", str(SCRIPT), str(path), *args],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, data, name="artifacts.json"):
        p = self.dir / name
        p.write_text(json.dumps(data), encoding="utf-8")
        return p


class Loading(Base):
    def test_gen1_has_no_file_version(self):
        r = rr.Roster(rr.load(self.write(gen1_roster())))
        self.assertEqual(r.gen["generation"], 1)

    def test_gen2_is_file_version_1_3(self):
        r = rr.Roster(rr.load(self.write(gen2_roster())))
        self.assertEqual(r.gen["generation"], 2)

    def test_unknown_version_parses_with_a_warning(self):
        data = gen2_roster()
        data["fileVersion"] = "2.0"
        r = rr.Roster(rr.load(self.write(data)))
        self.assertIsNone(r.gen["generation"])
        self.assertTrue(any("fileVersion" in w for w in r.warnings))

    def test_zip_with_artifacts_json_entry(self):
        p = self.dir / "export.zip"
        with zipfile.ZipFile(p, "w") as zf:
            zf.writestr("artifacts.json", json.dumps(gen2_roster()))
        r = rr.Roster(rr.load(p))
        self.assertEqual(len(r.heroes), 3)

    def test_utf8_bom_is_accepted(self):
        p = self.dir / "bom.json"
        p.write_bytes(b"\xef\xbb\xbf" + json.dumps(gen1_roster()).encode())
        self.assertEqual(len(rr.Roster(rr.load(p)).heroes), 3)

    def test_rejects_non_roster_json(self):
        with self.assertRaises(rr.RosterError):
            rr.load(self.write({"champions": []}))

    def test_cli_error_is_json_with_exit_2(self):
        code, out = run_cli(self.dir / "missing.json", "summary")
        self.assertEqual(code, 2)
        self.assertIn("error", json.loads(out))


class Privacy(Base):
    def test_account_id_and_name_never_printed(self):
        p = self.write(gen2_roster())
        for args in (["summary"], ["heroes"], ["hero", "Arbiter"], ["gear"], ["factions"]):
            code, out = run_cli(p, *args)
            self.assertEqual(code, 0, args)
            self.assertNotIn(ACCOUNT_ID, out, args)
            self.assertNotIn(ACCOUNT_NAME, out, args)

    def test_summary_says_what_was_redacted(self):
        s = rr.Roster(rr.load(self.write(gen2_roster()))).summary()
        self.assertEqual(s["redacted"], ["id", "name"])


class Encoding(Base):
    def setUp(self):
        super().setUp()
        self.r = rr.Roster(rr.load(self.write(gen2_roster())))

    def test_percent_fractions_become_percents(self):
        gloves = self.r.artifacts[3]
        self.assertEqual(gloves["main"]["stat"], "HP%")
        self.assertEqual(gloves["main"]["value"], 60.0)

    def test_flat_and_percent_hp_are_distinct(self):
        boots = self.r.artifacts[1]
        hp = [b for b in boots["subs"] if b["kind"] == "Health"][0]
        self.assertEqual(hp["stat"], "HP%")
        self.assertEqual(self.r.artifacts[5]["main"]["stat"], "HP")

    def test_glyph_adds_to_substat_total(self):
        spd = [b for b in self.r.artifacts[1]["subs"] if b["kind"] == "Speed"][0]
        self.assertEqual(spd["total"], 14.0)

    def test_value_already_in_percent_is_flagged_not_multiplied(self):
        data = gen1_roster()
        data["artifacts"][2]["primaryBonus"]["value"] = 60
        r = rr.Roster(rr.load(self.write(data)))
        self.assertEqual(r.artifacts[3]["main"]["value"], 60.0)
        self.assertTrue(any("already a percent" in w for w in r.warnings))

    def test_type_id_gives_base_and_ascension(self):
        arb = self.r.heroes[0]
        self.assertEqual(arb["baseTypeId"], 1230)
        self.assertEqual(arb["ascension"], 6)

    def test_mythic_rarity_normalised(self):
        self.assertEqual(self.r.artifacts[6]["rarity"], "Mythical")

    def test_known_set_mapped_with_confidence(self):
        self.assertEqual(self.r.artifacts[1]["set"], "Speed")
        self.assertEqual(self.r.artifacts[1]["mapping"], "high")
        self.assertEqual(self.r.artifacts[3]["set"], "Perception")
        self.assertEqual(self.r.artifacts[3]["mapping"], "medium")

    def test_unknown_set_passes_through_raw(self):
        a = self.r.artifacts[6]
        self.assertEqual(a["set"], "MercurialSomething")
        self.assertEqual(a["mapping"], "unmapped")
        self.assertTrue(any("MercurialSomething" in w for w in self.r.warnings))

    def test_cloak_is_the_amulet_slot(self):
        data = gen1_roster()
        data["artifacts"].append(art(7, "Cloak", "None", bonus("CriticalDamage", 0.2, False), []))
        r = rr.Roster(rr.load(self.write(data)))
        self.assertEqual(r.artifacts[7]["slot"], "Amulet")
        self.assertIsNone(r.artifacts[7]["set"])

    def test_mastery_id_decodes_tree_and_tier(self):
        m = {x["name"]: x for x in self.r.heroes[0]["masteries"]}
        self.assertEqual(m["Warmaster"]["tree"], "Offense")
        self.assertEqual(m["Warmaster"]["tier"], 6)
        self.assertEqual(m["Lore of Steel"]["tree"], "Support")
        self.assertEqual(m["Lore of Steel"]["tier"], 4)

    def test_faction_labels(self):
        self.assertEqual(self.r.heroes[0]["faction"], "Banner Lords")
        self.assertEqual(self.r.artifacts[6]["factionLock"], "Banner Lords")


class Ownership(Base):
    def setUp(self):
        super().setUp()
        self.r = rr.Roster(rr.load(self.write(gen2_roster())))

    def test_reverse_index_from_hero_artifact_lists(self):
        self.assertEqual(self.r.artifacts[1]["ownerName"], "Arbiter")
        self.assertIsNone(self.r.artifacts[4]["owner"])

    def test_empty_slots_and_set_counts(self):
        g = self.r.heroes[0]["gear"]
        self.assertEqual(g["emptyArtifactSlots"], ["Weapon", "Helmet", "Shield"])
        self.assertEqual(g["sets"], {"Speed": 2, "Perception": 1})

    def test_approx_stats_add_gear_and_label_themselves(self):
        s = self.r.heroes[0]["approxStats"]
        self.assertEqual(s["SPD"], 100 + 45 + 14 + 5 + 4)
        self.assertEqual(s["ACC"], 10 + 20 + 96)
        self.assertEqual(s["HP"], round(15000 * (1 + 0.66)))
        self.assertEqual(s["C.RATE"], 15.0)
        self.assertIn("approximate", s["label"])

    def test_hero_without_artifacts_key_is_tolerated(self):
        kael = self.r.heroes[1]
        self.assertEqual(kael["gear"]["equipped"], 0)
        self.assertEqual(len(kael["gear"]["emptyArtifactSlots"]), 6)

    def test_dangling_equipped_id_is_warned(self):
        data = gen1_roster()
        data["heroes"][0]["artifacts"].append(999)
        r = rr.Roster(rr.load(self.write(data)))
        self.assertTrue(any("not in the artifacts list" in w for w in r.warnings))


class Reports(Base):
    def setUp(self):
        super().setUp()
        self.r = rr.Roster(rr.load(self.write(gen2_roster())))

    def test_summary_excludes_food_and_counts_built(self):
        s = self.r.summary()
        self.assertEqual(s["counts"]["champions"], 2)
        self.assertEqual(s["counts"]["fodderAndFood"], 1)
        self.assertEqual(s["counts"]["sixStarLevel60"], 1)
        self.assertEqual(s["greatHall"]["totalLevels"], 18)
        self.assertEqual(s["stageSignal"]["stage"], "Early")
        self.assertEqual(s["shards"], {"ancient": 12, "sacred": 2})
        self.assertEqual(s["unassignedMasteryScrolls"], 40)

    def test_summary_flags_unfinished_masteries(self):
        gaps = self.r.summary()["investmentGaps"]
        self.assertEqual(gaps["sixStarLevel60WithoutAllMasteries"],
                         [{"name": "Arbiter", "masteries": 3}])
        self.assertEqual(gaps["ascensionBelowRank"][0]["name"], "Kael")

    def test_summary_lists_blind_spots(self):
        self.assertTrue(any("base stats" in b for b in self.r.summary()["blindSpots"]))

    def test_gear_speed_ranking_and_upgrade_candidates(self):
        g = self.r.gear()
        self.assertEqual(g["topSpeedSubstatPieces"][0]["id"], 5)
        self.assertEqual([p["id"] for p in g["speedUpgradeCandidates"]], [5])
        self.assertEqual(g["speedBoots"][0]["id"], 1)

    def test_sell_candidates_are_unequipped_non_mythical_with_reasons(self):
        sell = {p["id"]: p for p in self.r.gear()["sellCandidates"]["pieces"]}
        self.assertEqual(set(sell), {4})
        self.assertEqual(len(sell[4]["reasons"]), 3)

    def test_factions_readiness(self):
        f = self.r.factions()["factions"]
        self.assertEqual(f["Banner Lords"]["ready"], 1)
        self.assertFalse(f["Banner Lords"]["canField5"])
        self.assertEqual(f["Dark Elves"]["ready"], 1)

    def test_hero_lookup_is_case_and_punctuation_insensitive(self):
        self.assertEqual(self.r.hero_detail("arbiter")["matches"][0]["name"], "Arbiter")
        with self.assertRaises(rr.RosterError):
            self.r.hero_detail("Nobody")

    def test_heroes_min_stars_filter(self):
        rows = self.r.hero_rows(min_stars=6)["heroes"]
        self.assertEqual([h["name"] for h in rows], ["Arbiter"])

    def test_missing_optional_top_level_keys(self):
        data = {"heroes": copy.deepcopy(gen1_roster()["heroes"])}
        r = rr.Roster(rr.load(self.write(data)))
        s = r.summary()
        self.assertEqual(s["counts"]["artifacts"], 0)
        self.assertEqual(s["greatHall"]["totalLevels"], 0)

    def test_heroes_cli_is_valid_json_one_row_per_line(self):
        code, out = run_cli(self.write(gen2_roster()), "heroes")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)["heroes"]), 2)
        self.assertTrue(any(line.strip().startswith('{"id": 100') for line in out.splitlines()))

    def test_main_prints_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = rr.main([str(self.write(gen2_roster())), "summary"])
        self.assertEqual(code, 0)
        self.assertIn("counts", json.loads(buf.getvalue()))


class HellHades(Base):
    def setUp(self):
        super().setUp()
        self.path = self.write(hh_roster(), "raid_account.json")
        self.r = rr.Roster(rr.load(self.path), {1: "Unholy Grail"})

    def test_detected_as_hellhades(self):
        self.assertEqual(self.r.gen["generation"], "hellhades")

    def test_names_come_from_hero_types(self):
        self.assertEqual([h["name"] for h in self.r.heroes], ["Arbiter", "Horned Viper"])

    def test_integer_enums_decode(self):
        arb = self.r.heroes[0]
        self.assertEqual((arb["stars"], arb["rarity"], arb["faction"], arb["role"],
                          arb["affinity"]),
                         (6, "Legendary", "The Sacred Order", "Support", "Magic"))
        boots = self.r.artifacts[1]
        self.assertEqual((boots["slot"], boots["rank"], boots["rarity"], boots["set"]),
                         ("Boots", 6, "Legendary", "Speed"))
        self.assertEqual(self.r.artifacts[3]["slot"], "Amulet")

    def test_missing_is_absolute_means_percent(self):
        gloves = self.r.artifacts[2]
        self.assertEqual(gloves["main"]["stat"], "C.RATE")
        self.assertTrue(gloves["main"]["percent"])
        self.assertEqual(gloves["main"]["value"], 50.0)
        hp = [b for b in self.r.artifacts[1]["subs"] if b["kind"] == "Health"][0]
        self.assertEqual((hp["stat"], hp["value"], hp["rolls"]), ("HP%", 6.0, 0))

    def test_missing_level_is_zero(self):
        self.assertEqual(self.r.artifacts[3]["level"], 0)

    def test_unknown_set_id_is_shown_raw(self):
        a = self.r.artifacts[4]
        self.assertEqual((a["set"], a["mapping"]), ("set #60", "unmapped"))

    def test_faction_17_is_argonites_and_marked_inferred(self):
        viper = self.r.heroes[1]
        self.assertEqual(viper["faction"], "Argonites")
        self.assertEqual(viper["factionMapping"], "inferred")
        self.assertEqual(self.r.artifacts[3]["factionLock"], "Argonites")

    def test_awakening_blessing_relics_and_ascension(self):
        arb = self.r.heroes[0]
        self.assertEqual((arb["ascension"], arb["awakening"], arb["blessingId"]), (6, 2, 1102))
        self.assertEqual(arb["relics"][0]["name"], "Unholy Grail")
        self.assertEqual(self.r.artifacts[1]["ascension"]["bonus"]["total"], 2.0)

    def test_relic_without_relic_data_says_how_to_name_it(self):
        r = rr.Roster(rr.load(self.path))
        self.assertIn("--relic-data", r.heroes[0]["relics"][0]["name"])

    def test_approx_stats_skip_unscaled_hp_atk_def(self):
        s = self.r.heroes[0]["approxStats"]
        self.assertIsNone(s["HP"])
        self.assertIsNone(s["ATK"])
        self.assertEqual(s["SPD"], 110 + 45 + 14 + 2)
        self.assertEqual(s["ACC"], 10 + 20)
        self.assertEqual(s["C.RATE"], 15 + 50)
        self.assertIn("before rank and level", s["label"])

    def test_skills_and_masteries(self):
        arb = self.r.heroes[0]
        self.assertEqual(arb["skills"], [{"typeId": 20161, "level": 5},
                                         {"typeId": 20162, "level": 3}])
        self.assertEqual([m["name"] for m in arb["masteries"]], ["Warmaster", "Lore of Steel"])

    def test_summary_account_block(self):
        s = self.r.summary()
        self.assertEqual(s["arenaLeague"], "Silver IV")
        acct = s["account"]
        self.assertEqual(acct["resources"]["Silver"], 17633693)
        self.assertEqual(acct["books"], {"Rare": 0, "Epic": 12, "Legendary": 1})
        self.assertEqual(acct["potions"]["Magic"]["lesser"], 37)
        self.assertEqual(acct["keys"], {"CursedCity_Key": 8})
        self.assertEqual(acct["awakeningSouls"], 3)
        self.assertEqual(s["factionGuardians"]["Argonites"], {"slots": 2, "filled": 1})
        self.assertEqual(s["greatHall"]["totalLevels"], 5)
        self.assertEqual(s["counts"]["sixStarLevel60"], 1)
        self.assertEqual(s["investmentGaps"]["builtWithoutBlessing"], [])

    def test_blind_spots_are_the_hellhades_ones(self):
        self.assertIs(self.r.blind_spots, rr.BLIND_SPOTS_HH)

    def test_account_identifiers_dropped_and_never_printed(self):
        s = self.r.summary()
        self.assertEqual(s["redacted"], ["userId", "name", "userName", "clanId", "clanName",
                                         "createdOn", "accountCreatedOn"])
        rp = self.write(relic_data(), "raid_relic_data.json")
        for args in (["--relic-data", str(rp), "summary"], ["heroes"], ["hero", "Arbiter"],
                     ["gear"], ["factions"]):
            code, out = run_cli(self.path, *args)
            self.assertEqual(code, 0, args)
            for secret in (str(HH_USER_ID), ACCOUNT_NAME, HH_CLAN, "4242"):
                self.assertNotIn(secret, out, (args, secret))

    def test_heroes_rows_carry_awakening_and_blessing(self):
        row = self.r.hero_rows()["heroes"][0]
        self.assertEqual((row["awakening"], row["blessingId"]), (2, 1102))

    def test_relic_data_given_as_roster_is_explained(self):
        with self.assertRaises(rr.RosterError) as e:
            rr.load(self.write(relic_data(), "relics.json"))
        self.assertIn("--relic-data", str(e.exception))


if __name__ == "__main__":
    unittest.main()
