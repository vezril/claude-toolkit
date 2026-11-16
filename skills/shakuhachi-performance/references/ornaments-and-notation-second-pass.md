# The Shakuhachi: Ornament Vocabulary, Notation and Pedagogy (independent second pass)

Sections 5–10, continuing the earlier file (posture, fingering, meri/kari, registers).
Every claim is tagged `[V]` (verified — artifact named) or `[U]` (unverified — gap named).
All fetches **2026-11-13** unless stated. Translations from Japanese are mine (the
researcher's) unless attributed to a published translator.

## Sources this part rests on, in descending order of authority

| # | Source | What it is | Access |
|---|---|---|---|
| S1 | Riley Lee, *Yearning for the Bell: A Study of Transmission in the Shakuhachi Honkyoku Tradition*, PhD thesis, University of Sydney, 1992 | 417-pp. ethnomusicology thesis by an insider-performer; the standing authority on honkyoku notation vs. oral transmission | Read in full as text. PDF 5.05 MB from `https://content.app-sources.com/s/85453878298607106/uploads/Files/Riley-Thesis-v29-11-10-6869952.pdf`, linked from `https://rileylee.net/phd`. Fetched 2026-11-13, converted with `pdftotext -layout` (12,783 lines / 122,348 words) |
| S2 | 国際尺八研修館 (International Shakuhachi Training Centre, "KSK"), 「ワンポイントアドバイス」 monthly technique columns, 1997–2005, by 柿堺香 Kakizakai Kaoru (resident instructor; the site's named maintainer) | 9 years / ~105 columns of practical pedagogy from the Watazumi→Yokoyama lineage institution. Probably the single richest practical-pedagogy source in existence | `http://www.ksk-shakuhachi.com/全ワンポイントアドバイス/one{97,98,99,2000,01,02,03,04,05}.html`. HTTP-only, Shift-JIS; fetched with plain `curl` + `iconv -f SHIFT_JIS` 2026-11-13. 215 KB of plaintext |
| S3 | ja.wikipedia 「尺八」 | Japanese-language encyclopedia article; unusually well-sourced for a Wikipedia music article (cites 中塚竹禅 1979 and 月渓恒子 2008) | `https://ja.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles=尺八` 2026-11-13 |
| S4 | 公益財団法人 都山流尺八楽会 (Tozan-ryū Shakuhachi Gakkai, public-interest foundation), official site, pages 「都山流の資格 免状・免許状」 and 「免許状申請手続きについて」 | The school's own statement of its licensing system | `https://www.tozanryu.com/about-tozanryu/shikaku/` and `/member/license/` 2026-11-13 |
| S5 | 葛山幻海 Katsurayama Genkai, 尺八修理工房幻海 (Shakuhachi Repair Studio Genkai), 「尺八の吹き方、色々〜ユリから特殊技法まで〜」 parts ①–⑤ | A professional maker/repairer and author (『まるごと尺八の本』, ¥1600) classifying the whole ornament vocabulary **with per-school attributions**. **Commercial** — the pages advertise his book and his lessons. Practitioner authority, not peer-reviewed | `http://shakuhachi-genkai.com/practice/practice{12,13,14,15,16}.html` 2026-11-13 |
| S6 | 尺八.net glossary, 奏法 category | Anonymous informational site ("supervised by a shakuhachi performer", no named author). **Treat as tertiary; possibly SEO/AI-generated.** Used only for corroboration | `https://xn--45q56x.net/glossary-category/technique/` 2026-11-13 |

**How to read my S1 locators.** Three-digit numbers ("S1 thesis p. 145") are the
thesis's own printed page numbers, as they appear in the PDF. **Four- and five-digit
numbers ("S1 thesis p. 4526", "p. 10891") are LINE NUMBERS in my `pdftotext -layout`
extraction, not thesis pages** — I used them to keep passages findable and did not
convert them. Any quotation is verbatim either way; to resolve a bare line number, download
the thesis from `rileylee.net/phd` and extract it with `pdftotext -layout`.

### Sources I could not read

- **Deschênes, "Le shakuhachi japonais, ou l'Occident qui s'orientalise?", *Horizons philosophiques* 16(1) (2005): 136, DOI 10.7202/801311ar.** Érudit is open access but now sits behind an **Anubis proof-of-work JS challenge**; plain `curl` returns the challenge page, not the article. `[U]` — I have not read it and make no claim about its contents beyond its existence. (Fetch attempted 2026-11-13.)
- **Lee 1991 (*Musica Asiatica*) and Lee 1988 (*Asian Music*)** — metadata verified via Crossref only (below). I read Lee's own summaries of both **inside the thesis**, which is why the substantive claims below cite the thesis page, not the articles.
- **Karl Signell, "The Mystique of the Shakuhachi", *JAMIS* 1981** `[U]` — not located in full text; see §10b.

Crossref metadata verified 2026-11-13 (`api.crossref.org`):

| Citation | Verified fields |
|---|---|
| Lee, "Fu Ho U vs. Do Re Mi: The Technology of Notation Systems and Implications of Change in the Shakuhachi Tradition of Japan" | DOI 10.2307/833867, *Asian Music* **19**(2), p. 71, 1988 `[V]` — note **p. 71**, not the page sometimes cited |
| Lee, "Shakuhachi honkyoku notation: written sources in an oral tradition" | DOI 10.1017/cbo9780511896071.003, *Musica Asiatica*, pp. 18–35, 1991 `[V]` |
| Lependorf, "Contemporary Notation for the Shakuhachi: A Primer for Composers" | DOI 10.2307/833414, *Perspectives of New Music* **27**(2), p. 232, 1989 `[V]` |

---

## 5. The ornament and articulation vocabulary

### 5.1 The headline: the vocabulary is not shared

**This is the most important single fact in this section, and English-language
accounts almost always suppress it.** There is no pan-shakuhachi ornament
vocabulary. The same physical gesture carries different names in different
lineages; the same name denotes different gestures in different lineages; and some
terms exist only inside one lineage.

Three independent verifications:

1. **A lineage's own senior teacher says the terms are not defined.** Asked by a
   reader how なやし / かむり / 振り differ and whether there is a definition,
   Kakizakai answers: 「結論から申し上げると、『はっきりした使い分けは無さそうだ』ということです」
   — "to put the conclusion first, there does not appear to be any clear
   distinction in usage." He adds that there is no threshold of speed at which one
   name becomes another, and that 振り *furi* seems to have arisen as a noun out of
   coaching phrases like 「振りが浅い」 ("the *furi* is too shallow") and 「もっとえぐって」
   ("gouge it more"). S2, 2003年11月 column. `[V]`
2. **A maker's taxonomy tags nearly every term with a school.** Genkai's five-part
   classification routinely reads "…明暗対山流ではヤラヤラ、琴古流では鈴ゴロ（ゴロ）と表記される"
   ("…in Myōan Taizan-ryū it is written *yarayara*, in Kinko-ryū *suzugoro*
   (*goro*)"). S5 part ④. `[V]`
3. **Lee documents the same symbol being given new, lineage-specific meanings** as
   one of four standing categories of notation/performance discrepancy (§6.6
   below). S1, thesis pp. 145–146. `[V]`

A fourth, structural reason: Tozan-ryū has **no classical honkyoku at all** in its
repertoire (S1, thesis p. 436, p. 4526ff., p. 4988: "the Kinko ryû, with thirty-six
pieces, and the Tozan ryû, with [none]") `[V]`. A school that does not play koten
honkyoku has no occasion to name the koten-honkyoku ornaments, and *vice versa*.
So the vocabulary gap is partly a repertoire gap.

### 5.2 Breath and tone-colour techniques (吹奏法群)

Genkai's first group (S5 part ①) `[V]` for the list and the glosses; physical
detail on *muraiki* and *tamane* corroborated independently from S2.

| Term | Chars | Rōmaji | What the player does | Sound | Schools |
|---|---|---|---|---|---|
| ムラ息 | ムラ息 / 斑息 | *muraiki* | Large volume of breath driven abruptly so that the airstream partly **misses** the blowing edge. Kakizakai's decomposition: (a) *make a muraiki timbre* by **narrowing the oral cavity** (raise the tongue to constrict the air path) — his analogy is pinching a garden hose 10 cm back from the nozzle to make the water break up; this works **even at low volume**; (b) *aim strong breath at the sounding point* — strong breath straightens and therefore overshoots forward of the usual point, so blow "a little further in" than normal and **open the lip aperture wider**, not tighter | Breathy, hoarse, forceful; the "signature" shakuhachi sound to non-players | Universal in koten honkyoku and in contemporary writing; not school-specific. S2 97年5月, S5 ① `[V]` |
| 玉音 | 玉音 | *tamane* | **Flutter made in the throat, not with the tongue.** Kakizakai gives two principal methods, plus a third he does not name: (A) one method with larger, slower "grains"; (B) **vibrating the uvula** (口蓋垂) by narrowing the throat so the uvula closes the gap — his instruction is literally "think of snoring; lie on your back and snore deliberately, inhaling snores count too." Both methods tend to stop when you form the embouchure, so relaxation is the whole trick. Genkai's gloss: "vibrate the throat as when gargling" | A continuous granular flutter. Lee: "similar to flutter tonguing, except that the uvula is 'fluttered' instead of the tongue. The result is a **softer** sound" | Koten honkyoku generally; in Kinko-notated repertoire it marks the 鉢返し *hachigaeshi* section of 鈴慕-family pieces. S2 99年8月+9月, S5 ①, S1 thesis p. 213 + fn 123 `[V]` |
| フラッター | — | *furattā* (flutter) | Tongue flutter, i.e. the Western flute technique, **imported as a substitute for *tamane*** | Lighter than *tamane* | Modern; borrowed. S5 ① `[V]` |
| 浅音 / 浅息 / カスレ | 浅音 | *asane* / *asaiki* / *kasure* | Breath deliberately off the edge like *muraiki* but **soft** — not strong or violent | Soft, airy, veiled | S5 ① `[V]`; school attribution not given `[U]` |
| 空音 / 空息 / 笹音 | 空音 | *sorane* / *soraiki* / *sasane* | Off-edge blowing **between** *asane* and *muraiki* in force | Mid-strength breathy tone | S5 ① `[V]`. **Caution:** Genkai notes 空音 is also used in a completely different sense, like 虚吹 `[V]` |
| 虚吹き | 虚吹き | *karabuki* / *kyosui* | Deliberately coreless, pitchless-feeling blowing | "Wandering in emptiness" | S5 ① `[V]` |
| 棒吹き | 棒吹き | *bōbuki* | Constant pressure, **no** swell or decay — i.e. plain | Flat/straight | S5 ① `[V]` |
| 楔吹き | 楔吹き | *kusabibuki* | Loudest at the attack, then a steady decay to nothing. **No *yuri*.** Named for the wedge/cuneiform shape of the envelope | Like a decrescendo, "though the underlying idea is entirely different" (Genkai) | **Especially common in certain Myōan lineages** (Lee); listed without attribution by Genkai. S1 thesis fn 104, S5 ① `[V]` |
| 笹吹き | 笹吹き | *sasabuki* | Soft → loud → soft, fattest in the middle like a bamboo-grass leaf. No *yuri*. One breath | Lens-shaped envelope | S5 ① `[V]` |
| 鼓吹き | 鼓吹き | *tsuzumibuki* | Loud → soft → loud, **thinnest in the middle**, like a hand-drum body or a weight. *Yuri* sometimes added. One breath | Hourglass envelope | S5 ① `[V]` |
| ツブシ / ウカシ | — | *tsubushi* / *ukashi* | Deliberately "crush" / obscure the attack of a note | Indistinct onset. Genkai: **almost impossible on a modern *ji-nuri* (lacquer-bore) flute; works mainly on *ji-nashi* and mainly in the low (乙 *otsu*) register** | S5 ① `[V]` |
| シズメ吹き | 沈め吹き | *shizumebuki* | Jaw up/down plus breath acceleration/deceleration to imitate a repeated-note effect | Varies with direction and depth of the head motion | S5 ① `[V]`; school not given `[U]` |
| 吟 | 吟 | *gin* | On チ *chi* only (エ *e* in Myōan Shinpō-ryū): on a *ji-nashi* flute hole 3 sits sharp by construction, so one normally *meri*s it down to pitch. *Gin* deliberately **uses that sharp pitch**, pushing up into it | A sharpened, strained チ | Myōan Shinpō-ryū naming given; S5 ① `[V]` |
| 吼声 / 獅子吼 | 吼声 | *kōsei* / *shishiku* | Blow trumpet-fashion rather than flute-fashion | Thick, roaring | Contemporary works and **海童道 Watazumi-dō pieces**. S5 ⑤ `[V]` |

### 5.3 The ユリ *yuri* family

*Yuri* is **not** breath vibrato by default — it is the name of a family of
**pitch-shaking** gestures made with the head and jaw, with breath-vibrato as one
member. ja.wikipedia 尺八: "by meri/kari, i.e. the up-and-down motion of the jaw
(縦ユリ), or by swinging the head sideways (横ユリ), a kind of vibrato can be applied.
This motion is called ユリ (ユリ、あごユリ). Unlike flute vibrato produced by varying
airflow, this technique has a distinctive lustre. Vibrato by airflow variation, as
on the flute, is also used; this is called 息ユリ." `[V]`

| Term | Chars | Rōmaji | Gesture | Sound | Schools |
|---|---|---|---|---|---|
| 横ユリ | 横揺 | *yoko-yuri* | Swing the **head left–right** | Both schools use head motion but **differently**: Tozan's is modelled on a singer's vibrato — on long tones you blow straight (棒吹き) for 1–1½ beats first, *then* begin the *yuri*, giving a swell. Kinko's is **faster and finer and usually starts at the note's onset**, and its purpose is "to connect smoothly to the next note" rather than "to make the note sound pretty" | **Tozan and Kinko, with explicitly different styles.** S5 ② `[V]` |
| 縦ユリ | 縦揺 | *tate-yuri* | **Jaw / head up–down** — i.e. oscillating *meri*↔*kari* | Wider and larger pitch excursion than *yoko-yuri*; Genkai: **often used as a substitute for a repeated-note figure (打ち)** | Both; S3 + S5 ② `[V]` |
| あごユリ | 顎揺 | *ago-yuri* | Named in S3 as a synonym for *yuri* produced at the jaw | — | S3 `[V]` |
| 息ユリ | 息揺 | *iki-yuri* | Vary **breath strength**, not pitch geometry | Genkai: effectively a **tremolo (amplitude) rather than a vibrato (pitch)**; can be run on smoothly out of a *muraiki*, or made fine "like a cicada" | S3, S5 ②, S6 `[V]` |
| 回しユリ | 回し揺 | *mawashi-yuri* | **Rotate** the head — neither purely vertical nor horizontal, describing circles | Smooth, large pitch excursion. Genkai's two sub-variants: 回しユリ（上向き）emphasising the *kari* half, 回しユリ（下向き）emphasising the *meri* half | S5 ② `[V]`. Also attested in a **1983 Japanese commentary** as 「回はしユリ」 *mawashi yuri*, in Lee's translation of Okamoto: a *yuri* "executed by revolving the chin as if drawing circles," with the tail of the note played *meri*. S1 thesis p. 198 `[V]` |
| 平ユリ | 平ユリ | *hira-yuri* | "Common / flat *yuri*" — Okamoto's term, paired with *mawashi yuri*; in Lee's translation the symbol "indicates a *yuri* sound which is an exhalation that is alternately strong-weak-strong-weak, produced while blowing in a manner that is exactly like eating food" | Pulsed | Okamoto 1983, via S1 thesis p. 198 `[V]` |
| 上下揺 | 上下揺 | *jōge-yuri* | "Up-and-down *yuri*" | — | Named by Okamoto alongside *fune no kubi yuri* as further *yuri* types; S1 thesis fn 105 `[V]`. Presumably = 縦ユリ, but **Okamoto does not say so and I will not assume it** `[U]` |
| 舟首揺 | 舟首揺 | *fune no kubi yuri* | Literally "ship's-prow *yuri*"; *fune no kubi* is the spar at the very front of a boat | — | S1 thesis fn 105 `[V]`. **No physical description given in the source.** `[U]` |
| 淘り | 淘り | *yuri* (written 淘) | **Tōhoku-lineage spelling.** Okamoto argues the character is apt: grain in a water-filled container is sorted by shaking the container, and "the sound is shaken when playing the technique. It is like the water that falls from the container, and is **not** the so-called 揺り (shake, sway) technique" | — | **Tōhoku lineage** (奥州系). Okamoto via S1 thesis pp. 198–199 `[V]`. A beautiful, concrete example of §5.1: the same word, a different character, a different claimed concept |
| 底ユリ | 底揺 | *soko-yuri* | Not head motion at all: control of **breath strength and speed** to make a subtle deep wobble. "Often substituted with *yoko-yuri*, but that is not what it is" | "Shakes at a deeper place than the other *yuri*." Its conceit is the lingering ring of a **temple bell** (梵鐘の余韻). Oral teaching: 「底ユリは心でユル」 — "*soko-yuri* is shaken with the heart" | **Specific to the Ōshū (奥州) honkyoku lineages — 布袋軒 Hōtaiken, 松巌軒 Shōganken.** S5 ② `[V]` |
| 押ユリ | 押揺 | *oshi-yuri* | A composite of *yoko-yuri*, *mawashi-yuri* and *iki-yuri* | Also likened to the bell's lingering ring and its swing-back | **Specific to the 越後明暗寺 Echigo Myōanji honkyoku lineage.** S5 ② `[V]` |
| 手ユリ | 手揺 | *te-yuri* | Shake the instrument finely **with the hand** | Even tremolo rather than vibrato; used to depict the fine-grained tail of a repeated-note figure. Genkai: "sometimes also called 縦ユリ" — another vocabulary collision | S5 ② `[V]` |
| 指ユリ | 指揺 | *yubi-yuri* | Partially open and close a finger hole to shake the note | — | S6 only `[V]` for the term's existence; low-authority source |
| 首ユリ / 首振り | 首揺 / 首振り | *kubi-yuri* / *kubifuri* | Swinging the head/neck. **Genkai treats 首振り as a distinct named technique, not a synonym of *yoko-yuri***: a *single* abrupt swing producing "a sudden valley in the sound," the character of which depends entirely on the speed | In koten honkyoku it mostly follows 押し *oshi* or 打ち *uchi*; **in Tozan it is often notated with an explicit instruction such as "fold/bend on beat N" (○拍目で折る)** — i.e. metrically placed. In the 道曲 *dōkyoku* (Watazumi) repertoire it is **sometimes called カムリ *kamuri*** | S5 ①, S6 `[V]` |
| 大ユリ | 大揺 | *ō-yuri* | **NOT VERIFIED.** The term does not occur in S1, S2, S3, S5 or S6. Nine years of KSK columns contain zero instances of 大ユリ. It is plausibly a descriptive phrase ("big *yuri*") rather than a technical term, or school-specific beyond my sources | — | `[U]` — **flagged rather than glossed.** Do not state a definition for 大ユリ on the strength of English-language sources |

**Correction worth noting:** Kakizakai — teaching in a Kinko-notated koten honkyoku
lineage — states flatly that 「特に国際尺八研修館の講習会で取り上げる古典本曲ではビブラートはつけません」:
"in particular, **in the koten honkyoku we teach at the KSK we do not apply
vibrato**." He describes habitual vibrato as the commonest fault he sees, and
notes that students typically "apply too much of it but it is too small." S2
97年10月. `[V]` The English picture of honkyoku as pervasively vibrato-rich is at
odds with at least one major lineage's own instruction.

### 5.4 Finger attacks: 打ち *uchi*, 押し *oshi*, and the figures built from them

| Term | Chars | Rōmaji | What the player does | Sound | Schools |
|---|---|---|---|---|---|
| 打ち / 指打ち | 打ち | *uchi* / *yubi-uchi* | **Lift the finger high and strike the hole** (not stop the breath). The breath is continuous; the articulation is entirely in the finger. Named variants by target hole: ツル *tsuru* = hole 1; レエ *ree* = hole 2 by default; チリ *chiri* = hole 3 by default; ハラ *hara* (also written ア) = hole 4; ウル *uru* = hole 3 by default | Percussive re-articulation. **Speed is the whole aesthetic:** new pieces, *sankyoku* and contemporary works are struck fast; **koten honkyoku is struck slow — colloquially 鈍打 *donta*, "dull strike."** | Both schools; the *name set* (ツル/レエ/チリ/ハラ/ウル) is **notation-derived and therefore school-specific**. S5 ④ `[V]` |
| 五孔の打ち | 五孔の打ち | *gokō no uchi* | The thumb-hole (hole 5) strike; a whole KSK column is devoted to it, and a second to continuous hole-5 strikes (五孔の連続打ち) | — | KSK/Kinko-notation lineage. Kakizakai: 「どうしても親指を離すと尺八の保持が不安定になってしまう場合は持ち方が良く無い」 — if releasing the thumb destabilises the hold, the hold is wrong; part of the thumb must **not** be required to stay in contact. S2 2001年5月, 2002年10月, 2004年 `[V]` |
| 打ち（スリ） | — | *uchi (suri)* | **Not** a strike but a **slanting brush/graze across the hole** | A distinctive fricative/affricated noise | **Notated differently by school: Tozan 「ノ」, Kinko 「ル」.** S5 ④ `[V]` |
| 打チツメル | — | *uchi-tsumeru* | **Two different meanings** (Genkai says so explicitly): (a) "strike while *meri*-ing" — bending down through the strike; (b) "compress the strikes" — a run of paired strikes progressively dropping | (b) gives "a distinctive rhythm, like a woodpecker pecking a tree" | S5 ④ `[V]` |
| 押し | 押し | *oshi* | **Not** a high strike: keep the finger on the hole and "re-press" it — open it only slightly and immediately close. Also called 送り指 *okuri-yubi*, キザミ指 *kizami-yubi* | Minimal pitch change; the line stays **continuous** rather than being re-attacked | Both. S5 ④ `[V]`. Independently attested in the Okamoto/Lee analysis: in phrase 6 of a *Reibo*, "the 押し (*oshi*, literally 'push') technique is applied to the fourth hole. After this, the *oshi* technique is also applied to the third hole" — and in the second case "a special fingering technique is used. The finger of the third hole is **slid** up and down so as to produce a sound like the *nayashi* technique." S1 thesis p. 199 `[V]` |
| 頭押し | 頭押し | *atama-oshi* | An *oshi* placed as a grace note **before** the beat | **Western equivalent named by Genkai: 短前打音, the short appoggiatura/acciaccatura.** "Sometimes called ハズミ *hazumi*" | S5 ④ `[V]` |
| 押し直し | 押し直し | *oshi-naoshi* | An *oshi* placed as a grace note **after** the beat | 後打音, the Nachschlag | S5 ④ `[V]` |
| 刻み | 刻み | *kizami* | A run of *uchi* or *oshi* at an **even** interval | Steady trill-like pulse | S5 ④ `[V]` |
| 落し | 落し | *otoshi* | **A run of *uchi* or *oshi* that progressively accelerates — or decelerates.** Genkai's instruction: aim for the sound of a 鼓 *tsuzumi* being struck | Accelerating/decelerating pulse | S5 ④ `[V]`. **This is a correction:** English sources sometimes gloss オトシ *otoshi* as a falling pitch gesture. In the one named-practitioner taxonomy I could read it is a **rhythmic** device on a repeated-note figure, not a pitch drop. Note separately that 瀧落シ *taki-otoshi*, "falling waterfall", is a **section title** inside honkyoku, not an ornament (S1 thesis p. 10891) `[V]` — the two are easy to confuse |
| 刻み-落し | — | *kizami-otoshi* | Skilful combination of *kizami* and *otoshi* | Close to もみ手 *momide* but with a distinctive rhythmic feel | **The signature technique of 根笹派錦風流 Nezasa-ha Kinpū-ryū.** S5 ④ `[V]` |
| もみ手 | もみ手 | *momide* | A **composite**: two fingers, a *suri-age*, *oshi* on the upper note, *uchi* on the lower, progressively accelerating. Genkai's worked example for ツレ: "ツレー、レツ。ツレー、レツ。…" — *suri-age* on the first ツレ, *oshi* the レ, *uchi* the ツ simultaneously with a *suri-age*, then *oshi* → *uchi* → *suri-age*, repeating | Genkai: "together with *muraiki*, one of the shakuhachi techniques that stays in a lay listener's ear" | S5 ④ `[V]` |
| オドル | 踊る | *odoru* | *Momide* or a repeated-note figure **deliberately broken up so the rhythm is irregular** | Scattered | **Koten honkyoku.** S5 ④ `[V]` |
| あたり / アタリ | 当り | *atari* | Momentary strike-like opening and closing of a hole to put an accent on the onset or the middle of a note | Accent | **Attested in S6 only, and twice in S2 only as the ordinary verb/noun 当り, not as a labelled technique.** `[U]` — the *term* is real in current usage; I could not verify it against a named practitioner or a reference work, and I could not establish which schools use it as a technical term rather than 打ち. **Flagged.** The Japanese sources with real authority all call this family 打ち, not アタリ |
| ハズミ | 弾み | *hazumi* | Listed as a late addition to the 演奏技法群 group, and given as an alternative name for 頭押し | Spring/bounce | S5 ④ `[V]` for the term and the synonymy; no further physical detail `[U]` |
| 吹切 | 吹切 | *fukikiri* | Listed in S5 ④ as a late addition; **no gloss given on the page** | — | `[U]` — term exists in a practitioner's taxonomy, definition not recoverable from my sources |

### 5.5 Pitch slides and bends (ポルタメント群)

Genkai's third group (S5 ③) `[V]`; ja.wikipedia corroborates the first two `[V]`.

| Term | Chars | Rōmaji | What the player does | Schools / frequency |
|---|---|---|---|---|
| スリ上げ | 擦り上げ | *suriage* | **Slide** the finger off the hole (rather than lift it) so the pitch rises without a corner into the next note. ja.wikipedia adds the mechanism: closed → half-open → open executed smoothly, combined with *meri*/*kari*, gives a true portamento | Genkai: "**used constantly, in many pieces**" (常用される). Both schools; S3, S5 ③, S6 `[V]` |
| スリ下げ | 擦り下げ | *surisage* | The descending equivalent (e.g. レ→ツ). Requires the fingers **and** fine jaw control | Genkai: **常用外 — not in the common stock.** A real and useful asymmetry: the ascending slide is idiomatic, the descending one is not. S3 (as スリサゲ), S5 ③, S6 `[V]` |
| スリ | 擦り | *suri* | Distinct from *suriage*: go up momentarily to the neighbouring pitch and **immediately press back to the original**. Example: レ → midway between レ and チ → レ, with a rotating finger motion. Genkai likens it to the 龍笛 *ryūteki* technique in gagaku | S5 ③ `[V]` |
| スリ（消す） | — | *suri (kesu)* | **Use a *suri-age* to make the note disappear instead of chopping it off**, when stealing a breath (カンニングブレス / 息盗み) mid-phrase. The conceit is to make the listener hear the line as continuous across the breath. **On hole 5 this is specifically called 抜き手 *nukite*** | S5 ③ `[V]`. This is the best verified anchor for **ケシ / 消し** — see the row below |
| メリ込み（カザシ） | — | *merikomi (kazashi)* | Drop the jaw into *meri* (optionally with a *kazashi*, a partial shading of a hole) so a **hollow or dimple** forms in the line. Close to 首振り but "stickier, more viscous"; **in Tozan it is lighter/drier (サラッとしている)** | Present in koten honkyoku, but **especially常用 in Kinko**. Also called 引く *hiku* or 折（オル）*oru*. S5 ③ `[V]` |
| メリ込み（消す、引く） | — | *merikomi (kesu / hiku)* | End of a phrase: rather than cutting the note dead, **let it vanish while *meri*-ing down** | Also called 引く or 折. S5 ③ `[V]` |
| メリ込みスリ | — | *merikomi-suri* | *Merikomi* → back to true pitch → *suri-age* → back to true pitch | S5 ③ `[V]` |
| メリ込みスリ上げ | — | *merikomi-suriage* | *Merikomi* → true pitch → *suri-age* → and let it vanish from there | S5 ③ `[V]` |
| スリメリ | — | *suri-meri* | *Suri* then *meri* — e.g. レ → between レ and チ → レ → レのメリ → レ. The inverse of *merikomi-suri* | S5 ③ `[V]` |
| ナヤシ（琴古） | 撫やし | *nayashi* (Kinko) | **Kinko sense:** at the head of a phrase, start from a jaw-*meri* below and return up to true pitch. Example: ロのメリ → ロ. Sometimes a 首振り follows the *nayashi* | **Especially常用 in Kinko**, plus some koten honkyoku. S5 ③, S6 `[V]` |
| ナヤシ（明暗） | — | *nayashi* (Myōan) | **Myōan sense: a different technique with the same name.** Swing the head along a trajectory that **traces the hiragana 「ん」**, producing an abrupt *meri*→*kari* dip-and-rise. Genkai warns explicitly: "there are also techniques called *nayashi* (Kinko) and the *nayashi* of **Myōan Shinpō-ryū**, so do not confuse them" | **Myōan.** S5 ① `[V]`. **A third, distinct Myōan Shinpō-ryū *nayashi* is asserted to exist but is not described** `[U]` |
| 息ナヤシ | 息撫やし | *iki-nayashi* | Not a pitch bend in the usual sense: with the **same fingering**, alternate 乙 *otsu* and 甲 *kan* blowing continuously — e.g. 二四五のハ played otsu/kan/otsu/kan | **Mainly 明暗真法流 Myōan Shinpō-ryū.** S5 ① `[V]` |
| チギリ | 千切り | *chigiri* | *Nayashi* + 首振り combined, blown **together with コミ吹き**. Unlike Myōan *nayashi* it goes **from an already-*metta* (deeply flattened) state abruptly into *kari* then *meri*** | **The proprietary technique of 根笹派錦風流 Nezasa-ha Kinpū-ryū.** S5 ① `[V]` |
| フリ込み | 振り込み | *furikomi* | A *merikomi* **after** a 首振り. Expression depends on whether the 打ち, the 首振り and the *merikomi* are run together or kept distinct | S5 ① `[V]` |
| 口メリ | 口メリ | *kuchi-meri* | **The historically interesting one.** A *komusō* playing under a 天蓋 *tengai* (deep woven hat) could not bob his jaw without the hat swinging — so *meri*/*kari* were made by **protruding and retracting the lips** instead. Genkai: "**scarcely ever played today**" | Historical / *komusō* practice. S5 ③ `[V]` |
| 韻 | 韻 | *in* | The *lingering-resonance* device: the piece's flow continues **through** the silence after a note stops. Genkai: "treats the absence of sound as weightier than the presence of sound" (音有りよりも音無しを重用とする) | S5 ③ `[V]`. Belongs as much to §7 as to §5 |
| 回し | 回し | *mawashi* | Rotate the head slightly **before** a mid-phrase breath, giving a distinctive lingering resonance; functions like a 合いの手 *ai-no-te* (an interjected response) | S5 ③ `[V]` |
| ケシ / 消し | 消し | *keshi* | **Not verified as a standalone named ornament.** What *is* verified is the **verb** 消す "to make vanish" as a modifier on other techniques: スリ（消す）and メリ込み（消す、引く）above, both meaning "end the note by making it disappear rather than cutting it." Three instances of 消し- forms in nine years of KSK columns, none as a labelled ornament | `[U]` — **flagged.** If an English source gives you "keshi = a technique of fading the note," that is consistent with 消す usage, but I found no Japanese source that treats ケシ as a term in its own right |
| ネヤシ | — | *neyashi* | **Not verified at all.** Zero occurrences in S1, S2, S3, S5, S6. Strong suspicion that this is a **mis-transcription or regional variant of ナヤシ *nayashi*** (ne/na), but I have no source either way | `[U]` — **flagged. Do not gloss.** |

### 5.6 コロコロ *korokoro*, カラカラ *karakara* and the trill family

This is the family where the school-by-school divergence is sharpest and best
documented, so it is worth its own table. All rows S5 ④ unless marked `[V]`;
*korokoro* is also described physically and independently in S2.

| Term | Rōmaji | Fingering / action | Sound | Schools |
|---|---|---|---|---|
| コロコロ | *korokoro* | **KSK/Kinko-notation method (Kakizakai, verbatim):** "open hole 5 slightly, *meri*, and open and close holes 1 and 2 **alternately**." The pitch is **リ** *ri* throughout: "when you play *korokoro* it must be heard as リリリリリリ…". Two named faults: (a) hole 2 open goes sharp, so either *meri* more deeply when 2 is open, or narrow the finger-to-hole gap for 2; (b) if it sounds "ホヨホヨ" *hoyohoyo*, mushy, it is because **holes 1 and 2 are never closed at the same instant** — the cycle must pass through a both-closed state. Practise slowly with a metronome; "ten minutes a day and you will soon be a *korokoro* master" | A rolling, rapid alternation | S2 97年6月 `[V]` for this method, **explicitly as taught at KSK**; S3 describes it generically as "finely repeating the pitch up and down" `[V]` |
| コロコロ（明暗） | *korokoro* (Myōan) | Hole 1 **and** hole 2 both fully closed at the ロ, so the both-closed pitch is actually heard | The ロ is audible as a pitch. Sometimes written ホロホロ | **Myōan** |
| コロコロリン（都山） | *korokororin* (Tozan) | Tozan's *korokoro*; **faster alternation of holes 1 and 2 than Myōan's, with less of the both-closed state**; usually ends with a リン | Genkai: "sonically, 'ko-ko-ko-ko…' is the accurate rendering" — i.e. **it does not actually sound like "koro-koro"** | **Tozan** |
| ホロホロ | *horohoro* | A koten-honkyoku derivative: unlike コロ, **hole 4 is also closed and only hole 5 is open** | Larger pitch swing than *korokoro* | Koten honkyoku |
| コロロー | *kororō* | A slow, twice-through *korokoro*: コ = holes 4 and 5 shaded only, rest closed, *meri*. First ロ opens hole 1 with a deeper *meri*; second ロ opens hole 2, also deeper *meri*; third ロ is an ordinary ロ | "コロー、コロー、ロー". Also written ホロイ or ホロロ | — |
| リン | *rin* | A *koro* done very fast | — | **Tozan**, plus some honkyoku use at phrase heads to mark them; **notated ホロ or コロ in that case** |
| ヒラヒラ | *hirahira* | *Korokoro* **an octave up** | Little pitch change; Genkai: "like dappled sunlight drifting in the air" | Koten honkyoku |
| カラカラ | *karakara* | **Rapid repeated striking of hole 1** on Tozan 甲ハ / Kinko ヒ (including their *meri* and *dai-meri* forms) | "Like a bird twittering." On a poorly made flute it comes out "カッ、カッ、カッ" instead of "カラ、カラ" — colloquially 片カラ *kata-kara* or 片輪 *katawa*; shading or closing hole 2 can compensate | **Named カラカラ generally; written ヤラヤラ in 明暗対山流 Myōan Taizan-ryū and 鈴ゴロ/ゴロ in 琴古流 Kinko-ryū.** This single row is the cleanest proof of §5.1 |
| 鈴ゴロ | *suzugoro* | Nearly the same as *karakara* but the fingers alternate holes 1 and 2 like *korokoro* (sometimes hole 2 alone) | — | **Koten honkyoku; also written ヤラヤラ. In Kinko there are two kinds: 鈴ゴロ (also 片ゴロ *kata-goro*), a repeat of hole 1 (or 2), and ウハゴロ *uhagoro*, a repeat of hole 3 on the ハ fingering** |
| ヤラヤラ | *yarayara* | *Karakara* **in the low register** (乙/呂): repeat hole 1 or hole 3 on Tozan's ハ / Kinko's リ. **In 明暗対山流 it is in the high register and is therefore identical to *karakara*** | — | Attribution differs by school — another §5.1 case |
| フラ | *fura* | **A decomposed *korokoro*:** from holes 1-2-3 closed + holes 4-5 shaded (Kinko: 四五のハ), quickly open-close-open hole 1 or hole 2 | — | **Tozan** |
| コロコロ（玉音） | *korokoro (tamane)* | *Korokoro* **and** *tamane* simultaneously, with jaw *meri*/*kari* | "A bird-call-like, onomatopoeic effect" | Genkai: "said to be among the hardest things on the instrument" |
| サスリ | *sasuri* | Stroking/rubbing the finger holes to get a distinctive continuous noise | — | **Used in Takemitsu's *November Steps*** and in contemporary works generally. S5 ⑤ `[V]` |

### 5.7 込み吹き *komibuki* — and the correction it carries

| Term | Chars | Rōmaji | What it is | Schools |
|---|---|---|---|---|
| コミ吹き / 込み吹き | 込み吹き | *komibuki* | A pulsed, "pumped" breath technique. **Genkai's correction, which matters:** 「吹奏法の一種と誤解されがちだが、本来の意味はユリである」 — "it is commonly **mistaken** for a kind of blowing technique, but its real meaning is a *yuri*." He classifies it in the **vibrato/tremolo group**, not the blowing group, and adds the lineage's own gloss: "it looks like violent motion, but at bottom it means 動中静・静中動 — stillness within motion, motion within stillness." | **根笹派錦風流 Nezasa-ha Kinpū-ryū.** Blown together with チギリ. S5 ② `[V]` |

### 5.8 What a school's note-name set does to its vocabulary

A short but load-bearing point for §6: the *ornament* names are partly derived from
the *note* names, which differ by school. ja.wikipedia 尺八 `[V]`:

| School | The five basic fingerings | Notes |
|---|---|---|
| 琴古流 Kinko | ロ・ツ・レ・チ・リ (in 甲 *kan*: **ヒ**) | ja.wikipedia 尺八 `[V]` |
| 都山流 Tozan | ロ・ツ・レ・チ・**ハ** | ja.wikipedia 尺八 `[V]` |
| 竹保流 Chikuho | **フ・ホ・ウ・エ・ヤ・イ** — a *fu-ho-u* tablature (フホウ譜), inherited from 宗悦流 Sōetsu-ryū, **not** ロツレチ | ja.wikipedia 尺八 `[V]` |

Pitches on a 1.8 *shaku* flute, low register: **D4 (壱越) · F4 (勝絶) · G4 (双調) ·
A4 (黄鐘) · C5 (神仙)**, an octave up in 甲 — a 陽 *yō* / 律 *ritsu* scale. ja.wikipedia
尺八 `[V]`. Hence Genkai's カラカラ row above has to say "Tozan 甲ハ / Kinko ヒ" for
what is the **same note on the same flute**.

Composite figures inherit the note names and therefore cannot cross schools
unchanged — ツレー, ウツレー, ハラロ all name *fingering sequences*:

| Figure | Realisation | School |
|---|---|---|
| ウツレー | Written with a ウ, but the ウ is required to be **strike-noise only, not a sounding pitch**; the ツ is a *tsubushi*-ed (crushed) tone; the ツレ gap is short and quickly slid up; ツ is the emphasised note | **明暗 Myōan.** S5 ④ `[V]` |
| ツレー (Tozan) | Notated ツレ, but played with the **ウ (holes 1+4 open) clearly sounded**, then moving slowly to ツレ, with **ウ・ツ・レ of equal length** | **都山 Tozan.** S5 ④ `[V]` |
| ツレー (Kinko) | Notated ツレ, played as ウツレ — but the ウ has **two forms** (pressing hole 4, or pressing hole 3). Moving on to ツレ, hole 2 is slid up slowly **while** hole 4 (or 3) is re-pressed; "this re-press is purely a device for joining the notes smoothly, so do not emphasise it." **レ is the centre of gravity.** A second, more emphatic realisation also exists | **琴古 Kinko.** S5 ④ `[V]` |
| ハラロ（カル） | Notated ハラロ, actually blown 「ハーイ、ハロー」: 乙 二四五のハ → *kari* → *meri* simultaneously with a hole-2 strike → ロ | **琴古, and partly 明暗.** S5 ④ `[V]` |
| ハラロ（メル） | Notated ハラロ, blown 「ハーハーロー」: 乙 二四五のハ → hole-2 strike → ロ | **琴古, and partly 明暗.** S5 ④ `[V]` |
| ウのまる / ウ0 | ウ (a semitone above レ) **flattened further until it is in unison with レ**. Written as a ウ with a 0, sometimes with the 0 superimposed; spoken 「ウのまる」 | **KSK (Kinko notation), explicitly.** S2 99年11月 `[V]` |
| 三のウ | Named as a technique in the KSK columns (7 occurrences) alongside コロコロ in a passage arguing such techniques were devised over time rather than being original | Term `[V]`; **physical definition not stated in the columns** `[U]` |
| 二指連打 | Double-finger repeats: ツルツル, レエレエ, チリチリ, ウルウル, ハラハラ | S5 ④ `[V]` |
| 鼓打ち | *tsuzumi-uchi* — hold the flute at the shoulder and **strike the bottom end of the tube like a drum**; pitch varies with how far the holes are covered | Contemporary. S5 ⑤ `[V]` |
| 横笛吹き | *yokobue-buki* — blow across **hole 4** as if it were the blowing edge of a transverse flute. Genkai: 曲芸吹き, a stunt to impress an audience | S5 ⑤ `[V]` |
| 倍音奏法 | Overblow the **third partial** rather than the fundamental — e.g. the 3rd partial of ロ equals 甲チ. Genkai: beginners produce it by accident, advanced players on purpose; "regarded as improper (邪道), but worth knowing" | S5 ⑤ `[V]` |

---

## 6. Notation

### 6.1 The shared basis

All the traditional systems share four properties `[V]`:

1. **Katakana-derived tablature.** The symbols are (or derive from) kana standing
   for finger positions. Lee: "the tablature symbols [denote] fingerings and other
   pitch-changing techniques" (S1 thesis p. 7394). `[V]`
2. **It notates actions, not sounds.** Lee's formulation is the clearest statement
   in the literature and is worth quoting exactly: "Honkyoku notation **instructs
   or reminds the performer what to do rather than what sounds to produce. It is
   action or process rather than product oriented.** The symbols of honkyoku
   notation denote fingering positions, articulation methods, and other performance
   techniques. In this respect, it is similar to various tablature systems in other
   musical traditions in depicting the act of performing. In contrast, staff notation
   is product oriented, functioning primarily to prescribe (or describe) the final
   product, the sound." S1 thesis p. 145–146 region (p. 7388–7397 of the text
   extraction). `[V]`
3. **Vertical columns, read top-to-bottom, columns right-to-left.** `[U]` — this is
   universally stated in English sources and is consistent with the KSK column on
   「行の変わり目とフレーズ」 ("line changes and phrases", S2 2000年9月) which
   presupposes the score is organised in 行 *gyō*, lines/columns. **But I did not
   find an explicit statement of the reading direction in any of S1–S6**, because
   all of them are written for readers who can see a score. Mark it as near-certain
   but not sourced here.
4. **Pitch is not notated; duration barely is; timbre is.** Lee's three-way contrast
   with staff notation: "In honkyoku notation, pitch is not notated at all, other
   than indirectly through the tablature symbols denoting fingerings and other
   pitch-changing techniques. Secondly, though durations are notated in general,
   **they are at most used only as a broad and imprecise guide and are frequently
   ignored altogether**, in contrast to the rigid precision of staff notation in
   representing durations (Lee 1991:32-33). Finally, the timbre or tone colour of
   each note, a vital element of honkyoku performance, is directly or indirectly
   indicated by traditional shakuhachi notation. In contrast, timbre is all but
   ignored in the majority of music scores written in staff notation." S1 thesis
   p. 146. `[V]`

### 6.2 The modern systems are younger than the English literature implies

| Fact | Source |
|---|---|
| Notation in the honkyoku tradition "has been in use for **just over 150 years**" (as of 1992 — so from roughly the 1830s–40s) | S1 thesis p. 144, citing Lee 1991:19 `[V]` |
| The **ロツレ *ro-tsu-re* system was devised by 荒木古童 Araki Kodō** (1823–1908) after the abolition of the Fuke sect, "after the three kana symbolizing the first three open-hole finger positions, **which was suitable for notating *sankyoku* pieces**" | S1 thesis p. 4518–4526 `[V]` |
| **That system is the basis of both present-day Kinko notation and Tozan notation** | S1 thesis p. 4524–4526 `[V]` |
| Araki also "improved the finger-hole positions and the *utaguchi*" and spread the instrument nationally from Tokyo; he was 「琴古流中興の祖」, the restorer of Kinko-ryū | ja.wikipedia 尺八 `[V]` |

Two consequences worth stating plainly: (a) the notation that English writers treat
as the ancient tablature of Zen mendicants is a **Meiji-era reform instrument,
designed under pressure to make the shakuhachi usable in secular ensemble music**;
(b) Kinko and Tozan notation are **cousins, not unrelated systems** — the
differences below are differences within one family.

### 6.3 Before notation was printed: the score as a licence

The pre-printing condition is best shown by a single artifact. Lee reproduces (his
Figure 3) and translates a score of 「鹿の遠音」 *Shika no tōne* written in **black
and red ink by Araki Kodō II in the fifth month of Kaei 6 = May 1853** for 廣瀬茂竹
Hirose Mochiku, held by the 山陰尺八道場. `[V]`

**The decisive detail: the musical notation occupies only half the sheet. The other
half is a transmission certificate**, signed 「東京尺八指南 二代目 荒木古童」 ("Tokyo
Shakuhachi Instructor, Second Generation, Araki Kodō"), recording that Mochiku
visited, that they exchanged a *gaikyoku* for a *honkyoku*, and that Kodō
"transmitted, to its completion, a secret piece from this side, a piece called 'Shika
no tōne'." (Lee's translation; S1 thesis pp. 17–18.) `[V]` Lee's reading: "The score
**certifies** that the student now possesses the piece." `[V]`

So the score is not primarily a performance aid. It is the physical receipt for an
oral transfer — which is also Lee's larger thesis about why published notation
exists at all (§6.7).

### 6.4 琴古流 Kinko

| Property | Detail | Source |
|---|---|---|
| Note names | ロ・ツ・レ・チ・リ, with **ヒ** for リ in the 甲 *kan* register | ja.wikipedia 尺八 `[V]` |
| Auxiliary symbols | *meri*/*kari* indicated by **adding auxiliary marks** such as メ or カ to the base symbol | ja.wikipedia 尺八 `[V]` |
| Degrees of *meri* | 中メリ *chū-meri* ("middle *meri*") is a named degree of flattening, not just a direction | S1 thesis fn 103 `[V]` |
| Composite symbols | ウ with a 0 (「ウのまる」) = ウ flattened all the way into unison with レ | S2 99年11月 `[V]` |
| Ornament notation that is school-specific | 打ち（スリ）written 「ル」 (Tozan: 「ノ」); *karakara* written 鈴ゴロ/ゴロ (Myōan Taizan: ヤラヤラ); ハラロ written as three syllables but blown 「ハーイ、ハロー」 or 「ハーハーロー」 | S5 ④ `[V]` |
| Repertoire | **36 honkyoku**, fixed by 初代黒沢琴古 Kurosawa Kinko I (1710–1771), who collected pieces from *komusō* temples around Japan and "organised their notation symbols (譜字) and the order in which they are learned (習曲順)" | ja.wikipedia 尺八 `[V]` |
| Organisational shape | **Kinko is not one organisation.** ja.wikipedia: 「琴古流は大小いくつもの組織の総体であり琴古流として統一した組織をもつものではない」 — an aggregate of organisations large and small with no unified body. Representative societies named: 鈴慕会, 童門会, 竹盟社, 竹友社, **国際尺八研修館** | ja.wikipedia 尺八 `[V]` |
| Conservatism | Lee: Kinko honkyoku, transmitted largely inside organisations, are "conspicuously **resistant to change and variation** when compared with honkyoku transmitted outside such organizations" — in numbers, titles and performance. Its 36 pieces are a fraction of the ~200 honkyoku and variants said to exist (Tukitani 1990a:32) | S1 thesis p. 152 `[V]` |

**Rhythm in Kinko notation.** The honest answer: Kinko honkyoku notation carries
**no metric framework**, and duration is indicated only by the extension stroke
(the 「ー」 that appears throughout the KSK columns, e.g. 「ヒイーーーーヒイーーヒイーヒ」,
S2 2003年10月 `[V]`) plus column/line layout. Kakizakai's own worked example treats
the number of ー marks as showing *relative* length and then explains that the real
performance accelerates through the phrase regardless: 「後半になるに従って流れが早めに
なっていきます」 — "as you get to the later part, the flow becomes faster." `[V]` That
is: the notation shows a shape, the transmission supplies the time. I found **no
numerical statement** of how many kinds of duration mark Kinko notation has `[U]`.

### 6.5 都山流 Tozan — and why it is different

| Property | Detail | Source |
|---|---|---|
| Note names | ロ・ツ・レ・チ・**ハ** | ja.wikipedia 尺八 `[V]` |
| *Meri* indication | Tozan indicates *meri* by **writing the symbol smaller** (譜字を小文字にする), where Kinko adds an auxiliary mark | ja.wikipedia 尺八 `[V]` — a concrete, verifiable difference in notational technique, not just in vocabulary |
| Founding | 初世中尾都山 Nakao Tozan I (1876–1956) founded the school in **Osaka in 1896** | ja.wikipedia 尺八 `[V]` |
| What Tozan deliberately built | ja.wikipedia is explicit that Nakao put out "new departures in **記譜法 (notation method), 教授法 (teaching method), 合奏形式 (ensemble format)**" and built 「近代的な家元制度」, a modern *iemoto* system — and so grew to rival Kinko within a few years | ja.wikipedia 尺八 `[V]` |
| Rhythmic/metric notation | **Explicit and metric.** Genkai's 首振り entry: "in Tozan there are frequently explicit instructions such as 「○拍目で折る」 — *bend on beat N*." Tozan's 横ユリ instruction is likewise counted: blow straight for **1 to 1½ beats**, then begin the *yuri*. Both presuppose a beat the player counts | S5 ①, ② `[V]` |
| Why | The repertoire. Tozan's 本曲 are **Nakao's own modern compositions** for solo or shakuhachi duo; its other repertoire is *sankyoku* and 新日本音楽 ensemble work; it held the **exclusive right to publish the shakuhachi parts of Miyagi Michio's compositions**. Lee: Tozan "**completely excluded** from the repertoire … *koten honkyoku*." Ensemble music with a koto and a shamisen requires a shared beat; solo *suizen* does not | ja.wikipedia 尺八 `[V]`; S1 thesis p. 4554, p. 436 `[V]` |
| Pedagogy | A centrally administered, examined, graded ladder — see §8.2. Lee's footnote records **4,935 licensed teachers in 1984 in the largest of the three Tozan factions** | S4 `[V]`; S1 thesis fn at p. 4559 `[V]` |
| The cost | Lee: Tozan "**actively discourages its members from studying with any teacher who performs classical honkyoku**", and members "were (and in many cases still are) **forbidden** to learn and perform pieces other than those of the official Tozan repertoire"; talented members were barred from playing unauthorised compositions at official Tozan concerts (Kamisangō 1974:21) | S1 thesis pp. 152, 4569–4572 `[V]`. Lee is an ex-Tozan member writing about his own former school — note the position, but the citation to Kamisangō is independent |
| Splits | Tozan split around 1975 (昭和50年前後); three bodies now exist: 都山流尺八楽会, 日本尺八連盟, 新都山流 | ja.wikipedia 尺八 `[V]` |

So the causal story is clean and verifiable: **different repertoire → different
notational requirement → different pedagogy.** Tozan's rhythmic explicitness is not
modernising zeal in the abstract; it is what a school whose music is played
*with other instruments* has to have.

### 6.6 明暗 Myōan and the smaller systems

| System | What is verified |
|---|---|
| 明暗 Myōan | Myōan notation is a distinct system Lee used as a student alongside Chikuho, Kinko and Tozan (S1 thesis p. 7756) `[V]`. The two main modern streams are **明暗真法流 Myōan Shinpō-ryū** and **明暗対山流 Myōan Taizan-ryū**, the latter founded by 樋口対山 Higuchi Taizan (1856–1915), who studied 西園流 and worked to revive the 明暗教会 (ja.wikipedia 尺八) `[V]`. Its ornament vocabulary differs from Kinko's in named, documented ways (§5.6) `[V]`. **I could not obtain a symbol inventory or a statement of how Myōan notates duration** `[U]` |
| 竹保流 Chikuho | Uses a **フホウ譜** *fu-ho-u* tablature — フ・ホ・ウ・エ・ヤ・イ, **not** ロツレチ — inherited from 宗悦流 Sōetsu-ryū. Founded by 酒井竹保 Sakai Chikuho, 1917 (ja.wikipedia 尺八) `[V]`. Historically the oldest attested shakuhachi-family tablature: 宗勳 Sōkun's *Tanteki hiden fu* 『短笛秘伝譜』 already used "a notation system with the katakana *fu*, *ho*, *u*…" in the *hitoyogiri* era (S1 thesis p. 3085) `[V]` |
| 上田流 Ueda | 上田芳憧 Ueda Hōdō, expelled from Tozan, founded it in 1917 and **introduced Western staff notation and the seven-hole shakuhachi**. He **abandoned the staff-notation experiment partway**; the seven-hole flute of his design is still in use (ja.wikipedia 尺八) `[V]`. A rare documented case of a school *trying* staff notation and giving it up |
| 錦風流 Kinpū (根笹派 Nezasa-ha) | Has at least two proprietary techniques with proprietary names, チギリ and 刻み-落し, plus コミ吹き (S5) `[V]`. Notation details not obtained `[U]` |
| Watazumi / Yokoyama ("Dokyoku") | **Watazumi used "an extremely skeletal form of the フホウ *fu ho u* notation system."** Because Yokoyama's students found the *fu ho u* system took too long to learn, "**most of the scores used are written in Kinko notation**, and are more descriptive than the bare bones of Watazumi's scores." S1 thesis p. 9040–9043 `[V]` |

### 6.7 The Watazumi→Yokoyama lineage: Kinko notation, and the hand copy as the authoritative text

This confirms and sharpens the fact given in the usual account.

- **It is a Kinko-notation lineage.** Verified twice: from Lee (above) `[V]`, and from
  the lineage's own teaching material — the KSK column that works through
  「ウーーーウ0」 ends with the parenthesis 「（琴古流の記譜を用いています。）」, "Kinko-ryū
  notation is used here." S2 99年11月. `[V]`
- **Yokoyama refused to publish scores**, "because of the impossibility of creating a
  finished score to his satisfaction. **Scores can only be 'memos' of honkyoku
  itself.**" Over about twenty years he continually revised them, in a **cycle**: add
  detail to describe the piece better → realise the added detail does not represent
  the piece either → simplify again → repeat. By 1992 it was mostly his students
  attempting the notating. S1 thesis p. 9047ff. `[V]`
- **The lesson practice matched.** Lee, as a student of Yokoyama and of Sakai: "As a
  rule, **neither Sakai nor Yokoyama wrote on my score.** If I did not play an
  embellishment or note or phrase as they wished me to or if I omitted something,
  they would tell me and **play the passage in question for me again. It was up to
  me to remember the passage.**" Annotating was permitted but never instructed, in
  either direction. S1 thesis p. 7756ff. `[V]`
- **Verification status of the printed-volume details in the usual account.** The claims that
  the lineage's published score volumes are in Kinko notation *with Tozan available
  on request*, that applicants are asked which notation they read, and that before
  the printed volumes the transmission ran on **one teacher's handwritten scores,
  photocopied and circulated with a warning that they contained errors**, are
  **consistent with everything above but I could not verify them from the KSK site
  or from Lee** `[U]`. The KSK site as it stands in 2026 carries the course
  announcements, the advice archive and a goods PDF, not a score catalogue. The
  underlying pattern *is* verified in Lee: honkyoku manuscript scores "continue to
  be written and used today, and contribute to the variation and change that has
  always occurred", and "it is not unusual to find the existence of **numerous and
  inconsistent manuscript scores for a single koten honkyoku**" (S1 thesis
  pp. 1415–1430) `[V]`.

### 6.8 Western staff notation: when, and what it loses

| Claim | Status |
|---|---|
| Staff-notation use "is **almost entirely limited to modern compositions**" | S1 thesis p. 157 `[V]` |
| **"Scores of classical honkyoku in staff notation exist only as transcriptions in scholarly articles and, to my knowledge, have never been used in actual teaching/learning or performing situations."** | S1 thesis p. 157 `[V]` — this is the direct, authoritative statement of the point: honkyoku in staff notation is a **transcription, not a score**. Dated 1992; I have no evidence either way about 2026 `[U]` |
| Staff notation **caused pitch standardisation** in the tradition, "partly because staff notation denotes pitch while traditional shakuhachi notation denotes fingerings" | S1 thesis p. 157, citing Lee 1988:71–79 `[V]` |
| 上田流 adopted staff notation in 1917 and **later abandoned it** | ja.wikipedia 尺八 `[V]` |
| What staff notation loses: **timbre** (which traditional notation does indicate, directly or indirectly) and the **process/action** orientation; what it adds is rigid duration and absolute pitch | S1 thesis p. 146 `[V]` |
| For contemporary composers, the standard reference on notating shakuhachi in a Western score is **Lependorf, *Perspectives of New Music* 27(2) (1989): 232** | Citation verified via Crossref `[V]`; **I did not read the article** `[U]` — do not attribute content to it |

### 6.9 A published side-by-side of one piece in two notations — found

The briefing asked me to hunt for one. **Lee's thesis Figure 5** is exactly that:

> "For comparison, **Figure 5 presents the same part of two published scores of the
> honkyoku 'Kyūshū reibo', in the original Myōan notation system, and then as
> transnotated into the Tozan notation system.**"
> — S1 thesis p. 1418–1421 `[V]`

Context, which is the interesting part: Lee is documenting a **transnotation
economy**. Players write out, by hand, scores of pieces that are not in their own
lineage's repertoire, in their own notation system, "in an attempt to learn a
honkyoku without being taught by a teacher" — since cassettes, used alongside
recordings by members of the originating lineage. "In the case of Tozan ryû, such
manuscripts have frequently gone the full circle of standardization by being
published (privately) in a Tozan transnotation format. **The demand for such
transnotations is high due to the complete lack of classical honkyoku in the Tozan
ryû repertoire.**" `[V]` He names it as "one way in which numerous variations and
changes occur in honkyoku scores." `[V]`

A second instance of the same genre is named in the thesis: **Lee's own Chapter 6
transcribes and analyses six recorded honkyoku performances into staff notation**
side by side (Uramoto, Watazumi, Yokoyama, Iwamoto, Jin, Sakai, across the
"Shōganken reibo" group) `[V]`. And a third: **Okamoto 1983** prints the tablature
of one or more phrases, then a prose explanation of how to perform them, then "a
reproduction of the entire score of the 'Reibo' under scrutiny" at the end of the
analysis (S1 thesis pp. 197–199) `[V]` — i.e. tablature plus an exegesis of what the
tablature does not say. Of the three, Okamoto's is the most useful model for showing
what notation withholds.

### 6.10 The honkyoku rhythm problem — how it actually works

This is where English writing goes vague. The verifiable mechanics:

**(a) The notation genuinely does not fix duration.** Lee, as above: durations "are
at most used only as a broad and imprecise guide and are **frequently ignored
altogether**." S1 thesis p. 146. `[V]`

**(b) The discrepancies between score and performance are systematic, not random.**
Lee classified them, from the comparison of transcriptions-of-performances against
transnotations-of-scores, into **four categories** (S1 thesis p. 145, quoting Lee
1991:27, 32) `[V]`:

> 1. Instances where symbols are **consistently given new meanings**, which are
>    however different from their standard meanings. The consistency of these new
>    meanings may apply in a single piece only, **or throughout the honkyoku
>    repertoire of a particular lineage**.
> 2. Instances where symbols are **totally ignored**.
> 3. Instances where a pitch, duration or playing technique **is performed but is not
>    notated**.
> 4. Instances where meanings for symbols are **inconsistent** — a symbol may have the
>    standard meaning in one phrase and one or more different meanings in others.

Category 1 is the one that matters most: the divergence is *lineage-coded*. The score
plus the lineage's reading conventions is the piece; the score alone is not.

**(c) Therefore literal realisation fails, and fails proportionally.** Lee: "even if
one knows the standard meanings of all of the symbols used in a honkyoku notation,
one usually will not be able to perform honkyoku properly. A realization of a score
of a honkyoku using **only** the standard indications of the symbols might be so far
removed from the actual honkyoku as to be considered a different piece. **The closer
the adherence to the literal meaning of the symbols, the farther away honkyoku
becomes.**" S1 thesis p. 145. `[V]`

**(d) The tradition says so about itself, in print, since at least 1938.** Uramoto
Setchō, at a Fuke-shakuhachi seminar in Tokyo in 1938: "In the Fuke sect, **notation
is really just a memory aid.** It does not have an important function. Much [of the
Fuke tradition] does not have notation at all, being an oral tradition. When notation
is used, it is impossible not to adopt the limitations of that notation. **One ends up
playing the notation, and not playing true shakuhachi.**" (Uramoto, quoted in
Inagaki 1985:47; via S1 thesis p. 144.) `[V]`

And Hisamatsu Fūyō, mid-19th century, in his 『独問答』 *Hitori mondō*: "Question: Is
one who can play every piece without differing from the notation a skilful player?
Answer: Not at all. Someone who plays pieces without deviating may have a good
memory, but that is not enough for a skillful player." (Kurihara 1918:213; via S1
thesis p. 144.) `[V]` Lee's reading: "**Notation is thus not rejected in itself.
Problems occur only when it is thought to be in itself the essence of the matter.**"
`[V]`

**(e) "Free rhythm" is the wrong description — and a lineage teacher says so
outright.** This is the single most useful corrective I found, because it comes from
inside the practice rather than from a theorist:

> 「本曲は無拍のことが多く、また『自由リズム』といった説明をされることがあります。この『自由
> リズム』という言い方が非常に誤解を招きやすく、問題があります。『自由』という言葉が『好きな
> ように』という意味で捕えられてしまうと本曲の本質から遠くなってしまいかねません。好きかって
> に吹いて、いい本曲になるはずはありません。**本曲の「間」には最善の「間」があるはずです。
> ほんの一瞬ずれることで、だいなしになる瞬間もあります。**」
>
> "Honkyoku is often unmetered, and is sometimes explained as having 'free rhythm'.
> That phrase 'free rhythm' is extremely liable to be misunderstood, and it is a
> problem. If the word 'free' is taken to mean 'however you like', one ends up a long
> way from the essence of honkyoku. Blowing it as you please cannot possibly produce
> good honkyoku. **There must be a *best* 間 *ma* for a honkyoku. There are moments
> where being off by a single instant ruins it.**"
> — S2, 98年5月. My translation. `[V]`

**So the answer to "what fixes the rhythm, if the page doesn't?"** — (i) the
teacher's live model, replayed on demand in the lesson (§6.7, Lee's account of
Yokoyama and Sakai) `[V]`; (ii) the lineage's reading conventions for the symbols,
which are consistent *within* the lineage (Lee category 1) `[V]`; (iii) the student's
own annotation of his own copy, which the teacher neither supplies nor forbids `[V]`;
(iv) recordings, since the cassette era, which Lee treats as a real but partial
substitute: "If the essence of honkyoku lies in the **process**, then that essence can
only be suggested by recordings, which are representations of the **product** of a
single process" `[V]`; and (v) **唱譜 *shōfu*** — see §8.5, which is the specific
pedagogical mechanism by which *ma* is trained, and which I have not seen described
in English.

**And what the notation does fix,** on the KSK evidence: the **number and boundaries
of the phrases**. Lee: "the number of phrases notated in the score used by Sakai is
identical to the number of phrases in the transcription of Sakai's performance," and
the formal section divisions (竹調べ *take shirabe* → 鈴慕 *reibo* → 鉢返し *hachigaeshi*
→ 結 *musubi*, per Tukitani 1990b:15) are locatable in the transcriptions from the
scores that label them. S1 thesis pp. 213–214. `[V]` That is the practical division
of labour: **the page owns the architecture, the transmission owns the clock.**

---

## 7. 間 *ma*, 一息 one-breath phrases, and the notation–breath–phrase relationship

### 7.1 間 *ma* — Yokoyama's 絶対の間 *zettai no ma*

The best-sourced account of *ma* in honkyoku is Yokoyama's own, reported by Lee
(S1 thesis pp. 170–171) `[V]`:

- The operative term is 絶対の間 ***zettai no ma***. Lee renders it "absolute
  timing", then immediately qualifies: Yokoyama "points out that the word *ma* (間)
  … **denotes space as well as time**. *Zettai no ma* thus means 'absolute space' or
  'absolute interval' as well as 'absolute timing'." `[V]`
- **The analogy Yokoyama uses is the sword fight, not meditation.** "Yokoyama
  describes the idealized samurai as having to stake his very life on his ability to
  perform (with sword rather than shakuhachi) with *zettai no ma*. In a sword fight,
  the person who did not perform with 'absolute timing' lost the fight and frequently
  his life." The samurai "also had to judge absolutely the distance or spacing between
  one's sword and that of one's opponent." `[V]` **This matters:** the indigenous
  framing of *ma* here is **precision under consequence**, not relaxation or
  spaciousness.
- Lee's own gloss on the player's task: "the honkyoku player **must create the exact
  appropriate spaces or pauses** between phrases or notes when these occur." `[V]`
- *Ma* is not shakuhachi-specific: Lee lists blank space in brush painting, the long
  motionless pauses in Noh, the raked pebble expanses of dry gardens, the long
  silences in Japanese film, and calls it "one of the most pervasive and important
  concepts of Japanese art." `[V]`
- A related term: 中塚 Nakatsuka (1979:377) uses 絶対音楽 *zettai ongaku*, "absolute
  music", to distinguish honkyoku from "ordinary worldly music." S1 thesis fn 77 `[V]`

And from inside a lineage's own teaching, the operational version (§6.10e above):
**there is a best *ma*, and being off by an instant ruins it** (S2 98年5月) `[V]`. The
same column names the practical enemy of good *ma*: **running out of air**.
「息がなくなると『間』を早くとらえがちになってしまいます。必要なだけ、間をもてなくなって
しまうのです」 — "when the air runs out one starts taking the *ma* too fast; one can no
longer hold the *ma* as long as it needs." His two rules, in his order of emphasis
(the second being the one he says to watch especially): `[V]`

> 「息が余っても必要なだけ音をのばしたら音を切る。
> 息がなくなって音が切れてしまっても**必要な間合いは待つ**。」
>
> "Even if you have breath left, cut the note once you have held it as long as it
> needs. **Even if the note has broken off because you ran out of breath, wait out
> the interval that is needed.**" (My translation.)

### 7.2 一息 — the one-breath phrase as *the* structural unit

Lee states this as flatly as it can be stated (S1 thesis p. 171) `[V]`:

> "**Because the phrase is the single most important divisive unit in honkyoku**, the
> pauses between phrases are particularly important. Breaths are taken only during
> these pauses, so that **every phrase is only one breath's length.** … **All phrases
> in koten honkyoku must be performed in a single breath. The breathing always occurs
> between the phrases.**"

He then makes the inversion that is the real content of the idea `[V]`:

> "As there is no set rhythmic pulse or beat to adhere to, the breaths between each
> phrase need not fit within a set space or time. In fact, **the time allowed for
> taking any given breath is in a sense predetermined by the preceding and subsequent
> phrases** under the concept of *zettai no ma*. But conversely, **the phrases
> themselves are just as predetermined by the breath taken between them.** The breath,
> the space between the notes, is as important as the notes themselves in honkyoku.
> … **Breathing in the air needed to play a phrase is as much part of the process of
> performing as producing the sounds.**"

Contrast with metered wind music, in Lee's own terms: there, "the timing of the
performer's breathing is determined by the melody"; the player snatches breaths where
the music allows. **In honkyoku, "the timing of the breaths … are not subservient to
the sound element of the music."** `[V]`

**And this is exactly what the Western-musicological transcriptions got wrong.** Lee
documents it as a specific, repeated failure `[V]`:

| Analyst | Failure |
|---|---|
| **Malm 1959** | Uses "tonic", "dominant", **time signatures and bar lines** on honkyoku, "arbitrarily forc[ing] honkyoku into theoretical boundaries that are meaningless to traditional ways of viewing the music… **there are no beats in honkyoku**, much less a hierarchy of beats of the type that time signatures and bar lines imply." Uses the term "breath phrase" **once**, and only while discussing grace notes. "Like Weisgarber, the importance of the breath in performing honkyoku, as well as the phrase as a formal unit of honkyoku, escaped him." Also treats 「一二三鉢返」 as one piece when it is **two** (「一二三調」 + 「鉢返し」) |
| **Weisgarber 1968** | Assumes the "tonic" is G because G is the final note, "though the 'tonic' could equally be D"; same two-pieces-as-one error; "the most important unit of honkyoku, **the phrase as delineated by breaths, is also disregarded**." Uses "phrase" twice without defining it; his dotted phrase lines "**do not… correspond to breath phrases**" |

### 7.3 The notation–breath–phrase relationship: what actually goes wrong

The single most useful practical passage I found anywhere on this, from a lineage
teacher (S2, 2000年9月 「行の変わり目とフレーズ」). My translation `[V]`:

> "With koten honkyoku scores one tends to assume **the change of column is the
> change of phrase**. People frequently take a slow breath at the column boundary.
> But **the musical phrase boundary is sometimes somewhere else.** (Of course
> sometimes the column break and the phrase boundary do coincide.) Think hard about
> where one phrase actually ends; about whether a given place is somewhere you may
> breathe slowly or not. **Rewriting two columns as one may sometimes make the
> phrasing legible; so may splitting one written column into two.** …
> A second, related point is that **a breath is not always the same breath.** There
> are phrases where you have no choice but to breathe because you will run out, but
> where you would rather not — there, keep the breath as short as possible. And there
> are places where it is perfectly all right to take all the time you need."

Three things fall out of that, all verifiable:

1. **The score's line layout is a weak, sometimes misleading signal for the phrase.**
   The column break is a page-making artifact, not a phrase mark.
2. **Re-notating is a legitimate, taught remedy** — the student is expected to
   rewrite the lineage's own score to make its phrasing readable. This is the same
   practice Lee describes from the other side (students annotate; "neither Sakai nor
   Yokoyama wrote on my score") `[V]` and the same practice Yokoyama performed on his
   own scores for twenty years `[V]`. **The authoritative text is the one in your
   hand, modified.**
3. **Breaths are graded, not uniform.** The companion column (S2 2001年6月
   「100パーセントの呼吸」) attacks the specific beginner habit of "always inhaling to
   100% at every breath": 「これらのフレーズをいつでも同じ息の量で吹くととても退屈な演奏・表現に
   なっていきます」 — "blowing every one of these phrases on the same quantity of
   breath makes the playing and the expression extremely boring." The rule he gives:
   「フレーズが必要としている長さで吹くべきです」, play for the length the phrase needs;
   「息はそのための道具です」, the breath is the tool for that. `[V]`

### 7.4 Two further *ma* mechanics with no English equivalent I could find

| Idea | Content | Source |
|---|---|---|
| ***Ma* is made with dynamics, not only duration** | 「『間』は『音量の変化』と関係している、ということが以外に理解されていません」 — "it is surprisingly poorly understood that *ma* is bound up with **change in volume**." Kakizakai's instruction for deciding when to move to the next note: "do not attend only to time; attend to the change in volume." 「音量に変化を持たせて間を作る」 — "make the *ma* by giving the volume a shape." For players whose pitch and timbre are fine but whose honkyoku does not work, "dynamics may be the solution" | S2 99年7月 `[V]` |
| **Do not inhale into the resonance; do not blow straight after inhaling** | 「すぐ吸うな、すぐ吹くな」. When a note ends cleanly its 余韻 *yoin* (lingering resonance) continues after the sound is gone; **inhaling inside the *yoin* destroys it with the movement**, so the better a note's ending, the more carefully you must delay the breath. The converse: people start blowing immediately after inhaling, which makes "the beginning of the sound constrained by the act of inhaling. The note must come when the phrase needs it" — so leave a *ma* after the inhale too. His closing instruction: 「音のない所を『聴いて』見て下さい」, *listen* to the places with no sound | S2 2004年4月, corroborated by 2000年3月 (don't drop the instrument before the sound has died — it wrecks the 余韻) `[V]` |
| 黄金減衰 *ōgon gensui*, "golden decay" | A coined term — Kakizakai flags it as his own invention (「筆者（柿堺）の発案です」): by analogy with the golden ratio, there must be a **beautiful decay curve for volume** — neither an abrupt stop nor an over-long fade. A plucked string decays naturally; on the shakuhachi the player must control the end of the note, so it is a frequent trouble spot. Diagnostic he offers: most players have a 「苦手な音量」, an awkward volume level they cannot produce well, and that gap is what spoils the decay | S2 2005年8月 `[V]`. Included because it is an **explicitly new** concept from 2005 — a reminder that this vocabulary is still being made, not only inherited |

Related named devices already in §5: **韻 *in***, where "the flow of the piece
continues even though the sound has stopped… treating the absence of sound as
weightier than the presence of sound" (S5 ③) `[V]`; **スリ（消す）/ 抜き手**, the
technique whose entire purpose is to make a stolen mid-phrase breath inaudible so
the listener hears the line as unbroken (S5 ③) `[V]`. Both are *ma* technologies.

---

## 8. How it is taught

### 8.1 The headline: licensing is a school-by-school choice, not a property of Japanese traditional music

Two institutions, both teaching shakuhachi in Japan today, both descended from the
same instrument and partly the same notation:

| | 都山流尺八楽会 Tozan-ryū Shakuhachi Gakkai | 国際尺八研修館 KSK (Watazumi→Yokoyama) |
|---|---|---|
| Legal form | 公益財団法人, a **public-interest foundation** (Kyoto; est. 1896 as a school) `[V]` | A 研修館, a training hall, founded **1988 in Bisei, Okayama** by Yokoyama Katsuya; Tokyo office `[V]` |
| Head | 宗家 *sōke*; "all Tozan certificates and licences are conferred **directly by the sōke**" `[V]` | 館長 *kanchō* ("director"), Yokoyama until his death 21 Apr 2010 `[V]` |
| Grading | **8 named grades plus a recommendation route and two exams** — see §8.2 `[V]` | **None.** The words 師範, 免状, 免許, 名取, 家元, 宗家 occur **zero times** across the KSK top page and all nine years (≈105 columns, 215 KB) of its technique archive `[V]` — I grepped for each |
| Senior teachers | 師匠 *shishō*, defined as a holder of a 指南 licence or 准師範 and above who has filed a 指南開始届 `[V]` | **常任講師** *jōnin kōshi*, "resident instructors" — the label used in the site's own navigation `[V]`. Six are listed with personal sites: 古屋輝夫, 眞玉和司, 関一郎, 柿堺香, 石川利光, 岡田道明 `[V]` |
| Instead of certification | — | **A public competition.** 横山勝也伝承尺八古典本曲コンクール ("Yokoyama Katsuya Transmission Shakuhachi Koten Honkyoku Competition"), 2nd edition 29 Aug 2019: **18 applicants** to the recorded preliminary (judged 23 Jul), **10 in the final**, free admission, scores published `[V]` |
| Stated purpose | "育成・普及", nurture and diffusion, as a public-interest activity `[V]` | Yokoyama's own words, quoted on the site after his death: 『流も派も国境も超えた尺八のメッカを！』 — "a Mecca for the shakuhachi transcending *ryū*, *ha* and national borders!" `[V]` |

**So the licensing economy is institutional policy, not cultural destiny.** This is
the cleanest available counter to the common English claim that Japanese traditional
music is inherently an *iemoto* certification system. (Lee makes the structural
version of the point: the organisations' "primary functions have been and continue to
be **bureaucratic and social**, providing a power base from which a few members of the
tradition are able to exert influence on what is transmitted, and how, over a larger
number of members. **This is not to say that transmission does not take place within
the context of organizations, but that such transmission is not their main
function.**" S1 thesis p. 151 `[V]`)

### 8.2 Tozan's actual ranks, in order, with the real names

From the Tozan foundation's own 「都山流の資格 免状・免許状」 and 「免許状申請手続きについて」
pages `[V]`, fetched 2026-11-13. **Eight named grades.** The division between 免状
*menjō* (certificate) and 免許状 *menkyojō* (licence) is the school's own and is
load-bearing — 皆伝 is already a *licence*, not a certificate.

| # | Grade | Chars | Type | How you get it | What comes with it |
|---|---|---|---|---|---|
| 1 | 初伝 | *shoden* | 免状 | Teacher applies to the *sōke* on behalf of a student he has taught | — |
| 2 | 中伝 | *chūden* | 免状 | ditto | **竹号 *chikugō*, a "bamboo name", conferred by the teacher** |
| 3 | 奥伝 | *okuden* | 免状 | ditto | — |
| 4 | 皆伝 | *kaiden* | **免許状** | ditto | Eligibility to sit the *jun-shihan* exam |
| 5 | 指南 | *shinan* | 免許状 | — | Teaching qualification: with a 指南開始届 filed, you become a 師匠 and may take pupils |
| 6 | 准師範 | *jun-shihan* | 免許状 | **検定試験, a certification examination**, with 実技 (practical) and 楽理 (music-theory) components; the Gakkai examines and recommends to the *sōke*, who confers | Passing is called **開軒 *kaiken*** ("opening the eaves"). Also confers 師匠 status |
| 7 | 師範 | *shihan* | 免許状 | **検定試験**, sittable only **≥ 3 full years after passing *jun-shihan*** | **山号 *sangō*, a "mountain name"** |
| 8 | 大師範 | *dai-shihan* | 免許状 | **Promotion, not examination** — for *shihan* holders "who have been especially outstanding in their activity" | — |

Plus a side door: **推薦制度, a recommendation system** by which a 師匠's
recommendation can obtain 指南, 准師範 or 師範 **without the examination** `[V]`.

Membership structure: everyone holding a Tozan teaching qualification is
automatically a **正会員** (full member) of the foundation; since its recognition as a
public-interest corporation a **準会員** (associate member) class was added for others
`[V]`.

Scale, 1984: **4,935 licensed teachers in the largest of the three Tozan factions**
(S1 thesis fn at p. 4559) `[V]`. I found **no current figure** `[U]`. For the whole
instrument, ja.wikipedia says no proper survey of the playing population has ever
been done and the estimate is ~**30,000** players `[V]` — explicitly an estimate.

### 8.3 Kinko: no single system, but the same rank vocabulary — and a published price

Because Kinko is 「大小いくつもの組織の総体」, an aggregate of organisations with no
unified body `[V]`, there is **no "Kinko licensing system" to describe.** Each 会 sets
its own. But the rank *vocabulary* turns out to be largely shared with Tozan, which
weakens the usual Kinko-vs-Tozan framing.

**Worked example — 竹盟社 Chikumeisha** (founded Taishō 10 = 1921 around 山口四郎
Yamaguchi Shirō; on his death in Nov 1963 succeeded by his son 山口五郎 Yamaguchi
Gorō). Its 稽古案内 page, fetched 2026-11-13 `[V]`. **This is a commercial page and
these are its advertised prices:**

| Item | Amount |
|---|---|
| 入門料 enrolment | ¥10,000 |
| Monthly tuition, **初伝** | ¥10,000 |
| Monthly tuition, **中伝** | ¥12,000 |
| Monthly tuition, **奥伝・準師範** | ¥15,000 |
| Monthly tuition, **本曲** (honkyoku) | **¥20,000** |
| 詰稽古 intensive, per hour | ¥10,000 |
| Lessons | 4 per month, Mon and Fri (other days negotiable); free 30-min trial, instrument provided |
| Instruments sold on the premises | plastic ¥17,000; student/practice bamboo ¥30,000–90,000; upper-grade ¥100,000–260,000; 「五郎選」 (selected by Yamaguchi Gorō), stock only, ¥300,000–500,000 |

Three readings worth keeping. (a) The grade names 初伝・中伝・奥伝・準師範 are **the same
words Tozan uses** (Chikumeisha spells it 準師範, Tozan 准師範). (b) **Honkyoku is the
most expensive tier** — the top of the fee ladder, above 準師範. (c) 師範 holders run
the branch 稽古場 nationally, so the licence does organisational work here too.

On cost of licences in Kinko generally, the only figure I found is a 2014
Yahoo! Chiebukuro answer claiming a 師範免状 runs to "several hundred thousand yen"
(数十万円) `[U]` — **an anonymous forum post; I report it only as the order of
magnitude people discuss, not as a fact.**

**Kinko name-granting is verified:** 竹号 and 山号 in Tozan `[V]`; and the Kinko
practice of granting a professional name is visible in the data — Chikumeisha's
chief instructor is 松山**龍盟** Matsuyama Ryūmei, taking the 盟 of 竹**盟**社, and the
KSK instructors' names and 荒木**古童** Araki Kodō's lineage names work the same way.
A critical outside voice (尺八吹奏研究会, a practitioner site) argues of one teacher that
"he has no 師範 licence, so he has no right to use 盟 — and not just the 師範 licence:
he holds none of 皆伝, 奥伝, 中伝 or 初伝" `[U]` as to that individual, but it
independently confirms **that the name-character and the rank ladder are understood
to be linked** and are a live subject of dispute. Fetched via Yahoo! Japan search
2026-11-13.

### 8.4 Transmission by imitation, and the teacher's live model

The best first-hand account is Lee's, as a student of both Sakai (Chikuho) and
Yokoyama (S1 thesis p. 156 region) `[V]`:

- **The teacher does not write on your score.** "As a rule, neither Sakai nor
  Yokoyama wrote on my score."
- **The correction is a replay, not an explanation.** "If I did not play an
  embellishment or note or phrase as they wished me to or if I omitted something,
  they would tell me and **play the passage in question for me again. It was up to me
  to remember the passage.**"
- **Annotation is the student's own business, and is never instructed either way.**
  "Writing a word or symbol on the score as a reminder was completely permissible. If
  I thought that I could remember the passage without noting it down, that was also
  acceptable. … **my teachers did not tell me it was my responsibility to annotate
  the scores. Nothing was said on the matter one way or the other.**"
- **Lee notes that he himself does not manage this as a teacher outside Japan**: "I
  find myself making annotations to the scores of my students instead of allowing
  them to do it themselves. This may be indicative primarily of my own impatience and
  of the cultural background of both the students and myself **in which the teacher
  plays a more active role than is found in the shakuhachi tradition in Japan**." A
  rare, useful admission about what transplanting the pedagogy actually costs.
- **Recording the lesson was not normally allowed.** Lee's footnote 69: "For a brief
  period of time in the late 1970s, one teacher, **Sakai Chikuho II, allowed his
  lessons to be recorded, but charged the student extra for the privilege.**" `[V]`
- **And the relationship is designed to be broken.** "It is therefore necessary for
  the student of honkyoku eventually to **throw off the student role** in the
  teacher-student relationship and claim ownership of the honkyoku. This idea is
  behind Yokoyama's comment that **the student must eventually cut himself off from
  the teacher**." Lee relates Watazumi's refusal to acknowledge that anyone taught him
  "Reibo" to the same idea. `[V]`
- Yokoyama's own stated position, per Lee: **"neither authority nor authenticity is
  an issue when performing and transmitting honkyoku"**; he makes **no demand that
  students imitate his performances exactly**, unlike two other lineage heads Lee
  studied (Inoue and Aoki), who do; and the question of succession "does not even
  arise." Of the twenty or thirty pieces he learned from Watazumi he says he
  deliberately changed only one — 手向 *Tamuke*, which Watazumi played light and
  lively like a *min'yō* and Yokoyama could not bring himself to play that way —
  while acknowledging that the others changed anyway, "because Yokoyama did not have
  the capability to perform the pieces as Watazumi played them." S1 thesis
  pp. 9020–9040 `[V]`

So "rote imitation" is not a safe single description. **It is imitation of a live
model, replayed on demand, with the imitation explicitly expected to fail and
eventually to be abandoned.** Within the same instrument, Inoue's and Aoki's
lineages do demand exact imitation `[V]` — another school-by-school difference.

### 8.5 Two concrete taught practices English writing omits

**(a) 唱譜 *shōfu* — singing the tablature.** S2 99年10月 and 99年11月 `[V]`, my
translations. This is the mechanism by which *ma* is actually trained, and I have
not seen it described in English.

> "「唱譜」(*shōfu*) — do you know the word? It means **singing the shakuhachi score
> aloud with the voice**: 「ローレーチリロレーー」 and so on. Getting the pitches right
> matters enormously. You need not sing 「リのメリーー」 for every *meri* note, but
> when you sing, **the pitch must actually be the flattened pitch**. You need not
> sing on ロツレチ at all — all on 「アー」 is fine, as long as the pitches are right.
> … Those of you who practise by playing along with a master's CD: this time try
> **singing along** with the CD instead. *Shōfu* is especially effective for
> progress in honkyoku, because **the voice is far freer than the flute**. In that
> free state you experiment with changes of 間 *ma*, 音量 volume and 音程 pitch.
> There are cases of people who sing in tune turning tone-deaf the moment they pick
> up the shakuhachi. Humming is fine to start. **When you can sing a shakuhachi score
> you have never seen before, before playing it, your actual playing ability is
> already considerable.**"

The follow-up column handles "what about notes outside my vocal range" (answer:
transpose them an octave — easy to say, hard to do, and he gives three specific
passages to try) and gives a *shōfu* application for the ウのまる: **sing it as レ
while fingering ウ0**, "because then the pitch you actually blow comes out truer than
if you were singing ウ in your head." `[V]`

**(b) 暗譜 — memorisation by progressive erasure.** S2 2002年11月 「究極の暗譜法！」,
with Kakizakai flagging it as a method he devised himself `[V]`. Premise: honkyoku
should be memorised — 「本曲は暗譜して自分の中から湧き出て来てこそ本物です」, honkyoku is only
the real thing when it is memorised and welling up out of you; players who perform
honkyoku from the page "seem somehow to lack the tension" of those who do not. The
method, starting from "can already play it fluently from the score":

1. Photocopy the score with **a blank sheet laid over it so that only the first note
   of each 行 (column) is visible.** Play from that.
2. For any column where you do not even need the opening note, **erase it too**,
   leaving only the column number.
3. Where the next phrase does **not** come to mind, go back to the original and
   **write in just the opening of that phrase**.
4. Iterate — erase what surfaces, add back what doesn't. "You end up with a score in
   which only the places you snag on are left standing out of the white space."
5. "A score in that state **stays in the head extremely strongly as an image.** Play
   from it a few times and — how strange — you have it memorised."

His diagnosis of why the full score prevents memorisation is the interesting part:
「元の状態の譜面をいつまでも使っていると、暗譜している部分の映像が邪魔をして、暗譜していない部分
を際立たせてくれないのです」 — *the image of the parts you already know gets in the way
and stops the parts you don't know from standing out.* `[V]`

### 8.6 Universities, conservatoires and the state

| Institution / fact | Verified detail |
|---|---|
| **東京藝術大学 (Tokyo University of the Arts), 邦楽科・邦楽専攻** | The department exists in the 音楽学部 (Faculty of Music) and states its purpose as researching and teaching the practical performance and performance theory of eight named specialisations, **including 尺八** — the full list being 三味線音楽 (長唄, 常磐津, 清元), 邦楽囃子, 日本舞踊, 箏曲, **尺八**, 能楽, 能楽囃子, 雅楽 — "in order to train performers of advanced ability." `[V]` (geidai.ac.jp/department/music/traditional_japanese_music, 2026-11-13). Two further fields, 現代邦楽囃子 (percussion/flute) and 現代箏曲, were newly established in FY2016 `[V]` |
| **When shakuhachi entered Geidai** | **1977.** ja.wikipedia 山口五郎: 「1977年、東京芸術大学音楽科に尺八科が新設され、講師に任命される」 — in 1977 a **shakuhachi section was newly established** in the Geidai music department and Yamaguchi was appointed 講師 (lecturer). `[V]` So the university track is **under 50 years old**, younger than the Tozan licence system by eighty years |
| **山口五郎 Yamaguchi Gorō (1933–1999)** | Kinko-ryū. Son of 山口四郎; studied with his father from age 11; **NHK 邦楽技能者育成会 2nd cohort, 1956**; inherited the 竹盟社 sōke in 1963; 1974 Agency for Cultural Affairs Arts Festival Grand Prize; **1977 Geidai lecturer; 1987 Geidai 教授 (professor)**; **1992 重要無形文化財保持者 — Living National Treasure, the youngest ever in the hōgaku world**; 1995 Japan Art Academy Prize; 1996 Medal with Purple Ribbon. His 「巣鶴鈴慕」 is the recording on the **Voyager Golden Record** — ja.wikipedia 尺八 notes it is **the only Japanese piece** on it. `[V]` |
| **山本邦山 Yamamoto Hōzan (1937–2014)** | **Tozan-ryū** (taught by his father 山本鵬山, then 中西蝶山) — note the contrast with Yamaguchi: the two Geidai professors came from *opposite* schools. 1958 graduated Kyoto Junior College of Foreign Languages, English; 1975 Minister of Education Art Encouragement Prize; **1993 appointed 東京芸術大学教授**; **2002 Living National Treasure**; 2004 Medal with Purple Ribbon; 2009 Order of the Rising Sun; 2012 Japan Art Academy / Imperial Prize. Extensively recorded with jazz musicians (菊地雅章, Gary Peacock, 山下洋輔, 佐藤允彦, 富樫雅彦, Helen Merrill). `[V]` |
| **NHK 邦楽技能者育成会** | A real, dated, state-broadcaster training programme that produced the generation: Yamaguchi in **cohort 2 (1956)**, **Yokoyama Katsuya in cohort 6 (1960)**. `[V]` An institutional pathway that is essentially absent from English accounts |
| **東京音楽大学 (Tokyo College of Music)** | Yokoyama began teaching there in **1977** and was **名誉教授 (professor emeritus)** at his death; he also taught at Geidai from **1984** and was 客員教授 at くらしき作陽大学. `[V]` **Note the correction:** Yokoyama's professorship was at Tokyo College of Music, not Geidai; he *taught* at Geidai |
| **Compulsory schooling** | **From FY2002 (平成14年度), study of a Japanese instrument became compulsory in Japan's compulsory education** (義務教育に和楽器の履修が必須). The Tozan foundation ran preparatory activity before it took effect and documents member activity in its bulletin 『楽報』 from FY2000, classified by audience: 教員 (teachers), 生徒 (pupils), クラブ (club activity), その他. `[V]` This is the largest single institutional change in shakuhachi pedagogy in the modern period and it is not a *ryū* initiative at all — it is curriculum policy |

### 8.7 The modern learner's options, and the realistic curve

**Options, with Lee's assessment (1992) of the self-teaching route** `[V]`:

> "For the majority of potential shakuhachi players outside of Japan, these are the
> only feasible ways of learning anything about performing shakuhachi… As such,
> **they are better than nothing at all.** The obvious disadvantage of relying solely
> upon books and tape recordings… lies in the nature of honkyoku and the importance
> placed upon the **process** of performing. If the essence of honkyoku lies in the
> process, then that essence can only be suggested by recordings, which are
> representations of the **product** of a single process. … A great deal of diligent
> practice by a talented performer who has relied solely upon recordings and books
> may result in beautiful music, but it is unlikely that the essence of honkyoku will
> have been transmitted. **But then, much more unlikely events take place constantly
> in our universe.**"

He also notes **"graphic notations which have been developed recently as a
teach-yourself method"** as a third category alongside traditional and Western
notation `[V]` — a genre I could not characterise further `[U]`.

**Online teaching.** `[U]` — **I verified none of it.** No source in S1–S6 addresses
online lessons. What I *can* verify about the 2026 state of the sector is commercial
and in-person: KSK runs residential 本曲講習会 at ¥45,000 (students ¥36,000) for a
three-day course including two nights and six meals, materials extra, with a named
piece list per course, at 国際尺八研修館 in Bisei and at 三峰神社 in Chichibu, plus a
Rocky Mountain summer camp in Colorado (2020 listings; **all marked 中止, cancelled**)
`[V]`. Chikumeisha offers a free 30-minute trial lesson with a loaner instrument
`[V]`. **Both commercial.** The World Shakuhachi Festival is scheduled for
**20–26 August 2028** `[V]`.

**The realistic curve.** Two verified anchors, both practitioner statements:

1. **Producing a note at all is hard.** ja.wikipedia 尺八: unlike the recorder, whose
   fipple lets a beginner sound a note immediately, "to get a sound on the shakuhachi
   or the flute requires 熟練" — acquired skill. `[V]`
2. **There is a threshold effect, and below it progress does not stick.** S2 2003年8月
   「自転車に乗れるようになるまで」 ("until you can ride a bicycle"), my translation
   `[V]`: "Once you can ride a bicycle, you can ride it straight away next time even
   after a year off. But if you practise and still cannot ride, then a year later you
   must start again from scratch. That is, **once you reach a certain level, what you
   practised becomes firmly yours.** The same is exactly true of the shakuhachi. If
   you practise intensively for a set period (and better still succeed on a big
   stage) you reach a level; then when you come back to the piece later you reach a
   higher level far faster than before. **But if the intensive practice is
   insufficient, next time you must start over from the beginning.** I think this is
   especially pronounced in honkyoku, which is made out of 間 *ma*. Music that manages
   time by counting perhaps does not require much nervous attention to when the next
   note comes — look at the score, reproduce the specified length, and you are at
   least not wrong. But the length of a note in honkyoku, or the length of a silence,
   the 間 — that cannot be grasped that way. **Why can you avoid falling when the
   bicycle starts to go over? Nobody reasons it out in that instant; the 間 of
   honkyoku must be yours in the same way.** For that… first you need to practise to
   roughly the point of memorisation."

I found **no quantified learning curve anywhere** — no "N months to a stable *otsu*
ro", no hours-to-*shihan*. **Say plainly that nobody publishes one.** The nearest
thing to a quantification in my sources is structural, not temporal: Tozan's **≥ 3
years between passing *jun-shihan* and being allowed to sit the *shihan* exam** `[V]`.

---

## 9. Practical glossary

Grouped by function, alphabetised within group by rōmaji. **Source column**: `S1`
Lee thesis, `S2` KSK columns, `S3` ja.wikipedia 尺八, `S4` Tozan foundation, `S5`
Genkai, `S6` 尺八.net, `W` ja.wikipedia biography article. `[U]` flags a term whose
gloss I could not verify — these are listed deliberately so the gap is visible.
**167 entries.**

### 9.1 Instrument, registers, tuning

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| 顎当て | 顎当て | *ago-ate* | Chin rest / chin-contact adjustment offered as a lesson perk by one school | S-Chikumeisha `[V]` |
| 乙 | 乙 | *otsu* | The lower (1st) octave. Also written 呂 *ro* | S3 `[V]` |
| 大甲 | 大甲 | *dai-kan* | The 3rd octave, reached on partials; on a 1.8 flute up to about E7 with high technique | S3 `[V]` |
| 地 | 地 | *ji* | The lacquer filler built up inside the bore to tune it precisely | S3, S1 `[V]` |
| 地無し管 / 古管 | 地無し管 | *ji-nashi kan* / *ko-kan* | Older-type flute with the internal nodes left proud and no lacquer bore-filling; does not give accurate pitch, so the player must correct — and its individuality is part of the appeal in koten honkyoku | S3 `[V]` |
| 甲 | 甲 | *kan* | The upper (2nd) octave | S3 `[V]` |
| カリ | — | *kari* | Raise pitch by lifting the jaw/raising the blowing angle; usable range about **1 semitone** in ordinary playing | S3 `[V]` |
| メリ | — | *meri* | Lower pitch by drawing the jaw in; **up to more than 4 semitones** at maximum on near-open fingerings, about **2 semitones** in ordinary playing | S3 `[V]` |
| 中メリ | 中メリ | *chū-meri* | A named *degree* of flattening, "middle *meri*" | S1 `[V]` |
| 延管 | 延管 | *nobekan* | A flute made from one uncut piece of bamboo (historical norm; the two-piece jointed flute is now standard) | S3 `[V]` |
| 製管 / 製管師 | 製管 | *seikan* / *seikanshi* | Flute-making / flute-maker. Formerly one was not a full player until one could both play and make; full-time makers appeared from Meiji | S3 `[V]` |
| 尺 / 寸 | 尺・寸 | *shaku* / *sun* | Length units naming the flute. Standard **1尺8寸 ≈ 54.5 cm** in Edo-period Fuke practice | S3 `[V]` |
| 正寸 | 正寸 | *seisun* | "Length-accurate": a 正寸1尺8寸管 really is 1.8 shaku long, with **no guarantee** its 筒音 is D | S3 `[V]` |
| 正律 | 正律 | *seiritsu* | "Pitch-accurate": a 正律1尺8寸管 really sounds D, and **may not be** 1.8 shaku long. **Now the dominant convention**; hence the "D管 / E管 / A管" naming | S3 `[V]` |
| 筒音 | 筒音 | *tsuzune* | The all-holes-closed pitch; the flute's lowest note. 1.8 → D4; 1.6 → E4; 2.3 → A3 | S3 `[V]` |
| 歌口 | 歌口 | *utaguchi* | The blowing edge, bevelled **outward**, inlaid with buffalo horn, ivory or ebonite | S3 `[V]` |

### 9.2 Note names and notation

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| 暗譜 | 暗譜 | *anpu* | Memorisation. In the KSK lineage, the condition for honkyoku being "the real thing" | S2 `[V]` |
| 譜字 | 譜字 | *fuji* | A notation character — the tablature symbol itself | S3 `[V]` |
| フホウ譜 | フホウ譜 | *fu-ho-u fu* | Tablature using フ・ホ・ウ・エ・ヤ・イ rather than ロツレチ. Used by 竹保流; attested in 宗勳's 『短笛秘伝譜』 in the *hitoyogiri* era; Watazumi used "an extremely skeletal form" of it | S3, S1 `[V]` |
| 行 | 行 | *gyō* | A column/line of a vertical score. **Not reliably a phrase boundary** | S2 `[V]` |
| 習曲順 | 習曲順 | *shūkyoku-jun* | The fixed order in which a school's pieces are learned; organised for Kinko by Kurosawa Kinko I | S3 `[V]` |
| 唱譜 | 唱譜 | *shōfu* | **Singing the tablature aloud**, with the pitches (including *meri* pitches) correct; the core honkyoku practice device | S2 `[V]` |
| ロ・ツ・レ・チ・リ | — | *ro tsu re chi ri* | Kinko's five basic fingerings (リ → **ヒ** in *kan*); pitches D4·F4·G4·A4·C5 on a 1.8 flute | S3 `[V]` |
| ロ・ツ・レ・チ・ハ | — | *ro tsu re chi ha* | **Tozan's** five; same pitches, different fifth name | S3 `[V]` |
| ロツレ譜 | ロツレ譜 | *ro-tsu-re fu* | The notation system **devised by Araki Kodō** after the Fuke abolition, named for the first three open-hole kana, designed to suit *sankyoku*; **the basis of both modern Kinko and Tozan notation** | S1 `[V]` |
| 替え指 | 替え指 | *kae-yubi* | Alternate fingering; two whole KSK columns and nine mentions | S2 `[V]` |
| ウのまる / ウ0 | — | *u no maru* | ウ (a semitone above レ) flattened into unison with レ; written with a 0 | S2 `[V]` |
| 転譜 (transnotation) | — | — | Rewriting a piece from one school's notation into another's. **Lee's "transnotation"**; a whole informal economy, and a documented source of textual variation | S1 `[V]` |

### 9.3 Breath and tone colour

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| 浅音 / 浅息 | 浅音 | *asane* / *asaiki* | Soft off-edge breathy tone; also カスレ *kasure* | S5 `[V]` |
| 棒吹き | 棒吹き | *bōbuki* | Plain, even blowing with no swell or decay | S5 `[V]` |
| 吹切 | 吹切 | *fukikiri* | Listed as a technique; **no definition found** | S5 `[U]` |
| フラッター | — | *furattā* | Tongue flutter, imported as a substitute for *tamane*; lighter | S5 `[V]` |
| 吟 | 吟 | *gin* | Deliberately using the constructionally-sharp hole-3 pitch on a *ji-nashi* flute instead of *meri*-ing it to true pitch (Myōan Shinpō naming) | S5 `[V]` |
| 虚吹き | 虚吹き | *karabuki* / *kyosui* | Deliberately coreless blowing | S5 `[V]` |
| 吼声 / 獅子吼 | 吼声 | *kōsei* / *shishiku* | Blowing trumpet-fashion for a thick roar; contemporary and Watazumi-dō works | S5 `[V]` |
| 口メリ | 口メリ | *kuchi-meri* | *Meri*/*kari* made by **protruding and retracting the lips**, because a *komusō*'s 天蓋 hat would swing if he bobbed his jaw. Scarcely played today | S5 `[V]` |
| 楔吹き | 楔吹き | *kusabibuki* | Loud attack decaying steadily to nothing; no *yuri*. Named for the wedge shape. Especially common in some Myōan lineages | S1, S5 `[V]` |
| ムラ息 | ムラ息 | *muraiki* | Breathy/explosive attack: narrow the oral cavity (raise the tongue) *and* drive strong breath at the sounding point, aiming further in and with a **wider**, not tighter, lip aperture | S2, S5, S6 `[V]` |
| 黄金減衰 | 黄金減衰 | *ōgon gensui* | "Golden decay" — a coined (2005, Kakizakai) term for the ideal volume decay curve at a note's end | S2 `[V]` |
| 笹吹き | 笹吹き | *sasabuki* | Soft→loud→soft in one breath, fattest in the middle like a bamboo-grass leaf; no *yuri* | S5 `[V]` |
| シズメ吹き | 沈め吹き | *shizumebuki* | Jaw motion + breath acceleration imitating a repeated-note effect | S5 `[V]` |
| 空音 / 空息 | 空音 | *sorane* / *soraiki* | Off-edge tone between *asane* and *muraiki* in force; also 笹音 *sasane* | S5 `[V]` |
| 玉音 | 玉音 | *tamane* | **Throat flutter** — classically by vibrating the uvula (口蓋垂), "think of snoring"; ≥2 methods, differing in grain size and frequency. Softer than tongue flutter | S2, S1, S5 `[V]` |
| タンギング | — | *tangingu* | Tonguing (Tu/Ku); imported from the flute during the 新日本音楽 period; useful in fast passages. KSK has a whole column on it | S2, S5 `[V]` |
| 鼓吹き | 鼓吹き | *tsuzumibuki* | Loud→soft→loud in one breath, thinnest in the middle | S5 `[V]` |
| ツブシ / ウカシ | — | *tsubushi* / *ukashi* | Deliberately crushing/obscuring a note's attack; works mainly on *ji-nashi* flutes and in *otsu* | S5 `[V]` |
| 倍音奏法 | 倍音奏法 | *baion sōhō* | Deliberately overblowing the 3rd partial (3rd partial of ロ = 甲チ); "regarded as improper but worth knowing" | S5 `[V]` |

### 9.4 The *yuri* family

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| あごユリ | 顎揺 | *ago-yuri* | *Yuri* made at the jaw; given as a synonym of *yuri* | S3 `[V]` |
| 舟首揺 | 舟首揺 | *fune no kubi yuri* | "Ship's-prow *yuri*"; named by Okamoto. **No physical description in source** | S1 `[U]` |
| 平ユリ | 平ユリ | *hira-yuri* | "Flat/common *yuri*" — an exhalation alternately strong-weak-strong-weak, "exactly like eating food" (Okamoto, tr. Lee) | S1 `[V]` |
| 息ユリ | 息揺 | *iki-yuri* | Breath-strength *yuri* — effectively **tremolo** (amplitude) rather than vibrato | S3, S5, S6 `[V]` |
| 上下揺 | 上下揺 | *jōge-yuri* | "Up-and-down *yuri*"; named by Okamoto. Presumably = 縦ユリ, **not stated** | S1 `[U]` |
| カムリ / かむり | 冠り | *kamuri* | A pitch-dip gesture. **In the 道曲 (Watazumi) repertoire, a name for 首振り.** Kakizakai: **no clear distinction** from なやし or 振り, and no definition | S2, S5 `[V]` |
| 首振り / 首ユリ | 首振り | *kubifuri* / *kubi-yuri* | A **single** abrupt head swing making "a sudden valley in the sound." In koten honkyoku usually after 押し or 打ち; in Tozan often notated with an explicit beat ("fold on beat N") | S5, S6 `[V]` |
| 回しユリ | 回し揺 | *mawashi-yuri* | Rotate the head in circles; large smooth excursion. Sub-variants 上向き (*kari* half emphasised) and 下向き (*meri* half emphasised). Attested 1983 as 回はしユリ | S5, S1 `[V]` |
| 大ユリ | 大揺 | *ō-yuri* | **NOT VERIFIED in any source consulted. Do not gloss.** | — `[U]` |
| 押ユリ | 押揺 | *oshi-yuri* | Composite of *yoko-*, *mawashi-* and *iki-yuri*; **specific to the 越後明暗寺 lineage**; likened to a temple bell's swing-back | S5 `[V]` |
| 底ユリ | 底揺 | *soko-yuri* | Breath-controlled deep subtle wobble; **specific to the Ōshū lineages (布袋軒, 松巌軒)**; conceit is the temple bell's lingering ring; oral teaching 「底ユリは心でユル」 | S5 `[V]` |
| 縦ユリ | 縦揺 | *tate-yuri* | Vertical/jaw *yuri*; wider than *yoko-yuri*; often substitutes for a repeated-note figure | S3, S5 `[V]` |
| 手ユリ | 手揺 | *te-yuri* | Shaking the instrument with the hand; even tremolo. "Sometimes also called 縦ユリ" | S5 `[V]` |
| 淘り | 淘り | *yuri* (written 淘) | **Tōhoku-lineage spelling**, with the claim that the technique is grain-sorting-by-shaking, "**not** the so-called 揺り" | S1 `[V]` |
| 横ユリ | 横揺 | *yoko-yuri* | Horizontal head swing. **Tozan:** straight for 1–1½ beats then begin, singer-like swell. **Kinko:** faster, finer, from the onset, purpose is joining to the next note | S3, S5 `[V]` |
| 指ユリ | 指揺 | *yubi-yuri* | Partial opening/closing of a hole to shake the note | S6 `[V]` (low authority) |
| ユリ | 揺り | *yuri* | The whole family of pitch/timbre shaking gestures; **not** breath vibrato by default | S3 `[V]` |

### 9.5 Finger attacks and repeated figures

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| アタリ / あたり | 当り | *atari* | Momentary strike-like opening/closing to accent an onset or mid-note. **Term real in current usage but unverified in any authoritative source; the Japanese authorities call this family 打ち** | S6 `[U]` |
| 頭押し | 頭押し | *atama-oshi* | An *oshi* **before** the beat = the Western **short appoggiatura** (短前打音). Also ハズミ | S5 `[V]` |
| カラカラ | — | *karakara* | Rapid repeated strike of hole 1 on Tozan 甲ハ / Kinko ヒ. "Like a bird twittering." **Written ヤラヤラ in 明暗対山流, 鈴ゴロ/ゴロ in 琴古流.** A badly-made flute gives 片カラ / 片輪 | S5 `[V]` |
| 片ゴロ | 片ゴロ | *kata-goro* | Kinko's single-hole variant of 鈴ゴロ | S5 `[V]` |
| 刻み | 刻み | *kizami* | A run of *uchi* or *oshi* at an **even** interval | S5 `[V]` |
| 刻み-落し | — | *kizami-otoshi* | *Kizami* + *otoshi* combined; **the signature technique of 根笹派錦風流** | S5 `[V]` |
| コロコロ | — | *korokoro* | Rapid alternation of holes 1 and 2 with hole 5 slightly open and *meri*; **pitch must stay リ throughout**; the cycle must pass through a both-closed state or it sounds mushy (ホヨホヨ). **Realisations differ by school** — see コロコロリン, コロコロ（明暗） | S2, S3, S5 `[V]` |
| コロコロ（明暗） | — | *korokoro* (Myōan) | Both holes fully closed at the ロ so the ロ is heard as a pitch; sometimes written ホロホロ | S5 `[V]` |
| コロコロ（玉音） | — | *korokoro (tamane)* | *Korokoro* and *tamane* at once; "said to be among the hardest things on the instrument" | S5 `[V]` |
| コロコロリン | — | *korokororin* (Tozan) | Tozan's *korokoro*: faster, less both-closed state, usually ending in a リン. **Sonically "ko-ko-ko-ko", not "koro-koro"** | S5 `[V]` |
| コロロー | — | *kororō* | Slow twice-through *korokoro* with progressive deepening *meri*; also ホロイ, ホロロ | S5 `[V]` |
| 五孔の打ち | 五孔の打ち | *gokō no uchi* | The thumb-hole strike; its own KSK column, plus 五孔の連続打ち | S2 `[V]` |
| ハラロ | — | *hararo* | Kinko (and some Myōan) composite notated as three syllables; **actually blown 「ハーイ、ハロー」 (カル form) or 「ハーハーロー」 (メル form)** | S5 `[V]` |
| ハズミ | 弾み | *hazumi* | Alternative name for 頭押し; listed as a technique | S5 `[V]` |
| ヒラヒラ | — | *hirahira* | *Korokoro* an octave up; "like dappled sunlight drifting" | S5 `[V]` |
| ホロホロ | — | *horohoro* | Koten-honkyoku *korokoro* derivative with hole 4 also closed, only hole 5 open; larger swing | S5 `[V]` |
| フラ | — | *fura* | **Tozan:** a decomposed *korokoro* — one quick open-close-open of hole 1 or 2 from 四五のハ | S5 `[V]` |
| もみ手 | もみ手 | *momide* | A composite accelerating figure: two fingers, *suri-age* + *oshi* on the upper note + *uchi* on the lower, speeding up. "Together with *muraiki*, one of the techniques a lay listener remembers" | S5 `[V]` |
| 二指連打 | 二指連打 | *nishi renda* | Double-finger repeats: ツルツル, レエレエ, チリチリ, ウルウル, ハラハラ | S5 `[V]` |
| オドル | 踊る | *odoru* | *Momide* or a repeated figure **deliberately broken so the rhythm is irregular**; koten honkyoku | S5 `[V]` |
| 押し | 押し | *oshi* | Keep the finger down and **re-press**: open slightly and immediately close. Minimal pitch change, line stays continuous. Also 送り指, キザミ指 | S1, S5 `[V]` |
| 押し直し | 押し直し | *oshi-naoshi* | An *oshi* **after** the beat = the Nachschlag (後打音) | S5 `[V]` |
| 落し | 落し | *otoshi* | **A run of *uchi*/*oshi* that progressively accelerates or decelerates**, aiming at the sound of a struck *tsuzumi*. **Not a pitch drop** | S5 `[V]` |
| リン | — | *rin* | A very fast *koro*; Tozan, plus honkyoku phrase-head use, where it is **notated ホロ or コロ** | S5 `[V]` |
| サスリ | — | *sasuri* | Stroking/rubbing the finger holes for a continuous noise; **used in Takemitsu's *November Steps*** | S5 `[V]` |
| 鈴ゴロ | 鈴ゴロ | *suzugoro* | **Kinko's** name for the *karakara* family, with holes 1/2 alternating; Kinko has two kinds, 鈴ゴロ (hole 1 or 2) and ウハゴロ (hole 3 on the ハ fingering). Also written ヤラヤラ | S5 `[V]` |
| 打ち / 指打ち | 打ち | *uchi* / *yubi-uchi* | **Lift the finger high and strike the hole** with the breath unbroken. Named by target hole: ツル(1), レエ(2), チリ(3), ハラ/ア(4), ウル(3). **Fast in new/ensemble/modern pieces, slow in koten honkyoku — 鈍打 *donta*** | S2, S5, S6 `[V]` |
| 打ち（スリ） | — | *uchi (suri)* | A slanting **graze** across the hole, not a strike; fricative noise. **Tozan notates 「ノ」, Kinko 「ル」** | S5 `[V]` |
| 打チツメル | — | *uchi-tsumeru* | **Two meanings:** (a) strike while *meri*-ing down; (b) a run of paired strikes progressively dropping, "like a woodpecker" | S5 `[V]` |
| ウツレー | — | *utsurē* | **Myōan** composite: the ウ is **strike-noise only, not a pitch**; the ツ is *tsubushi*-ed; short ツレ gap, quick slide up; ツ emphasised | S5 `[V]` |
| ツレー（都山） | — | *tsurē* (Tozan) | Notated ツレ; the ウ is **clearly sounded**; ウ・ツ・レ **equal in length** | S5 `[V]` |
| ツレー（琴古） | — | *tsurē* (Kinko) | Notated ツレ; blown ウツレ, with **two forms of ウ** (press hole 4, or hole 3); hole 2 slid up while hole 4/3 is re-pressed, un-emphasised; **レ is the centre** | S5 `[V]` |
| 抜き手 | 抜き手 | *nukite* | The hole-5 case of スリ（消す） | S5 `[V]` |
| ヤラヤラ | — | *yarayara* | *Karakara* in the low register (Tozan ハ / Kinko リ, hole 1 or 3). **In 明暗対山流 it is in the high register and therefore identical to カラカラ** | S5 `[V]` |
| 鼓打ち | 鼓打ち | *tsuzumi-uchi* | Strike the **bottom end of the tube** like a drum; pitch varies with hole coverage | S5 `[V]` |
| 横笛吹き | 横笛吹き | *yokobue-buki* | Blow across **hole 4** as a transverse flute; a stunt (曲芸吹き) | S5 `[V]` |

### 9.6 Slides, bends and phrase shaping

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| チギリ | 千切り | *chigiri* | **錦風流's** proprietary technique: *nayashi* + 首振り, blown with コミ吹き, going from a deeply-*metta* state abruptly into *kari* then *meri* | S5 `[V]` |
| フリ込み | 振り込み | *furikomi* | A *merikomi* **after** a 首振り | S5 `[V]` |
| 振り | 振り | *furi* | A pitch-dip gesture whose noun form Kakizakai thinks arose out of coaching phrases ("the *furi* is too shallow"); **no clear distinction** from なやし or かむり | S2 `[V]` |
| 韻 | 韻 | *in* | The lingering-resonance device: the piece continues **through** the silence after a note. "Treats the absence of sound as weightier than the presence of sound" | S5 `[V]` |
| 息ナヤシ | 息撫やし | *iki-nayashi* | Continuous *otsu*/*kan* alternation on the **same fingering**; mainly 明暗真法流 | S5 `[V]` |
| ケシ / 消し | 消し | *keshi* | **Not verified as a standalone term.** Verified only as the verb 消す modifying other techniques (スリ（消す）, メリ込み（消す）) = end the note by making it vanish | S5 `[U]` |
| コミ吹き / 込み吹き | 込み吹き | *komibuki* | **錦風流 (根笹派)'s** pulsed breath technique, blown with チギリ. **"Commonly mistaken for a blowing technique, but its real meaning is a *yuri*"**; lineage gloss 動中静・静中動 | S5 `[V]` |
| 回し | 回し | *mawashi* | A slight head rotation **before** a mid-phrase breath, giving a lingering resonance like an 合いの手 | S5 `[V]` |
| メリ込み（カザシ） | — | *merikomi (kazashi)* | Jaw-*meri* (± hole shading) putting a **dimple** in the line; stickier than 首振り, **lighter/drier in Tozan**; especially common in Kinko. Also 引く, 折（オル） | S5 `[V]` |
| メリ込み（消す） | — | *merikomi (kesu)* | End of phrase: let the note **vanish while *meri*-ing down** rather than cutting it | S5 `[V]` |
| メリ込みスリ | — | *merikomi-suri* | *Merikomi* → true pitch → *suri-age* → true pitch | S5 `[V]` |
| ナヤシ（琴古） | 撫やし | *nayashi* (Kinko) | **Kinko sense:** at a phrase head, from a jaw-*meri* below up to true pitch (ロのメリ → ロ). In the KSK's koten honkyoku the dip is **a whole tone below for ロツレチリ, a semitone below for ツのメリ and ウ** | S5, S2, S6 `[V]` |
| ナヤシ（明暗） | — | *nayashi* (Myōan) | **Myōan sense — a different technique:** head swung along a trajectory tracing the hiragana 「ん」, giving an abrupt *meri*→*kari*. A third, 明暗真法流 *nayashi* is said to exist but is not described | S5 `[V]` / `[U]` |
| ネヤシ | — | *neyashi* | **NOT VERIFIED in any source. Probably a variant or mis-transcription of ナヤシ. Do not gloss.** | — `[U]` |
| スリ | 擦り | *suri* | Go up momentarily to the neighbouring pitch and **press straight back**, with a rotating finger motion; likened to the gagaku 龍笛 | S5 `[V]` |
| スリ上げ | 擦り上げ | *suriage* | **Slide** the finger off the hole so the pitch rises without a corner. **常用** — constantly used | S3, S5, S6 `[V]` |
| スリ（消す） | — | *suri (kesu)* | Use a *suri-age* to make the note vanish when stealing a mid-phrase breath, so the line sounds continuous | S5 `[V]` |
| スリメリ | — | *suri-meri* | *Suri* then *meri*; the inverse of *merikomi-suri* | S5 `[V]` |
| スリ下げ / スリサゲ | 擦り下げ | *surisage* | Descending slide; needs finger **and** jaw control. **常用外 — not in the common stock**, unlike *suriage* | S3, S5, S6 `[V]` |

### 9.7 Rhythm, phrase, aesthetic

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| 一息 | 一息 | *hitoiki* | One breath. **The structural unit: every koten honkyoku phrase is one breath long, and breaths fall only between phrases** | S1, S2 `[V]` |
| 息継ぎ | 息継ぎ | *ikitsugi* | Taking breath. **Not uniform**: some phrases demand the shortest possible breath, others allow all the time you need | S2, S6 `[V]` |
| 間 | 間 | *ma* | Interval — **of time and of space**. "There must be a *best ma*"; being off by an instant can ruin it. Trained via 唱譜 and via attention to **volume change**, not duration alone | S1, S2 `[V]` |
| 無拍 | 無拍 | *muhaku* | Unmetered. The accurate description of koten honkyoku, as against the misleading 「自由リズム」 | S2 `[V]` |
| 余韻 | 余韻 | *yoin* | The lingering resonance after the sound stops. **Inhaling inside it destroys it**; so does dropping the instrument too early | S2 `[V]` |
| 絶対の間 | 絶対の間 | *zettai no ma* | Yokoyama's term: "absolute *ma*" — timing *and* spacing, modelled on the swordsman's judgement of distance and instant, with one's life at stake | S1 `[V]` |
| 絶対音楽 | 絶対音楽 | *zettai ongaku* | Nakatsuka's (1979) term distinguishing honkyoku from "ordinary worldly music" | S1 `[V]` |
| 自由リズム | 自由リズム | *jiyū rizumu* | "Free rhythm" — **a description a lineage teacher explicitly calls misleading and a problem**, because "free" gets read as "however you like" | S2 `[V]` |

### 9.8 Repertoire, genre, history

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| 外曲 | 外曲 | *gaikyoku* | "Outside pieces" — repertoire from other genres arranged for the instrument | S3 `[V]` |
| 本曲 | 本曲 | *honkyoku* | "Original pieces" — the instrument's own solo/duo repertoire. The term was probably coined after the Fuke abolition to distinguish the old spiritual pieces from the growing ensemble repertoire | S3, S1 `[V]` |
| 古典本曲 | 古典本曲 | *koten honkyoku* | The narrower, pre-1871 Fuke-sect repertoire, as against post-1871 secular "honkyoku". **~150 pieces transmitted**; ~200 honkyoku and variants said to exist | S3, S1 `[V]` |
| 普化尺八 | 普化尺八 | *fuke shakuhachi* | The modern instrument type, developed in Japan from the late 16th c.: root-end bamboo, avg **54.5 cm**, bore **4 cm**, **5 holes (4 front, 1 back)** | S3 `[V]` |
| 普化宗 | 普化宗 | *Fuke-shū* | The sect to which playing was legally restricted in the Edo period; **dissolved by government in 1871** | S3 `[V]` |
| 吹禅 | 吹禅 | *suizen* | "Blowing Zen" — the religious use of the instrument | S1 `[V]` |
| 虚無僧 | 虚無僧 | *komusō* | The mendicant Fuke priests; on the sect's abolition many became shakuhachi teachers | S3 `[V]` |
| 法器 | 法器 | *hōki* | "Dharma implement" — the Edo-period legal/religious status of the flute, as a ritual object rather than a musical instrument | S3 `[V]` |
| 一節切 | 一節切 | *hitoyogiri* | The 15th–19th c. one-node vertical flute: avg **33.6 cm**, outer dia. **3 cm**, **5 holes (4+1)**; nearly extinct by the 19th c. | S3 `[V]` |
| 古代尺八 | 古代尺八 | *kodai shakuhachi* | The gagaku shakuhachi: avg **40 cm**, **6 holes (5+1)**, bore holes 2 cm; eight survive in the Shōsōin; extinct by the 10th c., **no notation survives** so its playing method is unknown | S3 `[V]` |
| 三曲 | 三曲 | *sankyoku* | The koto/shamisen/kokyū trio; from Meiji the shakuhachi commonly replaced the kokyū. **Kokyū trios still occur — ja.wikipedia explicitly rebuts the claim that they died out** | S3 `[V]` |
| 新日本音楽 | 新日本音楽 | *shin nihon ongaku* | The 1920s Miyagi Michio / Yoshida Seifū movement incorporating Western elements | S3 `[V]` |
| 鉢返し | 鉢返し | *hachigaeshi* | "Returning the bowl" — a formal section of *reibo*-family pieces, played with *tamane*; named for the *komusō*'s emptying and returning of the alms bowl mid-piece | S1 `[V]` |
| 竹調べ | 竹調べ | *take shirabe* | "Bamboo searching/melody" — the opening formal section | S1 `[V]` |
| 結 | 結 | *musubi* | "Closing" — a short concluding section in the high register, though many variants end low | S1 `[V]` |
| 瀧落シ | 瀧落シ | *taki-otoshi* | "Falling waterfall" — **a section title, not an ornament.** Easily confused with 落し | S1 `[V]` |
| 核音 | 核音 | *kakuon* | Core tone / tonal centre; the analytical concept used by Tukitani, Gutzwiller and others in place of a Western tonic | S1 `[V]` |

### 9.9 Schools, ranks, institutions

| Term | Chars | Rōmaji | Gloss | Src |
|---|---|---|---|---|
| 大師範 | 大師範 | *dai-shihan* | Tozan rank 8 — **promotion, not examination**, for outstanding activity | S4 `[V]` |
| 段 / 名取 | 段・名取 | *dan* / *natori* | Rank systems used in other Japanese arts; **absent from the KSK, verified by grep** | S2 `[V]` (negative) |
| 家元 | 家元 | *iemoto* | The head-of-house system; Nakao Tozan built 「近代的な家元制度」, a modern version of it | S3 `[V]` |
| 常任講師 | 常任講師 | *jōnin kōshi* | "Resident instructor" — the KSK's title for its senior teachers, **in place of any rank** | S2 `[V]` |
| 准師範 / 準師範 | 准師範 | *jun-shihan* | Tozan rank 6, by **practical + music-theory examination**; passing is 開軒 *kaiken*. Also a tuition tier at Chikumeisha (spelled 準師範) | S4 `[V]` |
| 皆伝 | 皆伝 | *kaiden* | Tozan rank 4 — already a 免許状 *licence*, not a 免状; gate to the *jun-shihan* exam | S4 `[V]` |
| 検定試験 | 検定試験 | *kentei shiken* | Tozan's certification examination, administered by the foundation, with practical and theory parts; results recommended to the *sōke* | S4 `[V]` |
| 免許状 | 免許状 | *menkyojō* | Licence — Tozan's higher-tier document (皆伝 and above) | S4 `[V]` |
| 免状 | 免状 | *menjō* | Certificate — Tozan's lower-tier document (初伝・中伝・奥伝) | S4 `[V]` |
| 奥伝 | 奥伝 | *okuden* | Tozan rank 3 | S4 `[V]` |
| 流 / 派 / 会 | 流・派・会 | *ryū* / *ha* / *kai* | "Stream" / "group" / "society" — the three organisational words. Lee: their primary functions "have been and continue to be **bureaucratic and social**" | S1 `[V]` |
| 山号 | 山号 | *sangō* | "Mountain name" — the professional name conferred with the Tozan 師範 licence | S4 `[V]` |
| 竹号 | 竹号 | *chikugō* | "Bamboo name" — conferred by the teacher on completion of Tozan 中伝 | S4 `[V]` |
| 師範 | 師範 | *shihan* | Tozan rank 7, by examination **≥3 years after *jun-shihan***; brings the 山号 | S4 `[V]` |
| 指南 | 指南 | *shinan* | Tozan rank 5 — the teaching licence; with a 指南開始届 filed you become a 師匠 | S4 `[V]` |
| 師匠 | 師匠 | *shishō* | Tozan's term for a qualified teacher: holder of 指南 or 准師範+ who has filed notice of commencement | S4 `[V]` |
| 初伝 | 初伝 | *shoden* | Tozan rank 1 | S4 `[V]` |
| 宗家 | 宗家 | *sōke* | The school head; **all Tozan certificates and licences are conferred directly by the *sōke*** | S4 `[V]` |
| 推薦制度 | 推薦制度 | *suisen seido* | Tozan's **recommendation route** to 指南 / 准師範 / 師範 **without examination** | S4 `[V]` |
| 正会員 / 準会員 | — | *sei-kaiin* / *jun-kaiin* | Full member (automatic for all Tozan teaching-qualification holders) / associate member (added after public-interest recognition) | S4 `[V]` |
| 邦楽技能者育成会 | 邦楽技能者育成会 | *hōgaku ginōsha ikuseikai* | **NHK's** traditional-music performer training programme. Yamaguchi Gorō cohort 2 (1956); Yokoyama Katsuya cohort 6 (1960) | W `[V]` |
| 邦楽科 | 邦楽科 | *hōgaku-ka* | Tokyo University of the Arts' traditional-music department; **shakuhachi is one of eight named specialisations**; the shakuhachi section was established **1977** | Geidai, W `[V]` |
| 重要無形文化財保持者 | — | *jūyō mukei bunkazai hojisha* | "Living National Treasure". Yamaguchi Gorō 1992 (youngest ever in hōgaku); Yamamoto Hōzan 2002 | W `[V]` |

---

## 10. Closing

### 10a. Corrections to the commonly repeated English account

Numbered, each with the source that contradicts the received version.

1. **"The shakuhachi ornament vocabulary" does not exist as a single thing.**
   The terms are lineage property. The same gesture is カラカラ in general usage,
   **ヤラヤラ in 明暗対山流 and 鈴ゴロ in 琴古流** (S5 ④) `[V]`; *nayashi* names **two
   different techniques** in Kinko and Myōan, and a third in Myōan Shinpō (S5 ①) `[V]`;
   *yuri* is written 淘り in the Tōhoku lineage **with an explicit denial that it is
   the 揺り technique** (Okamoto via S1) `[V]`. Any glossary that does not carry a
   school column is misrepresenting the subject.
2. **A lineage's own senior teacher states there is no definition distinguishing
   なやし, かむり and 振り.** 「はっきりした使い分けは無さそうだ」 (S2 2003年11月) `[V]`. English
   sources that give crisp separate definitions for all three are inventing precision.
3. **オトシ *otoshi* is not a pitch drop.** In the one named-practitioner taxonomy I
   could read, 落し is **a run of finger strikes that accelerates or decelerates** —
   a rhythmic device (S5 ④) `[V]`. The falling-waterfall association belongs to
   瀧落シ *taki-otoshi*, which is a **section title** (S1) `[V]`.
4. **込み吹き *komibuki* is not a blowing technique.** Genkai: "commonly mistaken
   for a kind of blowing technique, but **its real meaning is a *yuri***" — and he
   files it under vibrato/tremolo, not blowing (S5 ②) `[V]`. It is also
   **錦風流-specific**, not general.
5. **Honkyoku is not played with pervasive vibrato; at least one major lineage
   forbids it.** 「特に国際尺八研修館の講習会で取り上げる古典本曲ではビブラートはつけません」 — "in the
   koten honkyoku we teach at the KSK **we do not apply vibrato**" (S2 97年10月) `[V]`.
6. **"Free rhythm" is wrong, and the objection comes from inside the tradition, not
   from a critic.** 「この『自由リズム』という言い方が非常に誤解を招きやすく、問題があります… **本曲の「間」
   には最善の「間」があるはずです**」 — "that phrase 'free rhythm' is extremely liable to be
   misunderstood and is a problem… **there must be a *best ma* for a honkyoku**" (S2
   98年5月) `[V]`. 無拍 *muhaku*, "unmetered", is the accurate word.
7. **The notation is a Meiji reform instrument, not an ancient Zen tablature.**
   Notation has been in use "just over 150 years" as of 1992 `[V]`, and the ロツレ
   system was **devised by Araki Kodō after the Fuke sect's abolition specifically to
   make the instrument notatable for *sankyoku* ensemble work** (S1) `[V]`.
8. **Kinko and Tozan notation are cousins.** Araki's ロツレ system "became the basis
   for the present-day Kinko notation, **as well as for the notation system of
   today's largest shakuhachi school, Tozan ryû**" (S1) `[V]`. They are not
   independent traditions.
9. **The score was historically a licence as much as a text.** Araki Kodō II's
   May 1853 *Shika no tōne* score devotes **half the sheet to the notation and half
   to a signed transmission certificate**; Lee: "the score **certifies** that the
   student now possesses the piece" (S1 pp. 17–18) `[V]`.
10. **Lee's thesis argues that published honkyoku notation exists mainly for
    bureaucratic reasons.** "In my opinion, a major reason notation, especially
    published, copyrighted notation, for shakuhachi honkyoku exists at all is because
    of its **bureaucratic function of asserting and maintaining authority** rather
    than any function it might have in the transmitting and performing of honkyoku"
    (S1 p. 146) `[V]`. His case study: Chikuho ryū, where the incoming *iemoto*
    Shōdō **refused** his brother Chikuho II's Chikuho-notation transcriptions and
    reverted to the teacher Jin's original scores *in a foreign notation*, on the
    grounds that Chikuho II had put too many of his own idiosyncrasies in `[V]`.
11. **Honkyoku in staff notation is a transcription, and (as of 1992) had never been
    used in practice.** "Scores of classical honkyoku in staff notation exist **only
    as transcriptions in scholarly articles** and, to my knowledge, have **never been
    used in actual teaching/learning or performing situations**" (S1 p. 157) `[V]`.
12. **Tozan's rhythmic explicitness has a repertoire cause, not a cultural one.**
    Tozan has **no koten honkyoku at all**; its music is Nakao's compositions,
    *sankyoku* and 新日本音楽 ensemble work, and it held the exclusive right to publish
    the shakuhachi parts of Miyagi Michio's compositions (S1, S3) `[V]`. Music played
    with a koto needs a beat; *suizen* does not.
13. **Tozan did not merely "modernise" — it also restricted.** Lee: it "**actively
    discourages its members from studying with any teacher who performs classical
    honkyoku**"; members were and in many cases still are **forbidden** to learn or
    perform outside the official repertoire, citing Kamisangō 1974:21 (S1) `[V]`.
14. **Licensing is a school-by-school choice, not a property of Japanese traditional
    music.** Tozan: **8 named grades**, two examinations, a recommendation route, all
    conferred by the *sōke* (S4) `[V]`. The KSK, teaching the same instrument:
    **zero occurrences of 師範, 免状, 免許, 名取, 家元 or 宗家** across its site and nine
    years of its technique archive; its senior teachers are **常任講師**, resident
    instructors; and it substituted **a public competition** (18 applicants / 10
    finalists, 2019) `[V]`.
15. **There is no "Kinko licensing system", because there is no single Kinko
    organisation** — 「大小いくつもの組織の総体」, an aggregate with no unified body (S3)
    `[V]`. And where a Kinko society does grade, **the rank names are largely the
    same words Tozan uses** (初伝・中伝・奥伝・準師範 at 竹盟社) `[V]`, so the Kinko-vs-Tozan
    contrast on licensing is weaker than usually implied.
16. **The Watazumi/Yokoyama "Dokyoku" lineage is a Kinko-notation lineage.**
    Verified twice: Lee ("most of the scores used are written in Kinko notation")
    `[V]`, and from the lineage's own teaching page — 「（琴古流の記譜を用いています。）」 `[V]`.
    Watazumi himself used "an extremely skeletal form of the フホウ system"; Yokoyama
    switched because students found フホウ too slow to learn `[V]`.
17. **Yokoyama refused to publish scores, and revised his own in a loop.** "Scores
    can only be **'memos'** of honkyoku itself"; over ~20 years he cycled between
    adding detail and simplifying again, having realised the added detail did not
    represent the piece either (S1) `[V]`. The authoritative text inside the lineage
    was a hand copy, not a print.
18. **The teacher's correction is a replay, not an annotation.** "**Neither Sakai nor
    Yokoyama wrote on my score.** … they would tell me and **play the passage in
    question for me again. It was up to me to remember**" — and nothing was ever said
    about whether the student should annotate (S1) `[V]`. Lee adds that **he himself
    cannot teach that way outside Japan** and annotates his own students' scores `[V]`.
19. **"Rote imitation" is a school-specific policy.** Yokoyama made **no demand that
    students imitate him exactly**, held that "neither authority nor authenticity is
    an issue", and taught that **the student must eventually cut himself off from the
    teacher**; Inoue's and Aoki's lineages **do** demand exact imitation (S1) `[V]`.
20. **A column break in a honkyoku score is not a phrase boundary**, and the taught
    remedy is to **rewrite the score** — joining two columns into one, or splitting one
    into two — to make the phrasing legible (S2 2000年9月) `[V]`. The page owns the
    architecture, not the breathing.
21. **The breath-phrase is the structural unit, and the Western transcriptions
    missed it.** Lee shows **Malm (1959)** imposing time signatures and bar lines
    ("there are no beats in honkyoku"), using "breath phrase" once and only about
    grace notes, and treating 一二三調 + 鉢返し as one piece; and **Weisgarber (1968)**
    disregarding the breath-phrase entirely, with dotted phrase lines that "do not
    correspond to breath phrases" (S1) `[V]`.
22. **Yokoyama's *ma* is the swordsman's, not the meditator's.** 絶対の間 *zettai no
    ma* means absolute **space as well as** absolute timing, and the analogy Yokoyama
    uses is a sword fight where mistiming costs your life (S1) `[V]`.
23. **The university track is under 50 years old.** The 尺八科 at Tokyo University of
    the Arts was **newly established in 1977**, with Yamaguchi Gorō as its first
    lecturer; he became professor in 1987 (W) `[V]`. The Tozan licence system predates
    it by eighty years.
24. **The two Geidai shakuhachi professors came from opposite schools.** Yamaguchi
    Gorō was **Kinko**; Yamamoto Hōzan (prof. 1993) was **Tozan** (W) `[V]`. The
    conservatoire is not an extension of one school.
25. **Yokoyama's professorship was not at Geidai.** He *taught* at Geidai from 1984,
    but was **professor emeritus of Tokyo College of Music** (東京音楽大学), where he
    began teaching in 1977 (KSK's own biography page) `[V]`.
26. **The largest change in shakuhachi pedagogy in the modern period was state
    policy, not a school's.** From **FY2002 a Japanese instrument became compulsory
    in Japanese compulsory education**; the Tozan foundation ran preparatory activity
    ahead of it and documents member school work in its bulletin from FY2000, sorted
    by 教員 / 生徒 / クラブ (S4) `[V]`.
27. **Nobody publishes a learning curve.** No source I read gives hours, months or
    stages to competence. The nearest quantification is structural: Tozan's **≥3
    years** between the *jun-shihan* and *shihan* examinations (S4) `[V]`. The only
    substantive pedagogical claim I could verify is a **threshold effect**: below a
    certain level of intensive practice, progress does not persist and you start over
    (S2 2003年8月) `[V]`.
28. **The playing population figure is an estimate and the source says so.**
    ja.wikipedia: no proper survey of the shakuhachi playing population has ever been
    conducted; the estimate is about **30,000** `[V]`. Do not state it as a count.
29. **A side-by-side of one piece in two notations has been published** — Lee's
    thesis **Figure 5**, the same passage of 「九州鈴慕」 in **Myōan notation and in
    Tozan transnotation** `[V]`. English writing treats this comparison as
    unavailable; it has been in print since 1992.
30. **Three glosses commonly given in English could not be verified at all and
    should be withheld: 大ユリ *ō-yuri*, ネヤシ *neyashi*, ケシ *keshi* as a standalone
    term, and アタリ *atari* as a technical term distinct from 打ち.** Nine years of a
    lineage's own technique columns contain zero instances of 大ユリ, ネヤシ, オトシ,
    カラカラ, ケシ or 込み吹き. `[U]`

### 10b. Open questions

1. **Deschênes 2005 (DOI 10.7202/801311ar) is unread.** Crossref confirms *Horizons
   philosophiques* 16(1): 136, 2005 `[V]`, and Érudit is nominally open access, but
   both the HTML and the PDF URL now return an **Anubis proof-of-work JavaScript
   challenge** to `curl`. The self-orientalism argument is therefore **not
   represented in this file.** Needs a JS-capable fetch or library access.
2. **Signell 1981 is unread.** Metadata now resolves: DOI **10.67781/rppm5255**,
   *Journal of the American Musical Instrument Society*, 1981, **p. 90** `[V]` — note
   the page, which is often cited wrongly. Full text not located.
3. **Lee 1991 and Lee 1988 are unread in the original.** Everything I attribute to
   them is Lee's own summary of them **inside the thesis**, cited by thesis page. The
   four-category discrepancy taxonomy is quoted by Lee from Lee 1991:27, 32 — if the
   exact wording matters, check the article.
4. **No symbol inventory for any school.** I could not obtain, for Kinko, Tozan or
   Myōan: a count of symbols, a duration-mark table, or a reproduction of a score
   page. All my notational claims are about *principles* and *named differences*, not
   about the glyph set. **This is the biggest remaining gap in §6.**
5. **Reading direction of the score is unsourced.** Top-to-bottom, right-to-left is
   certainly right and is implied by the KSK's talk of 行, but I found no explicit
   statement in any of S1–S6, because all of them write for readers who can see a
   score `[U]`.
6. **Myōan notation is almost entirely undescribed here**, including how (or whether)
   it indicates duration, and what distinguishes 明暗真法流 from 明暗対山流 notationally.
   The 明暗真法流 *nayashi* is asserted to exist and differ from the other two but is
   never described `[U]`.
7. **Four technique terms remain unglossed:** 吹切 *fukikiri*, 三のウ *san no u*,
   舟首揺 *fune no kubi yuri*, 上下揺 *jōge-yuri* (the last two named by Okamoto without
   physical description) `[U]`.
8. **The briefing's KSK score-volume details are unverified:** printed volumes in Kinko
   notation with Tozan on request; applicants asked which notation they read; a
   predecessor era of one teacher's photocopied handwritten scores circulated with a
   warning about errors. All consistent with Lee and with the site, none findable on
   the 2026 site, which carries courses and the advice archive, not a score catalogue
   `[U]`. Worth chasing in the KSK application materials or a printed volume's
   front matter.
9. **Kinko licensing fees** — the only figure I found is an anonymous 2014 forum post
   giving 数十万円 for a 師範免状 `[U]`. No society publishes its licence prices; the
   published prices I verified are **tuition**, not certification.
10. **Online teaching is wholly unverified.** No source consulted addresses it. The
    2026 commercial offerings I could confirm are in-person: KSK residential courses
    at ¥45,000, Chikumeisha's free 30-minute trial `[V]`. This is a real gap for a
    "modern learner's options" section and will need primary sources (teacher sites,
    platforms) rather than the literature.
11. **Current Tozan membership and teacher counts.** The only count I have is
    **4,935 licensed teachers in 1984**, in the largest of three factions, from Lee's
    footnote `[V]`. The foundation publishes an 情報開示 (disclosure) page I did not
    mine; as a public-interest corporation it must file figures `[U]`.
12. **Lependorf 1989 is unread**, so this file says nothing about how contemporary
    composers are advised to notate the instrument beyond Genkai's incidental
    attributions (サスリ in *November Steps*, 吼声, ボイス・パーカッション) `[U]`. Given that
    §6.8 is thin on contemporary practice, this is the citation most worth obtaining
    next.
13. **Kakizakai's 「ワンポイントアドバイス」 was not exhaustively mined.** I read roughly
    25 of ~105 columns closely. The archive certainly contains more on *meri* (nine
    columns are titled around it), tonguing, dynamics, and stage practice. The 1997
    and 1998 indices are listed in §S2 and anyone continuing this work should start
    there rather than with English sources.
