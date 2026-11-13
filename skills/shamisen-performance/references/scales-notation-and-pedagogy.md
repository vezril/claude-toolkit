# Shamisen Scale Theory, Notation, and Pedagogy

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
player's opinion, and it says so itself (see §1.4 of `technique-and-tuning.md`).

**Commercial Japanese source: 獅子道 / shamimaster.com**, the Shinjuku Tsugaru Shamisen School of
**Koyama Kōzan 小山貢山** (blog handle "Shishido"), who is also the author of a Tsugaru method book
cited by Japanese Wikipedia (*Tsugaru Shamisen Nyūmon ALL IN ONE*, Chino Publishing, 2012)
**[V — ja.wikipedia 津軽三味線 footnote 3; shamimaster.com; shamimaster.livedoor.biz]**. Labelled
COMMERCIAL below.

**Search engines were unavailable to me** (DuckDuckGo served bot challenges, Mojeek 403), so this
is a direct-source sweep, not an exhaustive literature search. Gaps are listed in §10.

---


## 5. Scale theory

### 5.1 Koizumi Fumio's tetrachord theory

**Koizumi Fumio 小泉文夫** (b. Tokyo, registered 4 April 1927 — actual birth 29 March; d. 20 August
1983, liver failure, aged 56). Studied aesthetics at the University of Tokyo; taught at the Tokyo
National University of Fine Arts and Music (Geidai) from 1959, professor from 1975. Spent ~30 years
popularising folk and world music on radio and TV; Suntory Prize for Arts and Sciences, 1980.
Ryuichi Sakamoto studied ethnomusicology under him. Key work for scale theory: **『日本伝統音楽の
研究』 vol. 1, Ongaku no Tomo Sha, 1958**, subtitled 「民謡研究の方法と音階の基本構造」.
**[V — ja.wikipedia 小泉文夫; I did NOT read Koizumi's book — see §0.1]**

**The theory, as stated by the Japan Arts Council's official educational site** (translated):

> The musicologist Koizumi Fumio proposed this theory. He treated **the perfect fourth as the basic
> framework of Japanese melody and called it a tetrachord (テトラコルド)**. A perfect fourth spans
> six piano keys. Two such spans are used: **ド–ファ (C–F)** and **ソ–ド (G–C)**. The **middle tone**
> between each pair of outer notes can take **four heights**: between ド and ファ — ♭レ, レ, ♭ミ, ミ;
> between ソ and ド — ♭ラ, ラ, ♭シ, シ. **Stacking two tetrachords of the same type** gives a
> five-tone scale within the octave. Each of the four basic scales results from this process.
> **[V — 文化デジタルライブラリー, 「基本的な4種の五音音階」, www2.ntj.jac.go.jp/dglib/contents/learn/edc29/shiru/shikumi/onkai/goon/]**

Note what the official source actually says, and what it does *not*:

- The two tetrachord frames it uses, C–F and G–C, are **disjunct** (separated by the whole tone
  F–G). **Koizumi's full theory also treats conjunct joining** (two tetrachords sharing a boundary
  tone, producing non-pentatonic/wider-ambitus results) **— but the Bunka Digital Library page
  shows only the disjunct case, and I could not verify the conjunct machinery from a primary
  source. [U]** The "other pentatonic scales" sibling page confirms the limitation from the other
  direction: Japanese music "also includes scales that do not fit within a tetrachord frame," and
  it names **呂音階 *ryo*** and **呂陰音階 *ryo-in*** as examples **[V — 文化デジタルライブラリー,
  「その他の五音音階」]**.
- **核音 *kakuon*** ("nuclear tone," Ger. *Kernton*) is the companion concept that makes the theory
  work and that Western summaries usually drop. Britannica Japan defines it as a term of
  comparative/ethno-musicology: **a melodic tone whose pitch does not float, which governs its
  neighbouring tones, and which can serve as the final of a melody — a concept distinct from the
  tonic of modern European music.** Synonyms 基音, 中心音. **[V — Kotobank 「核音」, Britannica
  Japan]** In tetrachord terms the two *frame* tones of each fourth are the nuclear tones and the
  middle tone is the floating one. **That the frame tones specifically are Koizumi's kakuon is my
  inference from combining the two sources above — [U] as an attribution to Koizumi.**

### 5.2 The four tetrachords and the four scales — exact pitch content

From the Japan Arts Council page, verbatim pitch sets **[V — 文化デジタルライブラリー,
「基本的な4種の五音音階」]**:

| Scale | Pitch set as published | Semitone steps | Tetrachord type (C–F form) |
|---|---|---|---|
| **民謡音階 min'yō** | ド ♭ミ ファ ソ ♭シ (ド) = C E♭ F G B♭ (C) | 3–2–2–3–2 | C–E♭–F = **3 + 2** |
| **律音階 ritsu** | ド レ ファ ソ ラ (ド) = C D F G A (C) | 2–3–2–2–3 | C–D–F = **2 + 3** |
| **都節音階 miyako-bushi** | ド ♭レ ファ ソ ♭ラ (ド) = C D♭ F G A♭ (C) | 1–4–2–1–4 | C–D♭–F = **1 + 4** |
| **琉球音階 Ryūkyū** | ド ミ ファ ソ シ (ド) = C E F G B (C) | 4–1–2–4–1 | C–E–F = **4 + 1** |

(Semitone columns computed by me from the published pitch sets; each sums to 12.)

**Worked example — all four on D as the lower nuclear tone** (my transposition of the published
sets; arithmetic, not a source claim):

- **min'yō on D:** D – F – G – A – C – (D). Tetrachords D–F–G and A–C–D.
- **ritsu on D:** D – E – G – A – B – (D). Tetrachords D–E–G and A–B–D.
- **miyako-bushi on D:** D – E♭ – G – A – B♭ – (D). Tetrachords D–E♭–G and A–B♭–D.
- **Ryūkyū on D:** D – F♯ – G – A – C♯ – (D). Tetrachords D–F♯–G and A–C♯–D.

### 5.3 陽/陰 (yō / in) — and the error, which is bigger than is usually suggested

The standard dictionary definitions first:

- **陽旋法 / 陽音階 yō-senpō / yō-onkai**: "a five-tone scale **containing no semitones**; common in
  folk song; also called **田舎節 *inaka-bushi***." **[V — Kotobank 「陽旋法」, Digital Daijisen and
  Seisenban Nihon Kokugo Daijiten]**
- **陰旋法 / 陰音階 in-senpō / in-onkai**: "a five-tone scale **containing semitones**; developed in
  the shamisen and koto music of the mid-Edo period onward; = **都節 *miyako-bushi***."
  **[V — same two dictionaries]**
- 都節音階 is "nearly synonymous with 陰旋法"; representative pitches **ミ・ファ・ラ・シ・ド**
  (E F A B C) **[V — ja.wikipedia 都節音階, citing Nihon Kokugo Daijiten and Digital Daijisen]**.
  Note that E F A B C is the same interval sequence (1–4–2–1–4) as the Bunka Digital Library's
  C D♭ F G A♭ — the two publications simply pick different reference pitches, as the Wikipedia
  article itself observes.

**Now the error. It is not merely that Westerners mislabel these as "the Japanese minor/major
pentatonic." Japanese musicology has declared the yō/in framework itself wrong.** Heibonsha's
*Mypedia* says so in both entries:

> **陽旋法:** A mode without semitones, generally thought since the Meiji era to be one of the tone
> organisations of Japanese traditional music; also called inaka-bushi. **However, at present this
> is held to be erroneous**, for reasons including that the tone organisation of Japanese
> traditional music is **not modes but scales**, and that **two fundamentally different scales —
> 民謡音階 and 律音階 — are conflated inside this one term.**
>
> **陰旋法:** …roughly corresponds to the miyako-bushi scale. **However, at present this concept is
> held to be erroneous**, because Japanese traditional music's tone organisation is scales, not
> modes, and because the concept of its counterpart 陽旋法 is confused.
> *(my translations)* **[V — Kotobank 「陽旋法」 and 「陰旋法」, Heibonsha 百科事典マイペディア]**

So there are **three** distinct errors to name, in increasing severity:

1. **Mode vs scale.** 旋法 (*senpō*, "mode") imports a Western/medieval notion of a fixed rotation
   of a parent collection. Japanese practice is better described by *scales* generated from
   tetrachords with nuclear tones. **[V — Mypedia, both entries]**
2. **The yō basket conflates two different pitch sets.** 民謡音階 (C E♭ F G B♭, tetrachord 3+2) and
   律音階 (C D F G A, tetrachord 2+3) are **not the same collection** and not rotations of each
   other in function; lumping them as "the anhemitonic Japanese pentatonic" erases the distinction
   that matters most. **[V — Mypedia 陽旋法 + the Bunka Digital Library pitch sets]**
3. **"Japanese minor/major pentatonic" compounds both.** As pitch-class sets, **min'yō on C is
   literally the C minor pentatonic** and **ritsu on C is a rotation of the F major pentatonic** —
   which is exactly why the Western labels are seductive and exactly why they mislead. They name
   the *collection* and silently import the *tonal centre* that goes with the Western label, which
   is usually the wrong nuclear tone. And **neither Ryūkyū (C E F G B) nor miyako-bushi
   (C D♭ F G A♭) is a Western pentatonic at all** — the "major pentatonic = Ryūkyū" equation some
   English sources make is simply false. **[Set-identity arithmetic is mine from the published
   pitch sets; the underlying pitch sets are [V]; the critique is [V — Mypedia]]**

**Also worth recording:** the yō/in framework is itself a **Meiji-era construction** ("generally
thought *since the Meiji era*") **[V — Mypedia]**, i.e. it postdates the Edo repertoire it is
applied to, which is part of why it fits badly.

### 5.4 Which scales go with which genres

- **都節 / in:** the dominant scale of 近世邦楽 (early-modern Japanese art music) — "a shared trait
  of many genres" — and before the early modern period the semitone-free **律音階** had been
  dominant. A dated hinge event: **in mid-17th-century Kyoto, 八橋検校 Yatsuhashi Kengyō changed the
  tuning of the 筑紫箏 from ritsu to miyako-bushi, establishing the 八橋流.**
  **[V — ja.wikipedia 都節音階, citing 上参郷祐康 in Nipponica]**
- A **shamisen-specific worked illustration** exists in the official Japanese material: the Bunka
  Digital Library explains miyako-bushi using the **nagauta piece 「石橋」 *Shakkyō***, where the
  voice and shamisen together form **ド・♭レ・ファ・ソ・♭ラ** **[V — ja.wikipedia 都節音階 citing
  文化デジタルライブラリー]**. Use this as the canonical example rather than inventing one.
- **民謡音階:** folk song, by name and by the equivalence 陽 = 田舎節 = folk-song idiom
  **[V — Daijisen 陽旋法; Mypedia; Bunka Digital Library naming]**.
- **琉球音階:** Okinawan/Ryukyuan music **[V — named as such in the Bunka Digital Library]**.
- **Which Tsugaru pieces use which scale:** this was a gap in this file and it has since been
  closed by the `tsugaru-shamisen` skill, which maps the repertoire piece by piece. The answer is
  more interesting than the general expectation: **Jongara-bushi, Yosare-bushi and Ohara-bushi use
  the 民謡 min'yō pentatonic**, **Aiya-bushi uses 律 ritsu**, and **Tsugaru sansagari is a
  hybrid** — and, notably, **no Tsugaru piece uses 都節 miyako-bushi / the *in* scale at all.**
  That last point is worth carrying back into §5.3 of `technique-and-tuning.md`: the yō/in
  dichotomy is not merely a bad analytical frame in general, it has no purchase on this repertoire
  even descriptively. See `tsugaru-shamisen`'s `references/repertoire-and-technique.md` for the
  per-piece data and the caveat that the scale *mapping* there is the researcher's inference from
  verified pitch content rather than a source's own claim.
- Note also that English-language teaching frames scales as a separate curriculum unit: Bachido's
  course catalogue has a **"Scales" category with 9 courses**, including Kevin Kmetz's **"World
  Scales"** (46 lectures, $19.95) **[V — bachido.com/courses-page/ — COMMERCIAL]**. That is a
  modern, explicitly cross-cultural framing with no counterpart in the traditional iemoto
  curriculum.

### 5.5 Scale practice is partly set by vocal style, not instrumental theory

The claim is substantially supported, in three independent ways:

1. **The instrument has no absolute pitch and is tuned to the singer** (§2.6 of `technique-and-tuning.md`)
   **[V — Britannica Japan 本調子; ja.wikipedia 津軽三味線]**.
2. **Nipponica's striking formulation about the voice–shamisen relationship:** even when one person
   sings and plays, **in the learning process the shamisen melody is what is first normative
   (規範)**, and **"the song or narration is technically and aesthetically heightened as a
   *deviation* (ずれ) from the shamisen melody."** **[V — Kotobank, Nipponica 「三味線」三味線音楽;
   my translation]** The scale as realised is therefore a negotiation, with the vocal line
   systematically departing from the instrumental grid.
3. **The shamisen bends time for the voice:** in a Kiyomoto example (*Michitose*), **the shamisen
   follows the jōruri vocal, widening the beat at vocal highlights before returning to the original
   tempo** **[V — 文化デジタルライブラリー, 「拍節的なリズム・自由リズム」]**.

The strong form of the claim — that vocal style *determines* scale choice — is **[U]**; what is
verified is that pitch level, timing, and the realised melodic surface are all subordinated to the
voice.

---

## 6. Notation — there is no single system, and that is the point

### 6.1 The baseline: no notation at all, then too many

Nipponica's history (§6.6) opens by stating that **when the shamisen first arrived, scores were not
used for transmission at all**; the expedient was to **sing the melody by assigning the
instrument's sounds to verbal syllables and memorising it** **[V — Nipponica 「三味線」記譜と口三味線]**.

Heibonsha's older 三味線 entry states the modern situation bluntly (translated):

> Published scores are mostly for jiuta; in the modern period published scores appeared for nagauta
> too, but **in genres and schools with few audiences, each performer merely records the music in
> his or her own idiosyncratic notation as a memory aid.** Even published jiuta scores used
> different notation systems in different collections; at present what is called **家庭式三味線譜
> *katei-shiki shamisen-fu*** has spread [for jiuta], and in **nagauta and kouta** what is called
> **文化譜 *bunkafu*** has spread.
> **[V — Kotobank, Heibonsha 世界大百科事典（旧版）「三味線」 excerpt reproduced under 「文化譜」
> and 「口三味線」]**

That one paragraph gives the modern division of labour: **bunkafu = nagauta/kouta; katei-shiki =
jiuta.** It also explains *why* notations are mutually unintelligible: they were never meant to
circulate outside a school.

### 6.2 文化譜 bunkafu — the dominant modern tablature

- **What it is.** Also called **赤譜 *akafu*** ("red score") or **三線譜**. Written
  **horizontally**, with **three horizontal lines representing the three strings**, and **numbers
  on the lines giving the kandokoro**. **[V — ja.wikipedia 長唄; the three-line horizontal layout
  is also described at en.wikipedia "Shamisen" — uncited there]**
- **Numbering.** Open string = **0**; then semitone by semitone `1, 2, 3, #, 4, 5, 6, 7, 8, 9, ♭, 10`,
  with **0–10 spanning one octave** (see §3.3 of `technique-and-tuning.md` for the verbatim Japanese). **[V — ja.wikipedia 長唄
  raw wikitext]**
- **Who and when — with a name discrepancy I could not fully resolve.**
  - Japanese Wikipedia (長唄): devised in the **Taishō era** by **杵家彌七 Kineie Yashichi (4th
    generation)** together with her husband **赤星國清 Akahoshi Kunikiyo**. **[V — ja.wikipedia 長唄;
    section has no footnotes and the article carries a sourcing banner]**
  - Nipponica (藤田隆則): "in the Taishō period **4th-generation 杵屋弥七 *Kineya* Yashichi** created
    bunkafu." **[V — Nipponica 「三味線」記譜と口三味線]**
  - **杵家 (Kineie) and 杵屋 (Kineya) are different surnames.** I broke the tie against catalogue
    data: **National Diet Library records credit 「杵家, 弥七」 — Kine*ie* — on 三味線文化譜
    editions** (e.g. 『秋の色種：長唄：三味線文化譜』, 邦楽社, 1952.1; 『秋の色種(上調子)：長唄』,
    邦楽社, 1953.5; and earlier 『愛國軍歌集』 1936.2 and 『愛國歌謠集』 1939.2 issued by
    **三味線文化譜樂會**, the "Shamisen Bunkafu Society"). **[V — NDL Search opensearch API,
    ndlsearch.ndl.go.jp]** **Conclusion: 杵家彌七 Kineie Yashichi is the better-supported form;
    Nipponica's 杵屋 is likely a variant or an error. The spouse's name 赤星國清 rests on Japanese
    Wikipedia alone — [U].**
- **Publisher.** Bunkafu scores are published by **邦楽社 Hōgakusha**, from at least 1952
  **[V — NDL Search records above]**, and a dedicated **三味線文化譜樂會** was issuing bunkafu
  volumes by the 1930s **[V — same]**. Bunkafu's reach extends well past nagauta: NDL lists e.g.
  『秋田三味線民謡集：浅野梅若流：三味線文化譜』 (邦楽社, 1990/1993/1996) — i.e. **folk-song and
  regional repertoire is also published in bunkafu** **[V — NDL]**. A commercial Tsugaru school
  advertises transcription **into bunkafu**, into **箏譜** and into **工工四** (the Okinawan sanshin
  system), and also offers combined **五線譜＋文化譜** (staff + bunkafu) editions
  **[V — shamimaster.com/gakufu.html — COMMERCIAL]**.

### 6.3 研精会譜 kenseikai-fu — and how it differs

- Also called **小十郎譜 Kojūrō-fu**. Developed in the **Taishō era** by **吉住小十郎 Yoshizumi
  Kojūrō**, a pupil of the 4th-generation **吉住小三郎 Yoshizumi Kosaburō**.
  **[V — ja.wikipedia 長唄; Nipponica credits 「吉住小十郎による小十郎譜（研精会譜）」 and dates the
  staff-notation and Kojūrō-fu efforts to the Meiji period]** **Note a date discrepancy: Wikipedia
  says Taishō, Nipponica implies Meiji. [U] on the exact decade.**
- **How it differs — this is the substantive point.** Kenseikai-fu is written **vertically**, and
  its numbers **1–7 correspond to the Western solfège degrees do–ti**, usually in 2/4; octaves are
  marked by a **dot to the right (higher) or left (lower)** of the number, the lowest note being
  written `・7`. **[V — ja.wikipedia 長唄]** Nipponica classifies it as 「階名の数字譜」 — a
  *solfège* number notation **[V]**.
  So: **bunkafu is tablature (where to put your finger); kenseikai-fu is pitch notation (what note
  to sound).** Bunkafu tells you nothing directly about pitch; kenseikai-fu tells you nothing
  directly about string or position. They encode orthogonal information.

### 6.4 家庭式 katei-shiki and the other publisher/school systems

- **家庭式三味線譜 katei-shiki shamisen-fu.** Nipponica: **in the Taishō period the 大日本家庭音楽会
  (Dai-Nippon Katei Ongakukai, "Greater Japan Home Music Society") of Fukuoka published
  katei-shiki shamisen-fu** **[V — Nipponica 「三味線」記譜と口三味線]**. Heibonsha: it is **the
  system that has become standard for jiuta** **[V — Heibonsha 「三味線」, quoted in §6.1]**.
  **I could not find a description of how its symbols work. [U]** (It is absent from Japanese
  Wikipedia entirely — my search of ja.wikipedia for 家庭式譜 returned nothing relevant **[V — ja
  Wikipedia search API]**.)
- **青柳譜 Aoyagi-fu.** Shōwa era, devised by **杵屋彌之介 Kineya Yanosuke**, a member of the
  Kenseikai, named after his real name. It **extends kenseikai-fu by adding three vertical lines
  for the three strings (一の糸/二の糸/三の糸)**, specifically to make string choice and fingering
  clear to readers of kenseikai-fu. Vertical. **[V — ja.wikipedia 長唄]** This is a neat
  illustration of the tablature/pitch tension in §6.3: Aoyagi-fu is a pitch notation retrofitted
  with tablature.
- **栄二譜 Eiji-fu.** Shōwa era, by **杵屋栄二 Kineya Eiji**, to record rare pieces and **黒御簾音楽
  *kuromisu ongaku*** (the offstage/behind-the-blind kabuki music). Uses **twelve kana** for the 1–7
  degrees with dotted octaves as in kenseikai-fu, and **distinguishes the three strings by script
  type**: 一の糸 in variant kana, 二の糸 in hiragana, 三の糸 in katakana. **Not commercially
  published**; used within the profession (幕内) for archival records. **[V — ja.wikipedia 長唄]**
- **佐吉譜 Sakichi-fu** and **杵勝譜 Kinekatsu-fu** — listed by name only, no description.
  **[V that they exist as named systems — ja.wikipedia 長唄; [U] on content]**
- **大薩摩略譜** by **根岸の勘五郎 (11th-generation 杵屋六左衛門)**, and **三味線速記譜** by
  **田中正平 Tanaka Shōhei** **[V — Nipponica 「三味線」記譜と口三味線; [U] on how they work]**.
- **Historical published sources (all from Nipponica, 記譜と口三味線) [V]:**
  - **1664 (寛文4) 『糸竹初心集』 *Shichiku shoshinshū*** — presented a system assigning **a
    different kana to each sound as determined by kandokoro + right-hand technique**, which
    regularised how melodies were chanted and simultaneously recorded them; **but it used so many
    kana that it was hard to chant in practice**, and once melodies became patterned, note-by-note
    distinction stopped being necessary. Independently verified: Nakamura Sōsan 中村宗三, Kyoto,
    Akitaya Kuhē, 3 vols. — vol. 1 hitoyogiri shakuhachi, vol. 2 koto, vol. 3 shamisen; **the
    oldest published score book of early-modern Japanese music**; pitch is clear but note values
    are not; several decipherment/reconstruction attempts have been made. Mypedia specifies its
    three notation types as 指孔譜 (fingerhole), 弦譜 (string) and 感所譜 (kandokoro).
    **[V — Kotobank 「糸竹初心集」: Seisenban Nihon Kokugo Daijiten, Nipponica (千葉潤之介),
    Heibonsha (平野健次), Britannica Japan, Mypedia]**
  - **1685 (貞享2) 『大ぬさ』** and **1757 (宝暦7) 『浄瑠璃三味線独稽古』** — record 「糸の声」
    *ito no koe* ("voice of the strings"), i.e. **kuchi-jamisen** as it had by then formed.
  - **1762 (宝暦12) 『音曲力草』** — jiuta; detailed symbolisation of rhythm, technique and kandokoro.
  - **1793 (寛政5) 『五線録』** — practical score built **around kuchi-jamisen**, with kandokoro and
    metrical signs added as needed.
  - **1828 (文政11) 『絃曲大榛抄』** — uses the **十二律** (twelve Japanese pitch names) to notate
    **both shamisen and voice pitch strictly**, with innovations in metre notation.
  - **Gidayū-bushi's 朱 *shu*:** iroha kana assigned to kandokoro, written **in red** down the right
    margin of the chanter's practice text.
  - **Meiji onward:** attempts to put shamisen music into **Western staff notation**; Kojūrō-fu
    (kenseikai-fu); Aoyagi-fu.

### 6.5 口三味線 kuchi-jamisen / 唱歌 shōga — what the syllables encode

**What it is.** A 邦楽 term: chanting the shamisen's melody with the mouth. It is the shamisen
application of **唱歌 *shōga***, the mnemonic onomatopoeic singing of instrumental parts, which came
down **from gagaku via the 一節切 hitoyogiri** to the shamisen. The Okinawan sanshin equivalent is
**口三線 *kuchi-sanshin***. **[V — Kotobank 「口三味線」, Heibonsha (舘野善二); ja.wikipedia
唱歌(演奏法), oldid 100736582, which cites Tokumaru Yoshihiko 徳丸吉彦, 『音楽理論の基礎』 (Open
University of Japan, 2007/2010) and 『民族音楽学理論』 pp. 91–100]**

**What the syllables encode — and a flat contradiction between two reference works.** This matters
because English sources repeat one or the other without noticing.

**Account A — Heibonsha (舘野善二)** *(my translation)*:
> 「チン・トン・シャン」 has become almost a byword for shamisen music, but **チン is the sound of a
> stopped kandokoro on the 3rd string; トン is the open 2nd string; シャン is the 2nd and 3rd strings
> plucked together**; besides these, **a stopped note on the 1st and 2nd strings is ツン**, the 1st
> and 2nd together is **チャン**, the **open 3rd string is テン**, and **when the bachi scoops (すくう)
> the ラ-row syllables are used** — so from the chanted syllable alone you can immediately tell the
> string, whether it was stopped or open, how the bachi was used, and even left-hand fingerings such
> as hajiki. **Its defect is that it is unclear about pitch height.**
> **[V — Kotobank 「口三味線」, Heibonsha 改訂新版世界大百科事典]**

**Account B — Shogakukan *Seisenban Nihon Kokugo Daijiten*** *(my translation)*:
> **The sounds of the 1st, 2nd and 3rd strings are represented by トン, テン, チン respectively**, and
> **the sounds of scooping (すくう) those with the bachi by ロン, レン, ノン**; it can express
> distinctions of string, of playing technique and of timbre. (Earliest attestation given: a
> 1638 haikai text, 『鷹筑波』.)
> **[V — Kotobank 「口三味線」, Seisenban Nihon Kokugo Daijiten]**

**These are not reconcilable.** Heibonsha assigns テン to the *open 3rd string* and トン to the *open
2nd*; the Nihon Kokugo Daijiten assigns トン/テン/チン to strings 1/2/3 in order. Heibonsha says
scooping takes the whole **ラ-row** (ラ リ ル レ ロ); the Daijiten names three specific scoop
syllables **ロン / レン / ノン** (and ノン is not even in the ラ-row). My reading is that the
Daijiten gives a simplified, systematised gloss and Heibonsha gives the genre-practice version —
and that **kuchi-jamisen syllabaries differ by genre and school, exactly as the notations do.**
Japanese Wikipedia independently supports genre variation: in **gidayū-bushi shamisen, テン is the
open third string**, and **ツン is the same pitch played on the second string** — "a different word"
for the same pitch; it gives a gidayū *tsunagi* phrase chanted as **「ツ テ ト ドン テツ テ ト ツン」**
**[V — ja.wikipedia 唱歌(演奏法)]**. **Any English source that presents a single canonical
ten-ton-shan table is overstating. [Flag this.]**

**The one thing all sources agree on — what it does and does not carry.** Nipponica:
> Kuchi-jamisen is a melody-chanting method still in use today; by chanting it, **it expresses
> rhythm clearly and makes differences of playing technique and timbre explicit in kana**. **The
> number of kana used is small, and it does not indicate pitch or kandokoro.** However, the grouping
> of kana into phrases **makes the melody easy to remember and helps the player recognise melodies
> as patterns.**
> **[V — Kotobank, Nipponica 「三味線」記譜と口三味線; corroborated by Heibonsha's "defect: unclear
> about pitch," and by Heibonsha 「三味線」, which notes it is sometimes written down and functions
> "as an imperfect kind of score"]**

**Why it remains central to teaching** — Japanese Wikipedia (citing Tokumaru) gives three reasons:
a student can **practise a piece without an instrument**; a student can **learn a piece from a
teacher without either of them holding an instrument**; and learning the piece **with its technique
built into the syllables** prepares performance and **strengthens memory**. Writing the syllables
down gives a visual fallback when memory fails. **[V — ja.wikipedia 唱歌(演奏法)]**

That is the crux: kuchi-jamisen is a *gesture-and-rhythm* notation wearing the clothes of a tune.
It encodes exactly what tablature-plus-staff can't easily carry — which hand did what, and when —
and omits exactly what the ear and the tuning supply anyway.

### 6.6 Western staff notation: limited use, and what it loses

- Attempts to render shamisen music in staff notation date from the **Meiji period** and are listed
  by Nipponica as one experiment among many, not as a successor system
  **[V — Nipponica 「三味線」記譜と口三味線]**.
- The living practice is **hybrid**: a commercial Japanese school advertises producing **「五線譜＋
  文化譜」** combined editions from a customer's existing staff notation, and separately advertises
  transcription services *into* bunkafu — i.e. staff notation functions as an interchange format,
  with bunkafu supplying what it cannot say. **[V — shamimaster.com/gakufu.html — COMMERCIAL]**
- Western symbols have been **absorbed into the Japanese systems** rather than replacing them:
  dynamics, time signatures and fermatas have been adopted into the vertical tablature
  **[V — en.wikipedia "Shamisen" — uncited]**; kenseikai-fu's 1–7 are Western solfège degrees in a
  vertical Japanese layout **[V — ja.wikipedia 長唄]**.
- **What staff notation loses**, stated as a derivation from verified facts rather than as a sourced
  claim: (a) **string and kandokoro choice** — the same pitch on a different string is a different
  sound and in gidayū even a different *word* (テン vs ツン, §6.5) **[V on the テン/ツン fact]**;
  (b) **the sawari condition**, which depends on which string carries the note (§3.5 of `technique-and-tuning.md`) **[V]**;
  (c) **which technique produced the note** — sukui, uchi, hajiki and a plain stroke can all give
  the same pitch with different attack **[V]**; (d) **ma and elastic beat** (§8.4) **[V]**.
  **The synthesis in this paragraph is mine. [U] as a sourced assertion.**

### 6.7 Tsugaru: oral and aural first, notation late and partial

Within my scope only as a contrast case:

- Japanese Wikipedia states that **Tsugaru-jamisen's history is largely 口伝 (oral transmission)**,
  that **documentation is limited**, and that historical claims about it are reconstructions; it
  also says **schools are distinguished partly by transmission method, which may be oral or
  written (楽譜)** **[V — ja.wikipedia 津軽三味線; article carries 要出典 tags]**.
- **唄づけ *utazuke*** — improvised accompaniment responding to the singer — is named as a skill
  **"fewer players can do today"** **[V — same]**. That is the cost of notation-mediated learning
  stated by a Japanese source.
- Yet notation for Tsugaru is now commercially routine: bunkafu transcription is sold by the piece
  (a Tsugaru school quotes **¥20,000 for transcribing one 曲弾き *kyokubiki* solo** of ~3 minutes,
  and **¥5,000+** for bunkafu/koto/kunkunshi transcription generally)
  **[V — shamimaster.com/gakufu.html — COMMERCIAL]**. And NDL shows folk-song repertoire in bunkafu
  in print since at least 1990 **[V — NDL]**.
- **What this means for learning it:** a learner can now obtain a bunkafu score of most standard
  Tsugaru pieces, but the score records kandokoro, string and marked techniques — not the
  improvisatory *utazuke* relationship to a singer, and not the attack and ma. **Synthesis; [U] as
  a sourced claim.**

---

## 7. The iemoto system, natori, and how one actually learns

### 7.1 家元 iemoto — the structure

- **Definition and scope.** The 家元 is the supreme authority in a traditional Japanese art or
  martial discipline, or the family line holding that role; the system covers tea, flower
  arranging, calligraphy, noh, Japanese dance and the traditional musics. Some fields (go, shogi)
  once had it and dropped it. **[V — ja.wikipedia 家元]**
- **History.** Elements go back to Heian-period hereditary court offices; **iemoto-style families
  became common in the late Edo period**, when a wealthy merchant class expanded cultural
  participation; the term appears in a **1757** text. Its roots are often linked to esoteric
  Buddhist secret-transmission practice and to Neo-Confucian loyalty-to-master ideas; the article
  also draws an analogy to the Hongan-ji priesthood. **[V — ja.wikipedia 家元, citing Nishiyama
  Matsunosuke 西山松之助, 『家元の研究』, Yoshikawa Kōbunkan, 1982 — the standard study, which I did
  not read]**
- **How it works.** Authority normally passes **within the family**, though adoption or marriage can
  bring a capable student into the line. The iemoto typically controls **both artistic standards and
  organisational leadership**, decisions flowing top-down. Intermediate ranks — **名取 *natori*** and
  **師範 *shihan* (instructor)** — sit between the iemoto and ordinary students. The iemoto issues
  **licences and credentials**; where a branch issues a certificate, **the fee is split, half to
  headquarters and half retained by the branch**. Funds are collected from members and redistributed
  by the iemoto. Critics note members have little influence; many schools have recently moved
  finance and some artistic administration into corporate entities. The article also notes the
  system's undemocratic character and its succession/inheritance-tax problems.
  **[V — ja.wikipedia 家元]**
- Shamisen genres use these terms: 名取 / 家元 / 流派 appear in the Tsugaru article's 流派 section as
  licensing-and-school-system vocabulary **[V — ja.wikipedia 津軽三味線]**.

### 7.2 名取り natori — what it is, what it entails, what it costs

Nipponica's 名取 entry (服部幸雄) is the best source I found, and it is precise
*(my translation and paraphrase)* **[V — Kotobank 「名取」, Nipponica, 服部幸雄]**:

- **What it is:** in fields with an iemoto system — the "living arts" (flower, tea, incense), the
  various 邦楽 and 邦舞 — the iemoto **gives a disciple who has acquired the art to some degree
  several characters of the school's name**. (Digital Daijisen: "in an artistic discipline, having
  acquired a fixed level of skill, to be granted a **芸名 *geimei* (stage name)** by the iemoto or
  master; also the person so granted." **[V]** Nihon Kokugo Daijiten adds a dated attestation from
  a 1833–35 ninjōbon referring to "the natori of Kineya so-and-so." **[V]**)
- **Structure:** it commonly takes a **multi-layered form**, with the iemoto interposing several
  直属の取立て弟子 (directly-attached senior disciples) and thereby holding **a large number of
  natori disciples** at one remove.
- **What it entails:** becoming a natori **publicly declares that you are socially a member of the
  iemoto's organisation**. You gain **the guarantee of a status** and simultaneously **come under
  the constraints of the school's system**. A natori, **as the iemoto's alter ego, is permitted to
  take and teach students of their own.**
- **What it costs:** "In granting the name, **the iemoto normally receives a considerable sum of
  money (相当の金額)** and bestows a **免状 *menjō* (licence)** and a **名札 *nafuda* (name plaque)**."
  **No figure is given, and I could not verify any actual amount for any shamisen school. [U] on
  specific costs.** (The branch/headquarters 50/50 split of certificate fees is **[V —
  ja.wikipedia 家元]**, but that is a general statement, not shamisen-specific.)

### 7.3 Master–disciple transmission: imitation, and the absence of explanation

This is the part of the usual account I can support least directly, and I want to be honest about it.

**What I can verify:**

- The **oldest transmission mode used no scores at all** and relied on **chanting the melody to
  memorise it** **[V — Nipponica 「三味線」記譜と口三味線]**.
- Kuchi-jamisen's pedagogical function is explicitly **learning a piece from a teacher without an
  instrument**, and the reasons given are memory and technique-embedding — **not analysis or
  explanation** **[V — ja.wikipedia 唱歌(演奏法), citing Tokumaru]**.
- The shamisen melody is **規範 — normative — in the learning process**, with voice heightened as a
  deviation from it **[V — Nipponica 「三味線」]**. Learning is therefore "match the model, then
  deviate expressively," which is a description of transmission by imitation.
- Many genre/school notations exist **only as private memory aids**, each performer using an
  idiosyncratic system, in genres with small audiences **[V — Heibonsha 「三味線」]**. If the
  notation is private, the knowledge is not in the notation.
- The iemoto system's roots are linked to **esoteric Buddhist secret-transmission practice**
  **[V — ja.wikipedia 家元]**.

**What I cannot verify:** the specific claim that explanation is *deliberately* withheld, or that
teachers characteristically decline to explain. That is a widely repeated ethnographic
generalisation about Japanese arts pedagogy. **[U] — I found no source for it and will not assert
it.** Johnson 2010 and the Garland volume are the obvious places to check; I could not read either
(§0.1).

Counter-evidence worth recording, from a practising Japanese Tsugaru teacher (COMMERCIAL): his
blog account of a trial lesson is almost aggressively explanatory — he diagnoses *where* the
student is failing ("people always make mistakes in the same place"), notes that a bachi missing
its target is **usually the second string**, insists the **left-hand phrase must be automatic
before the right hand can get attention**, tells the student to **watch the bachi** (noting many
students watch their left hand instead, and that like touch-typing, almost nobody can do it without
looking at first), observes that students break down around the **third** repetition and, once the
errors are corrected verbally while playing, around the **seventh**, and prescribes **shorten the
phrase, then slow it down, then ten consecutive successes** as the definition of practice.
**[V — shamimaster.livedoor.biz/archives/52040423.html (2017-05-22), 小山貢山 / 獅子道 — COMMERCIAL]**
**This is one teacher, in the Tsugaru world (which the usual account itself identifies as the more
individualistic wing), so it does not refute the classical-iemoto generalisation — but it does mean
"Japanese shamisen teaching does not explain" is false as a blanket statement.**

### 7.4 How the Tsugaru world differs

- **Competitions and councils.** Japanese Wikipedia's Tsugaru article references national
  competitions (with 要出典 tags on that section) and lists multiple NPO/foundation bodies:
  **21世紀津軽三味線ネットワークジャパン**, **金木げんき倶楽部**, the **公益財団法人 日本民謡協会**,
  the **津軽三味線全国協議会**, and **NPO 日本伝統芸能振興会** **[V — ja.wikipedia 津軽三味線
  references and external links]**. A competition-and-association ecology is structurally different
  from licence-issuing hereditary houses.
- **But 流派 and 名取 exist in Tsugaru too** — the article's 流派 section uses exactly that
  vocabulary, and distinguishes schools by ensemble phrasing, bachi style and transmission method
  **[V — same]**. **So the "Tsugaru has no school system" framing is wrong.** What differs is that
  it coexists with competitions and with commercial, non-hereditary schools.
- **Workshops.** Bachido advertises a workshop/retreat culture implicitly (its archived 2013 site
  led with a "Free Online Workshop" **[V — web.archive.org snapshot 20130105 of bachido.com/learn]**);
  the Shinjuku school advertises **一回だけの飛び込み稽古** — single drop-in lessons with no
  commitment **[V — shamimaster.com — COMMERCIAL]**. Neither is conceivable inside a classical
  natori track.

### 7.5 The practical modern reality for a learner, especially a non-Japanese one

**Bachido (COMMERCIAL — this is a shop as well as a school; weigh accordingly).**
Founded **2011 by Kyle Abbott**; "the online 'home' for shamisen players around the world";
official Japan distributor **Ezo'n music Co., Ltd.**, CEO **Masahiro Nitta**. Site sections:
**School**, **Courses**, **Community** (Forums, Discord, Facebook group), **Resources**
(Shamipedia, Blogscast, News), and a large **Store** (instruments incl. minyo/nagauta/Tsugaru,
DIY kits, parts, bachi, koma, ito, dōkake, tuning devices, scorebooks, second-hand).
**[V — bachido.com homepage and /shamipedia/]**

Concrete, verifiable facts about the teaching offer **[V — bachido.com/school/ and /courses-page/]**:

- **Instructors:** Kyle Abbott, Kevin ("Keven") Kmetz, Mike Penny, **Ten Ten** (Aki Takahashi,
  "Certified Bachido Instructor"), Reigen Fujii, **Masahiro Nitta**.
- **Catalogue shape:** **Songs 37, Techniques 14, Scales 9**; **Weekly Lessons 44, Guided Courses
  16**; levels Beginner / Intermediate / Advanced.
- **Prices seen:** free (e.g. "Body Mechanics of Tsugaru Shamisen", 11 lectures) up to **$29.95**
  (e.g. "The Nitta Ryu Intensive Technique Pack", 23 lectures; "Spain" by Reigen Fujii, 15
  lectures); typical song courses **$4.99–$19.95**. A **one-year no-questions-asked refund** is
  advertised.
- **Extras:** an audio library of **Tsugaru repertoire**, and **"The Minyo Collection" — Ten Ten
  has recorded more than two hundred minyō songs** as a learning/preservation archive.
- **Technique-specific free/public material** exists on the site (hajiki tone consistency; a
  sukui drill series humorously titled "Lizard Dance Attack"; Reigen Fujii's "Proper Form"; the
  posture series).

**Kyle Abbott's book *Shamisen of Japan*** — the usual account names it. **I could not verify it.** A site
search for "shamisen-of-japan" on bachido.com returned only DIY-kit products, no book
**[V — bachido.com/?s=shamisen-of-japan]**. The store has a "Scorebooks and Media" category
**[V]** but I did not confirm the book is in it. **[U] on the book's current availability, edition,
and content.**

**Teachers outside Japan / online lessons.** Bachido's Discord, forums and Facebook group are the
documented community infrastructure **[V]**. One Tokyo school advertises in English ("We accept the
English mail, and pay by paypal. We can send the score abroad"; "Shamisen, Koto, Sanshin class in
Tokyo, Shinjuku without booking") and has taught visiting foreign students ("Shamisen Students from
Edinburgh" appears among its recent posts) **[V — shamimaster.com and shamimaster.livedoor.biz —
COMMERCIAL]**. **A survey of non-Japan-based teachers is [U] — out of reach without a search
engine.**

**Is self-teaching realistic? Two commercial sources, both self-interested, agree on a nuance.**

- The Japanese school states plainly: **「三味線の独学は可能です。ただ最初やスポット的には習った方が
  いいと思います。」** — "**Self-study of the shamisen is possible. But I think it is better to be
  taught at the start, and spot-wise [intermittently] thereafter.**" It also invites technical
  questions to the school and runs single drop-in lessons.
  **[V — shamimaster.com/gakufu.html — COMMERCIAL, and obviously a lesson-seller]**
- Bachido's own framing is that posture matters for "unlocking your full potential" but is "not a
  requirement for having fun with shamisen" **[V — COMMERCIAL]**.

**The specific things that are hard to self-teach.** The usual account names three; here is what the
evidence actually supports:

1. **Bachi angle / the bachi reliably hitting its target.** **Strongly supported.** A Japanese
   teacher devotes a whole article to it, identifies the **2nd string** as the usual miss, and
   diagnoses the root cause as **the left hand not yet being automatic** plus **watching the wrong
   hand** **[V — shamimaster.livedoor.biz, COMMERCIAL]**. Note that the diagnosis itself is the
   hard-to-self-teach part: a self-learner who misses the string will not know that the fault is in
   the other hand.
2. **Left-hand intonation.** **Strongly supported and mechanistically explained.** The neck is
   fretless, the correct positions are nonetheless fixed, the shifts must eventually be done
   **without looking**, and critically, **the kandokoro on strings 2 and 3 that are overtones of
   string 1 must be stopped especially accurately or the sawari will not ring — and sawari response
   is an explicit criterion of good performance, above all in niagari**
   **[V — Nipponica 「三味線」奏法]**. This is a textbook case of a skill with a *delayed, timbral*
   error signal rather than an obvious one: a self-learner can be flat by a few cents, hear nothing
   obviously wrong note-by-note, and simply never get the instrument to bloom.
3. **Sawari adjustment.** **Partly supported.** That sawari is an adjustable physical setup (carved
   hill-and-valley in the 乳袋, or the screw-driven **吾妻ざわり**) and that its effect is
   performance-critical are both verified **[V — Heibonsha 「さわり」; Nipponica]**. **That adjusting
   it is specifically hard to learn alone is [U] — I found no source saying so**, though it follows
   from the fact that the target is a timbre you have to have heard correctly to aim for. Note also
   that setup extends to parts choice, where Japanese convention is explicitly teacher-mediated:
   student-grade **ox-bone (shari) koma** are standard for practice; **plastic koma are recommended
   only at student level**; **ivory koma are normally used by the teacher or the 立三味線
   *tate-jamisen* (lead player) so the others can follow the tone**; and **many nagauta teachers
   disapprove of plastic bachi** **[V — en.wikipedia "Shamisen" — uncited section, so [U] on the
   details]**.

**An honest statement of the difficulty curve** (synthesis; **[U]** as a sourced claim): the early
weeks are unusually forgiving, because open strings plus a few kandokoro in one tuning will play
folk melodies, and bunkafu is legible in an afternoon. The curve turns steep where the error signal
stops being obvious: bachi-oto control, sawari-tuned intonation, the elasticity of ma, and the
genre-specific attack vocabulary. All four are things a teacher hears instantly and a recording of
yourself teaches you slowly.

---

## 8. Repertoire structure and general performance practice

(Not the Tsugaru repertoire — see the `tsugaru-shamisen` skill, which maps the three tunings
onto named Tsugaru pieces.)

### 8.1 前弾き maebiki — the instrumental introduction

- **Definition:** in 邦楽 vocal music accompanied by string instruments, **the instruments-only
  section played before the singing begins** — a prelude. **[V — Kotobank 「前弾き」, Digital Daijisen]**
- **Genre names and variants** **[V — Kotobank 「前弾き」, Britannica Japan]**: in **新内節** there
  are **several named maebiki used according to the mood of the piece**; in **箏曲** a fairly long
  maebiki is also called **序 *jo***; **義太夫節** and **薩摩琵琶** call it **弾き出し *hikidashi***;
  **筑前琵琶** calls it **開き *hiraki***; and gidayū and kouta have **オクリ *okuri***, which takes
  up the postlude of the previous scene/piece and becomes the prelude to the next.
- **Shinnai specifics:** the maebiki is **not composed afresh for each piece** — several existing
  pieces with different moods are kept, and an appropriate one is chosen; used for 端物 but hardly
  at all for 段物. **[V — Kotobank 「前弾き」, Heibonsha 世界大百科事典（旧版）新内節 excerpt]**
- In **Tsugaru**, maebiki is named as the instrumental prelude **which over time became an
  independent solo** **[V — ja.wikipedia 津軽三味線]**.

### 8.2 The shamisen–voice relationship: heterophony, properly sourced

Three verified pillars:

1. **The shamisen leads, and often outranks the singer in controlling the piece.** Nipponica: the
   歌物/語物 (song-genres / narrative-genres) division makes the shamisen look like a mere
   accompanying instrument, **"but as regards the progress of the piece, in many cases the shamisen
   player, rather than the singer or narrator, holds the initiative."**
   **[V — Nipponica 「三味線」三味線音楽; my translation]**
2. **The voice is defined as deviation from the shamisen line.** Same source: even for solo
   self-accompanied singing, the shamisen melody is first normative in learning, and **"the song or
   narration is technically and aesthetically heightened as a deviation (ずれ) from the shamisen
   melody."** **[V — same]** *This is the single best one-sentence statement of shamisen
   heterophony I found in any source, and it is a Japanese reference work saying it.* The two lines
   are the same melody and are deliberately not the same melody; the gap is the art. Calling it
   "the shamisen doubles the voice loosely" inverts the relationship — the voice departs from the
   shamisen, not the other way round.
3. **The texture is explicitly named heterophonic in the instrumental genres too.** Nipponica on
   jiuta tegoto: in tegoto, **掛合い *kakeai* between shamisen and shakuhachi or koto and
   "ヘテロフォニー的音構成" — heterophony-like tonal construction — were progressively stylised**,
   developing tegoto into an instrumental ensemble section independent of the vocal music.
   **[V — Nipponica 「三味線」三味線音楽]**

Supporting detail on layered lines: **替手 *kaete*** is a decorative melody written to go against
the basic **本手 *honte***; within one instrument, honte+kaete in the same tuning is specifically
called kaete, while **a different tuning usually makes it 上調子** instead
**[V — 文化デジタルライブラリー 用語事典 か行 「替手」; Kotobank 「上調子」 quoting Heibonsha
世界大百科事典（旧版）「替手」]**. The Bunka Digital Library illustrates both with nagauta *Shakkyō*
(uwajōshi part) and invites listeners to notice **how the timbres and melodic lines of koto and
shamisen cross and overlap** **[V — 文化デジタルライブラリー 「楽器の表現」]**.

### 8.3 合の手 ainote, 合方 aikata, 手事 tegoto — the interlude hierarchy

The three are **the same thing at three lengths**, and Japanese sources are consistent on this.

- **合の手 ainote** (also written 間の手 / 相の手, or just **合**): the **short shamisen melody that
  bridges one passage of singing to the next**. Functions: **help the singer breathe**; **express
  the meaning or mood of the text instrumentally**; and **in dance accompaniment, drive the
  dancer's movement**. Nipponica adds it also **guides the rhythm and tempo of the song**. Earliest
  attestation 1609–17. The biwa-music equivalent is **弾法 *danpō***. In gidayū, alongside short
  connective melodies there is **メリヤス *meriyasu***, played as background to long speeches or
  fitted to puppet action such as fight scenes.
  **[V — Kotobank 「合の手」: Digital Daijisen, Seisenban Nihon Kokugo Daijiten, Heibonsha (加納マリ),
  Nipponica (松井俊諭), Britannica Japan; and 文化デジタルライブラリー 用語事典 あ行]**
- **合方 aikata:** an ainote that has **grown long and become formalised**, built on a definite
  theme — **mostly in nagauta**. It gives the singer rest, emphasises the text's content, and is
  built as **a showpiece for the shamisen**. **Many have proper names:** 「晒しの合方」 (*Sarashime*,
  *Echigo-jishi*), 「鍛冶拍子の合方」 (*Kumo no Hyōshimai*, *Kokaji*), **「佃の合方」** (*Azuma
  Hakkei*), **「楽の合方」** (*Tsurukame*), 「雪の合方」 (cold/snow), 「砧の合方」, 「狂いの合方」,
  「虫の合方」. Nipponica notes they are composed **to express purely instrumentally the content of
  the text immediately preceding**. In kabuki 下座/黒御簾 music, "aikata" means the shamisen music
  played to an actor's entrance/exit or acting **without singing**.
  **[V — Kotobank 「合方」: Digital Daijisen, Heibonsha (蒲生郷昭), Nipponica (松井俊諭), Britannica
  Japan; Nipponica 「三味線」 names 砧/佃/楽 and says such aikata quote evocative figures from other
  genres or imitate natural sounds]**
- **手事 tegoto:** the long instrumental interlude in **地歌 jiuta and 箏曲 sōkyoku**, inserted to
  show off melodic beauty and technical interest. Structurally: early tegoto have a **段 *dan*
  structure** (初段, 2段…) which, if the dan are of equal length, permits the **段合せ** device of
  playing them simultaneously; an introduction (**序 / マクラ**) and/or a closing section
  (**チラシ**) may be attached. As koto variation against the jiuta sangen part grew, the
  **掛合 *kakeai*** technique of alternating shamisen and koto developed; the section containing the
  kakeai is the **本手事**, a following passage that approaches closure but reopens with kakeai is
  the **中チラシ**, and the true ending is the **本チラシ / 後チラシ**. Pieces weighted toward tegoto
  are **手事物 *tegotomono***, especially in Kyoto composition after the **化政期 (1804–30)** —
  hence **京流手事物 / 京風手事物**. Where a piece has more than one tegoto, the structurally
  less-defined one may just be called 合の手; and in the **山田流**, even tegoto-like passages are
  called 合の手 as a matter of principle.
  **[V — Kotobank 「手事」: Digital Daijisen, Seisenban Nihon Kokugo Daijiten, Heibonsha (平野健次);
  and 文化デジタルライブラリー 「楽器の表現」, which illustrates 手事物 with 「四季の眺」 (koto and
  shamisen sharing or alternating one melody) and 「嵯峨の秋」 (two koto in chase, or layering two
  different melodies)]**

### 8.4 間 ma, and why the rhythmic feel resists Western notation

- **The dictionary sense relevant here** is Daijisen's sense 6: in 邦楽, dance and theatre, **the
  temporal interval between beat and beat, action and action, line and line — and by extension,
  rhythm and tempo** (「間をとる」, 「間を外す」) **[V — Kotobank 「間」, Digital Daijisen]**.
- **The Japan Arts Council's pedagogical definition is stronger:** ma is **無音 — a silent span that
  is nonetheless treated as part of the music**. Music continues through these silent intervals;
  ma is understood as part of the performance itself, a structural element rather than empty space.
  **[V — 文化デジタルライブラリー 「間」]**
- **How it is coordinated:** the same page says that **shouts (掛け声), breaths, and the visible
  moment a player readies the instrument all serve as cues for coordinating timing**, and invites
  listeners to watch performers **share ma to align beat, rhythm and groove, sometimes
  instantaneously** **[V — same]**. The site treats **ノリ *nori*** (groove/momentum) as a third
  category alongside metrical and free rhythm **[V — 文化デジタルライブラリー 「拍とリズム」 index]**.
- **Why Western notation struggles** — four verified facts, from which the conclusion follows:
  1. **Whole genres and whole sections are in free rhythm (自由リズム), with no regular beat** —
     e.g. *Esashi Oiwake* in the **追分様式**, which stretches vowels and uses こぶし and ゆり
     ornaments over a wide range; also *Nanbu Ushioi Uta*, the shōmyō 「如来唄」, and the shakuhachi
     **「鹿の遠音」**, a two-player 連管 in which two melodies intertwine without a steady pulse.
     **[V — 文化デジタルライブラリー 「拍節的なリズム・自由リズム」]**
  2. **A single genre can contain both metrical and free rhythm, and a piece can change style
     midway.** **[V — same]**
  3. **Even metrical pieces routinely stretch or compress the beat** — the Kiyomoto *Michitose*
     example, where the shamisen widens the beat at vocal highlights and then returns to tempo.
     **[V — same]**
  4. **Kuchi-jamisen, the oldest and still-central mnemonic, encodes rhythm and gesture but not
     pitch** **[V — Nipponica]** — i.e. the native system optimises for exactly the dimension staff
     notation renders as rigid grid.

  The conclusion — that bar lines and note values misrepresent an elastic, cue-coordinated,
  partly-silent temporal practice — **is my synthesis of these four [V] facts; [U] as a sourced
  claim.**

### 8.5 How ensembles coordinate without a conductor

Four verified mechanisms:

1. **A designated lead player.** The **立三味線 *tate-jamisen*** is the lead shamisen, and the
   convention that the leader uses an **ivory koma** exists specifically **so other players can
   follow the leader's tone** **[V — en.wikipedia "Shamisen" — uncited, so [U] on the detail]**.
   In jōruri the shamisen player permanently paired with a given 太夫 is the
   **相三味線 *ai-jamisen*** or 相方 **[V — Kotobank 「合方」, Heibonsha (蒲生郷昭)]**.
2. **Audible and visible cues shared in the ma:** kakegoe shouts, breaths, the visible preparation
   of the instrument **[V — 文化デジタルライブラリー 「間」]**. Note that one named technique,
   **ケシ**, *is* a stroke executed together with a kakegoe **[V — Nipponica]** — the cue is built
   into the playing vocabulary. And **ainote is described as using kakegoe freely to drive the piece
   forward** **[V — Nipponica 「三味線」]**.
3. **An instrument that keeps the beat, where the genre provides one:** in the saibara 「伊勢の海」,
   the central performer of the back row sets the beat with the **笏拍子** clappers
   **[V — 文化デジタルライブラリー 「拍節的なリズム・自由リズム」]**.
4. **Yielding: the accompanist follows the voice.** The Kiyomoto case above; and in Tsugaru,
   **唄づけ *utazuke*** — improvised accompaniment that responds to the singer — is a named skill
   **[V — ja.wikipedia 津軽三味線]**. The "conductor" is, functionally, the singer's breath.

---

## 9. Practical glossary

Kanji / romanisation / one-line gloss. **[V]** = sourced above; **[U]** = unverified gloss.
Sources are the ones cited in the matching section.

### Instrument and setup (as they bear on technique)

| Term | Rōmaji | Gloss |
|---|---|---|
| 三味線 | shamisen | Three-stringed Japanese plucked lute, played with a large plectrum **[V]** |
| 棹 | sao | Neck; **fretless**, often in 3 detachable sections (三折) whose joints serve as fingering landmarks **[V]** |
| 胴 | dō | The square, skin-covered body, rested on the right thigh **[V]** |
| 撥 | bachi | Large hand-held ginkgo-leaf plectrum; distinguished from a finger-worn 爪 **[V]** |
| 撥皮 | bachikawa | Half-circle patch of skin over the striking area, where the bachi lands **[V]** |
| 撥音 | bachi-oto | The percussive sound of the bachi hitting the bachikawa; prized, and genre-variably cultivated **[V]** |
| 駒 / 下駒 | koma / shimogoma | Movable bridge between skin and strings **[V]** |
| 上駒 | kamigoma | Upper nut; **shortened so the 1st string bypasses it** (the sawari mechanism) **[V]** |
| さわり / サハリ | sawari | The buzzing sympathetic resonance of the open 1st string against the neck, and the device producing it **[V]** |
| 吾妻ざわり | azuma-zawari | Screw-adjustable sawari, standard in tokiwazu and kiyomoto **[V]** |
| 乳袋 | chibukuro | Upper neck area carved with the sawari "hill and valley" **[V]** |
| 一の糸 / 二の糸 / 三の糸 | ichi/ni/san no ito | 1st (thickest, lowest), 2nd, 3rd strings **[V]** |
| 胴掛け | dōkake | Cloth/leather cover on the dō where the right arm rests **[V]** |
| 指掛け | yubikake | Cloth band on the left hand to let it slide along the neck **[V — weak source]** |
| 枷 | kase | Small clamp tied to the neck to shorten the vibrating length for an uwajōshi part **[V]** |
| 勘減り | kanberi | Wear on the neck from repeated fingering **[V]** |
| 細棹 / 中棹 / 太棹 | hosozao / chūzao / futozao | Thin / medium / thick neck classes, mapping loosely onto genre **[V]** |

### Posture and hands

| Term | Rōmaji | Gloss |
|---|---|---|
| 正座 | seiza | Formal kneeling sit; the basic shamisen posture **[V]** |
| 爪弾き | tsumabiki | Playing with the fingernail instead of the bachi; the rule in kouta **[V]** |
| 勘所 | kandokoro | Stopping position on the fretless neck; = つぼ / 壺 / カンツボ; the Western "position" **[V]** |
| つぼ / 壺 | tsubo | Synonym of kandokoro **[V]** |

### Techniques

| Term | Rōmaji | Gloss |
|---|---|---|
| スクイ(撥) | sukui(-bachi) | Upstroke — scooping the string upward with the bachi; quieter, different timbre; usually in down-up patterns **[V]** |
| ハジキ | hajiki | Left-hand pluck / pull-off: hook, press toward the neck, release off the finger **[V]** |
| ウチ | uchi | Hammer-on: left-hand finger strikes the string onto the neck; marks the beat quietly **[V]** |
| スリ | suri | Slide along the string for a portamento effect **[V]** |
| コキ | koki | Grouped with suri as a rubbing/sliding ornament **[U — weak source]** |
| ケシ | keshi | Muting stroke: strike with a kakegoe and kill the resonance **[V]** |
| ウラハジキ | ura-hajiki | "Back-hand" plucking; no definition found **[U]** |
| カケバチ | kake-bachi | Left-hand pizzicato while the bachi mutes the string **[U — weak source]** |
| コカシバチ | kokashi-bachi | Listed as a shamisen technique with no definition **[U]** |
| 重音 | jūon | Double stop; "limited in practice" **[U — weak source]** |
| すり上げ / すり下げ | suriage / surisage | Upward / downward glissando — **term not verified; only generic スリ is** **[U]** |
| 押し撥 | oshibachi | **Not found in any source read; no definition asserted** **[U]** |
| 叩き / 弾き | tataki / hiki | The percussive vs delicate Tsugaru attack lineages **[V]** |
| カマシ | kamashi | Called "the hallmark technique of Tsugaru" by a commercial school; definition unverified **[U]** |
| 掛け声 | kakegoe | Vocal call; a timing cue, and part of the ケシ stroke and of ainote practice **[V]** |

### Tuning

| Term | Rōmaji | Gloss |
|---|---|---|
| 調弦 / 調子 | chōgen / chōshi | Tuning; a named tuning **[V]** |
| 本調子 | honchōshi | P4 + P5 (= octave 1st→3rd); e.g. B–E–B; the base tuning; stately, jōruri's default **[V]** |
| 二上り | niagari | 2nd string up a tone: P5 + P4; e.g. B–F♯–B; flashy, cheerful, rustic **[V]** |
| 三下り | sansagari | 3rd string down a tone: P4 + P4 (minor 7th 1st→3rd); e.g. B–E–A; chic/alluring/light, or feminine/sorrowful depending on source **[V]** |
| 一下り / 一上り / 六下り / 二上り三メリ | ichisagari etc. | Derived tunings; only ichisagari and ichiagari have definitions in sources read **[V/U]** |
| 低二上り / 三上り / 高本調子 / 高二上り / 高三下り | hikui-niagari etc. | Further derived tunings in Britannica Japan's chain **[V]** |
| 二上げ / 三下げ | nianage / sansage | Okinawan sanshin names for niagari / sansagari **[V]** |
| 上調子 | uwajōshi | A second, higher-tuned shamisen (P4 or P5 above the honte) using a kase; plays the melody an octave up; also a player rank **[V]** |
| 高音 | takane | Shinnai-bushi's name for the uwajōshi part **[V]** |
| 本手 / 替手 | honte / kaete | Basic melody / decorative counter-melody **[V]** |
| 本 / 尺・寸 | hon / shaku-sun | Conventions for naming the chosen absolute pitch level (1本 = 1st string on A; 4本 ≈ C; 2尺 ≈ C) **[V]** |

### Scale theory

| Term | Rōmaji | Gloss |
|---|---|---|
| テトラコルド | tetorakorudo | Koizumi's tetrachord: a perfect-4th frame with one variably-placed middle tone **[V]** |
| 核音 | kakuon | "Nuclear tone": a non-floating tone that governs its neighbours and can be the final; not the Western tonic **[V]** |
| 民謡音階 | min'yō onkai | C E♭ F G B♭ — tetrachord 3+2; folk-song scale **[V]** |
| 律音階 | ritsu onkai | C D F G A — tetrachord 2+3; the pre-Edo mainstream **[V]** |
| 都節音階 | miyako-bushi onkai | C D♭ F G A♭ — tetrachord 1+4; the Edo urban art-music scale **[V]** |
| 琉球音階 | Ryūkyū onkai | C E F G B — tetrachord 4+1; Okinawan **[V]** |
| 陰旋法 / 陰音階 | in-senpō / in-onkai | "Scale with semitones" ≈ miyako-bushi — **a Meiji-era concept now held to be erroneous** **[V]** |
| 陽旋法 / 陽音階 | yō-senpō / yō-onkai | "Scale without semitones," = 田舎節 — **erroneous: conflates min'yō and ritsu** **[V]** |
| 田舎節 | inaka-bushi | Older name for the yō grouping **[V]** |
| 呂音階 / 呂陰音階 | ryo / ryo-in onkai | Pentatonic scales that do *not* fit the tetrachord frame **[V]** |

### Notation

| Term | Rōmaji | Gloss |
|---|---|---|
| 勘所譜 | kandokoro-fu | Generic Japanese term for position-based tablature **[V]** |
| 朱 | shu | Gidayū-bushi's name for its kandokoro notation, written in red beside the text **[V]** |
| 文化譜 (赤譜) | bunkafu (akafu) | Dominant modern horizontal tablature: 3 lines = 3 strings, 0 = open, semitone steps 0–10 per octave; Taishō era, 杵家彌七 (4th gen.); publisher 邦楽社 **[V]** |
| 研精会譜 / 小十郎譜 | kenseikai-fu / Kojūrō-fu | Vertical **solfège number** notation (1–7 = do–ti, dotted octaves); 吉住小十郎 **[V]** |
| 家庭式三味線譜 | katei-shiki shamisen-fu | The standard jiuta system; Taishō era, 大日本家庭音楽会, Fukuoka; symbol system undocumented here **[V/U]** |
| 青柳譜 | Aoyagi-fu | Kenseikai-fu plus three vertical string-lines; Shōwa, 杵屋彌之介 **[V]** |
| 栄二譜 | Eiji-fu | Twelve kana for degrees, string shown by script type; archival, unpublished; 杵屋栄二 **[V]** |
| 佐吉譜 / 杵勝譜 | Sakichi-fu / Kinekatsu-fu | Named nagauta notations, undescribed **[U]** |
| 大薩摩略譜 / 三味線速記譜 | Ōzatsuma ryakufu / shamisen sokkifu | Further systems, by 根岸の勘五郎 and 田中正平 **[V]** |
| 口三味線 | kuchi-jamisen | Mnemonic syllable chanting of a shamisen part; encodes string, open/stopped, bachi use and left-hand technique, and rhythm — **but not pitch** **[V]** |
| 唱歌 | shōga | The general mnemonic-chanting practice, from gagaku, of which kuchi-jamisen is the shamisen form **[V]** |
| 糸の声 | ito no koe | Early name for kuchi-jamisen, recorded 1685 and 1757 **[V]** |
| 工工四 | kunkunshi | The Okinawan sanshin notation system (distinct from all of the above) **[V]** |

### Form and performance practice

| Term | Rōmaji | Gloss |
|---|---|---|
| 前弾き | maebiki | Instrumental prelude before the voice enters **[V]** |
| 弾き出し / 開き / オクリ / 序 | hikidashi / hiraki / okuri / jo | Genre-specific names for the prelude function **[V]** |
| 合の手 (合) | ainote (ai) | Short instrumental bridge between vocal passages; helps the singer breathe, guides tempo, paints the text **[V]** |
| 合方 | aikata | A long, themed, named ainote — mostly nagauta; also kabuki offstage shamisen without singing **[V]** |
| 手事 | tegoto | The long jiuta/sōkyoku instrumental interlude; 手事物 = pieces built around it **[V]** |
| 掛合 / 掛合い | kakeai | Alternation between instruments (or chanters) within a texture **[V]** |
| 段 / 段合せ / チラシ / マクラ | dan / dan-awase / chirashi / makura | Structural subdivisions of tegoto **[V]** |
| メリヤス | meriyasu | Gidayū background/action music under long speeches or puppet movement **[V]** |
| 黒御簾 / 下座音楽 | kuromisu / geza ongaku | Kabuki offstage music **[V]** |
| 歌物 / 語物 | utaimono / katarimono | Song genres vs narrative genres **[V]** |
| 間 | ma | The structurally meaningful silent interval; by extension rhythm and timing feel **[V]** |
| ノリ | nori | Groove, momentum — treated as a category beside metrical and free rhythm **[V]** |
| 拍節的なリズム / 自由リズム | hakusetsu-teki rizumu / jiyū rizumu | Metrical rhythm / free rhythm **[V]** |
| 立三味線 | tate-jamisen | Lead shamisen player in an ensemble **[V]** |
| 相三味線 / 相方 | ai-jamisen / aikata | The shamisen player permanently paired with a given jōruri chanter **[V]** |
| 唄づけ | utazuke | Improvised accompaniment responsive to the singer; a declining Tsugaru skill **[V]** |

### Pedagogy and institutions

| Term | Rōmaji | Gloss |
|---|---|---|
| 家元 | iemoto | Head of a hereditary school, and the system around it **[V]** |
| 流派 | ryūha | School / lineage **[V]** |
| 名取 / 名取り | natori | Rank at which the iemoto grants characters of the school name as a stage name, for a considerable fee, with a 免状 licence and 名札 plaque; permits taking students **[V]** |
| 芸名 | geimei | Stage name **[V]** |
| 師範 | shihan | Instructor rank between iemoto and ordinary students **[V]** |
| 免状 / 名札 | menjō / nafuda | Licence / name plaque issued with natori **[V]** |
| 取立て弟子 | toritate-deshi | Senior disciple interposed between iemoto and the mass of natori **[V]** |
| 稽古 | keiko | Lesson / practice session **[V — used in the Japanese sources read]** |
| 口伝 | kuden | Oral transmission; the primary mode in Tsugaru **[V]** |
| 曲弾き | kyokubiki | Virtuoso solo display playing (Tsugaru) **[V — named in commercial source]** |

---

## 10. Known gaps, flagged for a second pass

1. **Johnson 2010, Malm 2000, Garland vol. 7, Koizumi 1958 — none read.** Brill, Taylor & Francis
   and the Scholarly Publishing Collective all returned 403. These are the four sources most likely
   to settle the items below. **Attribute nothing to them on the strength of this document.**
2. **押し撥 oshibachi, すり上げ/すり下げ suriage/surisage, shamisen tremolo** — not verified anywhere.
3. **家庭式三味線譜** — attested as the jiuta standard with a publisher and era, but **I found no
   description of how it actually looks or works.** This is the biggest notation gap.
4. **The "deliberate absence of explanation" in iemoto pedagogy** — widely repeated, unverified
   here, and partially contradicted by a practising Japanese teacher's own account (§7.3).
5. **Actual natori costs** for any shamisen school — no figures found.
6. **Tsugaru pieces mapped to scales** — not verified for any individual piece.
7. **Standing posture and strap arrangements** — nothing found.
8. **Kyle Abbott's *Shamisen of Japan*** — not located on Bachido's current site.
9. **Conjunct tetrachord joining and the formal role of 核音 in Koizumi's own system** — the Japan
   Arts Council page shows only the disjunct case; the rest needs Koizumi or a musicology source.
10. **Date of kenseikai-fu** — Meiji (Nipponica) vs Taishō (Japanese Wikipedia).
11. **杵家 vs 杵屋 Yashichi** — resolved in favour of 杵家 on NDL catalogue evidence, but the spouse
    **赤星國清** rests on Japanese Wikipedia alone.
12. **No search engine was available**, so there may be open-access academic work on shamisen
    notation and pedagogy (J-Stage, CiNii, SOAS/ethnomusicology theses) that this sweep missed.
    Semantic Scholar's API rate-limited me out.
