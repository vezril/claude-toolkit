# Shamisen Technique and Tuning

Scope: posture, the bachi stroke, the three tunings, and left-hand position-finding. Construction, history/genres and the
Tsugaru tradition are covered by other agents; general technique that Tsugaru builds on is here.

**All web fetches: 2026-11-13.** Every claim is marked **[V]** (verified — the artifact I actually
read is named) or **[U]** (unverified / flagged).

## 0. Source audit — read this before trusting anything below

### 0.1 What I could NOT read, and what that means

Four sources would be the natural authorities here. Three could not be obtained:

- **Henry Johnson, *The Shamisen: Tradition and Diversity* (Brill, 2010).** Brill's website returned
  403/404 to every request. I verified the book's existence and metadata only: Henry Mabley Johnson,
  *The Shamisen*, Brill, 2010, ISBN 9789004181373 / 9004181377, ~145 pp. **[V — Open Library
  search API, `openlibrary.org/search.json`]**. I also verified two scholarly reviews exist:
  Anne Prescott, *Ethnomusicology* 57/1 (2013), 133–135, DOI 10.5406/ethnomusicology.57.1.0133;
  and David W. Hughes (SOAS), *Ethnomusicology Forum* 25/3 (2016), 371–373, DOI
  10.1080/17411912.2016.1234939 **[V — Crossref API]**. Both review PDFs are paywalled (403).
  **I therefore attribute nothing to Johnson's text. Any statement you see elsewhere sourced to
  "Johnson 2010" has not been checked here. [U]**
- **William P. Malm, *Traditional Japanese Music and Musical Instruments*.** Verified only:
  Kodansha International, 2000, ISBN 9784770023957, ~354 pp. **[V — Open Library search API]**.
  Its relationship to Malm's earlier *Japanese Music and Musical Instruments* (1959) is **[U]**.
  I did not read Malm; nothing here is attributed to him. (One Japanese Wikipedia article lists
  "Malm, *Japanese Music*" in a source list, but for percussion, not strings **[V — ja.wikipedia
  特殊奏法]**.)
- **Garland Encyclopedia of World Music vol. 7.** **Correction to the usual account:** volume 7 is not a
  Japan volume. It is *East Asia: China, Japan, and Korea*, eds. Robert C. Provine, Yosihiko
  Tokumaru, J. Lawrence Witzleben, Routledge, ISBN 0824060415, ~1,172 pp., first published
  2001–2002 **[V — Open Library search API]**. Not read; nothing attributed to it.
- **Koizumi Fumio, *Nihon dentō ongaku no kenkyū* 日本伝統音楽の研究 vol. 1 (1958).** Not read. Its
  existence, publisher (音楽之友社, 1958) and subtitle 「民謡研究の方法と音階の基本構造」 ("methods
  of folk-song research and the basic structure of scales") are **[V — ja.wikipedia 小泉文夫]**.
  His tetrachord theory below is sourced from a Japanese government educational site that
  summarises it, not from Koizumi himself.

### 0.2 What I did read, and how good it is

**Strong Japanese reference works (via Kotobank, which aggregates full entries):**
Shogakukan *Nihon Daihyakka Zensho* (Nipponica) — the 三味線 entry by **Fujita Takanori 藤田隆則**
is the single richest source in this document; Heibonsha *Kaitei-shinpan Sekai Daihyakka Jiten*
(entries signed Takeuchi Michitaka 竹内道敬, Hirano Kenji 平野健次, Kanō Mari 加納マリ, Ueda
Ryūnosuke 植田隆之助, Tachino Zenji 舘野善二, Gamō Satoaki 蒲生郷昭); Heibonsha *Mypedia*;
*Britannica Kokusai Dai-hyakka Jiten shōkōmoku jiten*; Shogakukan *Seisenban Nihon Kokugo
Daijiten*; Shogakukan *Digital Daijisen*. **These are the backbone of this document. I read them
in Japanese and translated; translations are mine and are flagged as paraphrase, not quotation.**

**Japan Arts Council 文化デジタルライブラリー (Bunka Digital Library)**, the official public
educational site for Japanese traditional performing arts (`www2.ntj.jac.go.jp/dglib/`). Read and
translated: the four-pentatonic-scale page, the "other pentatonic scales" page, the 間 page, the
metrical/free-rhythm page, the "instrumental expression" page, and two glossary rows.

**Japanese Wikipedia** (三味線, 長唄, 都節音階, 小泉文夫, 家元, 津軽三味線, 唱歌(演奏法), 記譜法,
特殊奏法) — read in Japanese and translated. **Several of these sections carry 要出典 /
"insufficient sources" banners and I say so inline.**

**English Wikipedia, "Shamisen"** — read; **its tuning section has no inline citations at all and
the article is tagged as needing more references**. Used only for corroboration.

**National Diet Library Search opensearch API** — used to verify who published bunkafu scores.

**Commercial English-language source: Bachido** (`bachido.com`), founded 2011 by **Kyle Abbott**;
"Official Distributor in Japan: Ezo'n music Co., Ltd., President & CEO **Masahiro Nitta**"
**[V — bachido.com homepage footer]**. Bachido sells instruments, parts, accessories and video
courses. **Everything sourced to Bachido below is explicitly labelled COMMERCIAL.** It is the main
English-language teaching resource and it is also a shop; its pedagogical claims are a working
player's opinion, and it says so itself (see §1.4).

**Commercial Japanese source: 獅子道 / shamimaster.com**, the Shinjuku Tsugaru Shamisen School of
**Koyama Kōzan 小山貢山** (blog handle "Shishido"), who is also the author of a Tsugaru method book
cited by Japanese Wikipedia (*Tsugaru Shamisen Nyūmon ALL IN ONE*, Chino Publishing, 2012)
**[V — ja.wikipedia 津軽三味線 footnote 3; shamimaster.com; shamimaster.livedoor.biz]**. Labelled
COMMERCIAL below.

**Search engines were unavailable to me** (DuckDuckGo served bot challenges, Mojeek 403), so this
is a direct-source sweep, not an exhaustive literature search. Gaps are listed in §10 of `scales-notation-and-pedagogy.md`.

---

## 1. Holding and posture

### 1.1 The basic seated position

The canonical Japanese description is compact and worth getting exactly right. Nipponica
(藤田隆則) states the basic stance as: sit in **seiza 正座**, place the **dō 胴** (body) on the
**right knee/thigh**, and fix the instrument by **pressing down on the upper part of the dō with
the right arm**; the left hand is **lightly placed against the sao 棹 (neck) — "but it must not
support the neck."** **[V — Kotobank, Nipponica 「三味線」, 奏法 section; my translation of
「正座して右膝の上に胴を置き、右腕で胴の上部を押さえて本体を固定する…左手を棹に軽く添えるが、
棹を支えてはいけない」]**

This is the single most important mechanical fact about shamisen posture and it directly confirms
the usual account's framing: **the instrument is held by the right arm clamping the dō against the body,
not by the left hand**, precisely because the left hand must be free to slide. Nipponica adds that
the left hand needs the ability to move from kandokoro to kandokoro quickly and that these motions
"require enough practised skill to be done without the help of sight" **[V — same]**.

The older Heibonsha *Sekai Daihyakka Jiten* 三味線 entry gives the same configuration in slightly
different words: left hand to the neck, **right wrist presses the dō**, and the plectrum held in
the right hand plucks the strings **from above downward** **[V — Kotobank, Heibonsha
世界大百科事典（旧版）三味線 excerpt quoted under 勘所]**.

### 1.2 Dōkake and yubikake

- **胴掛け / 胴掛 dōkake** (also 胴当て *dōate*): a cloth or leather cover fitted over the face of
  the dō **where the right arm rests during playing**; Nihon Kokugo Daijiten adds that it is there
  "so the plectrum-holding hand can rest on it." **[V — Kotobank 「胴掛」: Digital Daijisen +
  Seisenban Nihon Kokugo Daijiten]**
- **指掛け yubikake**: I could not find this in Kotobank (404 on 指掛 and 指掛け). English Wikipedia
  describes it as "a cloth band worn on the left hand" that "helps the hand slide along the neck"
  **[V — en.wikipedia "Shamisen", though that article is tagged as under-cited]**. The functional
  claim (reduces friction so the left hand glides) is consistent with Nipponica's insistence on
  free left-hand movement, but **the yubikake description rests on a weak source. [U] for anything
  more specific (material, which genres require it, whether it is worn on index+thumb).**

### 1.3 The bachi stroke

- The **撥 bachi** is a large ginkgo-leaf-shaped plectrum gripped in the hand (Japanese
  terminology distinguishes a gripped 撥 from a 爪 *tsume* worn on the finger)
  **[V — Kotobank 「撥」, Britannica Japan]**.
- Nipponica: plucking is done by **bringing the tip of the bachi down onto the string from
  diagonally above**. The descending bachi then **lands on the 撥皮 bachikawa** — the small
  half-circle patch of skin glued over the striking area — **and stops there, producing the
  撥音 bachi-oto**. The bachi-oto is **"valued as a percussive timbral effect."**
  **[V — Kotobach, Nipponica 「三味線」奏法; 撥皮 definition cross-checked at Kotobank 「撥皮」,
  Digital Daijisen]**
- **Genre split on the percussive strike:** Nipponica says **gidayū-bushi 義太夫節 has especially
  many expressive techniques for modulating the strength of the bachi-oto**, whereas **jiuta 地歌
  sometimes deliberately avoids the bachi-oto to aim for pure string tone alone**.
  **[V — Nipponica 「三味線」]** This is a clean, sourced correction to the common English claim
  that "the shamisen is always played percussively."
- **"The stroke comes from the wrist and the weight of the plectrum rather than the arm."** This is
  the standard teaching formulation, but **I could not verify it in any reference work. [U]**
  Nipponica specifies the stroke direction and landing point but not the joint that drives it. The
  nearest thing I found is Bachido's posture series, which argues the opposite emphasis — that a
  straight lower back and open chest set the body up "for flowing power into your arm"
  **[V — bachido.com/faq-items/seiza/ — COMMERCIAL, and explicitly flagged by the author as
  "solely my opinions and assumptions"]**.

### 1.4 Seated vs chair vs standing

- Nipponica gives **seiza as *the* basic posture** and mentions no alternative
  **[V — Nipponica 「三味線」]**.
- Bachido (COMMERCIAL) devotes a short series to this. Its position: seiza is "the perfect posture
  for playing shamisen," because with the legs folded under you the hips sit so that keeping a
  straight lower back is easy, whereas cross-legged sitting already bends the lower back and
  requires constant conscious effort; it notes the feet need not be crossed if that hurts. It then
  says great posture is achievable **in a chair** for those who find seiza too painful, and — in a
  notably unceremonious passage — that good posture is not a requirement for enjoying the
  instrument, that you can play reclined on a sofa, and that in that position the author puts the
  bachi aside and strikes with a fingernail instead.
  **[V — bachido.com/faq-items/{seiza, posture-in-a-chair, relaxing-works-too, other-benefits-of-seiza}/ —
  COMMERCIAL; author-flagged as opinion]**
- **Standing play** (common for modern Tsugaru stage performance and for 新内流し street
  performance): **I could not verify any description of standing posture or of the strap/harness
  arrangements used. [U]**
- **Kouta 小唄** is the clear exception to bachi technique: Nipponica states that **in kouta the
  bachi is in principle not used at all — the strings are played 爪弾き *tsumabiki*, with the
  fingernail** **[V — Nipponica 「三味線」, 撥 subsection]**. English Wikipedia agrees **[V]**.

### 1.5 Where Tsugaru posture differs

Within my scope only insofar as it is the general technique's extreme case:

- Japanese Wikipedia distinguishes two Tsugaru lineages of attack: **叩き tataki**, a forceful
  percussive style in which the bachi strikes the strings (and which "most modern Tsugaru-jamisen
  follows"), versus **弾き hiki**, a delicate style associated with Takahashi Chikuzan's line,
  followed by only a small number of players.
  **[V — ja.wikipedia 津軽三味線; note this article carries 要出典 tags elsewhere]**
- Bachido's free introductory course is literally titled **"Body Mechanics of Tsugaru Shamisen"**
  (11 lectures, Beginner, free) **[V — bachido.com/courses-page/ — COMMERCIAL]**, which is at least
  evidence that the Tsugaru world treats whole-body mechanics as a distinct taught subject rather
  than an afterthought.
- Specific claims that Tsugaru players sit lower, angle the instrument more steeply, or hold the
  dō further forward: **[U] — I found no source.**

---

## 2. The three standard tunings, with actual intervals

### 2.1 The headline correction: there is no fixed reference string

The tunings are usually framed as "relative intervals from the lowest string." **Japanese
musicology explicitly rejects that framing as a general rule.** Nipponica (藤田隆則):

> Shamisen tuning is defined not by absolute pitch but by the relative interval relationships
> between the strings… However, actual retuning is not necessarily mediated by honchōshi. For
> example, when changing from sansagari to niagari within a piece, the change is made **by lowering
> the first string by a major 2nd** — so the view that fixes the first string as the central tone
> does not hold.
> *(my translation)* **[V — Kotobank, Nipponica 「三味線」, 調弦 section]**

Heibonsha makes the same point from the other side: niagari "can equally be made by lowering the
first string of sansagari by a whole tone, or by raising both the second and third strings a whole
tone" **[V — Kotobank 「二上り」, Heibonsha, 竹内道敬]**. Britannica Japan names the result of
making niagari from sansagari by lowering string 1 as **低二上り *hikui-niagari* / low niagari**
**[V — Kotobank 「二上り」, Britannica Japan]**.

So: the three tunings are *interval patterns*, and which string you move to get between them is a
practical decision, usually the one that moves the fewest pegs. Describing them all as transforms
of string 1 is a pedagogical convenience, not how players operate mid-piece.

### 2.2 本調子 honchōshi — VERIFIED, with a precise interval reading

**The standard description is correct.** Independently in four reference works:

| Source | Statement |
|---|---|
| Nipponica (藤田隆則) | 2nd string a **perfect 4th above** the 1st; 3rd string a **perfect 5th above** the 2nd **[V]** |
| Heibonsha (竹内道敬) | 1st–2nd = **perfect 4th**, 2nd–3rd = **perfect 5th**; "since the shamisen has no absolute pitch, so long as the three strings stand in the relation **シ・ミ・シ (B–E–B)**, the overall pitch level is irrelevant" **[V]** |
| Seisenban Nihon Kokugo Daijiten | 1st–2nd = 4th, 2nd–3rd = 5th, **1st–3rd = octave**; "the oldest, most basic tuning method"; pieces in it are "generally stately and elegant" **[V]** |
| Britannica Japan | open strings tuned up a perfect 4th then a perfect 5th; **relative pitch names シ・ミ・シ** **[V]** |

So **honchōshi = perfect 4th + perfect 5th = octave overall**; the usual account's "4th + 5th" and its
example **B–E–B** are both correct, and B–E–B is literally the example Heibonsha uses.
Japanese Wikipedia gives the same with **C–F–C** **[V — ja.wikipedia 三味線, 調弦; section has no
footnotes and carries a sourcing warning]**; English Wikipedia also gives C–F–C **[V — uncited]**.

**Mood/genre:** "authentic, dignified, stately, old-fashioned" and the basic tuning of **jōruri**
**[V — Heibonsha 本調子]**; "**honkakuteki** (orthodox) / masculine" **[V — Nipponica]**. Because it
is the default, songbooks often **do not mark it at all**, and in jōruri the instructions ナオル /
ナオス ("return / put back") usually mean *go back to honchōshi* **[V — Britannica Japan 本調子]**.

### 2.3 二上り niagari — VERIFIED

**= honchōshi with the 2nd string raised a whole tone (major 2nd).** Result: 1st–2nd = **perfect
5th**, 2nd–3rd = **perfect 4th**. Example **C–G–C** / **B–F♯–B**. The name means "the second
[string] is raised."
**[V — Kotobank 「二上り」: Digital Daijisen, Heibonsha (竹内道敬), Mypedia, Britannica Japan; and
ja.wikipedia 三味線]**

**Mood:** "showy/flashy, cheerful, rustic (派手・陽気・田舎風)" **[V — Daijisen and Heibonsha]**;
Nipponica characterises it as "irregular/deviant, flashy, cheerful (変格的・派手・陽気)" **[V]**.
Used heavily in 唄物 *utaimono* (song genres) **[V — Heibonsha]**. The usual "bright/festive
association" is confirmed.

**One mechanical point specific to niagari** and important for technique (§3.5): Nipponica says
that **in niagari especially, if the sawari does not sound, the resonant brilliance and gaiety are
not obtained and the performance is not good** **[V — Nipponica 「三味線」奏法]**.

### 2.4 三下り sansagari — VERIFIED

**= honchōshi with the 3rd string lowered a whole tone (major 2nd).** Result: 1st–2nd = perfect
4th, 2nd–3rd = perfect 4th, so **all adjacent open-string intervals are perfect 4ths**, and the
3rd string is a **minor 7th** above the 1st. Example **C–F–B♭** / **B–E–A**.
**[V — Kotobank 「三下り」: Digital Daijisen, Heibonsha (竹内道敬), Mypedia, Britannica Japan;
ja.wikipedia 三味線 gives "2nd a P4 above the 1st, 3rd a minor 7th above the 1st, e.g. C–F–B♭"]**
The commonly given B–E–A is correct.

**Mood — and a correction.** The usual account's "melancholy association" is only half of what the
Japanese sources say, and the two halves disagree:

- **Heibonsha (竹内道敬): 艶 *tsuya* (glossy/alluring), 粋 *iki* (chic), 軽快 (light, brisk).** **[V]**
- **Digital Daijisen: 粋 and 艶**, much used in nagauta and kouta. **[V]**
- **Nipponica (藤田隆則): 女性的・優美・悲哀 — feminine, graceful, sorrowful.** **[V]**

So "melancholy" is attested (Nipponica) but the dominant characterisation in Japanese reference
works is *chic / alluring / light*, which is close to the opposite connotation. **Do not present
sansagari as simply "the sad tuning."** This is a genuine divergence between sources, not a
translation artefact.

**Genre:** nagauta メリヤス-mono and Fujie-ryū kokyū pieces are "almost all" in sansagari; in jiuta
it was in 端歌物 *hauta-mono* that it first came into heavy use (as against 三味線本手 and 長歌物,
which are almost all honchōshi) **[V — Britannica Japan 「三下り」]**.

### 2.5 Further tunings — what is actually attested

Nipponica lists the derived tunings as: **一下り ichisagari, 六下り rokusagari, 一上り ichiagari,
二上り三メリ niagari-san-meri** **[V — Nipponica 「三味線」調弦]**. Britannica Japan adds a whole
derivation chain **[V — Kotobank 「二上り」, 「三下り」, 「本調子」, Britannica Japan]**:

| Name | Derivation as given | Status |
|---|---|---|
| 低二上り hikui-niagari | niagari made by lowering sansagari's 1st string a whole tone | **[V]** |
| 三上り san-agari | niagari's 3rd string raised a whole tone | **[V]** |
| 高本調子 takahonchōshi | san-agari's 1st string raised a whole tone | **[V]** |
| 高二上り takaniagari | takahonchōshi's 2nd string raised a whole tone | **[V]** |
| 高三下り takasansagari | niagari's 1st string raised a whole tone | **[V]** |
| 一上り ichiagari | honchōshi's 1st string raised **"1音半"** (a tone and a half) | **[V]** as text; the interval looks anomalous beside the other named shifts and I could not corroborate it — **[U] on the interval** |
| 一下り ichisagari | honchōshi's 1st string lowered a whole tone | **[V]** |
| 六下り rokusagari, 二上り三メリ | named only; no definition found | **[U]** |

**Okinawan cognates:** the sanshin equivalents are called **二上げ *nianage*** and **三下げ
*sansage*** **[V — ja.wikipedia 三味線, 調弦]**.

**Not a tuning but often confused with one:** **上調子 uwajōshi** (in shinnai-bushi called
高音 *takane*) is a *second instrument* in a high register, not a tuning of the main one. A small
clamp called a **枷 kase** is tied onto the neck to shorten the vibrating length; the uwajōshi
instrument is tuned a perfect 4th or 5th above the 本手 *honte* (main part), with the effect that
it can play the same melody an octave higher. Used in Edo jōruri (katō-bushi, tokiwazu, kiyomoto,
shinnai) and in nagauta — obligatory in nagauta pieces with many ainote such as *Azuma Hakkei* and
*Aki no Irokusa*. In tokiwazu/kiyomoto "uwajōshi" is *also* a player-rank term (lowest of the
grades). **[V — Kotobank 「上調子」: Digital Daijisen, Seisenban Nihon Kokugo Daijiten, Heibonsha
(竹内道敬), Nipponica (渡辺尚子), Britannica Japan, Mypedia; and 文化デジタルライブラリー
「楽器の表現」, which illustrates it with nagauta *Shakkyō*]**

### 2.6 Absolute pitch: not fixed, but not arbitrary either

Pitch level follows the singer or the ensemble **[V — Britannica Japan 「本調子」: "the pitch level
is set appropriately according to the range of the singer or the instruments playing together";
and for Tsugaru, ja.wikipedia 津軽三味線: "the 一の糸 is adjusted to match the singer's pitch"]**.

But two naming conventions for the chosen level do exist, and they cross-check each other:

- **本 *hon*** (from shinobue sizing): Britannica says setting the 一の糸 to **黄鐘 ōshiki = A** makes
  the 二の糸 **壱越 ichikotsu = D**, and this is called **一本の調子 ("the 1-*hon* key")** — sometimes
  called 六本 if reckoned from the second string instead **[V — Kotobank 「本調子」, Britannica
  Japan]**. Japanese Wikipedia's Tsugaru article says western Japan uses 本, where **4本 ≈ C and
  each semitone up adds one 本** **[V — ja.wikipedia 津軽三味線]**. These agree: if 1本 = A, then
  2本 = B♭, 3本 = B, 4本 = C. **Good independent cross-check.**
- **尺/寸** (from shakuhachi lengths), used in eastern Japan: **2尺 ≈ C, each semitone up subtracts
  one 寸** **[V — ja.wikipedia 津軽三味線]**.
- Electronic **tuning meters for shamisen are commercially sold** **[V — ja.wikipedia 三味線;
  Bachido sells a "Tuning Devices" product category — COMMERCIAL]**.

### 2.7 Why tunings change mid-piece, and how players retune fast

- **Why.** Nipponica: the 調子 (tuning) is strongly bound up with the *mood* of the piece, so the
  choice of tuning is "an important compositional decision"; **when the mood of a piece changes
  within the piece, the tuning often changes too**; and derived tunings are frequently used for
  short stretches inside a piece specifically to get a change of timbre or of melodic shape.
  **[V — Nipponica 「三味線」調弦]**
- **The structural reason, in one sentence.** Britannica Japan: changing from honchōshi to niagari
  mid-piece **moves the position of the tonic (主音) up a fifth** and produces a flashy mood
  **[V — Kotobank 「二上り」, Britannica Japan]**. This is the key insight: retuning is Japanese
  shamisen music's modulation device. It does not transpose the whole instrument; it reshuffles
  which kandokoro on which string give the scale, and hence relocates the tonal centre and the
  available sawari-reinforced pitches.
- **How.** Nipponica: "changing the tuning within a piece is normally done **instantaneously,
  without interrupting the performance, by operating the tuning pegs with the left hand**"
  **[V — Nipponica 「三味線」調弦]**. Combined with §2.1: you move whichever single string gets you
  there — sansagari→niagari is one peg (string 1 down a tone), not two.

---

## 3. Kandokoro, fingering, and the consequences of having no frets

### 3.1 勘所 kandokoro — the term and its synonyms

- **Definition.** A term of 邦楽 (Japanese traditional music): the position at which a finger stops
  a string, adjusting the vibrating length to raise or lower the pitch. **Also called つぼ /
  壺(坪) *tsubo*, and カンツボ *kantsubo*.** It is the equivalent of the Western "position."
  Each instrument type, genre and school has **its own specific names for its kandokoro**.
  **[V — Kotobank 「勘所」: Heibonsha (植田隆之助) and Britannica Japan]** Also spelled 感所, 甲所,
  肝所 **[V — Daijisen, Britannica Japan]**.
- **勘所譜 kandokoro-fu**: the generic Japanese name for *a score notated primarily by indicating
  kandokoro* — i.e. tablature. **In gidayū-bushi this is called 朱 *shu* ("red")**
  **[V — Kotobank 「勘所」, Heibonsha (植田隆之助)]**. This gives you the native taxonomy: bunkafu,
  kenseikai-fu and katei-shiki are all *kandokoro-fu*; kuchi-jamisen is explicitly contrasted with
  them (§6.5 of `scales-notation-and-pedagogy.md`).
- A worn patch on the neck from repeated fingering has its own word: **勘減り *kanberi***
  **[V — ja.wikipedia 津軽三味線]**.

### 3.2 How positions are learned without frets

Nipponica is unusually explicit and I will reproduce the substance closely, since this is where
English accounts are thinnest:

> There are **no frets on the neck, but the positions at which accurate pitches are obtained are
> fixed**, and those positions are called kandokoro (or tsubo). The left hand requires the skill of
> **accurately grasping the kandokoro**, of pressing the string **as though rubbing it into the
> neck in order to apply vibrato**, and of **moving quickly from kandokoro to kandokoro**. These
> actions **demand enough mastery to be performed without the aid of sight**.
> *(my translation)* **[V — Kotobank, Nipponica 「三味線」奏法]**

Two practical learning aids are attested:

1. **The neck joints.** On a 継棹 *tsugizao* (a neck that disassembles for transport), **the joints
   between the sections serve as landmarks for fingering** **[V — Nipponica 「三味線」構造:
   「継棹の場合は棹の継ぎ目が運指のための目印となる」]**. Standard configurations: 三折 *mitsu-ore*
   (3 pieces); some schools use 六折, 九折, 十一折 **[V — Heibonsha 「三味線」]**.
2. **Harmonic/sawari reinforcement as an audible check.** See §3.5 — the sawari gives you an
   acoustic test for whether certain kandokoro are correctly placed.

Position *markers* (stickers, dots) used by modern beginners: **[U] — not found in any source I
read.**

### 3.3 Numbering conventions in tablature

Three distinct numbering systems are attested, and they are mutually incompatible. **This is the
most frequently botched detail in English accounts.**

| System | Open string | Numbering | Source |
|---|---|---|---|
| **文化譜 bunkafu** | **0** | semitone by semitone: `0, 1, 2, 3, #(=3#), 4, 5, 6, 7, 8, 9, ♭(=10♭), 10` — so **0 to 10 spans one octave**, with two of the twelve semitones written as `#` and `♭` signs instead of numbers | **[V — ja.wikipedia 長唄, raw wikitext, verbatim: 「各糸の開放弦を0とし、三味線の勘所を半音ずつ1,2,3,#(3#とも),4,5,6,7,8,9,♭(10♭とも),10……と表記し、0〜10で1オクターブとしたもの」]** |
| **Min'yō convention** | **0** | counts up from 0 at the open string | **[V — en.wikipedia "Shamisen" — uncited section, corroboration weak]** |
| **Jiuta convention** | **1** | the open string is 1, and the numbering **restarts at each octave** | **[V — en.wikipedia "Shamisen" — uncited]** |
| **研精会譜 kenseikai-fu** | — | **not positional at all**: numbers 1–7 are *solfège degrees* (do–ti), with octave shown by a dot right (higher) or left (lower) of the number; the lowest note is written `・7` | **[V — ja.wikipedia 長唄; Nipponica calls it 「階名の数字譜」, a solfège number notation]** |

That last row is the structural point: **kenseikai-fu numbers are pitches, bunkafu numbers are
places on the neck.** A reader who learns one and picks up the other will misread every note.

The vertical gidayū-lineage conventions use **kana, not numbers**: iroha syllables assigned to
kandokoro, written in red (朱) down the right-hand margin of the narration text
**[V — Nipponica 「三味線」記譜と口三味線]**. English Wikipedia describes a vertical tablature in
which **string 3 uses Arabic numerals, string 2 Chinese numerals, and string 1 Chinese numerals
preceded by イ** **[V — en.wikipedia, uncited]**.

### 3.4 Which fingers

Nipponica: the string is stopped **mainly with the index finger**, with the **middle and ring
fingers** brought in as the melodic motion requires, and **rarely the thumb**
**[V — Nipponica 「三味線」奏法]**.

Bachido adds a concrete worked example of index/ring division of labour for hajiki: to sound
Position 3 by hajiki you **hold the index finger at P.3 and pull the string with the ring finger**
(which happens to be sitting around P.4) — the ring finger's own position is irrelevant because
only the index finger's stop should be heard **[V — bachido.com/faq-items/firstly-what-is-hajiki/ —
COMMERCIAL]**.

### 3.5 Vibrato, microtonal inflection, and what fretlessness buys

- **Vibrato** is produced by **pressing the string as though rubbing it into the neck**
  (糸を棹に擦り込むようにして押さえ) **[V — Nipponica 「三味線」奏法]**. Note the mechanism: this is
  a lateral/longitudinal rub against the wood, not the finger-rocking vibrato of a violin.
- **Microtonal and portamento inflection** come from スリ *suri* (§4) and from the general freedom
  of a fretless neck. Bachido (COMMERCIAL) lists "the immensely wide variety of slides and vibrato
  you can create from the fretless neck" among its "advanced flavors"
  **[V — bachido.com/faq-items/a-few-flavors-are/]**.
- **The sawari constraint — the real musical price and payoff of fretlessness.** Nipponica:
  > In order to make the sawari of the first string sound, **the kandokoro on the second and third
  > strings that correspond to overtones of the first string must be stopped especially
  > accurately.** Giving the sawari resonance is an important criterion of evaluation in
  > performance. Especially in the niagari tuning, if the sawari does not sound, the brilliance and
  > gaiety that come from resonance are not obtained and it does not make a good performance.
  > *(my translation)* **[V — Kotobank, Nipponica 「三味線」奏法]**

  That is the answer to "what does fretlessness buy musically": it lets the player tune individual
  *melody notes* into exact harmonic agreement with the open first string so that the sawari drone
  rings sympathetically. Frets quantised to 12-tone equal temperament would make this impossible on
  most notes. (Background on the device: the 上駒 *kamigoma* is shortened so the 一の糸 bypasses it
  and lies directly on the neck, and the 乳袋 area is carved into a sawari "hill and valley" so the
  string's vibration becomes complex; the resulting 噪音 — noise-rich tone with added partials — is
  what players want. An adjustable screw version, **吾妻ざわり *azuma-zawari***, driven up from under
  the neck, is now standard in tokiwazu and kiyomoto. **[V — Kotobank 「さわり」: Heibonsha
  (加納マリ), Nipponica (卜田隆嗣), Britannica Japan, Mypedia]**)

---

## 4. Right-hand (and left-hand articulation) technique

Below, each entry gives the Japanese term, romanisation, plain-English description, and source.
**Where I could not verify a term the usual account asked about, I say so rather than guessing.**

### 4.1 Verified in reference works

| Term | Rōmaji | Description | Genre notes | Source |
|---|---|---|---|---|
| (basic stroke) | — | Bachi tip brought **down onto the string from diagonally above**, landing and stopping on the 撥皮, generating the 撥音 | bachi-oto modulation highly developed in **gidayū**; deliberately avoided in some **jiuta** playing | **[V — Nipponica 「三味線」奏法]** |
| **スクイ(撥)** | **sukui(-bachi)** | **Scooping the string upward** with the bachi. **Smaller in volume** than the downstroke and **different in timbre**. Most often used as a **pattern: strike down, then scoop the same string back up, repeated** | general | **[V — Nipponica 「三味線」奏法; ja.wikipedia 特殊奏法 glosses it as 「下から糸をすくう」]** |
| **スリ** | **suri** | Left hand **slides the finger along the string, giving a portamento effect** | general | **[V — Nipponica 「三味線」奏法]** |
| **ウチ** | **uchi** | Left-hand finger **strikes the string down onto the neck**, producing a **small sound that marks the beat clearly** (hammer-on) | general; ja.wikipedia glosses it as *martellato*, a strong accented strike | **[V — Nipponica; ja.wikipedia 特殊奏法]** |
| **ハジキ** | **hajiki** | Left hand **hooks a finger under the string, presses it toward the neck and releases it off the finger** — a left-hand pluck / pull-off | general | **[V — Nipponica 「三味線」奏法; ja.wikipedia 特殊奏法 glosses it as "left-hand pizzicato"]** |
| **ケシ** | **keshi** | **Strikes the string together with a 掛け声 *kakegoe* (vocal call) and kills the resonance** — i.e. a muting stroke with a shout | general | **[V — Nipponica 「三味線」奏法]** |
| **さわり** | **sawari** | Not a stroke but a sounding condition the right and left hands must cooperate to produce; see §3.5 | all genres; essential in niagari | **[V — Nipponica; Heibonsha 「さわり」]** |

Two important points from this table:

1. **ケシ keshi is the properly attested muting technique**, and it is bundled with a vocal call.
   English accounts that describe shamisen muting as a purely manual damping lose that.
2. The **percussive strike of the skin is not an extra technique — it is intrinsic to the basic
   stroke**, because the bachi always lands on the bachikawa. The variable is how much bachi-oto
   you want.

### 4.2 Attested, but on a weak source

Japanese Wikipedia's 特殊奏法 ("special playing techniques") article lists the following for
shamisen. **This article carries an "insufficient sources" banner and the string-instrument list
has no inline citations. Treat as [U] pending a better source.**

- **ウラハジキ *ura-hajiki*** — "back-hand plucking"; no description given. **[U]**
- **カケバチ *kake-bachi*** — left-hand pizzicato executed while the bachi keeps the string muted. **[U]**
- **コカシバチ *kokashi-bachi*** — listed with no description. **[U]**
- **コキ *koki*** — grouped with スリ as a sliding/rubbing ornament decorating the sustain. **[U]**
- **重音 *jūon*** — double stops, "limited in practice." **[U]**
- **ピチカート / グリッサンド** — Western loanwords used descriptively. **[U]**

The same article's **biwa** list (the shamisen's technical ancestor, and the source of the bachi)
includes **ハタキ・ウチバチ** (striking the string together with the soundboard), **スリ** (rubbing
the string sideways or lengthwise), **押し込み *oshikomi*** (portamento), **ユリ *yuri***
(resonance ornament) and **トレモロ**. **[U — same banner]**

### 4.3 Terms commonly named that I could NOT verify

I am reporting these as unverified rather than reconstructing them:

- **すり上げ *suriage* / すり下げ *surisage*** (upward / downward glissando). The generic **スリ** is
  solidly attested **[V]**, and directional *suriage/surisage* is standard in Tsugaru teaching
  materials as far as I know — **but I found no reference-work or primary source for the two
  directional terms. [U]**
- **押し撥 *oshibachi*** — **not found in any source I read. [U]** The nearest attested item is
  biwa **押し込み *oshikomi*** (portamento) in the weakly-sourced 特殊奏法 list, which is a
  *left-hand* technique and probably not what "oshibachi" means. **Do not assert a definition.**
- **トレモロ tremolo** on shamisen — attested for **koto and biwa** in 特殊奏法 **[U — weak source]**,
  **not attested for shamisen in anything I read. [U]**
- **叩き *tataki*** as a named Tsugaru attack-style **[V — ja.wikipedia 津軽三味線]**, but its
  precise mechanics **[U]**.
- **カマシ *kamashi*** — Bachido markets a course "Advanced Kamashi," calling kamashi "the hallmark
  technique of the tsugaru [shamisen]" **[V that Bachido says this — bachido.com/courses-page/ —
  COMMERCIAL]**. **No non-commercial source read; definition [U].** (Tsugaru-specific; another
  agent's scope.)

### 4.4 Techniques as *written* vs techniques as *expression* — a real pedagogical divide

Bachido (COMMERCIAL) makes an observation worth recording because it bears on notation:

> While these are properly called "techniques", techniques for shamisen are usually something
> pre-determined. When learning a song (Sakura Sakura, for example), one will read the song
> notation to find which/where each technique is executed. **It's static and fixed.** …that's great
> if the goal is to play in a formal ensemble, but for the emotion-expressing side of shamisen, I
> much prefer the term 'flavors'…
> **[V as a quotation from bachido.com/faq-items/a-few-flavors-are/ — COMMERCIAL]**

Its list of "flavors" includes two items not in any Japanese reference work I read: **striking
nearer to or further from the bridge** (affecting volume and sharpness), and **simultaneously
touching the string with the thumb as the bachi strikes down** to get a subtle harmonic/damped
tone. **[V that Bachido teaches these — COMMERCIAL; [U] as to whether they carry Japanese names.]**

Bachido also publishes a usefully specific physical diagnosis for hajiki: because the string is
still vibrating from the bachi stroke, placing the ring finger *on top of* the vibrating string
makes the ring finger's own position sound (producing an unwanted pitch); the remedy is to place
the ring finger **between the two strings** rather than on top, then pull sideways until the string
slips off. Doing it the wrong way yields **an uchi (hammer-on) immediately followed by a hajiki** —
Bachido reframes the error as a usable ornament.
**[V — bachido.com/shamipedia/hajiki-consisent-tone/ and its four sub-articles — COMMERCIAL]**

---

