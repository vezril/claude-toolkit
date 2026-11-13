# The Shakuhachi: Technique, Notation and Pedagogy

Research notes, scope 4 of a multi-agent reference project. The instrument as an object, the
pre-modern history and the schools' own histories, and the Dokyoku/Yokoyama lineage's internal
affairs are held by other researchers. This file owns **how the instrument is played, written down
and taught**.

**All web fetches 2026-11-13 unless a different date is stated.** Every substantive claim is marked
**[V]** (verified — the artefact I actually read is named) or **[U]** (unverified, with a note on
what is missing). Japanese translations and paraphrases are **mine** and are flagged as such; they
are paraphrase, not quotation, unless the Japanese is given alongside.

---

## 0. Source audit — read this before trusting anything below

### 0.1 What I read in full

**Japanese reference works, via Kotobank** (`kotobank.jp/word/尺八-75849`, fetched 2026-11-13 —
scraped the HTML directly rather than through a summarising fetcher, so I read the entries in
Japanese). Four of these matter:

| Source | Signed author | Why it matters |
|---|---|---|
| 小学館 日本大百科全書 (Nipponica), 「尺八」 | **月溪恒子 Tsukitani Tsuneko (1944–2010)** | Tsukitani was *the* academic specialist on classical honkyoku (author of 『尺八古典本曲の研究』). Her 普化尺八 §「形態と奏法」 gives the single most authoritative short taxonomy of shakuhachi technique in existence, and her §「記譜法」 is the best compact statement of the notation situation. **This is the backbone of sections 3, 5 and 6 below.** |
| 平凡社 改訂新版 世界大百科事典, 「尺八」 | **上参郷祐康 Kamisangō Yūkō** | Kamisangō is the historian whose essay is translated in Blasdel's English manual. His 「楽器と奏法」 section gives hand assignment, the meri/kari definition, the half/quarter-hole statement, the register mechanism, and the *shōga* teaching method. |
| ブリタニカ国際大百科事典 小項目事典, 「尺八」 | unsigned | Thin; corroborates lengths only. Its 「開孔音列」 line came through my scrape corrupted and I do not use it. |
| 山川出版社 山川日本史小辞典 改訂新版, 「尺八」 | unsigned | Short but gives the *supporting-finger* detail (both middle fingers hold the instrument) and the honkyoku-free-rhythm / gaikyoku-metrical opposition. |
| ヤマハミュージックメディア 音楽用語ダス, 「尺八」 | unsigned | Corroborates the register mechanism and the "about 2.5 octaves" range. |
| 平凡社 百科事典マイペディア | unsigned | Thin. |

**Japanese Wikipedia 「尺八」** — read the raw wikitext via the MediaWiki API
(`ja.wikipedia.org/w/api.php?action=parse&page=尺八&prop=wikitext`, 17,881 characters, fetched
2026-11-13). Its 「音域・音階などについて」 section carries **a complete 42-row chromatic
fingering table for both Kinko and Tozan from C4 to E7** and its 「奏法」 section carries the
meri/kari range figures. **Important caveat: that table and that section carry no inline
citations.** I reproduce the table because it is the only complete published chart I could obtain
in machine-readable form, and I say in §2.5 exactly what I did and did not independently verify
against it. The article's history/schools sections *are* referenced (Tsukitani's chapter in
『日本の伝統芸能講座』, Kubota Toshiko, Nakatsuka Chikuzen) but the technique sections are not.

**Gunnar Jinmei Linder, "Analysis of Transmission in Japanese Traditional Art Forms: Part 2,
A Comprehensive Study of Shakuhachi Lineages," *Journal of East Asian Identities* 2 (March 2017):
117–127** — open access at `jeai.edu.yamaguchi-u.ac.jp/Vol-02/no-10.pdf`, read in full. [V]
Linder is unusually well placed: PhD in Japanology (Stockholm), **MA in shakuhachi as a performing
art from Tokyo University of the Arts (Tokyo Geidai), and a Kinko-ryū *shihan* licence from
Yamaguchi Gorō (1933–99)** — so he is simultaneously inside the transmission and analysing it.
Used for §8 and for the lineage-typology in §6.4.

**Marty Regan, *Composing for Japanese Instruments* (written 2004, ePapyrus 2006)** — open PDF at
`sonicgallery.org/wp-content/uploads/2014/01/composingjapan.pdf`, read in full. [V] A composer's
orientation essay, not a technical treatise; useful only for the Geidai/foreign-student fact in §8
and for its own bibliography. **Label: self-published by a working composer, not peer-reviewed.**

**Amy D. Simon, "Shakuhachi Honkyoku: Motivic Analysis of Sōkaku Reibo," *Analytical Approaches to
World Music* 5/2 (2017)** — open access at `iftawm.org/journal/oldsite/articles/2017a/`. [V]
Downloaded and read; peer-reviewed. Used in §7 for the phrase-structure point.

**Gunnar Jinmei Linder, *Deconstructing Tradition in Japanese Music: A Study of Shakuhachi,
Historical Authenticity and Transmission of Tradition* (PhD diss., Stockholm University, 2012)** —
the DiVA full-text PDF (`diva-portal.org/smash/get/diva2:488776/FULLTEXT01.pdf`) **downloaded
incompletely over repeated attempts** (the file kept growing past 17 MB without completing and
`pdftotext` could not reconstruct its xref table). **I therefore did not read it, and nothing below
is attributed to it. [U]** Its existence and open-access status are [V] from Linder's own 2017
article, which cites it and gives the DiVA URL. **This is the biggest gap in this file** — it is the
one monograph-length academic treatment of shakuhachi transmission in English by someone holding a
shihan licence, and a future pass should get it.

### 0.2 What I could not read

- **Riley Lee, "Shakuhachi honkyoku notation: written sources in an oral tradition," *Musica
  Asiatica* 6 (1991): 18–35, DOI 10.1017/cbo9780511896071.003.** Metadata [V — Crossref API,
  `api.crossref.org/works?query.bibliographic=shakuhachi+notation+honkyoku`, 2026-11-13]. The
  Cambridge Core PDF URL returns the site's HTML shell, not the file. **Not read. This is the
  canonical treatment of the honkyoku-rhythm question that §6.7 addresses, and §6.7 is therefore
  built from Japanese reference works and school sources instead, not from Lee. [U]**
- **Riley Lee, "Fu Ho U vs. Do Re Mi: The Technology of Notation Systems and Implications of Change
  in the Shakuhachi Tradition of Japan," *Asian Music* 19/2 (1988), DOI 10.2307/833867.** Metadata
  [V — Crossref]. Not read; JSTOR 403. Its framing (notation as a *technology* with consequences
  for what can be transmitted) is the right frame for §6 and I note where I am reasoning in that
  direction without his text.
- **Riley Lee, *Yearning for the Bell: A Study of Transmission in the Shakuhachi Honkyoku
  Tradition* (PhD diss., University of Sydney, 1992).** Record exists at
  `ses.library.usyd.edu.au/handle/2123/1742` [V — the URL appears in Yahoo! Japan search results,
  2026-11-13]; both the handle page (403) and the bitstream PDF (an HTML "repository has moved"
  page) failed. **Not read. [U]**
- **Donald P. Berger, "The Shakuhachi and the Kinko Ryū Notation," *Asian Music* 1/2 (1969),
  DOI 10.2307/833910.** Metadata [V — Crossref]. Not read. This is the one English article devoted
  specifically to Kinko notation; §6.2 is not built on it.
- **Jeffrey Lependorf, "Contemporary Notation for the Shakuhachi: A Primer for Composers,"
  *Perspectives of New Music* 27/2 (1989), DOI 10.2307/833414.** Metadata [V — Crossref]. Not read.
  Independently recommended as the best source on notating shakuhachi for Western composers by
  Regan 2006 (p. ~428 of the extracted text) [V].
- **Christopher Yohmei Blasdel with Kamisangō Yūkō, *The Shakuhachi: A Manual for Learning*
  (Ongaku no Tomo Sha, 1988; Printed Matter Press, 2008).** Not read. Existence and the fact that
  Kamisangō's historical essay 「尺八楽略史—吹禅のために」 occupies pp. 69–132 (1988) / 69–125
  (2008) of it are [V — Linder 2017, bibliography]. **This is the standard English method book and
  its absence is why §1 (posture/embouchure) is the thinnest section here.**
- **Tsukitani Tsuneko, 『尺八古典本曲の研究』 (Shuppan Geijutsu-sha, 2000; 2006 printing cited by
  both Linder and Simon).** Not read. Existence and use [V — cited by Linder 2017 and Simon 2017].
  The authoritative Japanese monograph on classical honkyoku.
- **UNSW music-acoustics detail.** `newt.phys.unsw.edu.au/jw/shakuhachiresults.html` fetched
  2026-11-13 [V] but it is a short teaser page: it states the method and principles (below) and puts
  the actual impedance spectra in images and the numbers in linked papers I did not retrieve.
- **The Japan Arts Council 文化デジタルライブラリー** (`www2.ntj.jac.go.jp/dglib/`) — I did not
  obtain any shakuhachi-specific page from it in this pass. Its pages are JavaScript-rendered and I
  had no search-index snippet for a shakuhachi notation page. **Nothing here rests on it. [U]**

### 0.3 Commercial and hobbyist sources, labelled

- **`tozanryu.com`** — the official site of 公益財団法人 都山流尺八楽会 (Tozan-ryū Shakuhachi
  Gakkai, a Japanese public-interest incorporated foundation). This is a **school's own
  self-description**, which is exactly what §8.2 needs; it is authoritative about its own rank
  system and about nothing else. Fetched 2026-11-13.
- **`jonkara.com/wagaku_manual/instrument/shakuhachi/`** — documentation for a Japanese notation
  *app*. Commercial. Used only for the Kinko *mabyōshi* dot mechanism, and one of its claims is
  flagged as wrong in §6.2.
- **`kochyo.co.jp/onritsu/`** (ワダ楽器 蝴蝶宝, a wooden-shakuhachi maker) — reached, but its
  fingering tables are **images** and its text came through mis-encoded. **Produced nothing.**
- I have deliberately **not** used the large enthusiast reference sites (komuso.com / the
  International Shakuhachi Society, individual teachers' blogs) as the basis for any factual claim,
  because they are the main vector of the homogenised English account this file is supposed to
  correct. Where they are the only source for a term, I say so and mark it [U].

### 0.4 The register problem, named in the literature

Two publications say out loud that the English-language shakuhachi literature has a mystification
problem, and they are old:

- **Karl Signell, "The Mystique of the Shakuhachi," *Journal of the American Musical Instrument
  Society* (1981).** [U — I have the citation from a parallel strand's Crossref/bibliographic
  pass, not from the article; I did not read it and did not independently verify the volume/pages.]
- **Bruno Deschênes, "Le shakuhachi japonais, ou l'Occident qui s'orientalise?," *Horizons
  philosophiques* 16/1 (2005): 136–, DOI 10.7202/801311ar** — reported to be open access on Érudit.
  [U — citation from the same parallel strand pass; not read.]

Linder 2017 makes the historical version of the same point from primary documents and **I did read
that**: the Zen connection "was constructed during the Edo period, and it has been re-constructed
since the 1970s until today"; the repertoire does come from the komusō, "but there are no strong
pieces of evidence that they in general were devout Buddhist monks" — the 「慶長掟書」*Keichō
okite-gaki*, the document most often cited for the Fuke sect's privileges, is itself "a forgery of
a much later date," and its latest version tells the komusō to **look** like a monk while keeping
"the intention and resolution of a samurai," describing the sect as one "for martial practice"
(Linder 2017, pp. 121 and n. 11). [V]

This matters for technique writing, not just history writing: a great deal of what circulates in
English as *instruction* about breath and posture is this reconstructed register in imperative mood.
§1.4 separates the two.

---

## 1. Posture, embouchure and breath

This is the weakest-sourced section in the file. The Japanese encyclopedias describe hand placement
and the embouchure's *acoustic function* precisely and say essentially nothing about posture or
breath mechanics; the method books that do are the ones I could not read. I flag the gaps rather
than filling them.

### 1.1 Holding position and hand placement

The instrument is held **vertically**, in front of the body, and blown over its upper rim; it is an
end-blown vertical flute (縦笛 *tatebue*). [V — 平凡社世界大百科事典, 「竹製，ノンリードの縦笛」;
Britannica Japan, same]

Finger assignment, from the **bottom hole upward**: right ring finger (hole 1), right index finger
(hole 2), left ring finger (hole 3), left index finger (hole 4), left thumb (hole 5, the single
hole on the **back**). [V — 平凡社世界大百科事典 (Kamisangō): 「5孔の指遣いは下から順に右薬指，
右人差指，左薬指，左人差指，左親指」 — my translation] Kamisangō adds immediately that
「左右の手は上下逆でもよい」 — **the hands may be reversed**, left below and right above. [V]
The Yamaha 音楽用語ダス entry puts it as a default: 「通常は右手を下に構えるが、逆でも構わない」
("normally the right hand is held below, but the reverse is fine"). [V] So, unlike the Western
flute, **there is no fixed handedness.**

The **middle fingers of both hands do not cover holes; they support the instrument.** [V —
山川日本史小辞典: 「両手中指は楽器を支えるために使い，両手人差し指と薬指，左手親指で穴を開閉し
演奏する」 — my translation] This is a genuinely useful detail that the English accounts usually
skip: the five holes are worked by only *five* of the eight available fingers, and two of the
remaining three have a load-bearing job.

**Posture of the body (sitting *seiza* vs on a chair, spine, shoulders, head angle):** I found no
statement in any reference work I read. The encyclopedias are silent. **[U — no source found. Do
not fill this in from memory; this is exactly where the English literature invents.]**

### 1.2 Why the embouchure is formed against the *utaguchi*, not into a mouthpiece

The *utaguchi* 歌口 ("song mouth") is not a mouthpiece at all. It is made by **slicing the front of
the tube's upper end away at an angle, outward**, so that the rim of the bore presents a curved
**sharp angle (鋭角)** to the player. [V — 平凡社世界大百科事典: 「上端には材質の堅い節の部分を
当て，管の前面を斜めに切り落とし，そこに生ずる弧形の鋭角を歌口とする」] A hard inlay — water
buffalo horn, ivory, or ebonite — is normally set into that edge; **its primary job is to keep the
edge sharp and durable, and its shape differs from school to school.** [V — 平凡社世界大百科事典:
「歌口を鋭くかつ丈夫に保つために通常は水牛角などを細工して埋め込むが，その形が流派により異なる」;
ja.wikipedia 尺八 adds 水牛の角・象牙・エボナイト and that a claim that the inlay changes the tone
exists but is contested]

The player blows the breath **from the lips directly onto that sharp angle**. [V — 平凡社:
「唇からの呼気を歌口の鋭角に吹きつけて音を発し」; Nipponica (Tsukitani): 「その鋭い角に直接息を
吹き付けて音を発するのが特徴である」 — "blowing the breath directly onto that sharp angle is the
distinguishing feature"]

The consequence, and the reason the question in the usual account has a real answer: **because the edge is
part of the instrument and the air-jet-forming channel is part of the player, the player's face is
part of the acoustic system.** The UNSW music-acoustics group states this in those terms: the air
jet interacts with both the bore impedance and the **radiation** impedance, and "the radiation load
is baffled by the player's face"; consequently "large changes in the relative geometry of the
instrument and the face" are what give the instrument its pitch and timbre flexibility. The same
page notes two structural absences versus a Western flute: the shakuhachi has **no narrow chimney**
(the raised wall of a flute's embouchure hole) and **no short resonator upstream of the jet** (the
flute's closed head-joint stub beyond the embouchure). [V — `newt.phys.unsw.edu.au/jw/shakuhachiresults.html`,
fetched 2026-11-13; measurements made on the instrument alone, without a player, on a "Bei Shu"
instrument from Nagano, and the spectra are published as images that I did not read numerically]

Japanese Wikipedia makes the pedagogical version of the same contrast explicitly: a recorder
(「いわゆる縦笛」) has a **fipple/block** in its mouthpiece, so a beginner gets a sound immediately;
on the shakuhachi and the transverse flute, 「音を出すには熟練が必要である」 — producing a sound
requires acquired skill. [V — ja.wikipedia 尺八 §奏法, uncited section]

### 1.3 Why beginners cannot get a sound at all, and what changes

**What is verified:** the player must shape the air jet themselves. Japanese Wikipedia puts it as
「奏者が自らの口形（アンブシュア）によって吹き込む空気の束を調整しなければならない」 — the
player must regulate the *bundle of air* they blow in by means of their own embouchure — and names
the flute as the comparable case and the recorder as the contrasting one. [V, uncited section]

**What follows acoustically and is verified at the level of principle, not of the beginner's body:**
as an end-blown flute the instrument is **open at the point of excitation**, so it "operates at
minima of the acoustic impedance," and the radiation impedance — and hence the tuning of those
minima — **varies with playing position**. [V — UNSW page] In plain terms: where the player's face
sits relative to the edge is not a comfort choice, it retunes the resonance. A beginner who has not
stabilised that geometry is not merely blowing badly, they are also moving the instrument's tuning
around while they blow.

**What I could not verify:** any quantitative account of the beginner's actual problem — jet width,
jet velocity, aperture dimensions, the angle of attack, the proportion of the edge covered by the
lower lip, blowing pressure in kPa, or how long any of it takes to acquire. **[U — no measured
figures found in any source I could read. The UNSW group's shakuhachi work is a conference abstract
(Wolfe & Smith, *JASA* 108/5 Suppl. (2000): 2552, DOI 10.1121/1.4743469 — metadata only), and
Castellengo & Fabre's comparative chapter (DOI 10.4324/9781315077192-10) is behind Routledge.]**
If you need numbers here, those two are the targets.

The lower lip against the edge, the chin as the contact point, and the size of the aperture: the
only *verified* statement I have about the contact is indirect but precise, and it comes from the
meri/kari definition — the contact point (支点, fulcrum) is between the instrument and the
**lower jaw, slightly below the lower lip**. [V — ja.wikipedia 尺八 §奏法: 「楽器と下顎（下唇より
やや下）との接点を支点にして」, uncited section] The aperture's dimensions: **[U].**

### 1.4 Breath support and the *hara* claim — convention vs. documented physiology

**The honest state of the evidence.** I found, in the Japanese reference works, **no mention at all
of abdominal breathing, *hara* 腹, *tanden* 丹田, or breath support as a physiological matter.**
Nipponica's technique taxonomy (§5 below) does name three techniques that are explicitly
breath-and-throat techniques — **タマネ, ムラ息, コミ吹き** — and it classifies them as
「のどや息を使った特殊奏」, "special techniques using the throat and the breath." [V — Nipponica,
Tsukitani] That is the extent of what the encyclopedias say about breath. **They do not say that
shakuhachi playing uses abdominal breathing, and they do not say it does not.**

So the position to take is:

- **Pedagogical convention:** that shakuhachi is taught with abdominal/diaphragmatic breathing, and
  that teachers frame it in terms of *hara*, is widely reported in English-language instruction.
  **[U — I could not verify this against any source I read in this pass. It is plausible and I
  expect it is true, but I am not able to name an artefact for it, and the method books that would
  settle it (Blasdel 1988; the school method series) are exactly the ones I could not obtain.]**
- **Documented physiology:** **none found.** I located no respiratory-physiology study of
  shakuhachi players — no spirometry, no EMG, no pressure measurement, nothing. **[U]** The only
  instrument-side physical work I found is acoustic (impedance spectra, no player) rather than
  physiological.
- **The mystical register:** claims that the breath *is* the meditation (*suizen* 吹禅, "blowing
  Zen"), or that one note attains Buddhahood (*ichion jōbutsu* 一音成仏), are **real emic
  statements from inside living lineages** and should be reported as such — Linder documents both,
  attributing *dōkyoku*/*hotchiku* vocabulary to Watazumi and quoting Endō Kenji, a student in that
  line, on *ichion jōbutsu* [V — Linder 2017, pp. 122–123]. They are **not** physiological or
  technical claims and should never be relayed as instruction. Linder's own verdict on the frame is
  in §0.4.
- **One documented feedback loop worth knowing**, because it explains why the mystical register is
  *growing* rather than fading: Linder reports Okuda Atsuya telling him in July 2009 that the
  interest from the West after he began playing *hotchiku* and released a Zen-titled CD "had given
  impetus to his activities in Japan" — "by giving what is asked for, the receiver in a way endorses
  the transmitter." [V — Linder 2017, p. 125 and n. 28]

**One-breath phrasing as the actual structural fact about breath** is treated in §7.2, where it is
better sourced.

---

## 2. Note names, fingerings and pitches on a 1.8 shaku instrument

### 2.1 The instrument and the reference length

Standard length is **1 shaku 8 sun ≈ 54.5 cm**, measured on the 曲尺 *kanejaku* carpenter's
scale; the lowest note, with **all five holes closed**, is the 筒音 *tsutsune* ("tube note"), and on
the standard instrument that is **D4** (Japanese 十二律 name 壱越 *ichikotsu*). Lengths run roughly
1.3 shaku to 3 shaku in 1-sun steps, each sun raising or lowering the *tsutsune* by about a
semitone — so the family is a set of **transposing instruments**. [V — Nipponica (Tsukitani):
「管長の標準は曲尺の1尺8寸（約54.5センチメートル）。1尺3寸ぐらいから3尺くらいまで、1寸刻みで
長短各種あり、1寸の増減で基音（指孔を全閉した筒音）がほぼ半音上下する」; 平凡社世界大百科事典
gives 1尺2寸–約3尺 and 「約1寸の差で半音ずつ違う移調楽器」; ja.wikipedia 尺八 gives a
1.1–2.3 shaku table]

Note the hedge in Tsukitani's wording — 「ほぼ半音」, *roughly* a semitone — and Japanese
Wikipedia's harder version of the same caveat: because length and *tsutsune* do not correspond
exactly once bore geometry is involved, instruments are specified either 正寸 *seisun* ("correct in
length") or 正律 *seiritsu* ("correct in pitch"), and **a 正寸 1.8 shaku instrument is not
guaranteed to sound D**. 正律 is now the mainstream specification, and instruments are often just
called "D kan," "E kan," "A kan." [V — ja.wikipedia 尺八 §正寸と正律, uncited; **correction to that
article: its 正律 table lists 二尺二寸管 as "Bb4", which is wrong by an octave — the surrounding
rows run B3, A3, so it must be Bb3. Typo in the source.**]

**Five holes: four on the front, one on the back.** [V — 平凡社, Nipponica, Britannica Japan, Mypedia
— all four agree]

### 2.2 The 五音 *go-on* — ロ ツ レ チ リ / ロ ツ レ チ ハ

The "five notes" are the pitches obtainable **without half-holing and without meri/kari**, by
opening the holes in sequence from the bottom. Japanese sources call these the 幹音 *kan'on*
("trunk notes") or 基本音列 *kihon onretsu* ("basic pitch series").

On a **1.8 shaku** instrument in the lower register they are, verified three ways:

| 譜字 (Kinko) | 譜字 (Tozan) | Romanisation | Pitch (1.8 shaku) | 十二律 name |
|---|---|---|---|---|
| ロ | ロ | ro | **D4** | 壱越 ichikotsu |
| ツ | ツ | tsu | **F4** | 勝絶 shōzetsu |
| レ | レ | re | **G4** | 双調 sōjō |
| チ | チ | chi | **A4** | 黄鐘 ōshiki |
| **リ** | **ハ** | ri / ha | **C5** | 神仙 shinsen |

[V, three independent sources agreeing on the pitch content:
(a) **Nipponica (Tsukitani)**: 「指孔の開閉の組合せによる基本音列（レ・ファ・ソ・ラ・ド）」 — the
basic series by hole-combination is **re–fa–so–la–do**, i.e. D–F–G–A–C in fixed-do;
(b) **ja.wikipedia 尺八**: names them ロ・ツ・レ・チ・リ in Kinko and ロ・ツ・レ・チ・ハ in Tozan and
gives 「一尺八寸管では乙音域でD4（壱越）・F4（勝絶）・G4（双調）・A4（黄鐘）・C5（神仙）」;
(c) the 42-row chromatic table in the same article, independently, puts 乙ロ at D4, 乙ツ at F4,
乙レ at G4, 乙チ at A4, 乙リ at C5.]

**This is the single most important divergence to get right and the English literature routinely
blurs it: the fifth degree is called リ *ri* in Kinko-ryū and ハ *ha* in Tozan-ryū, and they are the
same pitch (C5 on 1.8 shaku).** [V — ja.wikipedia 尺八, stated in prose and borne out by its table]

The resulting scale, D–F–G–A–C, is identified in Japanese sources as the **陽音階 *yō-onkai* /
律音階 *ritsu-onkai*** — the anhemitonic pentatonic without semitones, *not* the semitone-containing
都節 *miyako-bushi* scale. [V — ja.wikipedia 尺八: 「これは陽音階や律音階となり」] This is worth
stating because the *miyako-bushi* trichord is what analysts reach for in the **repertoire**: Simon
2017 notes that previous honkyoku analyses have relied on octave-species scales and on "trichords
spanning a perfect fourth," and that three transpositions of the *miyako-bushi* trichord
(m2 + M3 = P4) account for *part* of what is heard in Sōkaku Reibo but leave "several frequently
occurring tones and intervals … unaccounted for." [V — Simon 2017, p. 1] **The instrument's open
fingerings are anhemitonic; the music is not. The semitones come from meri and half-holing, which is
why §3 matters so much.**

### 2.3 Which holes are closed

**I could not verify a hole-by-hole chart from any source I was able to read, and I am not going to
invent one.** [U]

What is verified about hole mechanics:

- Holes are **numbered from the bottom** (1 at the bottom front, 5 the thumb hole at the back) —
  this follows from Kamisangō's finger list being given 「下から順に」 ("in order from the bottom").
  [V, inferred from 平凡社世界大百科事典 — the inference is mine]
- The pitch series is produced by 「指孔の開閉の組合せ」, combinations of opening and closing the
  finger holes. [V — Nipponica]
- Because the holes are **stopped by the bare fingertip directly**, not by keys or pads, not only
  fully-open and fully-closed but **半開 *hankai* (half-open) and 四半開 *shihankai* (quarter-open)**
  are available, which "allows the pitch to be varied subtly." [V — 平凡社世界大百科事典:
  「指孔を指先で直接押さえるので，全開・全閉のみならず，半開，四半開も可能で，音高を微妙に変化
  させ得る」] Nipponica's list of finger operations is slightly different and finer: 「半開・4分の3
  開・4分の1開・かざし指」 — **half-open, three-quarters-open, one-quarter-open, and *kazashi*
  fingering**. [V — Nipponica]

What a reader will want and I cannot supply: the explicit statement "ro = all closed; tsu = hole 1
open; re = holes 1–2 open; chi = holes 1–3 open; ri/ha = holes 1–4 open; all five open = D5." That
pattern is **consistent** with the verified pitches and with the verified fact that D5 is reachable
in the lower register as 乙イ (Kinko) / 乙ヒ (Tozan) as well as by overblowing ro [V — the
ja.wikipedia table lists D5 as 「乙 イ・甲 ロ」 in Kinko and 「乙 ヒ・甲 ロ」 in Tozan], and it is
what the successive-opening description implies. **But "consistent with" is not "verified," the
inference is mine, and the real charts in the method books assign specific partial closures to
specific notes that a naive successive-opening model would get wrong.** Treat the hole patterns as
**[U]** until checked against a published 運指表.

Sources that would settle it, and why I failed on each: `kochyo.co.jp/onritsu/` (a maker's
"音律と運指表" page — reached, but the charts are JPEGs and the page text came through mis-encoded);
`尺八.net` and several teacher blogs (enthusiast/commercial, unverified); Blasdel's manual
(unobtainable). The Japan Arts Council 文化デジタルライブラリー would be the right institutional
source and I did not reach a shakuhachi page on it.

### 2.4 Five holes, full chromatic capability — the mechanism

Twelve semitones from five holes is achieved by **three** stacked mechanisms, not one:

1. **Hole combinations** → the five 幹音 (D F G A C) plus the octave.
2. **Partial covering of a hole** — half, three-quarters, one-quarter, and *kazashi* (§3.3).
3. **Changing the lip–*utaguchi* geometry** — メリ meri down, カリ kari up (§3.1).

The reference works state the conclusion flatly. 平凡社世界大百科事典: 「指孔半開とメリ・カリの
併用により，音域内のすべての微分音を奏し得，かつポルタメント奏法も可能であり，これが尺八独特の
味わいを出す大きな特色となっている」 — by combining half-holing with meri/kari, **every microtone
in the range** can be played, and portamento too, and this is the major characteristic that produces
the instrument's distinctive flavour. [V, my translation] Japanese Wikipedia says the same at
semitone resolution: with these, 「基本的な運指において、西洋の12音音階すべての演奏が可能」. [V,
uncited section]

Note the stronger claim in the Japanese: not "chromatic" but **all microtones**. The chromatic scale
is a by-product; the instrument's resolution is continuous.

**Historical corollary worth keeping:** that this is *difficult* rather than impossible is why
multi-hole instruments were invented under Western-music influence from the 1920s — 七孔 (7-hole),
九孔 (9-hole), and the オークラウロ *Ōkuraulo* (a metal instrument with a flute key system).
Only the 7-hole saw any real use, and chiefly outside the classical repertoire. [V — 平凡社世界大
百科事典: 「洋楽の影響を受けて，半音階の吹奏を容易にするために尺八の孔数を増やした多孔尺八が
1920年代から現れる」; Nipponica dates them 昭和初期 and says 「ほとんど普及せず」] ja.wikipedia
adds 6-hole instruments, and the point that more holes means more stable extra notes but more
fingering constraints. [V, uncited]

### 2.5 The fingering / pitch reference table for 1.8 shaku

**Provenance, stated plainly, because this is the artefact most likely to be reused:** the table
below is **transcribed from the 42-row table in the 「音域・音階などについて」 section of Japanese
Wikipedia's 「尺八」 article**, read as raw wikitext via the MediaWiki API on 2026-11-13. **That
table carries no citation in the article.** What I independently verified against other sources:

| Claim | Verified against |
|---|---|
| 乙ロ = D4, 乙ツ = F4, 乙レ = G4, 乙チ = A4, 乙リ = C5 | **Nipponica (Tsukitani)** — basic series re-fa-so-la-do [V] |
| Kinko's fifth degree is リ, Tozan's is ハ | ja.wikipedia prose + table, mutually consistent [V]; **not** externally corroborated [U] |
| 乙 = 1st octave, 甲 = 2nd, 大甲 = 3rd; 甲 is the 2nd harmonic on the same fingering | **平凡社世界大百科事典 and Yamaha 音楽用語ダス**, independently [V] |
| Total range ≈ 2.5 octaves | **平凡社世界大百科事典** (「約2オクターブ半」) and **Yamaha** [V]; ja.wikipedia says 「2オクターブ強」 for C4–E6 and treats 大甲 as extra [V] — see §4.4 for the discrepancy |
| The meri/kari and half-hole symbols (メ, 中, カ, parenthesised Tozan glyphs) | ja.wikipedia only [U] |
| **Every individual row below C4–E7 as a fingering-to-pitch mapping** | **ja.wikipedia only. Not independently verified. [U]** |

Read 乙 *otsu* = lower register, 甲 *kan* = upper, 大甲 *dai-kan* = top. メ = メリ *meri*;
中 = 中メリ *chū-meri* ("middle meri," a lesser degree); 大 = 大メリ *dai-meri*. In the Tozan
column, **the parenthesised glyphs are written in the real scores as small-size characters**, not
with parentheses — that is Tozan's way of marking a meri note. [V — ja.wikipedia's own note:
「都山流のカッコ付きの文字は、実際の楽譜では小文字で書かれる」]

| Pitch (1.8 shaku) | 十二律 | Kinko 琴古流 | Tozan 都山流 |
|---|---|---|---|
| C4 | 神仙 shinsen | 乙 ロ大 | 乙 (ロ)メ |
| C#4 | 上無 kamimu | 乙 ロメ | 乙 (ロ) |
| **D4** | 壱越 ichikotsu | **乙 ロ** | **乙 ロ** |
| Eb4 | 断金 dankin | 乙 ツメ | 乙 (ツ) |
| E4 | 平調 hyōjō | 乙 ツ中 | 乙 ツメ |
| **F4** | 勝絶 shōzetsu | **乙 ツ** ・レメ | **乙 ツ** ・(レ)メ |
| F#4 | 下無 shimomu | 乙 レ中 | 乙 (レ) |
| **G4** | 双調 sōjō | **乙 レ** | **乙 レ** |
| Ab4 | 鳧鐘 fushō | 乙 チメ ・**ウ** | 乙 (チ) ・**ウ** |
| **A4** | 黄鐘 ōshiki | **乙 チ** | **乙 チ** |
| Bb4 | 鸞鏡 rankei | 乙 リメ | 乙 (ハ) |
| B4 | 盤渉 banshiki | 乙 リ中 | 乙 ハメ |
| **C5** | 神仙 shinsen | **乙 リ** | **乙 ハ** |
| C#5 | 上無 | 乙 イメ ・甲 ロメ | 乙 (ヒ) ・甲 (ロ) |
| D5 | 壱越 | 乙 イ ・**甲 ロ** | 乙 ヒ ・**甲 ロ** |
| Eb5 | 断金 | 甲 ツメ | 甲 (ツ) |
| E5 | 平調 | 甲 ツ中 | 甲 ツメ |
| F5 | 勝絶 | 甲 ツ ・レメ | 甲 ツ ・(レ)メ |
| F#5 | 下無 | 甲 レ中 | 甲 (レ) |
| G5 | 双調 | 甲 レ | 甲 レ |
| Ab5 | 鳧鐘 | 甲 チメ ・ウ | 甲 (チ) ・ウ |
| A5 | 黄鐘 | 甲 チ | 甲 チ |
| Bb5 | 鸞鏡 | 甲 ヒメ | 甲 (ハ) |
| B5 | 盤渉 | 甲 ヒ中 | 甲 ハメ |
| C6 | 神仙 | 甲 ヒ | 甲 ハ |
| C#6 | 上無 | 甲 イメ | 甲 (ヒ) |
| D6 | 壱越 | 甲 イ ・ハ五 | 甲 ヒ ・ピ |
| Eb6 | 断金 | ハ三 | タ |
| E6 | 平調 | ハ四 | 四 |
| **F6** | 勝絶 | 大甲 ツ | 大甲 ツ |
| F#6 | 下無 | 大甲 レ中 | 大甲 (レ) |
| G6 | 双調 | 大甲 レ | 大甲 レ |
| Ab6 | 鳧鐘 | 大甲 チメ | 大甲 (チ) |
| A6 | 黄鐘 | 大甲 チ | 大甲 チ |
| Bb6 | 鸞鏡 | 大甲 ヒメ | 大甲 (ハ) |
| B6 | 盤渉 | 大甲 ヒ中 | 大甲 ハメ |
| C7 | 神仙 | 大甲 ヒ | 大甲 ハ |
| C#7 | 上無 | 大甲 イメ | 大甲 (ヒ) |
| D7 | 壱越 | 大甲 ハ五 | 大甲 ピ |
| Eb7 | 断金 | 大甲 ハ三 | 大甲 タ |
| E7 | 平調 | 大甲 ハ四 | 大甲 四 |

[V as a transcription of ja.wikipedia 尺八, 2026-11-13; **[U] as a factual fingering chart**, with
the exceptions listed in the provenance table above. The article itself warns:
「運指名は代表的なもののみ示した。実際には他にも特殊な運指やその名前がある」 — only
representative fingering names are shown; other special fingerings and names exist.]

**Six things to read off this table.**

1. **C4 and C#4 exist below the fundamental.** ロ大メリ *ro-dai-meri* reaches **C4, a whole tone
   below the open tube**, and ロメリ gives C#4. That is the clearest demonstration that meri is not
   a small adjustment — see §3.2.
2. **The two schools' meri marks do not map onto each other by any single rule — the correspondence
   is note-by-note, and this is the most consequential thing in the table.** Kinko grades meri with
   three marks (**メ**, **中**, **大**); Tozan grades it with two devices (**glyph size** and **メ**).
   Laying the pairs side by side:

   | Pitch | Kinko | Tozan | Semitones below the open note |
   |---|---|---|---|
   | Eb4 | ツ**メ** | **small** ツ | 2 below ツ (F) |
   | E4 | ツ**中** | ツ**メ** | 1 below ツ |
   | F#4 | レ**中** | **small** レ | 1 below レ (G) |
   | F4 | レ**メ** | **small** レ + **メ** | 2 below レ |
   | Ab4 | チ**メ** | **small** チ | 1 below チ (A) |
   | Bb4 | リ**メ** | **small** ハ | 2 below リ/ハ (C) |
   | B4 | リ**中** | ハ**メ** | 1 below リ/ハ |
   | C#4 | ロ**メ** | **small** ロ | 1 below ロ (D) |
   | C4 | ロ**大** | **small** ロ + **メ** | 2 below ロ |

   **There is no consistent translation.** Kinko's **メ** means *two* semitones on ツ and リ but
   *one* on チ and ロ; Tozan's **small glyph** means *two* on ツ and ハ but *one* on レ, チ and ロ.
   Tozan's **メ** on a full-size glyph is the *shallow* meri (= Kinko 中), but Tozan's **メ** on a
   small glyph *deepens* it (= Kinko メ or 大). **So "Tozan's メ equals Kinko's 中" holds for ツ and
   ハ and fails for レ and ロ.** The reason is that the marks are not interval symbols at all — they
   name **degrees of chin displacement**, and §3.2 already established that a given displacement
   yields a different interval on every fingering. **Reading one school's score with the other
   school's habits produces semitone errors whose direction and size vary from note to note.**
   [V as a reading of the ja.wikipedia table; the tabulation and the conclusion are mine. **This
   is also, independently, a reason to doubt any English source that states a flat equivalence
   between the two notations' accidentals.**]
3. **ウ *u* is a cross-fingering,** not a meri note: both schools give **ウ** as an *alternative*
   to チメリ / small-チ for Ab. An Ab produced by a cross-fingering and an Ab produced by dropping
   the chin are **different sounds** (§3.4) and the notation keeps them distinct.
4. **The register boundary is not where you would guess.** D6 and Eb6–E6 are notated with
   *special* glyphs (Kinko ハ五 / ハ三 / ハ四; Tozan ピ / タ / 四) with **no 甲 or 大甲 prefix at
   all** — they are a transitional zone of their own. 大甲 proper starts at **F6**.
5. **F6 is the hardest note on the instrument.** Japanese Wikipedia says so explicitly:
   「全音域中で、一尺八寸管のF6相当の1音だけは演奏が極めて困難である」 — of the whole range, the
   single note corresponding to F6 is extremely difficult. [V, uncited] Note that it is also the
   *first* note of 大甲, i.e. the register's bottom note is its worst note.
6. **イ *i* (Kinko) / ヒ *hi* (Tozan) in the lower register is the all-open fingering** giving D5 —
   the octave of ro reached without overblowing. Kinko then reuses **ヒ** for the *kan* C6, where
   Tozan uses **ハ**. So **ヒ means different pitches in the two schools**: C6-area in Kinko, D5-area
   in Tozan. [V as a reading of the table]

### 2.6 The derived notes, named

- **ハ *ha*** — in **Tozan**, the fifth degree of the *go-on*, C5/C6 (where Kinko says リ/ヒ). In
  **Kinko**, ハ is not a *go-on* name at all: it appears only in the compound top-register
  fingerings **ハ五 / ハ三 / ハ四**. [V — ja.wikipedia table] **These are different uses of the same
  character in the two schools and this is the most common point of confusion in English accounts.**
- **ヒ *hi*** — **Kinko**: the upper-register C (甲ヒ = C6, 大甲ヒ = C7), i.e. the *kan*-register
  counterpart of 乙リ. **Tozan**: D5/D6, the all-open fingering. [V — ja.wikipedia table]
- **イ *i*** — **Kinko** only: the all-open fingering, 乙イ = D5, 甲イ = C#6. [V — ja.wikipedia table]
  Tozan has no イ in this table.
- **ロの大メリ *ro no dai-meri*** — ロ with the deepest chin-down, **C4**, a whole tone below the
  fundamental; written 乙ロ大 in Kinko and as a small ロ in Tozan. [V — ja.wikipedia table]
- **ウ *u*** — a cross-fingering for Ab4/Ab5, in both schools. [V — ja.wikipedia table]
- **ピ *pi*, タ *ta*, 四 *shi*** — Tozan's special top-register glyphs for D6, Eb6, E6 (and their
  octaves in 大甲). [V — ja.wikipedia table] **What finger positions these denote: [U].**
- **中 *chū*** — Kinko's intermediate-meri marker (中メリ). [V — ja.wikipedia table; the gloss
  "intermediate degree of meri" is my inference from its consistent position one semitone above the
  メ row throughout the table.]

The 竹保流 *Chikuho-ryū* uses an **entirely different set of syllables** — **フホウエヤイ**
*fu-ho-u-e-ya-i* instead of ロツレチ — in a notation called フホウ譜 *fuhō-fu*. [V — ja.wikipedia
尺八 §竹保流: 「譜にロツレチではなく、フホウエヤイを用いるフホウ譜を用いている」; corroborated
independently and in more detail by Nipponica, §6.6 below] **The syllable set itself is not shared
across the tradition.**

---

## 3. メリ *meri* and カリ *kari*

### 3.1 What they are

**メリ *meri* lowers the pitch; カリ *kari* raises it.** The mechanism is a change in the
**gap/geometry between the lips and the *utaguchi***, and the physical action is a rotation of the
head about the contact point between instrument and jaw:

- **メリ** — 「あごを引いて音を下げ」, draw the chin **in/down**, pitch falls. [V — 平凡社世界大
  百科事典 (Kamisangō)]
- **カリ** — 「あごを出して音を上げる」, push the chin **out/up**, pitch rises. [V — same]

Japanese Wikipedia gives the kinematics more precisely: the **contact point between the instrument
and the lower jaw (slightly below the lower lip) is the fulcrum (支点)**; pulling the chin in
(沈める, "sinking" it) gives meri, floating it up gives kari. [V — ja.wikipedia 尺八 §奏法, uncited]
Kamisangō's framing is the complementary one — 「唇と歌口の間隙を変える」, *changing the gap between
lip and utaguchi* — and that is the more useful description acoustically, because the thing that
changes is how much of the edge the lip covers and at what angle the jet meets it. [V]

Acoustically this is the "large change in the relative geometry of the instrument and the face" that
the UNSW group names as the source of the instrument's pitch and timbre flexibility; since the
radiation impedance is baffled by the face and **varies with playing position**, moving the chin
retunes the impedance minima rather than merely bending a note by force. [V — UNSW page, as in §1.2]
**That is the formal reason meri changes timbre as well as pitch** (§3.4).

### 3.2 The degrees, and how far it actually goes

| Term | Characters | Effect | Source |
|---|---|---|---|
| カリ | — | up, "about 1 semitone" in normal use | ja.wikipedia [V, uncited] |
| メリ | — | down; ~1 semitone (Tozan reading) or ~2 (Kinko reading) — see below | ja.wikipedia [V, uncited] |
| 中メリ | *chū-meri* | intermediate degree, Kinko notation | ja.wikipedia table [V, uncited]; gloss mine |
| 大メリ | *dai-meri* | down a whole tone or more; ロ大メリ reaches C4 from D4 | ja.wikipedia [V, uncited] |

**Real numbers, and they are larger than most English accounts suggest.** Japanese Wikipedia states
that the available meri/kari range **widens as the fingering approaches fully open**
(「メリ、カリの範囲は開放管（指で手孔を押さえない）の状態に近いほど広くなり」) and that **meri can
reach more than four semitones at maximum** (「メリでは最大で半音4個ぶん以上になる」), while the
range used in ordinary playing is **about 2 semitones of meri and about 1 semitone of kari**
(「通常の演奏に用いる範囲はメリで2半音、カリで1半音程度」). [V — ja.wikipedia 尺八 §奏法, uncited
section; these are the only quantitative figures I found anywhere, and they are unsourced in the
article. Treat the numbers as the tradition's own rule of thumb, not as measurement. [U] for
provenance.]

Two consequences worth stating explicitly because they are usually missed:

- **The asymmetry is real and large: meri has roughly twice the working range of kari, and up to
  four times the maximum range.** The instrument bends down far more readily than up. This is why
  the chromatic notes in §2.5 are overwhelmingly notated as meri-from-above rather than
  kari-from-below.
- **The range is fingering-dependent.** Near-closed fingerings bend less. So "meri lowers by a
  semitone" is not a constant; it is a different interval on every note, and the player's job is to
  land the pitch, not to apply a fixed displacement.

### 3.3 Partial-holing and *kazashi*

Two source lists, and they do not quite match:

- **平凡社世界大百科事典 (Kamisangō)**: because the fingertip stops the hole directly, **全開
  (fully open) / 全閉 (fully closed) / 半開 (half) / 四半開 (quarter)** are all available. [V]
- **Nipponica (Tsukitani)**: 「半開・4分の3開・4分の1開・かざし指」 — **half-open,
  three-quarters-open, one-quarter-open, and *kazashi*-finger**. [V]

So the attested degrees are **half, three-quarters, and one-quarter**, and **かざし / かざし指
*kazashi* / *kazashi-yubi* is listed by Tsukitani as a distinct category alongside the partial
openings, not as a synonym for them.** [V]

**What *kazashi* physically is: I could not verify it.** Neither encyclopedia defines it, and I
found no definition in any source I read. The common English gloss is "shading" — holding a finger
*near* the hole without touching it, so as to flatten the pitch slightly without the discontinuity
of a partial cover. **That gloss is [U]: I cannot name an artefact for it, and the character
かざす (to hold something over/above something) is consistent with it but does not prove it.**
I flag it rather than assert it; the usual account is right that flagging beats a confident wrong gloss.

**半音 *hanon*** literally means "semitone" in general Japanese musical usage and I did **not** find
it used as the name of a partial-holing technique in any source I read. **[U — if a school uses
半音 as a technique name, I did not verify it, and I suspect the usual account has picked this up from an
English source conflating "the semitone you get" with "the technique that gets it."]**

### 3.4 The crucial point: meri notes have a different timbre

This is the claim that matters musically and it is **verified at the level of the sources' own
emphasis**, if not with spectra.

- 平凡社世界大百科事典 treats the width of **timbral** variation as a defining characteristic of the
  instrument in its own right, listed immediately after the microtonal/portamento capability:
  「加えて音色の変化の幅の大きさもこの楽器の特色である」 — "in addition, the great width of timbral
  change is also a characteristic of this instrument." [V]
- ja.wikipedia: by changing the **shape of the oral cavity** and the **flow rate**, the harmonic
  composition can be varied at will, from a well-projecting tone to a round soft one
  (「口腔内の形状変化や流量変化等により、倍音構成はよく通る音色や丸く柔らかいものなど、適宜変化
  させることができる」). [V, uncited]
- The acoustic reason: because the face baffles the radiation impedance and the face's position is
  what meri changes, a meri note is not the same resonator excited the same way at a lower
  frequency — the **radiation condition and the impedance minima have both moved**. [V — UNSW page;
  the application to meri specifically is my inference]

**The musical consequence — that the timbral difference is exploited rather than corrected for —
is the single most important thing in this file and I can support it structurally rather than by
direct quotation.** The structural evidence is in §2.5: both schools maintain **two different
notations for the same pitch** — Ab is either チメリ *or* ウ; F is either ツ *or* レメリ; C#5 is
either 乙イメ *or* 甲ロメ. A notation that cared only about pitch would not need the distinction. It
keeps the distinction because **which route you take to the pitch is part of the musical text**. [V
for the existence of the alternative spellings — ja.wikipedia table; the argument from them is mine]

A second structural argument: the Japanese reference works describe the capability as **「音域内の
すべての微分音」** (all microtones in the range) rather than as "chromatic," i.e. they frame the
instrument as having continuous pitch and continuous timbre, with the twelve semitones as a
subset. [V — 平凡社] A tradition that thought of meri as a correction mechanism would not describe
it that way.

**What would settle it quantitatively:** spectral comparison of ツ (F, open fingering) against
レメリ (F, meri fingering). **No such measurement found. [U]**

### 3.5 Cross-fingerings

**Verified:** ウ *u* exists as an alternative fingering to チメリ for Ab in **both** schools, in
both 乙 and 甲. [V — ja.wikipedia table] The 大甲 rows drop it, giving only 大甲チメ / 大甲(チ) —
so the cross-fingering is not available at the top. [V, same table]

**Also verified as structurally present:** F4 and F5 each have two spellings (ツ, and レメリ) in
both schools. [V — ja.wikipedia table] This is a cross-relation between the open series and the
meri series rather than a "cross-fingering" in the Western woodwind sense.

**Any further catalogue of cross-fingerings: [U].** ja.wikipedia says explicitly that special
fingerings beyond its table exist; it does not list them, and I found no list.

---

## 4. Registers: 乙 *otsu*, 甲 *kan*, 大甲 *dai-kan*

### 4.1 The three registers and how they are produced

| Register | Characters | Also called | Mechanism |
|---|---|---|---|
| 1st octave | **乙 *otsu*** | **呂 *ryo*** | fundamental |
| 2nd octave | **甲 *kan*** | — | **the same fingering, with the breath made sharper** — the 2nd harmonic |
| 3rd octave | **大甲 *dai-kan*** | — | the **3rd and 4th harmonics** |

[V — 平凡社世界大百科事典 (Kamisangō): 「第1オクターブ（呂（りよ）または乙（おつ））…第2オク
ターブ（甲（かん））は同じ指法で呼気の鋭さを変えた2倍音として得られ，その上の音（大甲（だい
かん））は3倍音・4倍音を利用する」; independently corroborated by Yamaha 音楽用語ダス: 「同じ指使い
で鋭く息を吹き入れて発する第2オクターブの音（甲）、独特な指使いで、不完全ながらに得ることが
できる第3オクターブ（大甲）」]

**呂 *ryo* and 乙 *otsu* are two names for the same register.** [V — 平凡社; Yamaha] The app
documentation at jonkara.com uses 呂音/乙音, 甲音, 大甲音 with 音 appended. [V — commercial source]

### 4.2 How the overblow is produced

Two different descriptions, and the difference is informative:

- **Kamisangō (平凡社)**: 甲 is the second harmonic obtained on **the same fingering** by changing
  **the sharpness of the exhaled breath** (「呼気の鋭さを変えた2倍音」). [V]
- **Yamaha 音楽用語ダス**: same for 甲 (「鋭く息を吹き入れて」), but 大甲 requires a **distinctive
  fingering** (「独特な指使いで」) and is obtainable only **incompletely** (「不完全ながらに」). [V]

So: **the octave break is a breath event on an unchanged fingering; the third register is not** —
it needs its own fingerings, which is exactly what the special glyphs ハ五/ハ三/ハ四 and ピ/タ/四
in §2.5 encode. [V, synthesis mine] "Sharpness" (鋭さ) rather than "pressure" is the sources'
word; it bundles jet velocity, aperture and angle, and no source I read decomposes it. [U]

### 4.3 Ranges on 1.8 shaku

- **乙 *otsu***: D4 up to C5 as open notes (C4 reachable by ロ大メリ), i.e. the written span in the
  table runs **C4–D5**. [V — ja.wikipedia table]
- **甲 *kan***: C#5/D5 up to C#6. [V — same]
- **The transitional glyphs** (Kinko ハ五/ハ三/ハ四, Tozan ピ/タ/四) cover **D6–E6** and carry no
  register prefix. [V — same]
- **大甲 *dai-kan***: begins at **F6**; the table runs to **E7**. [V — same]

### 4.4 Where the practical top is — and a discrepancy to report

The sources disagree, and the disagreement is about what counts as playable:

| Source | Stated range |
|---|---|
| 平凡社世界大百科事典 (Kamisangō) | 「音域は約2オクターブ半に及ぶ」 — about **2.5 octaves** [V] |
| ヤマハ 音楽用語ダス | 「常用される音域は、ほぼ2オクターブ半に及ぶ」 — the **commonly used** range is about 2.5 octaves, 大甲 being obtainable only incompletely [V] |
| ja.wikipedia 尺八 | 「基本的には音域は2オクターブ強（一尺八寸管でC4-E6）」 — basically **a little over 2 octaves, C4–E6**, with 大甲 as a further ~octave used **infrequently**; and with high technique up to about **E7** [V, uncited] |

**Reconcile them like this:** the *reliable* range is about two octaves and a bit, roughly **C4 to
E6**; "about 2.5 octaves" is the conventional encyclopedia figure and matches C4–E6 plus the lower
part of 大甲; and **E7 is the ceiling claimed for a high-technique player, not a working range.**
[Synthesis mine; the three figures are each V]

Add the F6 anomaly from §2.5: **the bottom note of 大甲 (F6) is described as extremely difficult**,
so the top register does not begin where it is notated to begin — in practice players enter it
above its own floor. [V — ja.wikipedia, uncited]

**What I could not find:** any statement of which register honkyoku actually inhabits, or
measurement of how far into 大甲 any recorded performance goes. **[U]**

---

## 5. The ornament and articulation vocabulary

### 5.0 Read this before using the table: the vocabulary is not shared

**The single most important fact about shakuhachi ornament vocabulary is that there is no single
vocabulary.** The Japanese reference works say so directly about the notation
(「派生音や音価表記の方法は…各流とも異なり、指法も微妙な差があって複雑である」 — the methods of
notating derived pitches and durations differ in *every* school, and the fingerings differ subtly
too, making it complex) [V — Nipponica, Tsukitani], and the trade glossary says it about individual
techniques over and over: of the finger-strike, 「流派や指孔によって様々な呼び名がある」 — the names
vary by school *and by which hole is struck*. [V — 尺八修理工房幻海 glossary, ア行]

Three patterns recur and are worth naming up front:

1. **Same technique, different name.** *nayashi* ナヤシ is called **チギリ** *chigiri* in
   根笹派錦風流 Nezasa-ha Kinpū-ryū; the finger-strike is called **鈴打ち** *suzu-uchi* in
   明暗真法流 Myōan Shinpō-ryū; **カラカラ** is called **鈴ゴロ** *suzu-goro* in the Myōan and Kinko
   lines; the two-finger trill is **もみ手** *momite* in Tozan but notated **オドル** *odoru* in
   other schools. [V — 幻海 glossary, カ行/ナ行/マ行]
2. **Same name, different action.** **縦ユリ** *tate-yuri* ("vertical yuri") is executed by
   **shaking the head vertically in Tozan-ryū** and by **shaking with the hand in Kinko-ryū**
   (「都山流は首を縦に揺る・琴古流は手で縦に揺る」). [V — 幻海 glossary, ヤ行] **This is the
   clearest single example of why "which school?" must precede any technique description.**
3. **Same name, two different techniques with different spellings.** 玉音 and タマ音 are both read
   *tamane* and are **different techniques** — throat vs tongue. See §5.3.

### 5.1 The authoritative Japanese taxonomy

Tsukitani Tsuneko's Nipponica entry classifies the technique vocabulary **by the body part that
produces it**, which is the right axis and the one English accounts usually abandon. Verbatim,
with my translation:

> 「指やあごの微妙な運動による微分音やポルタメント奏（**メリ込、スリ上げ、ナヤシ**など）、細かい
> 指の動きによるトレモロ奏（**コロコロ、カラカラ**）、あごの連続運動によるビブラート奏（**縦ユリ・
> 横ユリ・斜ユリ**）、のどや息を使った特殊奏（**タマネ、ムラ息、コミ吹**）など、多彩な技法を用いる」

— microtone and portamento playing by subtle finger and chin movements (*meri-komi, suri-age,
nayashi* etc.); tremolo playing by fine finger movements (*korokoro, karakara*); vibrato playing by
continuous chin movement (*tate-yuri, yoko-yuri, **naname-yuri***); and special techniques using the
throat and the breath (*tamane, mura-iki, komi-buki*). [V — Nipponica, 「尺八」§普化尺八/形態と奏法]

**Note 斜ユリ *naname-yuri* ("diagonal yuri").** Tsukitani's triad is 縦/横/斜 — vertical,
horizontal, **diagonal** — not 縦/横/大. **I found no source for 大ユリ *dai-yuri* and it is not
in Tsukitani's list, the trade glossary's list, or the ja.wikipedia account. [U — flagging rather
than glossing: if 大ユリ is a real term it belongs to a school I did not reach, and the usual account's
"slow 大ユリ" may be an English-literature coinage.]**

A second, independent taxonomy on the same axis comes from a Japanese engineering paper, and it is
valuable because it was built in order to *measure* the techniques:

**Utsugi Yōsuke 宇都木陽介 & Moriyama Tsuyoshi 森山剛 (Tokyo Polytechnic University),
「尺八演奏音からの奏法の識別」 / "Classification of Playing Methods Used in Shakuhachi
Performance," 情報処理学会研究報告 IPSJ SIG Technical Report Vol. 2009-MUS-80 No. 4 (2009-05-21),
6 pp.** [V — downloaded and read in full from `mega.t-kougei.ac.jp/media/moriyama/publications/IPSJ-MUS09080004.pdf`,
2026-11-13] Their 表1 lists the determinants of a technique as **運指** fingering (全て押さえる /
浮かす / 離す — fully stopped / **floated** / released), **息** breath (strong, weak, much, little,
wavering), **角度** angle (swing horizontally / shake vertically), **舌** tongue (roll). Their
classification:

| Cause | Techniques |
|---|---|
| 手孔を塞ぐ量 — *amount* the hole is covered | メリ (中メリ, 大メリ), カリ |
| 手孔を塞ぐ指の変動 — *movement* of the stopping finger | スリアゲ, ナヤシ |
| 手孔を押さえる速さと繰り返し — *speed and repetition* of stopping | ウチ (打ち), オシ (押し), カラカラ, コロコロ |
| 尺八の角度の変化 — change in the instrument's *angle* | ユリ, オトシ |
| 息の吹き込む量 — *quantity* of breath blown | ムライキ (ムラ息) |
| 舌の動き (タンギング) — *tongue* movement | タマネ (玉音) |
| 特定の音階の配列 — a specific *pitch sequence* | ハラロ |

[V — Utsugi & Moriyama 2009, §2.2]

**Two things to notice.** First, **ハラロ *hararo* is classified as a technique even though it is
just a sequence of pitches** — in this tradition a named melodic formula counts as a playing
technique, which tells you something real about how the vocabulary is organised. Second, this paper
puts **オトシ under instrument-angle change** and **タマネ under the tongue**, where other sources
put otoshi under finger repetition and tamane in the throat. Those are genuine disagreements and
I report them in §5.3 and §5.5 rather than picking a winner.

**The recording basis, because it makes the paper's descriptions usable:** two **Kinko-ryū shihan**
— 青木彰時 Aoki Shōji and 佐野鈴霏 Sano Reihi — recorded on their own 1.8 shaku instruments in a
Yamaha CEFINE sound-isolation booth (RODE NT2000 mic, Yamaha AW2400 recorder), playing the basic
scale note-by-note and continuously from 乙ロの大メリ to 大甲の四のハ, **14 pairs of 同音異奏
(same-pitch-different-fingering)**, each technique in both 乙 and 甲 on the base note レ, and then
the honkyoku **『鹿の遠音』 *Shika no Tōne*** complete. Classification accuracy across eight
techniques averaged **82%**, rising to **98%** if スリアゲ and ナヤシ are merged into one class.
[V — Utsugi & Moriyama 2009, §4] **So the techniques are physically distinguishable from the sound
alone — which is a real, if narrow, empirical answer to "is this a measurable thing or a mystique?"
— except that suriage and nayashi are nearly not, and the authors attribute the residual confusion
to differences between the two players rather than between the techniques.** [V, §4.3]

### 5.2 Source labelling for the rest of this section

Beyond Tsukitani and Utsugi & Moriyama, the fine-grained vocabulary below comes largely from one
source, and you must know what it is:

**尺八修理工房幻海 (Shakuhachi Repair Studio GENKAI), 「尺八用語集」, `shakuhachi-genkai.com/study03.html`
and `glossary01.html`–`glossary09.html`** — fetched and scraped 2026-11-13; I read all nine
kana-row pages. **This is a commercial shakuhachi repair and sales studio, not an academic or
institutional source.** Three things make it usable anyway: (a) it names its own printed references
(『新音楽辞典』, 『最新音楽用語事典』, and **田辺尚雄『邦楽用語辞典』** — Tanabe Hisao being a
foundational Japanese musicologist); (b) it gives **hole-by-hole physical instructions**, which no
encyclopedia does; (c) **Japanese Wikipedia's 「尺八」 article cites this studio's site as a source**
for instrument damage. [V — ja.wikipedia 尺八, ref `ging2012-1`] It also marks its own opinions as
opinions (「ここからは私見だが」). **Treat every claim sourced to it below as a trade
practitioner's account: good on physical detail, unaudited on school attribution, and in places
visibly the author's own usage.** I mark it **[V/trade]**.

### 5.3 The techniques, term by term

#### ムラ息 / ムライキ *mura-iki*

| | |
|---|---|
| **Characters** | ムラ息, also written ムライキ |
| **Physical action** | Drastically increase the quantity of breath so that most of what emerges is **wind noise across the edge rather than the tone of the pipe** |
| **Sound** | Breathy/explosive; pitch stays roughly constant while **power rises sharply at the attack and then decays gradually**, with a **relatively large power-spectrum slope at the onset**, and it is usually accompanied by 息混ぜ, audible breath mixed into the tone |
| **Classification** | 息の吹き込む量 — breath *quantity* |
| **Schools** | Pan-traditional; Tsukitani lists it as one of three throat/breath techniques for the instrument generally |

[Action and classification: **V** — Utsugi & Moriyama 2009 §2.2, §2.3.2; acoustic description: **V**
— same, §2.3.2, verbatim 「音高はほぼ一定に推移する．パワー遷移は，遷移部で急激に立ち上がり，
その後ゆるやかに減少する．息混ぜを伴うことが多く，音の立ち上がり部分において，パワースペクトル
傾斜が比較的大きな値を示す」; general-vocabulary status: **V** — Nipponica]

**The graded family around it is specific and worth having**, because "muraiki" in English usually
swallows all of it: **笹音 *sasane*** is half-muraiki, husky "like the touch of a bamboo-grass leaf,"
also called 半ムラ息; **浅音 *asane*** is deliberately husky but blown less forcefully than muraiki,
or alternatively blown with **less than half the normal breath quantity** for a soft tone, in which
case you **kari slightly so the pitch does not sag**; **ソラ音 *sorane*** (空音/空息) is, *in
Kinko-ryū*, deliberately aiming the breath **off** the sounding edge — harder than asane, softer
than muraiki; **ウカシ *ukashi*** (浮カシ) is a thick breath flowed in gently so the tone seems to
float up — like muraiki but not violent, **available only in 乙 and only on a 地無し instrument**.
[V/trade — 幻海 glossary, ア行 and サ行] That last restriction is a real claim about the
instrument–technique relationship and I have seen it nowhere in English. **[U] as to whether other
schools accept it.**

#### コロコロ *korokoro* and カラカラ *karakara*

Both are **トレモロ奏 by fine finger movement** [V — Nipponica] and both are **repetition-of-stopping**
techniques [V — Utsugi & Moriyama §2.2]. The acoustic signature given in the measurement paper is
the same for both: 「音高は，オクターブ間の上昇・下降を繰り返し，パワーも，その音高変化に合わせて，
急激な上昇・下降を繰り返す」 — **the pitch repeatedly rises and falls between octaves, and the power
rises and falls sharply in step with it.** [V — Utsugi & Moriyama §2.3.3]

The hole-level recipes differ, and this is the part no encyclopedia gives:

| | コロコロ | カラカラ |
|---|---|---|
| Chin | **meri** throughout | (not specified; three graded forms exist — see below) |
| Hole 5 (thumb) | **half closed** | **closed** |
| Hole 4 | **kazashi** (shaded) | **kazashi** — 1/2 closed for meri, 3/4 for dai-meri |
| Hole 3 | **closed** | **open** |
| Hole 2 | — | open or closed, **either is acceptable** |
| Holes 1 & 2 | **alternately opened and closed** | — |
| Hole 1 | — | **struck/chopped finely** (叩き or 刻み) |
| Target sound | "korokoro / pokopoko," likened to the *kodama* tree-spirits in *Princess Mononoke* | a bird calling **"chi-chi-chi"** — the faster and finer, the better |

[V/trade — 幻海 glossary, カ行 (カラカラ) and コロコロ. **Note the author's own framing: "the tone
changes a lot depending on how much hole 4 is shaded, so it is interesting to try various amounts"
— i.e. this is an adjustable continuum, not a fixed fingering.**]

Additional facts from the same source, all [V/trade]:

- **カラカラ comes in three grades** — 通常 (ordinary), メリ, and 大メリ — and **the dai-meri form
  is written in small characters.** (Compare §2.5: Tozan marks deep meri by glyph size. Same
  convention, different context.)
- **カラカラ is called 鈴ゴロ *suzu-goro* in the Myōan and Kinko lines.** A near relative,
  **上ゴロ *uwa-goro*,** is karakara on hole 3.
- **An instrument on which karakara will not sound properly is called 片鳴り *katanari* or
  片カラ *katakara*, and whether karakara works is used as a test when choosing an instrument.**
  [This is a maker's/dealer's claim and exactly the sort of thing a repair studio would know.]
- **In Tozan-ryū, korokoro usually continues as コロコロリン *korokororin*** — the リン being the
  last instant done very fast, with the chin **kari'd at the moment of stopping.**
- **ホロホロ *horohoro*** = korokoro in the **乙** register, found in **Myōan-line** hands.
- **ヒラヒラ *hirahira*** = korokoro on **ピ** (two octaves above 乙 D), appearing in **Myōan-line
  honkyoku.**
- **ヤラヤラ *yarayara*** = in **大甲**, hole 5 closed, alternating strikes on holes 1 and 2 —
  korokoro an octave up; **Myōan-line.**

**A discrepancy to report rather than resolve:** the measurement paper describes both korokoro and
karakara as octave-alternating; the trade glossary's recipes describe adjacent-hole alternation with
a shaded hole 4, which would more naturally produce a narrower warble plus a register flip. **These
may be describing different schools' versions, or the measured players' version may differ from the
recipe. [U]**

#### 玉音 *tamane* vs タマ音 *tamane* — two different techniques, same reading

This is the clearest terminological trap in the whole vocabulary and **both spellings are attested
in the same glossary with explicitly different definitions**:

- **玉音 *tamane* (the one the source calls 「正式な奏法」, the formal technique): a THROAT flutter.**
  「のどをうがいをする時の様に震わせて音を変化させる」 — vibrate the throat **as when gargling**.
  The recommended learning sequence is: get the feeling of gargling with water, then dry-gargle
  without water, then add the tone. Being able to do it **fast or slow at will** is the essential
  point. The glossary adds that **Yokoyama Katsuya** practised it by playing the whole of 『六段』
  in tamane. Related terms: 筒音, 口車. [V/trade — 幻海 glossary, タ行]
- **タマ音: a TONGUE flutter**, i.e. Western **flutter-tongue / Flatterzunge**, rolled-r articulation.
  The glossary's verdict is that the tongue version is hard to control for speed and "lacks
  flavour," so it does **not** suit honkyoku, but is recommended for modern and ensemble pieces
  because of its pitch stability. It suggests 錦風流's **口車 *kuchiguruma*** corresponds to this.
  [V/trade — 幻海 glossary, タ行 and ハ行]

**This resolves a real conflict between my two best sources:** Tsukitani classes タマネ among
「のどや息を使った特殊奏」, **throat and breath** [V — Nipponica], while Utsugi & Moriyama class
タマネ(玉音) under 「舌の動きによる奏法（タンギング）」, **tongue** [V — Utsugi & Moriyama §2.2].
They are not contradicting each other about one technique; **there are two techniques, and at least
one of my sources has attached the wrong one to the written form 玉音.** Which is "correct" is
**[U]**, and an English writer should say "throat tamane" or "tongue tamane" and never just "tamane."

The measured signature, for whichever one the Kinko shihan played:
「音高が安定しない．小刻みな立ち上がりを生ずるが，全体的になだらかなパワー遷移となる」 — **pitch
is unstable; it produces small rapid onsets but an overall smooth power envelope.** [V — Utsugi &
Moriyama §2.3.3]

**タバ音 *tabane*** is reported as a higher-order technique above tamane, done **with abdominal
pressure alone**, with the glossary author saying only a handful of people in Japan can do it and
openly guessing at the mechanism (「詳しくはよく解らない」). **[U — the source itself does not claim
to know. Report the term, not a definition.]**

#### あたり *atari* and 打ち *uchi* — the finger attacks

- **打ち *uchi* / 打ち指 *uchi-yubi* / 叩き *tataki*** — **striking a finger hole** to inflect the
  note. **The names vary by school and by which hole is struck**: e.g. the hole-1 strike on ツ is
  called **ル** *ru*, and on レ it is called **エ** *e*. **明暗真法流 Myōan Shinpō-ryū calls it
  鈴打ち *suzu-uchi*.** [V/trade — 幻海 glossary, ア行]
- **押し *oshi* / 押し指 *oshi-yubi*** — **re-pressing** a hole already stopped (as against striking
  an open one). [V/trade — 幻海, ハ行 under ハズミ指]
- **ハズミ指 *hazumi-yubi*** is the umbrella term: a kind of **ghost note** produced to help a note
  start or to emphasise its momentum, of **two kinds, 押し指 and 打ち指**, and **common in
  Myōan-line technique**. [V/trade — 幻海, ハ行]

**The measured distinction between uchi and oshi is crisp and is the most useful single sentence I
found about them:** 「両者共に，音高変化の際，瞬間的にパワーが上昇するが，**オシでは，音高が上昇し，
ウチでは，下降する**」 — in both, power rises instantaneously at the pitch change, but **in *oshi*
the pitch rises and in *uchi* it falls.** [V — Utsugi & Moriyama §2.3.2] Both are short-duration
techniques by the paper's own classification. [V, §2.3.2]

**あたり *atari*: I could not verify this term in any source I read. [U]** It does not appear in
Tsukitani's taxonomy, in Utsugi & Moriyama's list, or anywhere in the nine-page 幻海 glossary (which
*does* carry 打ち, 押し, ハズミ指, 落し, 刻み, もみ手 and オドリ). **Flagging it rather than glossing
it.** It is plausibly a school-specific name for the same gesture — the glossary's own statement that
the finger-strike has many names by school and hole makes that likely — but I have no artefact and
will not invent a definition.

**ゴースト・ノート** is in the glossary as a real analytic concept rather than an import: a note that
is not actually sounded but is heard as if played — e.g. in 「ツレー」 on holes 3 and 4, opening hole
3 before ツ has sounded still reads as "tsu-re." The glossary's remark is worth quoting:
「上級者ほど実際には聴こえない音を大切にする」 — the more advanced the player, the more they value
the notes that are not actually heard. [V/trade — 幻海, カ行]

#### ユリ *yuri* — the vibratos

**Definition:** ユリ (搖り) is vibrato: 「首を振ることや息などによって音の高低を動揺させ」 — setting
the pitch oscillating by **shaking the head, or by the breath**, giving a distinctive quaver.
[V/trade — 幻海, ヤ行] ja.wikipedia adds the key contrast with the flute: **meri/kari — the chin's
vertical motion (縦ユリ) or the neck's horizontal swing (横ユリ) — produce a vibrato that "differs
from the flute's vibrato by breath-flow variation" and has 「独特の艶」, a distinctive lustre**; and
breath-flow vibrato **is** also used, and is then called **息ユリ *iki-yuri*.** [V — ja.wikipedia
尺八 §奏法, uncited]

**The attested varieties:**

| Term | Characters | What it is | Source |
|---|---|---|---|
| 縦ユリ | *tate-yuri* | "vertical." **Tozan: shake the head vertically. Kinko: shake with the HAND vertically.** | Tsukitani [V]; the school split [V/trade] |
| 横ユリ | *yoko-yuri* | "horizontal" — swing the neck side to side | Tsukitani [V]; ja.wikipedia [V] |
| 斜ユリ | *naname-yuri* | "diagonal" | **Tsukitani [V]** — and *only* Tsukitani; no description found [U] |
| 回しユリ | *mawashi-yuri* | "circling" yuri | [V/trade] |
| 息ユリ | *iki-yuri* | breath-flow vibrato, as on the flute | ja.wikipedia [V]; [V/trade] |
| 手ユリ | *te-yuri* | "hand" yuri | [V/trade] — listed, not defined [U] |
| 底ユリ | *soko-yuri* | "bottom" yuri | [V/trade] — listed, not defined [U] |
| ナヤシユリ | *nayashi-yuri* | yuri that gradually returns to meri or kari | [V/trade] |

**Three ways of shaping a yuri**, all [V/trade — 幻海, ヤ行]: (1) constant width throughout;
(2) progressively **narrowing** the width, getting finer; (3) *nayashi-yuri*, yuri-ing while
gradually returning to meri or kari. And the explicit warning that matters:
「流派によっても名称が同じでもユリ方が違うものもある」 — **even where the name is the same, the way
of doing the yuri can differ by school.**

- **ユリ込み *yurikomi*** — stopping the note with a *meri-komi* while yuri-ing; the glossary advises
  keeping the yuri from getting sluggish. [V/trade]
- **フリ *furi* (振り)** — draw the chin in and quickly return: a **single** *tate-yuri*, "a light
  flick of the chin." **フリ込み *furikomi*** — *meri-komi* immediately after a *furi*, or passing
  from *furi* into *yuri*. [V/trade]
- **シズメ吹き *shizume-buki* (沈め吹き)** — meri→kari→meri→kari repeated several times, "an
  exaggerated 回しユリ done several times"; **common on ロの大メリ and ウのメリ**, with the point that
  the meri should be **louder** than the kari. [V/trade]
- **十三冠 *jūsan-kamuri*** — a characteristic **melodic formula built out of yuri**, appearing in
  classical honkyoku such as 『阿字観』; 十六カムリ and 三十六カムリ also exist. [V/trade] A named
  yuri-formula, i.e. the same "a figure is a technique" logic as *hararo*.

Yuri's measured signature: it needs **a certain minimum duration** because both pitch and power
change comparatively gradually. [V — Utsugi & Moriyama §2.3.1]

#### ナヤシ *nayashi*

**Tsukitani classes it with the portamento techniques, produced by subtle finger and chin movement**
[V — Nipponica]; Utsugi & Moriyama class it with 手孔を塞ぐ指の変動, movement of the stopping finger
[V].

The trade glossary gives it as **an application of 縦ユリ, in two broadly different forms, and says
which form is used depends on the piece, the school and the transmitting region**:

1. **A portamento** using chin meri→kari together with finger *kazashi*, **notated 「～」** — e.g.
   レのメリ → レ. It **begins a semitone higher than Tozan-ryū's スリ上げ** and has a muffled,
   distinctive atmosphere (くぐもった独特の雰囲気).
2. **A head-shake tracing the hiragana 「ん」**: down quickly first, back up to the middle more
   slowly, then one more quick nod down-and-up — which produces a characteristic **valley** in the
   sound. The glossary says to do it somewhat boldly.

And the regional difference, which is exactly the kind of thing the usual account asked for:
**「京都系のナヤシは公家風に艶っぽく、九州系のナヤシは野性味を帯びて荒々しく」** — Kyoto-line
nayashi is courtly and glossy; Kyūshū-line nayashi is wild and rough. **In 錦風流 Kinpū-ryū it is
called チギリ *chigiri*.** [V/trade — 幻海, ナ行]

**Measured distinction from suriage, which is the most useful empirical result in the literature I
read:** both show continuously **rising** pitch with a gradual power transition, but **in *suriage*
there is a drop in power between the preceding and the following note, while in *nayashi* there
essentially is not.** [V — Utsugi & Moriyama §2.3.1, verbatim 「スリ上げでは，音高変化の際，前音と
後音の間でパワーの減少が起こるのに対し，ナヤシでは，ほぼ起こらない」] This is also where their
classifier failed: 9 of 14 *suriage* instances were misread as *nayashi*, and the authors trace the
failure to **differences between the two players**, not to the technique. [V, §4.3] **That is a
quantified statement that the suriage/nayashi boundary is player-dependent — which is worth more
than any prose definition.**

- **息ナヤシ *iki-nayashi*** — a breath-based pitch inflection: **continuously alternating 乙 and 甲
  on the same fingering**, e.g. 二四五のハ played otsu-kan-otsu-kan. [V/trade — 幻海, ア行]
- **ツキ *tsuki*** — meri→kari, pushing the drawn-in chin lightly out; **also called 小ナヤシ
  *ko-nayashi*.** [V/trade — 幻海, タ行]
- **ネヤシ:** **I could not verify this term in any source I read. [U]** The 幻海 glossary's ナ行
  page carries only ナヤシ, ヌキテ, 音味 and 音色. **It is very likely a mis-transcription of ナヤシ**
  (ネ and ナ differ by one stroke in handwriting and are adjacent in romanisation), but I am
  flagging it rather than asserting that. **Do not define ネヤシ.**

#### スリ上げ *suri-age* / スリ下げ *suri-sage*, 摺り *suri*, and the slides

**ja.wikipedia's general statement:** performing the hole's closed → half-open → open motion
smoothly, **combined with meri/kari**, produces a smooth **portamento**, and this is called
スリアゲ / スリサゲ. [V — ja.wikipedia 尺八 §奏法, uncited]

**摺り / 擦り *suri* is the umbrella term** ("sliding the note"), subdivided into *suri-age* (up)
and *suri-sage* (down), and the trade glossary lists **five notated varieties**, which is the sort of
thing only a score-reader would know: ①スリの一 — slide the upper note a little and let it die away
lightly; ②スリの二 — slide and continue into the next note; ③メリ込みスリ上げ — from a *meri-komi*,
slide up sharply and die away; ④メリ込みスリ — from a *meri-komi*, slide and move to the next note,
or die away lightly; ⑤スリメル — from a *suri* or a *kari*, *meri-komi* into the next note or into
silence. [V/trade — 幻海, サ行]

**The mechanics are three alternative routes, not one:** *suri-age* can be done (a) by gradually
sliding the finger up off the hole, (b) by raising the chin from a meri, or (c) by both at once.
*suri-sage* is harder and **needs both**: the glossary's worked example is that to slide G down to F
you first drop the **chin** to near **Eb** and then slide **up** with the **finger**, so the note has
no corner on it (「音の角がたたない」). [V/trade — 幻海, サ行] **That is a counter-intuitive and very
concrete instruction — a descending slide executed by an overshoot downward in the chin and a
recovery upward in the finger — and it is exactly the sort of thing that vanishes in English
summaries.**

#### 押し *oshi*, オトシ *otoshi*, ケシ, and the other finger-repetition family

- **押し *oshi*** — see the finger attacks above: **pitch rises**, power spikes. [V — Utsugi &
  Moriyama]
- **オトシ / 落し *otoshi*** — **my two sources disagree and the disagreement is substantive.**
  - **Utsugi & Moriyama**: classed under **change in the instrument's angle**, and measured as
    「音高が連続的に減少する．パワーは，比較的小さく，音高の変化後急激に減少する」 — **pitch
    decreases continuously; power is comparatively small and drops sharply after the pitch
    change.** [V]
  - **幻海 glossary**: 「指を連打する技法のひとつ」 — **one of the finger-repetition techniques**,
    and not a plain repetition: like a drum roll, the intervals between strikes **progressively
    narrow**, growing louder then softer. [V/trade]
  - **These describe different physical events.** Either the two traditions use the name differently
    or one source is wrong. **Report both; do not merge them. [U] as to which applies where.**
  - The glossary's contrast term is useful either way: **刻み *kizami*** is the same repetition but
    at **constant tempo from the start**, "tapping out the rhythm matter-of-factly," without
    otoshi's dynamic shaping. [V/trade]
- **オドリ / オドル *odori*/*odoru*** — a finger-repetition technique, "similar to *momite* but not
  as precise as *momite*"; the glossary notes it is **also** the word for a beginner's fingers
  getting tangled when they cannot keep up. [V/trade] And: **what Tozan calls もみ手, other schools
  notate as オドル.** [V/trade — 幻海, マ行]
- **もみ手 *momite*** — alternately striking **two** holes rapidly; the worked example is holes 2 and
  3, giving the rhythm 「ツレーレツ・ツレーレツ」, with hole 2 **struck** and hole 3 **chopped
  (刻む)**. Equivalent to the Western **trill**. **Tozan-ryū's term.** [V/trade — 幻海, マ行; the
  trill equivalence is also in 幻海's トリル entry]
- **ケシ:** **I could not verify ケシ as a technique name in any source I read. [U]** The glossary
  has **切 *kiru*** — "stopping the note without leaving any after-ring" — and **韻 *in*** — "cutting
  the sound suddenly, or letting the after-ring be heard so as to give the listener the illusion
  that you are still blowing" [V/trade — 幻海, カ行 and ア行] — and its スリ and メリ込み entries
  repeatedly use the verb **消す** *kesu*, "to extinguish / let die away," as a score instruction
  (「軽く消す」, 「スリ上げて消す」). **My best reading is that ケシ is the nominal form of that
  verb — a notated "let it die away" — but I have no artefact that names ケシ as a term, and I am
  not going to assert it.** Flagged.

#### 込み吹き *komi-buki* — and it is school-specific

**Tsukitani lists コミ吹 among the three throat-and-breath special techniques** alongside タマネ and
ムラ息 [V — Nipponica], so it has general-vocabulary status. But the trade glossary gives it a
specific home and a specific story, and this is the best school-attribution I obtained for any
technique:

> 「奥州系の根笹派・錦風流で発達した吹奏技法。息で一定の間隔で切りつつ断続的に吹く。これは、
> 東北の風の強い地方を托鉢する虚無僧たちが風に負けずに音を出し続けるためにあみだした技法だと
> いわれている。」

— a blowing technique **developed in the Ōshū-line 根笹派錦風流 Nezasa-ha Kinpū-ryū**: the breath
is **interrupted at regular intervals**, blown discontinuously. It is **said** to have been devised
so that komusō begging in the windy Tōhoku region could keep producing sound against the wind. The
glossary offers an alternative explanation (people in that region simply liked repeated-note
sounds, as in Tsugaru-shamisen's 「ベンベンベンベン」), and reports that **two subtly different
manners are said to exist, a warrior-class one and a townsman one** — while flagging, honestly, that
Uchiyama Reigetsu's writing says only 「コミはそれぞれかなり異なる」 (komi differ considerably from
one another), so the difference may simply be between transmitters. [V/trade — 幻海, カ行; the
「いわれている」 hedges are the source's own, and the wind story should be reported as tradition, not
fact — **[U] as to origin**]

**チギリ / ツギリ / チキリ *chigiri*** is the other 錦風流 term: a technique close to head-shaking
or *nayashi*, **used together with komibuki**. [V/trade — 幻海, タ行]

#### 口メリ *kuchi-meri* — the technique that exists because of a hat

Lowering the pitch **using only the shape of the mouth and the delivery of the breath, without
moving the chin up or down.** The glossary's explanation of why: the komusō wore the 天蓋 *tengai*,
the deep woven basket hat, and if they had bobbed their chins on every meri **the hat would have
wobbled and looked absurd**, so this was devised instead. It is **little used today, but suits the
classical honkyoku better.** [V/trade — 幻海, カ行] **[U] as to the historical claim** — it is the
right shape for a retrospective rationalisation — **but the technique itself is a real and
important one**, because it is a meri that does *not* change the face-to-edge geometry, and
therefore ought to have a different timbre from a chin-meri at the same pitch. That prediction is
testable and I found no test. [U]

#### The 虚無僧吹き *komusō-buki* family — dynamic-envelope techniques

A set of techniques distinguished **purely by the shape of the loudness envelope over a single long
note**, all of which exclude vibrato. The glossary groups them explicitly:
「笹吹き・鼓吹き・棒吹き・くさび吹きなどがあり、これらをまとめて虚無僧吹きと総称する」. [V/trade —
幻海, ア行/カ行/サ行/タ行/ハ行]

| Term | Characters | Envelope | Image behind the name |
|---|---|---|---|
| くさび吹き | *kusabi-buki* 楔吹き | **loud → soft** | a **cuneiform wedge**, thick at the start, tapering |
| 笹吹き | *sasa-buki* | **soft → loud → soft** | the shape of a **bamboo-grass leaf** |
| 鼓吹き | *tsuzumi-buki* 鼓吹 | **strong → weak → strong** | the waist of a **tsuzumi drum** |
| 棒吹き | *bō-buki* 棒吹き | **flat throughout** | a **stick**; "magnificent but poor in feeling" |
| 虚吹き | *utsuro-buki* / *kyosui* 虚吹 | dead straight, **dim/hazy tone** | "empty blowing" |

[V/trade] The glossary names **神如道 Jin Nyodō** as having been outstandingly good at *tsuzumi-buki*
and says it was one of the reasons he was reckoned a master. [V/trade]

#### Other verified terms worth having

- **ハラロ *hararo*** — a characteristic figure in **Kinko-ryū and Myōan-line honkyoku**, executed
  with **chin meri/kari**, with several variants; the commonest moves **四五のハ(メリ) → 二四五のハ(カリ)
  → 四五のハ(メリ + hole-2 strike) → ロ**, which "sounds like *do–re, do, re*" in Western terms.
  [V/trade — 幻海, ハ行] **Utsugi & Moriyama describe its pitch contour differently**, as moving
  リ→ヒ→リ→ロ [V]. Both agree it is a four-event figure returning to ro; the fingerings named differ.
  **[U] as to which is standard.**
- **アメ *ame*** — fingers **fully open**, chin drawn **deeply** in: meri. [V/trade]
- **枝折 *edaore*** — "branch-snap": *meri-komi*-ing **quickly, as if a dry branch snapped off**; the
  glossary calls it one of the classical techniques. [V/trade]
- **抱 *kakae*** — meri-ing with the finger in *kazashi*; **明暗真法流's name for it.** [V/trade]
- **吟 *gin*** — **明暗真法流's "hand"**: *nayashi* upward, **only on エ (= チ).** [V/trade] Note the
  syllable **エ** — Myōan Shinpō-ryū uses the フホウエヤ series, not ロツレチ (§6.6).
- **ヌキテ *nukite* (抜き手)** — moving from a note to **the Myōan line's イ (which Kinko and Tozan
  call ヒ)** by opening hole 5 so the residual resonance "escapes out the back," giving a softer
  colour than simply opening the back hole. Close to *suriage*. [V/trade] **This contradicts
  ja.wikipedia's table, where イ is a *Kinko* fingering name and ヒ the Kinko upper-register C.
  Report the contradiction. [U]**
- **引 *hiki*** — lowering by a **semitone** from the previous note. [V/trade]
- **ハル *haru* (張る)** — synonymous with カル (*karu*, to kari). [V/trade] The glossary adds a
  pleasing etymology: the ordinary Japanese word **メリハリ** ("light and shade," modulation,
  contrast), written 乙張り, comes from the shakuhachi's distinction between meri and kari.
  **[U] — folk etymology is plausible here and widely repeated, but I did not verify it in a
  dictionary.**
- **吹き込み *fukikomi*** — blow in **strongly** from the point where the mark appears; at the **end**
  of a measure, blow in strongly and cut. **Common in Ōshū-line honkyoku.** At the **end of a
  piece** it is called **露切り *tsuyukiri*** and is blown "with a *bwah*" after the resonance has
  died — originally to blow the condensation out of the bore on the begging round. [V/trade]
- **露切 *tsuyukiri*** as a **closing formula**: originally the practical act, it became a fixed
  cadential phrase. The glossary gives the actual phrases: **Kinko-ryū 「レロー」; Kinpū-ryū
  「ツレー、ロ（チギリ）」.** [V/trade] **This is a tiny but concrete side-by-side of two schools'
  notated text for the same function and I have seen nothing like it in English.**
- **活殺 *ikekoroshi* / *kassatsu*** — in hōgaku performance generally, combining **opposite
  qualities** (loud/soft, high/low, fast/slow) contrastively. [V/trade]
- **気を取る *ki o toru*** — deliberately defeating the listener's prediction of the next note, with
  the glossary's own caution that overdoing it just produces incoherence. [V/trade]
- **倍音奏法 / ハーモニクス** — on a 1.8 shaku instrument with **all five holes closed**, sounding
  not the usual D but **the third harmonic, 甲 A**; the glossary claims shakuhachi and flute are
  the rare woodwinds able to control the third harmonic, and that this is a "back-door" technique
  usually frowned on. [V/trade; the "rare woodwinds" claim is **[U]**]
- **渡し物 *watashimono*** — transposing a piece from one 律 to another (e.g. 壱越律/D to 黄鐘律/A).
  **The glossary's point is the important one: this is not Western transposition, because moving the
  律 changes which notes require meri/kari, and therefore the melody and the technique change with
  it.** [V/trade] **This is the cleanest statement anywhere of why shakuhachi "keys" are not keys.**
- **五調子 *gochōshi*** — a set of five modes (本調子/大極調子/曙調子/雲井調子/夕暮調子, mapped by
  the glossary onto pre-Edo names 黄鐘調/盤渉調/一越調/平調子/双調). **根笹派錦風流 plays honkyoku
  in the five chōshi more actively than other schools, hence 「錦風流五調子」.** [V/trade; the
  glossary itself marks two of the five mappings 「要検証」, needs verification — **[U]**]
- **本手 *honte* / 破手 *hade*** — a classification of the classical honkyoku repertoire **by
  character**: *honte* are the training and ritual pieces (e.g. 『三虚霊』, 『調子』); *hade* are
  the descriptive/titled pieces (e.g. 『瀧落』, 『鹿の遠音』, 『鶴の巣籠』), also called **ヒルカラ**
  because only ceremonial pieces were permitted in the morning and these could be played only from
  the afternoon. [V/trade] **Relevant to §7: the repertoire itself is split by function, and the
  free-rhythm aesthetic is not evenly distributed across it.**

### 5.4 Terms I could not verify — flagged, not glossed

| Term | Status |
|---|---|
| **あたり / アタリ** | Not found in Tsukitani, Utsugi & Moriyama, or the nine-page 幻海 glossary. **[U] — no definition offered.** Likely a school-specific name for a finger attack, given that uchi is explicitly reported to have many school- and hole-specific names. |
| **ネヤシ** | Not found anywhere. **[U]** Probably a mis-transcription of ナヤシ. No definition offered. |
| **ケシ** | Not found as a term. The verb 消す appears repeatedly as a score instruction, and 切 and 韻 cover the "stop the note" territory. **[U]** No definition offered. |
| **大ユリ** | Not found. Tsukitani's triad is 縦/横/**斜**. **[U]** |
| **半音 as a technique name** | Not found. 半音 appears only in its ordinary sense, "semitone." The partial-cover vocabulary is 半開/四半開/4分の3開/4分の1開/かざし. **[U]** |
| **タバ音** | Term **[V/trade]**, mechanism **[U]** — the source itself says it does not know. |
| **斜ユリ, 手ユリ, 底ユリ** | Terms **[V]** / **[V/trade]**; physical descriptions **[U]** — listed by their sources without definition. |

### 5.5 Two conflicts the literature has not resolved

1. **オトシ** is a finger-repetition technique (trade glossary) or an instrument-angle technique with
   continuously falling pitch (measurement paper). **Unresolved.**
2. **玉音 / タマネ** is a throat technique (Tsukitani) or a tongue technique (Utsugi & Moriyama); the
   trade glossary says **both exist as separate techniques with different written forms** (玉音 =
   throat, タマ音 = tongue). **The trade glossary's distinction is the only account that makes both
   of the other two sources true at once, which is weak evidence in its favour, but it is a trade
   source and this is unresolved.**

Both conflicts are between sources I rate highly. **Report them; do not homogenise them.**

---

## 6. Notation — there is no single system, and that is the point

### 6.1 The shared basis

Every shakuhachi notation in current use is an **奏法譜 *sōhō-fu*, a "playing-method score"** — not a
pitch notation. Tsukitani's formulation is the one to use:

> 「記譜法は、指使いにつけられた名称を片仮名文字で表記する奏法譜。この文字を譜字(ふじ)といい…」

— the notation is a *playing-method score* that writes, in **katakana**, the **names given to the
fingerings**; these characters are called **譜字 *fuji*** ("score characters"). [V — Nipponica,
Tsukitani, my translation]

Kamisangō states the shared principle and the divergence in the same breath:

> 「尺八の楽譜は，流派により異なるが，記譜法の原理はすべて同一で，指法を示す片仮名の譜字（ロ，ツ，
> レ……など）を縦に書き連ね，それにリズムなどを表す補助記号を添えた奏法譜である。教習の際には
> 譜字の片仮名をそのまま発音し，旋律を声で歌って覚える方法がとられる。」

— shakuhachi scores **differ by school, but the principle of notation is identical in all of them**:
katakana *fuji* indicating the **fingering** (ro, tsu, re…) written **in a vertical column**, with
**auxiliary symbols appended to show rhythm and so on**. And: in instruction, **the katakana are
pronounced as they stand and the melody is learned by singing it with the voice.** [V — 平凡社世界大
百科事典, Kamisangō, my translation]

Three load-bearing consequences:

1. **The score names finger positions and actions, not pitches.** A 譜字 is the name of a fingering.
   What pitch comes out depends on the instrument's length, so **the same score played on a 1.6
   shaku instrument yields a different key with no change to the page** — the notation is
   transposition-neutral by construction. [V, inference from the 奏法譜 definition + the transposing
   family in §2.1]
2. **It is a tablature, which is why the notation can record the *route* to a pitch.** Everything in
   §3.4 and §3.5 — チメリ vs ウ for the same Ab, ツ vs レメリ for the same F — is sayable in this
   notation and unsayable on a staff.
3. **The 譜字 are also the syllables you sing.** This is **唱歌 *shōga*** (§8.3), and it is why the
   notation is katakana in the first place: 「邦楽器の楽譜にカナ文字が多いのも唱歌のため」 — the
   reason hōgaku scores are full of kana is *shōga*. [V/trade — 幻海 glossary, サ行]

Vertical, right-to-left reading: the column direction is **vertical** [V — Kamisangō, 「縦に書き
連ね」]. Right-to-left column order is **[U]** — it follows from ordinary Japanese vertical
typesetting and from the Kinko concertina format described in §6.5, but no source I read states it
of shakuhachi scores explicitly.

**The generic term for this notation family** is **孔名譜 *kōmei-fu*** ("hole-name score"), also
**管名譜 *kanmei-fu*** — the notation used for hōgaku wind instruments generally, including the
hichiriki and the ryūteki. The trade glossary makes a precise correction worth keeping: **for the
shakuhachi the characters are strictly not hole-names but fingering-names** —
「正確には尺八の場合は孔名ではなく、指遣いの『ロツレチハ（リ）、フホウエヤ』であらわす」.
[V/trade — 幻海 glossary, カ行]

### 6.2 The two historical systems: フホウ式 and ロツレ式

This is the fact most often missing from English accounts, and Tsukitani states it cleanly:

> 「この文字を譜字(ふじ)といい、『フホウ式』（旧譜）と『ロツレ式』（新譜）の2種がある。」

— there are **two kinds of 譜字: the フホウ式 *fuhō-shiki* (旧譜, the "old notation") and the
ロツレ式 *rotsure-shiki* (新譜, the "new notation")**. [V — Nipponica, Tsukitani]

| | **フホウ式 / フホウ譜** | **ロツレ式 / ロツレ譜** |
|---|---|---|
| Syllables | フ ホ ウ エ ヤ (イ) | ロ ツ レ チ リ/ハ |
| Earliest use | the **一節切 *hitoyogiri*** in the **17th century** | also used briefly for the *hitoyogiri* (小竹 *kotake*) |
| In fuke shakuhachi | the line of **尾崎真龍 Ozaki Shinryū (1820–1888)**; **明暗真法流 Myōan Shinpō-ryū**; **宗悦流 Sōetsu-ryū** — the last two now **defunct** | **established as the Kinko-ryū shakuhachi notation from the 18th century onward**, and so down to today |
| Surviving today | **only in 竹保流 Chikuho-ryū** | **almost all current notation** |

[V — Nipponica, Tsukitani, 「フホウ譜は17世紀に一節切で用いられ、普化尺八では尾崎真龍（1820―1888）
の系統、明暗真法流、宗悦流（ともに廃流）などで使用された。宗悦流の末流、竹保流にのみ現行される。
ロツレ譜は一節切（小竹(こたけ)）にも一時使われたが、18世紀以降琴古(きんこ)流尺八譜として定着し
今日に至る」; independently corroborated for Chikuho by ja.wikipedia 尺八 §竹保流]

The *hitoyogiri*'s own notation used **thirteen characters**: 「フホウエヤリヒ上神イタルチ」.
[V/trade — 幻海 glossary, ハ行] That is the ancestor of the フホウ series and shows it was a larger
set than the five-syllable core.

**Why this matters:** the ロツレチリ system that English writing treats as "shakuhachi notation" is
one of two historical systems, **it is the newer one**, and its dominance is a consequence of
Kinko-ryū's institutional success in Edo rather than of anything intrinsic. The fact that
**明暗真法流's own technique names use エ** — 吟 *gin* is defined as nayashi-up "only on エ (= チ)"
(§5.3) — is a live trace of the other system inside a school's technique vocabulary. [V/trade]

### 6.3 琴古流 Kinko notation

**What is verified:**

- **Established as the Kinko-ryū notation from the 18th century**; the first Kurosawa Kinko
  (1710–1771) 「これらの曲の譜字や習曲順の整理を行い」 — **put in order both the 譜字 and the order
  in which pieces are studied** — as part of fixing the 36-piece honkyoku canon. [V — Nipponica;
  ja.wikipedia 尺八 §琴古流本曲] **So the notation and the curriculum were systematised in the same
  act, by the same person.** That is a notable fact about what a "school" is.
- **No bar lines.** [V — jonkara.com, commercial; corroborated observationally by the 紫千会 blog
  below, which says Kinko notation has 「小節という概念がない」, no concept of a measure]
- **Rhythm, where indicated, is indicated by 間拍子 *mabyōshi* — dots placed beside the notes.**
  [V — jonkara.com, commercial] **間拍子 is a standard hōgaku term, not a Kinko coinage:** it is
  given as a synonym of 間 *ma* itself in the Heibonsha encyclopedia (「日本音楽の用語。間拍子とも
  いう。リズム，拍節，テンポなどを示す」). [V — 平凡社世界大百科事典, 「間」] So the Kinko rhythm
  mark is literally called "the *ma* beat."
- **Note durations are drawn as lines ABOVE the note** (Tozan draws them beside it). [V —
  jonkara.com, commercial]
- **Kinko notation is used for the classical repertoire.** [V — jonkara.com]

**One claim I flag as wrong or at best badly put:** jonkara.com states that in Kinko notation "all
pieces are effectively in 4/2 time." [V as a transcription of what the page says] **That is a
notation-software author's simplification and it contradicts the Japanese reference works, which
describe honkyoku as 自由リズム, free rhythm** (山川日本史小辞典: 「自由リズムの独奏曲を本曲、箏や
三味線と三曲で演奏される拍節的な曲を外曲とよぶ」 — free-rhythm solo pieces are *honkyoku*,
metrical pieces played in *sankyoku* with koto and shamisen are *gaikyoku*) [V]. A uniform 4/2 may
be a workable internal representation for an app handling *gaikyoku*; it is not a description of
Kinko honkyoku. **Do not repeat it.**

**Publishers.** Kinko-ryū 「は大小いくつもの組織の総体であり琴古流として統一した組織をもつもの
ではない」 — it is an aggregate of many organisations large and small and **has no unified Kinko-ryū
body**; the representative 会派 today are **鈴慕会 Reibokai, 童門会 Dōmonkai, 竹盟社 Chikumeisha,
竹友社 Chikuyūsha, 国際尺八研修館 (International Shakuhachi Training Centre)**. [V — ja.wikipedia
尺八 §琴古流, uncited] **Scores are published and sold by these 会派 themselves**: 竹友社 describes
itself as 「宗家竹友社‐琴古流尺八の楽譜販売・尺八教室」, "head-house Chikuyūsha — Kinko-ryū
shakuhachi score sales and shakuhachi classes," i.e. score publishing and teaching are the same
business [V — `chikuyusha.jp`, 2026-11-13, **commercial**], and 竹盟社 likewise publishes the
Yamaguchi Shirō / Yamaguchi Gorō Kinko koten-honkyoku editions [V — `chikumeisha.org`,
**commercial**]. **There is no single Kinko publisher, because there is no single Kinko.**

### 6.4 都山流 Tozan notation

Tozan-ryū was founded in **Osaka in 1896 by Nakao Tozan I**, with **no direct connection to the
Fuke sect**. [V — ja.wikipedia 尺八; Nipponica dates it 1896/明治29] The Japanese sources are
explicit that **notation was one of the things he deliberately re-engineered**:

> 「中尾は独自の工夫新作により自流の曲目を増やし、**記譜法**、教授法、合奏形式などにも新機軸を
> 打ち出し、近代的な家元制度を整えて短年月のうちに西日本で門弟を増やし」

— Nakao increased his school's repertoire with his own new compositions and **broke new ground in
notation, in teaching method, and in ensemble format**, while building a **modern iemoto system**,
rapidly increasing his pupils in western Japan. [V — ja.wikipedia 尺八, citing Kotobank 中尾都山,
my translation]

**How Tozan notation differs, verified:**

| | Kinko | Tozan |
|---|---|---|
| Bar lines 小節線 | **none** | **present** |
| 間拍子 dots | **yes** | **none** |
| Duration lines | drawn **above** the note | drawn **beside** the note |
| Meri marking | add メ / 中 | **reduce the glyph size** (§2.5) |
| Basis | Edo-period 奏法譜 lineage | **Kinko notation + Western staff notation** |
| Typical repertoire | classical | Meiji-and-later, folk song, newer pieces |

[V — jonkara.com, commercial, for the bar lines / mabyōshi / duration-line / basis rows; V —
ja.wikipedia 尺八's table for the meri-marking row]

**Why it is more explicitly metric: because the school's repertoire and pedagogy are different, and
because being readable without a teacher was the business model.** The clearest statement of this I
found is a first-hand observational comparison by a university traditional-instrument circle:

> **千葉大学和楽器サークル「紫千会」ブログ, 「いとたけ考 9月 ～都山と琴古の楽譜の考察～」,
> 2017-09-05** (`shisenkai.hatenadiary.com/entry/2017/09/05/000335`, read 2026-11-13).
> **Label: a student circle's blog — hobbyist, first-hand, not peer-reviewed.** Its value is that
> the author had **both scores of the same piece on the desk** and measured them.

The piece compared is the classical 大曲 **『尾上の松』 *Onoe no Matsu*,** about 20 minutes long.
Findings, all [V as that author's first-hand report, **[U]** as generalisations]:

| | Tozan edition | Kinko edition |
|---|---|---|
| **Physical format** | **B4** across an opening; **5 sheets of B5** for the whole piece | **A3 tall**, horizontally a **折り本 concertina-folded book at 9 cm per page**, **14 pages → ~126 cm when fully extended** |
| **Price** | **about ¥600** | **¥1,800** |
| **Tempo marks** | **yes** — e.g. 「徐」; and classical pieces have marked tempo changes, so the cues let you get through it at sight | not mentioned |
| **Sung text** | in **readable modern type** | usually on **page 1**, music from page 2; also on the score but in **old-form hiragana**, "honestly hard to read" |
| **Bar lines** | present → "simple and easy to read" | **no concept of a measure** |
| **The shamisen's line** | **omitted** where the shakuhachi part diverges — which the author regrets | printed **in thin small characters down the left** for the call-and-response passages, as a signpost |
| **Variant readings** | 手付 improved with its own independent motion, but **does not accommodate many 社中**; "especially not well suited to playing with Yamada-ryū" | **「或」 *aru*, "alternatively"** — a mark under which **a different 手付 is printed**, because transmission differs by lineage and teacher and the same piece differs partly by **社中** (studio); also 「或」 with 「1拍子」 written, because **how long a note is held differs by studio** |
| **Weaknesses** | lost ensemble information | no bar lines is "a bottleneck in ensemble rehearsal"; being old, some 手付 are "musically wrong (e.g. where the breaths fall)"; expensive; **many titles 在庫なし, out of stock — the author calls it a 「楽譜危機」, a score crisis** |
| **For 「間」** | — | "for grasping 「間」 I think the Kinko score is better" |

And the author's explanation of Tozan's Meiji expansion, which is the single most important sentence
about shakuhachi notation I read anywhere:

> 「明治期に都山流が一気に広まった理由として、この見やすい・わかりやすい楽譜が挙げられます。
> **わざわざ師匠に習わなくても、楽譜を見れば曲が吹ける。これは革命ですね。**」

— the reason Tozan-ryū spread all at once in the Meiji period was this easy-to-read, easy-to-follow
score. **You could play the piece by looking at the score without having to go to a teacher at all.
That was a revolution.** [V as that author's claim; the causal history is **[U]** but it is
consistent with the encyclopedias' account of Nakao's notation+pedagogy+iemoto package and with
Tozan becoming the largest organisation in the shakuhachi world]

**That is the "notation as a technology" thesis stated by a practitioner without having read Lee.**
The 「或」 mechanism is its exact mirror image: Kinko notation **prints the disagreement between
studios into the page**, including disagreement about *duration*; Tozan notation **resolves it** and
sells for a third of the price. Those are two different theories of what a score is for.

### 6.5 明暗 Myōan notation

**What is verified:**

- The Myōan styles are **not a single formalised school**: 「便宜的な総称として明暗流または明暗
  諸派と呼ばれている」 — "Myōan-ryū" or "the Myōan branches" is a **convenient collective name**
  for the diverse lines that kept transmitting classical honkyoku other than Kinko's after the Fuke
  sect's abolition, and they **lack the organisational strength of the modern schools**.
  [V — 平凡社世界大百科事典 and Nipponica, independently] Linder calls the same thing a generic label
  rather than a formalised style, "consisting of several sub-schools devoted to the meditative
  aspect of shakuhachi playing," and divides it into the **'old' Myōan style** (pieces from the
  Myōan temple in Kyoto) and the **明暗対山派 Myōan Taizan-ha** (pieces transmitted by **樋口対山
  Higuchi Taizan, 1856–1914**, "the second major compiler of honkyoku after Kurosawa Kinko I").
  [V — Linder 2017, p. 122, citing Tsukitani 2006, p. 103]
- **明暗真法流 Myōan Shinpō-ryū historically used the フホウ式 notation, and it is defunct.**
  [V — Nipponica]
- **明暗対山流 / 明暗対山派 is explicitly named by Tsukitani as one of the schools whose methods of
  notating derived pitches and note values differ from the others.** [V — Nipponica; see §6.6]
- Myōan-line **technique** vocabulary is partly its own: **鈴打ち** for the finger-strike, **鈴ゴロ**
  for karakara, **抱** for kazashi-meri, **吟**, **ホロホロ**, **ヒラヒラ**, **ヤラヤラ**,
  **ハズミ指**, and **イ** where Kinko/Tozan say **ヒ** (§5.3). [V/trade — 幻海 glossary]
- 対山譜 circulated as **manuscript**: a repair studio offering a facsimile describes its holding as
  「明暗対山の鈴木対山（樋口対山）の貴重な直筆の譜本」, a **precious autograph score-book in
  Taizan's own hand**, "probably the earliest surviving Taizan score," retaining older forms (虚空
  not yet split from 後虚空, 虚霊 still containing コロコロ). [V/trade — `shakuhachi-genkai.com/score/score01-02.html`,
  2026-11-13]

**What I could NOT verify, and it is a real hole: how Myōan notation marks duration, what its
auxiliary symbols are, and how it differs on the page from Kinko's.** No source I reached describes
the mechanics. **[U]** The right targets are Tsukitani 2000/2006 and the Taizan-ha and Icchōken
school materials.

### 6.6 How many systems, really

Tsukitani's closing sentence on notation is the one to quote whenever someone says "shakuhachi
notation":

> 「現行譜のほとんどがロツレ式だが、**派生音や音価表記の方法は根笹派錦風流、西園流、明暗対山流
> （または明暗対山派）、都山流、上田流など、各流とも異なり、指法も微妙な差があって複雑である。**」

— almost all current scores are ロツレ式, **but the methods of notating the derived pitches and the
note values differ in every school — Nezasa-ha Kinpū-ryū, Seien-ryū, Myōan Taizan-ryū, Tozan-ryū,
Ueda-ryū and others — and the fingerings too differ subtly, making it complex.** [V — Nipponica,
Tsukitani, my translation]

So the real inventory is: **one principle (katakana fingering-tablature in a vertical column with
auxiliary marks), two syllable families (フホウ / ロツレ), and as many duration-and-accidental
conventions as there are schools.** Named in the sources: 琴古流, 都山流, 上田流, 竹保流,
根笹派錦風流, 西園流, 明暗対山流 — seven, and Tsukitani's 「など」 means that is not a closed list.

**Ueda-ryū is the instructive failure.** Founded 1917 by Ueda Hōdō after expulsion from Tozan, it
**introduced Western staff notation and the 7-hole instrument** in the name of modernising the
shakuhachi — and **「五線譜の採用は途中で断念した」, the adoption of staff notation was abandoned
part way, while the 7-hole instrument survived and is still used.** [V — ja.wikipedia 尺八 §上田流,
uncited] **A school tried replacing the tablature with staves, inside the tradition, with
institutional backing, and gave up — while the hardware change it introduced at the same time
stuck.** That is a much better argument about what the tablature is doing than any aesthetic claim.

### 6.7 Western staff notation: when it is used, and what it loses

**Verified uses:**

- **Within the tradition, as an attempted replacement: tried and abandoned** (Ueda-ryū, above). [V]
- **As a design input, not a replacement: Tozan notation is described as based on Kinko notation
  *and* Western staff notation** — i.e. staff notation's contribution was the metric apparatus (bar
  lines, explicit durations) imported into the tablature, not the staff itself. [V — jonkara.com,
  commercial]
- **From outside, by composers.** Contemporary composition for shakuhachi from the 1960s is
  substantial and staff-based: Takemitsu's *Eclipse* and *November Steps* (1967, for Yokoyama
  Katsuya and the biwa player Tsuruta Kinshi, premiered by the New York Philharmonic in 1967 after
  being commissioned in 1964), Hirose Ryōhei's shakuhachi concerto, Fujikura Dai's shakuhachi
  concerto. [V — ja.wikipedia 尺八 §現代音楽と尺八, which carries a 節スタブ stub banner; the 1964
  commission / NY Phil detail is from the article's second 現代音楽 section]
- **An entire body of scholarship exists on notating shakuhachi for Western composers** and I did
  not read it: **Lependorf, "Contemporary Notation for the Shakuhachi: A Primer for Composers,"
  *Perspectives of New Music* 27/2 (1989), DOI 10.2307/833414**, plus Cronin, "On Writing for
  Shakuhachi: A Western Perspective," Samuelson, "Shakuhachi and the American Composer," Denyer,
  and Benítez, all in *Flute and Shakuhachi* (Routledge, 2020, DOI 10.4324/9781315077192).
  [V — Crossref metadata only; **not read**] Regan 2006 independently names Lependorf as the thing
  to read, "packed with informative, detailed information about shakuhachi techniques and approaches
  to notation." [V — Regan 2006]

**What staff notation loses, argued from the verified structure of the tablature rather than
asserted:**

1. **The route to the pitch.** A staff says Ab; the tablature says **チメリ or ウ**, which are
   different sounds (§3.4–3.5). Likewise F: **ツ or レメリ**. A staff cannot express the choice; a
   staff plus fingering annotations is the tablature re-imported. [V for the alternative spellings;
   argument mine]
2. **Transposition-neutrality.** The tablature is length-independent (§6.1); staff notation fixes
   concert pitch and so forces a decision the tablature does not have to make. And **渡し物
   *watashimono*** shows the stakes: moving a piece to another 律 is *not* Western transposition,
   because which notes need meri/kari changes, so **the melody and the technique change with the
   transposition** — a staff transposition would silently misrepresent the result. [V/trade for
   watashimono; argument mine]
3. **The named techniques.** There is no staff symbol for *nayashi*-as-opposed-to-*suriage*, for
   *korokoro* vs *karakara* vs *horohoro* vs *hirahira* vs *yarayara*, for the five grades of *suri*
   or the five of *meri-komi*, or for *kuchi-meri* as opposed to chin-meri. Staff notation of these
   is always a legend plus symbols invented for the occasion — which is exactly what the Lependorf
   literature exists to standardise. [V for the vocabulary; argument mine]
4. **Studio-level disagreement.** Kinko's 「或」 prints alternative readings **including alternative
   durations**; a staff score has nowhere to put them without becoming a critical edition. [V for
   「或」, 紫千会; argument mine]

**On the status of honkyoku in staff notation:** I did not find a source that states in so many
words that staff-notated honkyoku is a transcription rather than a score. **[U]** But the
components of the argument are each verified: honkyoku is **自由リズム**, free rhythm [V — 山川];
honkyoku notation does not fix duration (§6.8); Kinko notation deliberately records that durations
differ by studio [V — 紫千会]; and one measured study found the suriage/nayashi distinction to be
**player-dependent** [V — Utsugi & Moriyama §4.3]. **A staff rendering must therefore resolve
choices the source notation leaves open, which makes it a record of one performance rather than the
piece's text.** The argument is mine; the premises are sourced.

### 6.8 The honkyoku rhythm problem

This is the part usually hand-waved, so here is what is actually established, in order of
evidential strength.

**(a) The repertoire is formally divided by whether it has metre at all.** 「自由リズムの独奏曲を
本曲、箏や三味線と三曲で演奏される**拍節的**な曲を外曲とよぶ」 — **free-rhythm** solo pieces are
*honkyoku*; **metrical** pieces played with koto and shamisen in *sankyoku* are *gaikyoku*.
[V — 山川日本史小辞典] This is a definitional statement in a reference work, not an aesthetic one.

**(b) The notation does not carry what you need to play it, and this is stated as a technical
problem by engineers who needed the data.** Utsugi & Moriyama open their paper with it:

> 「日本の伝統音楽の楽譜の多くには、楽曲を演奏するために必要な**奏法についての情報が無いもの**が
> 多い。その上、演奏そのものがとても繊細なもののため、熟練した奏者でなければ、楽曲音源の中から
> 全ての奏法を識別することは難しい。故に、**初心者がそれら二つの情報から、独学で楽曲を演奏する
> ことはほぼ不可能だと言える**。実際には、初心者は、**師範から口承で演奏法を伝承される形**をとって
> おり、演奏法は**不文的に継承されている**。」

— many Japanese traditional scores **lack the information about playing technique needed to perform
the piece**. On top of that the playing is so delicate that only a trained player can identify all
the techniques from a recording. Therefore **it is close to impossible for a beginner to play a
piece by self-study from those two sources** (score and recording). In practice the beginner
**receives the playing method orally from a *shihan*, and the playing method is transmitted
unwritten**. [V — Utsugi & Moriyama 2009 §1, my translation] **That is the honkyoku-transmission
claim made as a premise in a peer-reviewed engineering paper whose entire motivation is that the
information is not on the page.** It is better evidence than an aesthetic essay, because the authors
need it to be true in order to justify their project — and their project is to *recover* the missing
information from audio.

**(c) The notation does record duration — partially, inconsistently, and with the disagreement
printed.** This is the nuance that gets lost when the point is made too strongly:

- Kamisangō says auxiliary symbols for **rhythm** are part of the shared principle: 「それに
  リズムなどを表す補助記号を添えた」. [V] So it is **not** true that honkyoku notation has no
  rhythmic apparatus at all.
- Kinko's apparatus is **間拍子 dots** and **duration lines above the note**. [V — jonkara.com]
- But Kinko notation has **no bar lines and no concept of a measure** [V — 紫千会], and it
  **explicitly prints 「或」 variants that include how long a note is held** (「『或』の下に1拍子と
  書いてある…社中によって延ばす長さが違うことがあるためです」 — under 「或」 it says "one beat,"
  because the length held differs by studio). [V — 紫千会]
- Tsukitani's statement that 音価表記 — **note-value notation** — differs in every school [V] means
  there is no cross-school standard for what a duration mark means.

**So the accurate formulation is: the notation fixes the sequence of actions and partially
constrains their durations, by means that differ per school and per studio, and it prints its own
known variants. What it does not fix is the realisation.** [Synthesis mine from the above, each
premise V]

**(d) How this works pedagogically.** Three verified mechanisms:

1. **唱歌 *shōga*.** The teacher and student **sing the 譜字 aloud**, and 「教習の際には譜字の
   片仮名をそのまま発音し、旋律を声で歌って覚える方法がとられる」 — in instruction, the katakana are
   pronounced as written and the melody is **memorised by singing it with the voice**. [V — 平凡社,
   Kamisangō] The trade glossary adds that *shōga* conveys 「曲調や強弱などの微妙なニュアンス」 —
   subtle nuances of character and dynamics — through **timbre**, that it is used for 練習・暗譜・
   伝承 (practice, memorisation and transmission), that the koto/shamisen equivalent is called
   **口三味線 *kuchi-jamisen***, and that **a ハリセン** — a leather-wrapped fan-shaped clapper —
   **is often used to beat the rhythm during shōga.** [V/trade — 幻海, サ行 and ハ行] **So the
   duration information is carried in a sung-and-clapped performance of the notation, by a human,
   in the room.** That is the mechanism, stated concretely, and it is not mystical.
2. **The teacher's live model.** Utsugi & Moriyama's 「師範から口承で」 (above) [V]; and the whole
   licensing apparatus of §8 presupposes face-to-face transmission.
3. **The score as a mnemonic for something already heard.** The 紫千会 author's remark that the
   Tozan score was revolutionary **because you could play from it without a teacher** [V] is the
   negative image of this: the Kinko score is not designed to be sufficient.

**(e) A concrete illustration from inside a lineage.** A parallel strand on this project reports,
verified, that in the Watazumi/Yokoyama line ("Dokyoku" in English) the practical transmission before
its printed score volumes **ran on one teacher's handwritten scores, photocopied and circulated with
a warning that they contained errors** — and that its printed volumes are issued **in 琴古 notation**,
with Tozan available on request, applicants being asked which they read. [V — reported to me by the
parallel strand holding that scope, 2026-11-13; I did not verify it myself and **defer the detail
to them**.] **Even inside a single lineage, the authoritative text was a hand copy known to be
faulty — and when it was printed, it was printed in another school's notation.**

**(f) What I could not do.** **The canonical scholarly treatment is Riley Lee's and I did not read
it** — "Shakuhachi honkyoku notation: written sources in an oral tradition," *Musica Asiatica* 6
(1991): 18–35, DOI 10.1017/cbo9780511896071.003, with its companion "Fu Ho U vs. Do Re Mi: The
Technology of Notation Systems and Implications of Change in the Shakuhachi Tradition of Japan,"
*Asian Music* 19/2 (1988), DOI 10.2307/833867. [V — Crossref metadata; **both paywalled, neither
read**] Lee is both a scholar and a Yokoyama student, so he is inside the tradition he analyses.
**Everything in §6.8 is independent of him, which also means it has not been checked against him.**

**(g) A published side-by-side of the same piece in two notations.** The closest I found is the
紫千会 comparison of 『尾上の松』 in Kinko and Tozan editions (§6.4) — **first-hand but a student
blog, and a *gaikyoku*, not a honkyoku.** I found no published side-by-side of a **honkyoku** in two
notations. **[U — this remains the gold and it is still unmined.** The obvious candidates are
『鹿の遠音』 or 『巣鶴鈴慕』, which exist in multiple schools' editions; Tsukitani 2000 is the likely
place for a scholarly juxtaposition.]

---

## 7. 間 *ma*, the one-breath phrase, and the relation of notation to breath

### 7.1 間 *ma* — what the Japanese reference works actually say

The English literature treats *ma* as an untranslatable aesthetic mystery. The Japanese
encyclopedias treat it as **a technical term with three concrete senses**, and give it the synonym
**間拍子 *mabyōshi*** — the same word that names the Kinko rhythm dots (§6.3). [V — 平凡社世界大
百科事典, 「間」, fetched 2026-11-13]

**平凡社 改訂新版 世界大百科事典, 「間」** — 「日本音楽の用語。間拍子ともいう。リズム，拍節，
テンポなどを示す」, a term of Japanese music, also called *mabyōshi*, indicating rhythm, metre and
tempo, with three senses: [V, my translation]

1. **リズム rhythm.** Literally "between sound and sound"; in hōgaku instruments with a percussive
   character, **how the subtle stretching and shrinking of the intervals is managed is what counts**
   (「間隔の微妙な伸縮の取り方が重視される」). Good and bad rhythmic sense are expressed as
   **「間がよい」/「間が悪い」**, "the ma is good / the ma is bad." In *yōkyoku* there are even
   **named ma** — 半声の間, 本間, ヤの間, ヤアの間 — for the blanks arising before each line when
   irregular line-lengths are fitted into the eight-beat frame.
2. **拍節 metre.** In 近世邦楽 the basic 1拍子 (= 2 beats) has a **表間 *omote-ma*** (first beat) and
   **裏間 *ura-ma*** (second beat).
3. **テンポ tempo.** 地歌箏曲 distinguishes **小間 *koma*** from **大間 *ōma*** (slow, each *koma*
   beat doubled); fast is **早間 *hayama*** — whence 「早間小唄」.

**So *ma* is, in its primary technical usage, the hōgaku word for rhythm/metre/tempo — the thing a
Western musician would call "time."** Any account that presents *ma* as purely "the silence between
sounds" has taken one sense of a three-sense technical term and dropped the other two.

**And the aesthetic sense is also real, and is also attested in a reference work**, not only in
popular writing. Nipponica's 「間」 entry:

> 「西洋のリズムは音や動作を伴う拍子そのものが耳に響くが、日本の間は拍子と拍子のあいだの**空白を
> 意識する**違いがある。**この空白はからっぽの空ではなく、次の拍子への緊張感を充実させた空である。**
> つまり微妙に伸縮する時間の空白が間であり」

— in Western rhythm the beat itself, carried by sound or motion, is what sounds in the ear; Japanese
*ma* differs in that **the blank between beat and beat is what is attended to**. **That blank is not
an empty emptiness; it is an emptiness filled out with tension toward the next beat.** *Ma* is
therefore the subtly stretching and shrinking blank of time. [V — Nipponica, 「間」, my translation]

The same entry grounds this in a primary Edo source rather than in assertion: 『南方録』 says that
in musical metre "coinciding is good, but *hitting* the beat is unskilful," citing the gagaku
dancer's 峯すりの足 — the secret being that the peak of the dance step should **not** land on the
peak of the beat-stroke but be displaced by a hair.
「どうやら日本の間にはリズムやタイミングのずれを喜ぶ不規則性が加味されている」 — Japanese *ma*
seems to have built into it an irregularity that **takes pleasure in displacement of rhythm and
timing.** [V — Nipponica, 「間」]

Heibonsha's companion essay on 間 adds, from Zeami: in Noh music 「演奏の焦点はむしろ休拍の置き方に
あって、いかに〈間を数える〉かということが、技術の最高の秘伝とされている」 — the focus of
performance lies rather in the placing of the rests, and **how to "count the ma" is held to be the
highest secret of technique**; in early-modern dance, 「いかに〈間を抜く〉か」, how to *omit* the ma,
is the point of the art, because riding the beat too well is disliked; and Zeami's 〈せぬひま〉, the
"interval of not-doing," must be made interesting. [V — 平凡社世界大百科事典, 「間」 essay, my
translation] **Note that these are Noh and dance, not shakuhachi** — I found **no** shakuhachi-specific
treatment of *ma* in a reference work. **[U] for the application to shakuhachi**; the
transferability is the standard assumption in hōgaku writing and the 紫千会 author makes it
casually ("for grasping 「間」 the Kinko score is better") [V as their claim].

### 7.2 一息 the one-breath phrase as the structural unit

**What is verified:**

- **Honkyoku is 自由リズム, free rhythm, and solo** (斉奏 in unison is also permitted).
  [V — 山川日本史小辞典; Nipponica: 「すべて独奏曲（斉奏も可）」]
- **The breath is a constraint the player works around, and the tradition has a name for breaking
  it: 息継ぎ / 息盗み *iki-nusumi*, "breath-stealing"** — the Western *cunning breath*. Defined as
  what you do when, somewhere other than at a composer's indication or a break in the piece, 「どう
  しても一息では吹ききれず息を吸わなければいけない場合がある」 — **you simply cannot blow it to the
  end on one breath and must take air** — and you then breathe **concealed**. The trade glossary's
  caution is the interesting part: you may not steal a breath just anywhere; you must understand the
  piece and the melody thoroughly and take care **not to destroy their atmosphere**. [V/trade — 幻海
  glossary, ア行, my translation] **A technique exists specifically for failing to complete a phrase
  on one breath, and it is governed by a rule about phrase integrity. That is strong indirect
  evidence that the one-breath phrase is the normative unit.**
- **Slur marks are read as breath instructions.** The glossary's スラー entry: for strings a slur
  shows one bow-stroke, but for winds and voice 「一息で奏するつもりでおこなう」 — you take it as
  *intending to play it on one breath* — and therefore **the break between two slurs is to be made
  audible by changing the breath or cutting it.** [V/trade — 幻海, サ行] So in a shakuhachi score the
  phrase mark **is** the breath mark, and **the articulation of the piece is the articulation of the
  breathing.**
- **A phrase-end formula exists and is literally about breath: 露切り *tsuyukiri*** — the closing
  blow-through, originally to clear condensation from the bore, which became a fixed cadential
  phrase (Kinko 「レロー」, Kinpū-ryū 「ツレー、ロ（チギリ）」); at the very end of a piece it is
  blown **after the resonance has died away**. [V/trade — 幻海, ハ行 and タ行]
- **And a whole family of techniques is defined by the loudness shape of a single long note** — the
  虚無僧吹き set in §5.3 (wedge, bamboo-leaf, drum, stick). **These are only definable if the single
  sustained breath is the unit being shaped.** [V/trade; the inference is mine]

**What is NOT verified:** I found **no** source stating in so many words that the one-breath phrase
is the structural unit of honkyoku, and no measurement of honkyoku phrase lengths. **[U]** The
inference above is mine, built on verified pieces. Simon 2017 analyses *Sōkaku Reibo* in terms of
**"pitch and rhythm cells"** and smaller motivic elements rather than breath-phrases [V — Simon
2017, p. 1], so the one published analytical study I read **does not use the breath-phrase as its
unit** — which is worth knowing before asserting that it is the unit.

### 7.3 How notation, breath and phrase hold together

Putting §6.8 and §7.2 side by side, the system is coherent and not mysterious:

| Layer | What fixes it | Evidence |
|---|---|---|
| **Which actions, in which order** | the 譜字 column — fully determined by the page | V — Kamisangō, Tsukitani |
| **Which of several routes to a pitch** | the 譜字 choice (チメリ vs ウ) — on the page | V — ja.wikipedia table |
| **Approximate durations** | auxiliary marks (間拍子 dots, duration lines) — on the page, **but school-specific and sometimes printed as alternatives** | V — Kamisangō, jonkara, 紫千会 |
| **Actual durations and the placing of the blanks** | **間 — realised in performance, learned by 唱歌 and by the teacher's live model** | V — 平凡社/Nipponica 「間」; V — Kamisangō on shōga; V — Utsugi & Moriyama on oral transmission |
| **Where the phrase ends** | **the breath** — slurs read as one-breath units, with *iki-nusumi* as the licensed exception | V/trade — 幻海 |

**The piece is not "missing" its rhythm. Its rhythm is located in a different place: in a sung,
clapped, embodied model that the notation indexes rather than encodes.** The engineers' sentence is
the proof of the arrangement from the outside — self-study from score plus recording is "close to
impossible" [V] — and the Tozan reform is the proof from the inside: when a school decided the score
*should* be sufficient, it had to add bar lines, explicit durations and tempo marks, and it also had
to **throw away** the 「或」 variants and the shamisen cue-line to do it. [V — jonkara, 紫千会]

---

## 8. How it is taught

### 8.1 The Edo-period arrangement, briefly, because it explains the rest

**Before 1871 there were no *ryūha* in the modern sense.** Tsukitani: 「虚無僧の修行として尺八が
吹かれた江戸時代には、普化宗寺院の尺八指南役（**吹合(ふきあわせ)**）によって教授され、**流派の
ような組織は存在しなかった**」 — in the Edo period, when the shakuhachi was blown as komusō
practice, it was taught by the **fukiawase**, the shakuhachi instructors of the Fuke-sect temples,
and **no organisation of the kind a school is existed**. 「**家元組織としての流が確立するのは普化宗
廃止（1871）後**で、1896年に都山流、1917年に上田流と竹保流の近代流派が誕生」 — the *ryū* as an
**iemoto organisation** was established only **after** the Fuke sect's abolition in 1871, with
Tozan-ryū in 1896 and Ueda-ryū and Chikuho-ryū in 1917. [V — Nipponica, my translation]

Kurosawa Kinko I was one such fukiawase in Edo. [V — Nipponica, 「江戸の吹合として活躍した黒沢琴古」]
And Linder adds the institutional detail that matters: **the Kinko line was given special permission
to set up 吹合所 *fukiawase-jo*, studios for teaching the shakuhachi to lay people, in Edo** — which
"led to the spread of shakuhachi in the developing urban culture of the Edo period." [V — Linder
2017, p. 123, citing Tsukitani 2006 p. 48 and his own dissertation p. 125]

**So the licensing economy is a Meiji-and-later institution laid over an older teacher-to-pupil
arrangement, not an ancient feature of the tradition.** Anyone who presents the ranks as
centuries-old is wrong.

### 8.2 都山流 Tozan-ryū: the examination ladder, verified from the school itself

Source: **公益財団法人 都山流尺八楽会 (Tozan-ryū Shakuhachi Gakkai, a Japanese public-interest
incorporated foundation), `tozanryu.com/about-tozanryu/shikaku/` and `/member/license/`, fetched
2026-11-13.** [V — the school's own authoritative self-description; **it is authoritative about its
own system and about nothing else.**]

**The governing fact:** 「都山流の免状・免許状は、すべて都山流宗家より直接付与されます」 — all Tozan
certificates and licences are granted **directly by the Tozan 宗家 (sōke, head house)**. [V]

| Step | Name | How obtained |
|---|---|---|
| 1 | **初伝免状** *shoden* | taught by a certified 師匠; the teacher files the application with the sōke |
| 2 | **中伝免状** *chūden* | as above |
| 3 | **奥伝免状** *okuden* | as above |
| 4 | **皆伝免許状** *kaiden* — note 免許状, a *licence*, not 免状, a *certificate* | after okuden |
| 5 | **准師範** *junshihan* | requires kaiden **plus passing the 准師範検定試験**, the junshihan examination |
| 6 | **師範** *shihan* | requires passing the **師範検定試験**, which may be sat only **once more than 3 years have passed** since passing the junshihan exam |
| 7 | **大師範** *daishihan* | granted to shihan holders who have been **especially active** — i.e. by recognition, not examination |

[V — all seven, tozanryu.com/about-tozanryu/shikaku/]

**Teaching rights are a separate axis.** A **指南免許状 *shinan* licence** — or any licence at
junshihan or above — **plus filing a 指南開始届, a notice of commencement of teaching**, makes a
person a **師匠 *shishō*,** a teacher entitled to present students for certification. There is also
a **推薦制度, a recommendation system**, under which a shishō can recommend someone for 指南, 准師範
or 師範. [V — same]

**Name-granting (雅号 *gagō*), and the shakuhachi version is specific:**

- **竹号 *chikugō*** ("bamboo name") — granted **by the teacher** to those who complete **中伝**. [V]
- **山号 *sangō*** ("mountain name") — granted to those who obtain the **師範** licence. [V]

**Note that these are not called 名取 *natori*.** 名取 is a widely used term in Japanese performing
arts for the stage-name grant, but **I did not find it used in any shakuhachi source I read** —
Tozan says 竹号/山号, and the trade glossary's nine kana-row pages do not carry 名取. **[U] for 名取
in a shakuhachi context; say 竹号/山号 instead.** The 「-山」 element in Tozan names (都山, 対山,
鯛山) and the 「竹-」/「-竹」 element elsewhere (竹保, 竹禅, 虚竹) are the visible result of exactly
this system.

**Counts, since the usual account asked for real numbers: seven grades on the main ladder, plus 指南 as a
parallel teaching licence; one examination to enter 准師範 and one to enter 師範; a hard 3-year
minimum between them; 大師範 by recognition with no stated criterion beyond "especially active."**
[V] **I found no published figure for how many holders of each rank exist. [U]**

Tozan's organisational history is relevant to how any of this is administered: it introduced a
**評議員制 (board-of-councillors system)** and built a **centralised** organisation, became the
largest body in the shakuhachi world, and then **split around 1975 (昭和50年前後) into three — 都山流
尺八楽会, 日本尺八連盟, and 新都山流.** [V — ja.wikipedia 尺八 §都山流, uncited for the split date]
**So "the Tozan rank system" is in fact at least three parallel rank systems.**

### 8.3 琴古流 Kinko-ryū: no single system, because no single school

**The structural fact first:** 「琴古流は大小いくつもの組織の総体であり**琴古流として統一した組織
をもつものではない**」 — Kinko-ryū is an aggregate of organisations and **has no unified Kinko-ryū
body**; the representative 会派 are 鈴慕会, 童門会, 竹盟社, 竹友社, 国際尺八研修館. [V —
ja.wikipedia 尺八 §琴古流, uncited] **There is therefore no "the Kinko licensing system." Each 会派
runs its own.** Two, read directly:

**竹盟社 Chikumeisha** (the Yamaguchi line; HQ in Nakano, Tokyo; chief shakuhachi instructor
松山龍盟 Matsuyama Ryūmei; branches nationwide each run by qualified 師範).
[V — `chikumeisha.org/lesson.html`, 2026-11-13, **commercial**]

| Tier | Monthly fee 月謝 |
|---|---|
| 初伝 *shoden* | ¥10,000 |
| 中伝 *chūden* | ¥12,000 |
| 奥伝・準師範 *okuden / junshihan* | ¥15,000 |
| **本曲 *honkyoku*** | **¥20,000** |

Entrance fee 入門料 ¥10,000; private intensive 詰稽古 ¥10,000/hour; lessons about 4×/month, mainly
Mondays (09:00–21:00) and Fridays (13:00–21:00); **free 30-minute trial lesson, instrument provided
if you have none.** [V — same]

**Read that table again: *honkyoku* is the top tier and the most expensive.** The classical solo
repertoire — the material the English literature treats as the essence of the instrument — is in
this school's economy **the last thing you are taught and the thing you pay most for.** That is a
concrete, verifiable fact about the pedagogy and it is the opposite of the impression an English
reader gets.

**竹友社 Chikuyūsha** (「宗家竹友社」, head-house Chikuyūsha; score sales and classes in one
business). [V — `chikuyusha.jp/join.html`, 2026-11-13, **commercial**] Entrance fee ¥10,000; monthly
fee **¥3,000–15,000, "determined case by case according to the day, the teacher, and whether the
pieces are 初伝～皆伝 level"**; 4 lessons/month as standard, no lesson in a fifth week; free trial
lesson. **Membership of 全国竹友会 (the national Chikuyū association) becomes available on completing
初伝級**, and it is possible to take lessons **without joining at all**. Teachers with a teaching
qualification are called **開軒師範 *kaiken shihan*.** The page gives **no** list of 免状 types, no
名取/竹号 system, and no stated order of pieces. [V — including the absences]

**So the same rank names — 初伝・中伝・奥伝・皆伝・準師範・師範 — recur in Kinko 会派 and in Tozan,
but the apparatus around them differs:** Tozan centralises issuance in the sōke and gates two steps
behind formal examinations with a statutory interval; the Kinko 会派 run them as **fee tiers in a
studio**, with membership optional in at least one case. [V, comparison mine] Whether any Kinko
会派 holds formal examinations is **[U]** — neither page I read mentions one.

### 8.4 A school with no ranks at all

The Watazumi/Yokoyama line's institution has **no grading or licensing of any kind — no 師範, no
免状, no 段, no 名取 — its senior teachers being titled 常任講師, "resident instructors," with a
public competition substituted for certification.** [V — reported to me by the parallel strand
holding the Dokyoku scope, 2026-11-13; I did not verify it myself and **defer the detail to them**.]

**This matters out of proportion to its length: it shows that the licensing economy is a
school-by-school choice, not a property of Japanese traditional music.** The standard English
sentence "Japanese traditional arts transmit through the iemoto system" is false as a
generalisation about the shakuhachi, in two directions at once — the ranks postdate 1871 (§8.1), and
at least one major contemporary lineage has none.

Note also that Linder's own typology of shakuhachi lineages is **by repertoire transmitted, not by
rank structure**: (1) lineages transmitting only or mainly the komusō pieces (the Myōan styles,
Watazumi-dō); (2) lineages transmitting both honkyoku and the ensemble/modern repertoire (Kinko-ryū,
the Yokoyama style, Chikuho-ryū); (3) Meiji-founded lineages transmitting ensemble pieces plus solos
composed within the lineage (Tozan-ryū and its kin). [V — Linder 2017, pp. 120–121] **And the word
*honkyoku* itself is school-relative: type (1) and (2) lineages' pieces are 古典本曲 *koten
honkyoku*, while type (3) lineages' newly composed pieces are "the honkyoku of such-and-such a
lineage" — e.g. 都山流本曲, composed by Nakao Tozan in the late 19th century.** [V — Linder 2017,
p. 120, citing Tsukitani 2006 pp. 13–14 and Kamisangō (1974) in Blasdel 2008]

### 8.5 Rote, imitation and the live model

- **The score is indexed to a sung model, not read silently.** 唱歌 *shōga*: the katakana are
  pronounced as written and the melody is **memorised by singing** [V — 平凡社, Kamisangō]; *shōga*
  conveys character and dynamics through the voice's own timbre, is used for **practice,
  memorisation and transmission**, has the string-instrument counterpart **口三味線**, and is often
  accompanied by a **ハリセン** clapper beating the rhythm [V/trade — 幻海].
- **The playing method is transmitted orally and unwritten**, 「師範から口承で」, and self-study from
  score plus recording is "close to impossible" [V — Utsugi & Moriyama 2009 §1].
- **Studio-level variance is institutionalised rather than suppressed**: the Kinko 「或」 mechanism
  prints alternative 手付 and alternative held-lengths because transmission differs by lineage,
  teacher and 社中 [V — 紫千会].
- **And there is a documented case of a lineage running on photocopied handwritten scores known to
  contain errors** [V — parallel strand, §6.8(e)].

**What this is not:** it is not evidence that the transmission is ineffable. Utsugi & Moriyama's
result — eight techniques classifiable from audio alone at 82%, with the single failure mode being
**player-dependence** in the suriage/nayashi distinction [V] — says the content being transmitted is
largely objectifiable. **What the oral channel carries is the information the notation declines to
fix, plus the per-studio choices it prints as options.**

### 8.6 Universities and conservatoires

**東京藝術大学 Tokyo University of the Arts (Tokyo Geidai) has a 邦楽科 / 邦楽専攻 and 尺八 is one of
its 専攻.** The full list of specialisations is 「三味線音楽（長唄、常磐津、清元）、邦楽囃子、
日本舞踊、箏曲、**尺八**、能楽、能楽囃子、雅楽」 — shamisen music (nagauta, tokiwazu, kiyomoto),
hōgaku hayashi, Japanese dance, koto, **shakuhachi**, Noh, Noh hayashi, gagaku. Provision runs
**undergraduate (学部), master's (修士課程), and doctoral (博士後期課程), the doctoral programme
including an annual doctoral recital.** The department describes itself as studying and teaching
each specialisation's classical tradition alongside practical instruction and performance theory,
while also building broad musical knowledge **including Western music**, and producing both
performers and educators; students take their specialisation practical **plus courses in other
Japanese and Western music, solfège, and performance theory.** **The page does not mention
school-specific tracks such as 琴古流 or 都山流.** [V — `geidai.ac.jp/department/music/traditional_japanese_music`,
fetched 2026-11-13 — the university's own page]

Corroborating, from two directions:

- **Linder holds an MA in shakuhachi as a performing art from Tokyo Geidai** (1997; MA thesis
  「琴古流尺八の外曲に関する研究−地歌合奏に於ける装飾奏法の考察」, "Research on Kinko-ryū
  shakuhachi *gaikyoku*: a study of ornamental techniques in jiuta ensemble playing") **and
  separately a Kinko-ryū shihan licence from Yamaguchi Gorō.** [V — Linder 2017, bibliography and
  author note] **Two parallel credentials, academic and guild, held by the same person — which is
  the clearest demonstration that the conservatoire route does not replace the licence route.**
- **Teaching staff and the foreign-student route:** Regan reports that the Japanese Ministry of
  Education scholarship let several of the most prominent non-Japanese players — **Gunnar Linder,
  Christopher Blasdel, David Wheeler, Bruce Huebner, Anne Norman** — study with **Yamaguchi Gorō,
  Kawase Junsuke and Aoki Reibo at Tokyo University of Fine Arts and Music**, and that Riley Lee's
  Japanese research was funded by the Japan Foundation; he adds that the number of Westerners
  getting such opportunities is a small fraction of the potential interest. [V — Regan 2006,
  **self-published**]

The three teachers named are **all Kinko-ryū** figures, which is consistent with the Geidai page's
silence about school tracks being a silence about *official* tracks rather than about who actually
teaches. **[U] as to current staffing and as to whether Tozan is represented.**

Earlier precedent: 初代川瀬順輔 (1870–1959), called one of the fathers of the modern shakuhachi,
studied under Araki Kodō II **and under 上原六四郎 Uehara Rokushirō, a professor at the
東京音楽学校 (Tokyo Academy of Music, Geidai's predecessor)**, and opened his own 道場 in Tokyo in
1902. [V — ja.wikipedia 尺八, citing Saitō Kei 2017] **So the academic and the guild worlds have
been interpenetrating since before 1900.**

**Kyoto City University of Arts** maintains a **日本伝統音楽研究センター (Research Centre for
Japanese Traditional Music)**, which published Kubota Satoko's two-volume jiuta-sōkyoku研究 in 2011.
[V — Linder 2017, bibliography] **Whether it offers shakuhachi performance instruction: [U].**

### 8.7 The modern learner's options, and what I could not establish

**Verified:**

- **Studio lessons at a 会派 or with an independent teacher**, roughly 4×/month, at **¥3,000–20,000
  per month** depending on school, level and teacher, plus a **¥10,000** joining fee at both Kinko
  houses I read; **free trial lessons and loan instruments are normal.** [V — chikumeisha.org,
  chikuyusha.jp, both **commercial**]
- **Teachers outside any school are now common:** 「近年では、特定の流派に所属しない奏者・指導者も
  数多く存在する」 — in recent years there are **many players and teachers who belong to no
  particular school.** [V — ja.wikipedia 尺八 §その他, uncited]
- **Online/remote teaching is a documented research object**, not just a practice: **Sarah Renata
  Strothers, "Virtual shakuhachi with dai-shihan Michael Chikuzen Gould," *Perfect Beat* (2021),
  DOI 10.1558/prbt.19346.** [V — Crossref metadata, 2026-11-13; **not read**] The title alone
  verifies that a 大師範 was teaching shakuhachi virtually and that it was written up academically.
- **How many players there are: nobody knows, and the Japanese Wikipedia says so.** 「尺八の吹奏
  人口についての本格的な調査はされておらず、正確な人口は不明である。推定では**3万人程度**と
  いわれている」 — there has been **no proper survey**, the exact number is unknown, and the estimate
  is **about 30,000**. [V — ja.wikipedia 尺八, and note what it cites: **a music-shop blog post from
  2015**, reached via a web-archive mirror because the site tripped a spam filter. **So the one
  number in circulation rests on a shop owner's estimate. Treat 30,000 as a folk figure. [U]**]

**Not verified — and these are the questions a prospective learner actually asks:**

- **How long until a beginner reliably produces a tone.** No source. **[U]**
- **How long to 初伝 / 中伝 / 奥伝 / 皆伝 / 師範.** Only one interval is documented anywhere: Tozan's
  **statutory minimum of 3 years between passing the junshihan and sitting the shihan examination**
  [V]. Everything else is **[U]**. The 竹盟社 fee ladder implies a progression but attaches no times.
- **Pass rates for the Tozan examinations, or the number of holders at each rank.** **[U]**
- **Whether meri notes, korokoro etc. are taught early or late.** **[U]** — though the 竹盟社 tier
  table does establish that **honkyoku comes last** [V], which bounds the answer from one side.

**Say plainly: the realistic learning curve is undocumented in anything I could read.** Anyone
quoting "three years to a good tone" or similar in English is not citing a source, and the honest
answer is that the one published interval is an administrative waiting period, not a learning time.

---

## 9. Practical glossary

Ordered by romanisation. **Source key:** **E** = Japanese printed encyclopedia via Kotobank
(Nipponica / 平凡社世界大百科事典 / Britannica Japan / 山川 / ヤマハ); **W** = ja.wikipedia 「尺八」
(**uncited sections** where marked *); **A** = Utsugi & Moriyama 2009 (academic, measured);
**L** = Linder 2017 (academic); **T** = 尺八修理工房幻海 glossary (**trade**); **S** = 千葉大学紫千会
blog (**hobbyist, first-hand**); **O** = school's own site (**tozanryu.com / chikumeisha.org /
chikuyusha.jp / geidai.ac.jp**); **J** = jonkara.com (**commercial**); **?** = **unverified, flagged
in §5.4.** All translations mine.

| Romanisation | Japanese | Gloss | Src |
|---|---|---|---|
| **ame** | アメ | Fingers fully open, chin drawn deeply in: a deep meri | T |
| **asane** | 浅音 | Deliberately husky tone, less forceful than *muraiki*; or playing on under half the normal breath, kari-ing slightly so the pitch does not sag | T |
| **atari** | あたり / アタリ | **Unverified.** Not in any source I read; probably a school name for a finger attack | ? |
| **bōbuki** | 棒吹き | "Stick blowing" — dead flat dynamics from start to finish; "magnificent but poor in feeling" | T |
| **chigiri** | チギリ / ツギリ | 錦風流 Kinpū-ryū's name for *nayashi*; close to a head-shake, used with *komibuki* | T |
| **chikugō** | 竹号 | "Bamboo name," granted by the teacher on completing 中伝 in Tozan-ryū | O |
| **chū / chū-meri** | 中 / 中メリ | Kinko notation mark for an intermediate degree of meri, one semitone less than メ | W* |
| **dai-kan** | 大甲 | The third register, using the 3rd and 4th harmonics; begins at F6 on 1.8 shaku and needs its own fingerings | E, W* |
| **dai-meri** | 大メリ | Deep meri, a whole tone or more; ロ大メリ reaches C4 from D4 | W* |
| **dai-dai-meri** | 大々メリ | A degree beyond *dai-meri* | T |
| **dai-shihan** | 大師範 | Tozan's top grade, granted by recognition to especially active shihan | O |
| **edaore** | 枝折 | "Branch-snap": *meri-komi*-ing quickly, as if a dry branch broke | T |
| **fuhō-shiki / fuhō-fu** | フホウ式 / フホウ譜 | The **older** notation system, syllables フホウエヤ(イ); used for the *hitoyogiri*, the Ozaki Shinryū line, Myōan Shinpō-ryū, Sōetsu-ryū; **surviving only in Chikuho-ryū** | E |
| **fuji** | 譜字 | "Score character" — the katakana that names a fingering | E |
| **fukiawase** | 吹合 | The shakuhachi instructor at a Fuke-sect temple; the pre-1871 teaching role | E |
| **fukiawase-jo** | 吹合所 | Edo studios the Kinko line was licensed to run for teaching lay people | L |
| **fukikomi** | 吹き込み | Blow in strongly from the mark; at a measure's end, blow strongly and cut. Common in Ōshū-line honkyoku | T |
| **furi** | フリ / 振り | Draw the chin in and return quickly — a single *tate-yuri* | T |
| **furikomi** | フリ込み | *meri-komi* straight after a *furi*, or *furi* into *yuri* | T |
| **gagō** | 雅号 | Art-name; in Tozan realised as 竹号 and 山号 | O |
| **gaikyoku** | 外曲 | Pieces of other genres arranged for shakuhachi — **metrical**, played in *sankyoku* | E |
| **gin** | 吟 | 明暗真法流's "hand": *nayashi* upward, only on エ (= チ) | T |
| **gochōshi** | 五調子 | A set of five modes; 根笹派錦風流 plays honkyoku across all five more than other schools | T |
| **go-on** | 五音 | The five open notes: ロツレチリ (Kinko) / ロツレチハ (Tozan) = D F G A C on 1.8 shaku | E, W |
| **ha** | ハ | **Tozan**: the fifth degree, C5/C6. **Kinko**: not a *go-on* name; appears only in ハ五/ハ三/ハ四 | W* |
| **hade / hirukara** | 破手 / ヒルカラ | Honkyoku repertoire class: the descriptive/titled pieces, playable only after noon. Opposite of 本手 | T |
| **hankai** | 半開 | Half-open hole | E |
| **hararo** | ハラロ | A named melodic figure in Kinko and Myōan honkyoku, executed with chin meri/kari; classified as a *technique* | T, A |
| **haru** | ハル / 張る | Synonym of カル (to kari). Said to be the origin of the ordinary word メリハリ (**[U]**) | T |
| **hazumi-yubi** | ハズミ指 | Umbrella term for ghost-note finger articulations: 押し指 and 打ち指. Common in Myōan technique | T |
| **hi** | ヒ | **Kinko**: upper-register C (甲ヒ = C6). **Tozan**: D5/D6, the all-open fingering. **Different pitches in the two schools** | W* |
| **hiki** | 引 | Lower by a semitone from the preceding note | T |
| **hirahira** | ヒラヒラ | *korokoro* on ピ (two octaves above 乙 D); Myōan-line honkyoku | T |
| **honkyoku** | 本曲 | "Original pieces" — for shakuhachi alone; **free rhythm**; in Kinko houses the **highest and dearest** teaching tier | E, O |
| **honte** | 本手 | Honkyoku repertoire class: the training and ritual pieces. Opposite of 破手 | T |
| **horohoro** | ホロホロ | *korokoro* in the 乙 register; Myōan-line | T |
| **i** | イ | **Kinko**: the all-open fingering, 乙イ = D5. Myōan reportedly uses イ where Kinko/Tozan say ヒ (**conflict, [U]**) | W*, T |
| **ichion jōbutsu** | 一音成仏 | "Buddhahood in one sound" — an **emic** formulation, documented in the Watazumi/Okuda line | L |
| **ikekoroshi / kassatsu** | 活殺 | Combining opposite qualities (loud/soft, high/low, fast/slow) contrastively | T |
| **iki-nayashi** | 息ナヤシ | Breath-based inflection: continuously alternating 乙 and 甲 on one fingering | T |
| **iki-nusumi** | 息盗み | "Breath-stealing," the cunning breath — concealed breathing where a phrase cannot be finished on one breath; governed by a rule about not breaking the phrase's atmosphere | T |
| **iki-yuri** | 息ユリ | Breath-flow vibrato, as on the flute — distinguished from chin/neck yuri | W*, T |
| **in** | 韻 | Cutting the sound suddenly, or letting the after-ring sound so the listener thinks you are still blowing | T |
| **jinashi** | 地無し尺八 | Instrument with the internal nodes left and no lacquer paste; suits honkyoku; pitch low (the trade source likes ~435 Hz) | T, E |
| **jinuri** | 地塗り尺八 | Bore smoothed with paste and lacquer and tuned to Western pitch; stable, loud, suits ensemble | T, E |
| **jūsan-kamuri** | 十三冠 | A melodic formula built from *yuri*, found in classical honkyoku (e.g. 『阿字観』); 十六/三十六カムリ also exist | T |
| **kaiden** | 皆伝免許状 | Tozan's fourth step, and the first that is a 免許状 (licence) rather than a 免状 | O |
| **kae-yubi** | 替え指 | Cross-fingering: the same pitch by another stopping. **The timbre changes slightly, which enriches expression**; each school has its own | T |
| **kakae** | 抱 | Meri-ing with the finger in *kazashi*; 明暗真法流's term | T |
| **kan** | 甲 | The second register — **the same fingering with a sharper breath**, the 2nd harmonic | E |
| **kan'on** | 幹音 | "Trunk notes" — the pitches available without half-holing or meri/kari | E |
| **karakara** | カラカラ | Fine tremolo; hole 5 closed, hole 4 *kazashi*, hole 3 open, hole 1 struck finely; sounds like a bird's "chi-chi-chi." Three grades (plain/meri/dai-meri). Called **鈴ゴロ** in Myōan and Kinko lines | E, T, A |
| **kari** | カリ | Raise the pitch by pushing the chin out/up; working range ~1 semitone | E, W* |
| **katanari / katakara** | 片鳴り / 片カラ | An instrument on which *karakara* will not sound properly — used as a buying test | T |
| **kazashi** | かざし / かざし指 | Holding the finger **over** the hole without stopping it, lowering the pitch "by about half"; listed by Tsukitani as a category distinct from the partial openings | E, T |
| **keshi** | ケシ | **Unverified as a term.** The verb 消す ("let it die away") is a common score instruction; 切 and 韻 cover the stopping techniques | ? |
| **kizami** | 刻み | Repeated strikes at **constant** tempo, without *otoshi*'s dynamic shaping | T |
| **kiru** | 切 | Stop the note leaving no after-ring | T |
| **komibuki** | コミ吹き / 込み吹き | Pulsed breath, interrupted at regular intervals. **Developed in the Ōshū-line 根笹派錦風流**; traditionally explained as a way to keep sounding against the Tōhoku wind (**[U]** as to origin) | E, T |
| **kōmei-fu** | 孔名譜 / 管名譜 | The hōgaku wind-notation family. For shakuhachi the characters are strictly **fingering** names, not hole names | T |
| **korokoro** | コロコロ | Tremolo; chin in meri, hole 3 closed, hole 4 *kazashi*, hole 5 half closed, **holes 1 and 2 alternated**. In Tozan usually ends as **コロコロリン** | E, T, A |
| **koten honkyoku** | 古典本曲 | The honkyoku originating in the Fuke-sect period, as against modern schools' own 本曲 | E, L |
| **kuchiguruma** | 口車 | 錦風流 term, reported to correspond to tongue flutter | T |
| **kuchi-jamisen** | 口三味線 | The string-instrument counterpart of *shōga* | T |
| **kuchi-meri** | 口メリ | Lowering the pitch **by mouth shape and breath alone, without moving the chin** — said to have been devised because the komusō's 天蓋 hat would wobble. Little used today; suits koten honkyoku | T |
| **kusabi-buki** | くさび吹き / 楔吹き | "Wedge blowing": loud at the start, tapering away | T |
| **ma** | 間 | Hōgaku term, **synonym 間拍子**, covering (1) rhythm — the management of subtle stretching and shrinking; (2) metre — 表間 / 裏間; (3) tempo — 小間 / 大間 / 早間. Aesthetically, the attended-to **blank between beats, "not an empty emptiness but an emptiness filled with tension toward the next beat"** | E |
| **mabyōshi** | 間拍子 | Both a synonym of 間 and the name of Kinko notation's rhythm **dots** beside the notes | E, J |
| **mawashi-yuri** | 回しユリ | "Circling" yuri | T |
| **meri** | メリ / 沈 | Lower the pitch by drawing the chin in/down, pivoting on the instrument-to-jaw contact; working range ~2 semitones, **maximum over 4 semitones**, widest near the all-open fingering | E, W* |
| **meri-komi** | メリ込み | A family of five notated meri inflections (at a note's end, into the next note, with *suri-age*, with *suri*, and メリ上げ) | E, T |
| **meri-hari** | メリハリ / 乙張り | The ordinary Japanese word for light-and-shade/contrast, **said** to derive from meri and kari (**[U]**) | T |
| **momite** | もみ手 | Rapid alternation of strikes on **two** holes (e.g. 2 and 3 → 「ツレーレツ」) = Western trill. **Tozan's term**; other schools notate オドル | T |
| **muraiki** | ムラ息 / ムライキ | Breathy/explosive attack — mostly wind noise across the edge. Pitch roughly constant; power spikes then decays; large power-spectrum slope at onset; usually with audible 息混ぜ | E, T, A |
| **naname-yuri** | 斜ユリ | "Diagonal" yuri. **Listed by Tsukitani; no description found** | E |
| **natori** | 名取 | **Unverified in a shakuhachi context.** Tozan says 竹号/山号 | ? |
| **nayashi** | ナヤシ | An application of *tate-yuri*, in two forms: (1) a portamento by chin meri→kari plus finger *kazashi*, notated 「～」, starting a semitone above Tozan's *suri-age*, muffled; (2) a head-shake tracing hiragana 「ん」, creating a valley in the sound. **Kyoto-line: courtly and glossy. Kyūshū-line: wild and rough. Kinpū-ryū: called チギリ.** Measured: rising pitch with **no** power dip between notes (unlike *suri-age*) | E, T, A |
| **neyashi** | ネヤシ | **Unverified.** Not found anywhere; probably a mis-transcription of ナヤシ | ? |
| **nukite** | ヌキテ / 抜き手 | Moving to the Myōan line's イ by opening hole 5 so the resonance escapes out the back; softer than simply opening the thumb hole. Close to *suri-age* | T |
| **odoru / odori** | オドル / オドリ | A finger-repetition technique, "like *momite* but less precise"; **the term other schools use where Tozan says もみ手**. Also the word for a beginner's fingers tangling | T |
| **okuden** | 奥伝 | Third rank in both the Tozan ladder and the Kinko houses' tiers | O |
| **ōma** | 大間 | Slow tempo, each *koma* beat doubled | E |
| **oshi** | 押し / 押し指 | Re-pressing an already-stopped hole. Measured: power spikes and **the pitch rises** | T, A |
| **otoshi** | オトシ / 落し | **Disputed.** Trade: a finger-repetition with progressively narrowing intervals, growing louder then softer. Measured: an instrument-**angle** technique with **continuously falling pitch** and power dropping sharply after it | T, A |
| **otsu** | 乙 | The lower register, D4–C#5 on 1.8 shaku. Synonym **呂 *ryo***, more usual in Kinko writing | E, T |
| **rotsure-shiki** | ロツレ式 / ロツレ譜 | The **newer** notation system, syllables ロツレチ; **established as the Kinko notation from the 18th century**, now almost universal | E |
| **ryo** | 呂 | = 乙 *otsu* | E, T |
| **sangō** | 山号 | "Mountain name," granted on obtaining the Tozan 師範 licence | O |
| **sasabuki** | 笹吹き | "Bamboo-grass-leaf blowing": soft → loud → soft | T |
| **sasane** | 笹音 | Half-*muraiki*; husky, "like the touch of a bamboo-grass leaf" | T |
| **seiritsu** | 正律 | Instrument specified **by pitch** — a 正律 1.8 shaku really sounds D but may not measure 1.8 shaku. Now the mainstream specification | W* |
| **seisun** | 正寸 | Instrument specified **by length** — exactly 1.8 shaku, with no guarantee it sounds D | W* |
| **shichiku** | 糸竹 | "Strings and bamboo" — the koto/shamisen/shakuhachi world | T |
| **shihan** | 師範 | Master-teacher grade. **Tozan: by examination, sat only after 3+ years as 准師範.** Kinko houses: a tier, apparatus unstated | O |
| **shihankai** | 四半開 | Quarter-open hole (Kamisangō); Tsukitani's finer list adds 4分の3開 and 4分の1開 | E |
| **shinan** | 指南免許状 | Tozan's parallel **teaching** licence; with a 指南開始届 it makes one a 師匠 | O |
| **shishō** | 師匠 | A teacher entitled to present students for certification | O |
| **shizume-buki** | シズメ吹き / 沈め吹き | meri→kari repeated several times, an exaggerated *mawashi-yuri*; common on ロの大メリ and ウのメリ; the meri should be louder | T |
| **shoden** | 初伝 | First rank, Tozan and the Kinko houses alike | O |
| **shōga** | 唱歌 | Singing the 譜字 aloud to learn, memorise and transmit the melody; **the reason hōgaku notation is katakana**; often beaten with a ハリセン clapper | E, T |
| **sōhō-fu** | 奏法譜 | "Playing-method score" — the correct generic name for shakuhachi notation | E |
| **soko-yuri** | 底ユリ | "Bottom" yuri. **Listed, not defined** | T |
| **sorane** | ソラ音 / 空音 | **In Kinko**, deliberately aiming the breath off the sounding edge: between *asane* and *muraiki* in force | T |
| **suizen** | 吹禅 | "Blowing Zen" — playing as Zen practice, one of the Fuke sect's three stated uses of the instrument alongside liturgy and begging | E |
| **suri** | 摺り / 擦り / スリ | Umbrella term for sliding the note; five notated varieties | T |
| **suri-age** | スリ上げ | Upward portamento, by sliding the finger off the hole, or raising the chin from meri, or both. Measured: rising pitch **with a power dip between the notes** | E, T, A |
| **suri-sage** | スリ下げ | Downward portamento; **needs chin and finger together** — e.g. G→F by dropping the chin to near Eb then sliding **up** with the finger, so the note has no corner | W*, T |
| **suzu-goro** | 鈴ゴロ | Myōan-and-Kinko-line name for *karakara* | T |
| **suzu-uchi** | 鈴打ち | 明暗真法流's name for the finger-strike | T |
| **tabane** | タバ音 | Reported as a higher-order *tamane* done by abdominal pressure alone; **the source openly says it does not know the mechanism** | T |
| **tamane (throat)** | 玉音 | Flutter made by **vibrating the throat as when gargling**; learned via water-gargle → dry-gargle → with tone; must be controllable fast and slow. Yokoyama Katsuya practised it through the whole of 『六段』 | T |
| **tamane (tongue)** | タマ音 | **Tongue** flutter = Western Flatterzunge; harder to control, "lacks flavour," suited to modern and ensemble work rather than honkyoku | T |
| **tate-yuri** | 縦ユリ | "Vertical" yuri. **Tozan: shake the head vertically. Kinko: shake with the hand** | E, T |
| **te-yuri** | 手ユリ | "Hand" yuri. **Listed, not defined** | T |
| **tsuki** | ツキ | meri→kari, pushing the drawn-in chin lightly out; also called **小ナヤシ** | T |
| **tsutsune** | 筒音 | The note with all five holes closed — the instrument's lowest, D4 on 1.8 shaku | E, W* |
| **tsuyukiri** | 露切り | Originally blowing condensation out of the bore on the begging round; became a **fixed closing phrase** — Kinko 「レロー」, Kinpū-ryū 「ツレー、ロ（チギリ）」 | T |
| **tsuzumi-buki** | 鼓吹き | "Drum blowing": strong → weak → strong. 神如道 Jin Nyodō was celebrated for it | T |
| **u** | ウ | A **cross-fingering** for Ab4/Ab5 in both schools, alternative to チメリ; not available in 大甲 | W*, T |
| **uchi** | 打ち / 打ち指 / 叩き | Striking a finger hole. **Names vary by school and by hole** — the hole-1 strike is ル on ツ, エ on レ. Measured: power spikes and **the pitch falls** | T, A |
| **ukashi** | ウカシ / 浮カシ | Thick breath flowed gently so the tone seems to float; like *muraiki* but not violent; **only in 乙 and only on a 地無し instrument** | T |
| **utaguchi** | 歌口 | The blowing edge — the tube's front sliced away **outward** so the bore rim presents a curved **sharp angle**; usually inlaid with buffalo horn, ivory or ebonite to keep the edge sharp, **the inlay's shape differing by school** | E |
| **utsuro-buki** | 虚吹 | "Empty blowing" — dead straight with a dim, hazy tone | T |
| **watashimono** | 渡し物 | Moving a piece from one 律 to another. **Not Western transposition: which notes need meri/kari changes, so the melody and technique change with it** | T |
| **yarayara** | ヤラヤラ | In 大甲, hole 5 closed, alternating strikes on holes 1 and 2 — *korokoro* an octave up; Myōan-line | T |
| **yō-onkai / ritsu-onkai** | 陽音階 / 律音階 | The anhemitonic pentatonic the five open notes form (D F G A C) — **not** *miyako-bushi* | W |
| **yoko-yuri** | 横ユリ | "Horizontal" yuri — swing the neck side to side | E, W* |
| **yuri** | ユリ / 搖り | Vibrato by shaking the head or by the breath; distinguished from the flute's breath vibrato by its 「独特の艶」. Three shapings: constant width, narrowing, or *nayashi-yuri*. **Even where the name is the same the execution can differ by school** | E, W*, T |
| **yurikomi** | ユリ込み | Stopping the note with a *meri-komi* while yuri-ing | T |

**Count: 130 entries, of which 6 are explicitly flagged unverifiable.**

---

## 10. Corrections to the commonly repeated English account

1. **"The five notes are ro-tsu-re-chi-ri."** Half right. **ロツレチリ is Kinko-ryū; Tozan-ryū says
   ロツレチハ.** They are the same five pitches (D F G A C on 1.8 shaku). [V — ja.wikipedia, prose
   and table] Worse, **ヒ and イ and ハ denote different pitches in different schools** (§2.6), so a
   bare syllable name is ambiguous without naming the school.
2. **"Shakuhachi notation is the ro-tsu-re system."** It is **one of two** historical systems, and
   **the newer one**: the フホウ式 *fuhō* system is the older, was used for the *hitoyogiri* in the
   17th century and in several fuke lines, and **still survives in 竹保流 Chikuho-ryū.** [V —
   Nipponica] The ロツレ system's dominance is a consequence of Kinko-ryū's institutional success,
   not of anything intrinsic.
3. **"Meri lowers the note by a semitone."** The working range is **about two semitones of meri
   against about one of kari — an asymmetry of roughly 2:1 — the maximum exceeds four semitones, and
   the range widens the closer the fingering is to fully open.** [V — ja.wikipedia §奏法] So the
   displacement is not a constant and the player is landing a pitch, not applying an interval.
4. **"Meri is how you get the notes between the five."** It is **one of three** stacked mechanisms —
   hole combinations, **partial covering at half / three-quarters / one-quarter / *kazashi***, and
   chin geometry — and the Japanese sources claim not twelve semitones but **every microtone in the
   range** (「音域内のすべての微分音」). [V — 平凡社; Nipponica]
5. **"The embouchure is like a flute's."** Structurally it is **not**: the shakuhachi has **no
   narrow chimney** and **no short resonator upstream of the jet**, and **the player's face baffles
   the radiation impedance**, so playing position retunes the impedance minima. [V — UNSW] The
   title of the one acoustics study on the subject concedes the point: "Some acoustics of the
   shakuhachi — **and of the shakuhachi player's face**." [V — Crossref metadata, DOI
   10.1121/1.4743469] **Meri and kari are acoustics, not merely technique.**
6. **"The right hand goes below."** It is the default, not a rule: both Kamisangō and the Yamaha
   dictionary state explicitly that **the hands may be reversed.** [V] And **the middle fingers of
   both hands cover no hole at all — they hold the instrument.** [V — 山川]
7. **"Shakuhachi playing uses *hara* breathing."** **I could not verify this in any Japanese
   reference work, and I found no respiratory physiology of shakuhachi players whatsoever.** [U]
   What the encyclopedias do say about breath is narrower and more useful: three named
   throat-and-breath techniques (タマネ, ムラ息, コミ吹) [V — Nipponica]. Report the pedagogical
   convention as convention; do not dress it as physiology.
8. **"*Tamane* is a throat flutter"** / **"*tamane* is flutter-tongue."** Both are in print, from
   good sources, and the likeliest resolution is that **玉音 (throat) and タマ音 (tongue) are two
   different techniques sharing a reading.** [V for the disagreement — Nipponica vs Utsugi &
   Moriyama; V/trade for the resolution] Never write "tamane" unqualified.
9. **"*Ma* is the pregnant silence between the notes."** That is **one sense of a three-sense
   technical term.** 間 is given in the Heibonsha encyclopedia as the ordinary hōgaku word for
   **rhythm, metre and tempo**, synonymous with **間拍子** — which is also the name of Kinko
   notation's rhythm dots. 表間/裏間 are beats one and two; 小間/大間/早間 are tempi; 「間がよい」
   means "has good time." [V] The aesthetic sense is real and is also in the reference works
   (Nipponica: the blank "is not an empty emptiness but an emptiness filled with tension toward the
   next beat"), but it is the third sense, not the whole word. [V]
10. **"Honkyoku notation contains no rhythm."** Too strong. **Auxiliary rhythm symbols are part of
    the shared principle** [V — Kamisangō], Kinko has 間拍子 dots and duration lines [V], and
    Tsukitani's point is that **音価表記 differs in every school** [V] — not that it is absent. The
    accurate claim: the notation fixes the sequence of actions and **partially** constrains
    durations by school- and studio-specific means, and **prints its own known variants** — Kinko's
    「或」 marks carry alternative 手付 and alternative held-lengths "because the length held differs
    by studio." [V — 紫千会] What is not fixed is the realisation.
11. **"The piece lives in the oral tradition" — true, and here is the actual mechanism.** It is not
    ineffability. It is **唱歌**: teacher and student **sing the 譜字 aloud**, often with a ハリセン
    clapper beating time, and the melody is **memorised by singing** [V — Kamisangō; V/trade]. The
    strongest evidence is from engineers who needed the data and could not get it from the page:
    many hōgaku scores **lack the technique information needed to perform the piece**, so
    self-study from score plus recording is **"close to impossible"** and the beginner **receives
    the playing method orally from a shihan, transmitted unwritten.** [V — Utsugi & Moriyama 2009]
12. **"Japanese traditional arts transmit through the iemoto system."** False as a generalisation
    about the shakuhachi, in two directions. **(a)** Before 1871 there were **no ryūha**: teaching
    was by the temples' 吹合 and 「流派のような組織は存在しなかった」 [V — Nipponica]; the *ryū* as
    an iemoto organisation is post-1871, and Tozan's is explicitly a **modern** iemoto system
    designed by its founder [V]. **(b)** At least one major contemporary lineage has **no grading or
    licensing of any kind** [V — parallel strand]. And **Kinko-ryū has no unified body at all**,
    so "the Kinko licensing system" does not exist — each 会派 runs its own [V].
13. **"Honkyoku is the core of the tradition, so it is what you learn."** In 竹盟社's published fee
    structure **honkyoku is the top tier and the most expensive (¥20,000/month against ¥10,000 for
    初伝)** — you reach it last and pay most for it. [V — chikumeisha.org] And in Linder's typology
    **the word itself is school-relative**: for Meiji-founded schools "honkyoku" means their
    founder's own compositions [V — Linder 2017].
14. **"Western staff notation was never used for shakuhachi."** 上田流 Ueda-ryū, founded 1917,
    **introduced staff notation and the 7-hole instrument together in order to modernise the
    instrument — and abandoned the staff notation part-way while the 7-hole instrument survived and
    is still played.** [V — ja.wikipedia §上田流] That is a better argument about what the tablature
    does than any aesthetic claim. Conversely, **Tozan notation is itself partly derived from staff
    notation** [V — jonkara, commercial]: the bar lines and explicit durations are the import.
15. **"Tozan notation is simply a later, westernised variant."** It was a **deliberate product
    decision with a business model**: Nakao Tozan 「記譜法、教授法、合奏形式などにも新機軸を打ち出し」
    — broke new ground in notation, teaching method **and** ensemble format at once, while building
    a modern iemoto system [V]. A practitioner's verdict on why it spread:
    「わざわざ師匠に習わなくても、楽譜を見れば曲が吹ける。これは革命ですね」 — you could play from
    the score **without going to a teacher at all; that was a revolution.** [V — 紫千会, hobbyist]
    The price difference is still visible: the same piece, ¥600 in Tozan and ¥1,800 in Kinko. [V]
16. **"The shakuhachi is a Zen instrument."** Out of scope here and held by another researcher, but
    it bears on how technique is written about, so: Linder, from primary documents, holds the Zen
    connection to have been **constructed in the Edo period and re-constructed since the 1970s**;
    the most-cited document for the Fuke sect's privileges, the 「慶長掟書」, is **a forgery of a
    much later date** whose latest version tells the komusō to *look* like monks while keeping "the
    intention and resolution of a samurai," describing the sect as one **for martial practice**.
    [V — Linder 2017, pp. 121 and n. 11] The problem has been named in English scholarship since
    **1981** (Signell, "The Mystique of the Shakuhachi") [U — citation only]. And Linder documents
    the feedback loop: Okuda Atsuya told him that Western interest in his Zen-framed recordings
    **gave impetus to his activities in Japan** [V].
17. **"A score is a score."** Two schools had opposite theories of what one is for. Kinko notation
    **prints the disagreement between studios into the page** (the 「或」 variants, including
    duration) and carries the shamisen's line in small characters down the left as an ensemble cue.
    Tozan notation **resolves** the disagreement, adds bar lines and tempo marks, **drops** the
    shamisen cue line where the parts diverge, and sells for a third of the price. [V — 紫千会]
18. **A specific factual correction to a source other writers use.** Japanese Wikipedia's 正律 table
    lists **二尺二寸管 as "Bb4"**; the surrounding rows are B3 and A3, so it must be **Bb3**. A
    one-octave typo in the most-copied English-accessible fingering source. [V — ja.wikipedia 尺八
    §正寸と正律]
19. **"Shakuhachi has no academic home."** **東京藝術大学 has a 邦楽科 with 尺八 as one of its
    専攻, at undergraduate, master's and doctoral level, the doctorate including an annual
    recital** — alongside shamisen (nagauta/tokiwazu/kiyomoto), hayashi, dance, koto, Noh, Noh
    hayashi and gagaku; the curriculum includes Western music and solfège. [V — geidai.ac.jp]
    Linder holds **both** a Geidai MA in shakuhachi performance **and** a Kinko shihan licence from
    Yamaguchi Gorō [V], which shows the two credential systems run in parallel rather than one
    replacing the other. The interpenetration is old: 初代川瀬順輔 studied under a professor of the
    東京音楽学校 before 1902. [V]
20. **"About 30,000 people play the shakuhachi."** This figure comes, via Japanese Wikipedia, from
    **a music shop's blog post of 2015**, retrieved through a web-archive mirror; the article itself
    says **「本格的な調査はされておらず、正確な人口は不明」** — there has been **no proper survey**
    and the exact figure is unknown. [V — ja.wikipedia 尺八, including the admission] **Cite it as a
    folk estimate or not at all.**
21. **"F6 / the top of the third register is just hard."** It is more specific than that: **the
    single note corresponding to F6 on 1.8 shaku is described as extremely difficult** — and F6 is
    **the bottom note of 大甲**, so the register's floor is its worst note. [V — ja.wikipedia §音域]
    The practical ceiling is about **E6** for reliable playing (「2オクターブ強」), ~2.5 octaves in
    the conventional encyclopedia figure, with **E7** claimed only for high technique. [V — three
    sources, §4.4]

---

## 11. Open questions

**Documentary gaps I could not close in this pass, in rough order of how much they would improve
this file:**

1. **A verified hole-by-hole fingering chart.** §2.3 is the weakest part of the single most useful
   artefact here. The successive-opening model is consistent with everything verified but is **my
   inference**. Targets: Blasdel's manual; a school method book; the Japan Arts Council
   文化デジタルライブラリー instrument guide. **I reached two of its pages and both were
   JavaScript-rendered, serving only navigation chrome:** `.../edc6/edc_new/html/501_shakuhachi.html`
   (title 「楽器図鑑尺八(しゃくはち)」 plus links to `gakkizukan.html`, `500_shakuhachis.html`,
   `shakuhachiFamily_general.html`) and `.../500_shakuhachis.html` (an index whose shakuhachi entry
   is a bare link). Both fetched 2026-11-13. **Try `shakuhachiFamily_general.html`, a headless
   browser, or a search-index snippet** — the usual account's warning about this site was accurate and its
   content is genuinely inaccessible to a plain fetch.
2. **Linder's 2012 Stockholm dissertation**, `diva-portal.org/smash/get/diva2:488776/FULLTEXT01.pdf`.
   **My download failed repeatedly** (the file grew past 17 MB without completing; `pdftotext` could
   not rebuild its xref). It is open access and is the one monograph-length academic treatment of
   shakuhachi transmission in English by a shihan. **Get it with a resumable download.**
3. **Riley Lee's two notation papers and his 1992 Sydney dissertation.** All three failed (Cambridge
   shell, JSTOR 403, Sydney repository moved). §6.8 stands independent of Lee, which also means it
   is unchecked against him.
4. **Myōan notation mechanics** — how it marks duration, what its auxiliary symbols are, how its page
   differs from Kinko's. Nothing found. §6.5 is a hole.
5. **A published side-by-side of the same *honkyoku* in two notations.** I found only a *gaikyoku*
   comparison, and that in a student blog. Candidates: 『鹿の遠音』, 『巣鶴鈴慕』; Tsukitani 2000 is
   the likely scholarly venue.
6. **Quantitative embouchure and breath data** — aperture dimensions, jet velocity, blowing pressure,
   and *any* respiratory physiology of shakuhachi players. Nothing found. Targets: Castellengo &
   Fabre's comparative chapter (DOI 10.4324/9781315077192-10); the UNSW group's linked papers
   (`WOLFE.pdf`, `JSV.pdf`, `ASA.html` off the shakuhachi page); Yoshikawa's acoustics work.
7. **A spectral comparison of ツ against レメリ** — the same pitch by open fingering and by meri. The
   whole "meri notes have a different timbre" argument in §3.4 is currently structural (the notation
   maintains the distinction) rather than measured. **Utsugi & Moriyama recorded exactly this — 14
   pairs of 同音異奏 — but report only classification accuracy, not spectra.** Their database would
   settle it; it is not public ("there is no standard database of shakuhachi techniques, so we made
   one").
8. **Whether *kuchi-meri* and chin-meri at the same pitch differ in timbre.** A clean, cheap,
   decisive experiment on the §3.4 question, since kuchi-meri by definition does **not** move the
   face relative to the edge. No test found.
9. **Resolution of the オトシ conflict** (finger repetition vs falling-pitch angle technique) and of
   the コロコロ/カラカラ conflict (octave alternation vs adjacent-hole warble). Both are
   source-against-source and may simply be school-against-school.
10. **あたり, ネヤシ, ケシ, 大ユリ, 半音-as-technique** — five terms in circulation in English that I
    could not find in any Japanese source. Either they are school-specific terms from lines I did
    not reach, or they are English-literature artefacts. **Someone with Blasdel's manual and a Myōan
    method book could settle all five in an afternoon.**
11. **Descriptions for 斜ユリ, 手ユリ, 底ユリ, タバ音** — terms attested without definitions.
12. **The realistic learning curve.** Not one published figure for time-to-tone or
    time-to-rank, anywhere. The only documented interval in the whole system is Tozan's
    **administrative** 3-year minimum between the junshihan and shihan examinations.
13. **Rank-holder counts and examination pass rates** for Tozan, and whether any Kinko 会派 examines
    at all.
14. **Current Geidai shakuhachi staffing**, and whether Tozan-ryū is represented there at all — the
    three teachers named in my sources are all Kinko figures.
15. **Right-to-left column order** is assumed from ordinary Japanese typesetting and from the Kinko
    concertina format; no source states it of shakuhachi scores.
16. **Whether 都山流's post-1975 three-way split** produced divergent rank systems or notation. The
    split is verified; its consequences are not.

**One correction to add to §10, arising from the table itself (numbered 22 for continuity):**

22. **"Kinko's メ is Tozan's メ" / "the two notations' accidentals correspond."** They do not, and
    there is **no single rule that translates one into the other** — the mapping is note-by-note.
    Kinko's **メ** is two semitones on ツ and リ but one on チ and ロ; Tozan's **small glyph** is two
    on ツ and ハ but one on レ, チ and ロ; and Tozan's **メ** *shallows* the meri on a full-size glyph
    but *deepens* it on a small one. The reason is structural: these marks name **degrees of chin
    displacement**, not intervals, and a given displacement yields a different interval on every
    fingering (§3.2). Full tabulation in §2.5, point 2. [V as a reading of the ja.wikipedia table;
    the conclusion is mine.] **This is the single likeliest place for an English reference to be
    quietly wrong.**
