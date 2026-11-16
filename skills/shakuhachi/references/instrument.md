# The Shakuhachi (尺八) as a Physical Object — Research Notes

Research notes for a reference skill. **Scope: the instrument itself.** History, genres, the
Dokyoku school, and technique/notation are *covered elsewhere* by other researchers; where this
file touches them it is only to explain a physical feature.

Every claim is tagged:

- **[V]** — verified: I opened the named artifact myself. URL and fetch date given.
- **[U]** — unverified: what is missing is stated.

All Japanese→English translations are **mine** unless a published translation is named.
All fetch dates are 2026-11-13 unless otherwise stated.

## 0. The source base, and what it is worth

| Source | What it is | Reliability for this topic |
|---|---|---|
| `ja.wikipedia.org/wiki/尺八`, raw wikitext via the MediaWiki API, revision timestamp **2026-09-19T22:33:36Z** | Japanese Wikipedia. Footnoted to 月渓恒子 (Tsukitani Tsuneko), 久保田敏子 (Kubota Satoko), kotobank, and maker sites | **[V]** The single densest technical source I found. Internally inconsistent in one place (see §1.5). Cites real scholarship; not itself scholarship |
| `kotobank.jp/word/尺八-75849` | Aggregator serving the printed Japanese encyclopedias: 改訂新版 世界大百科事典 (Heibonsha), 日本大百科全書 / ニッポニカ (Shogakukan), 精選版 日本国語大辞典, デジタル大辞泉, ブリタニカ国際大百科事典 小項目事典, 百科事典マイペディア, 音楽用語ダス (Yamaha), 山川 日本史小辞典 | **[V]** Best reference-grade source. Read via a summarising fetch, not transcribed verbatim — see the caveat below |
| Wolfe & Smith, "Acoustics of the air-jet family of instruments", *Proc. 7th Western Pacific Regional Acoustics Conference (WESTPRAC VII)*, Kumamoto, 3–5 Oct 2000, pp. 575–580 (paginated "WOLFE 104-1"…"104-6") — PDF at `newt.phys.unsw.edu.au/jw/WOLFE.pdf` | Peer-reviewed-ish conference paper, UNSW music acoustics group | **[V]** I read all 6 pages. **The only real measured shakuhachi acoustics I could obtain in full.** |
| `newt.phys.unsw.edu.au/jw/shakuhachiresults.html` and `/jw/ASA.html` | UNSW project pages for the JASA 2000 abstract | **[V]** Method and qualitative findings; the impedance spectra are images with no tabulated values |

**Caveat on kotobank** [V]: the fetch tool returned a summary with short Japanese quotations
rather than a verbatim transcription, declining to reproduce the copyrighted text in full. So for
kotobank I have **accurate attributions and figures, with only short verbatim quotes**. Where a
kotobank figure matters I have cross-checked it against the Wikipedia wikitext, which I did
transcribe exactly. Claims resting on the kotobank summary alone are marked as such.

## 1. Anatomy and vocabulary

### 1.1 The one-sentence physical description

The modern shakuhachi is an **end-blown, open-ended, approximately cylindrical bamboo air-reed
flute**, made from the root end of *madake* bamboo, with **four finger holes on the front and one
on the back** (five in total), blown across a bevelled notch cut into the rim of the upper end.
[V] — ja.wikipedia 尺八 wikitext, rev. 2026-09-19, §楽器の構造: 「真竹の根元を使い、7個の竹の節を
含むようにして作るものが一般的である。一般的に手孔は前面に4つ、背面に1つある。上部の歌口に
息を吹きつけて音を出す。」 (my translation: "it is generally made using the root end of madake,
so as to include seven bamboo nodes. The finger holes are generally four on the front and one on
the back. Sound is produced by blowing against the utaguchi at the top.") Cross-checked [V]
against Wolfe & Smith 2000 p. 104-2: "The shakuhachi is an approximately cylindrical instrument,
traditionally made of bamboo, with five tone holes for four fingers and one thumb."

Classification [V]: ja.wikipedia opens 「日本の木管楽器の一種である。リードのない**エアリード**
楽器に分類される」 — a Japanese woodwind, classified as a **reedless air-reed instrument**.
Heibonsha 世界大百科事典 via kotobank calls it a reedless bamboo flute grouped with the flutes
[V, kotobank summary].

### 1.2 歌口 *utaguchi* — the blowing edge

| Fact | Status |
|---|---|
| 歌口 (*utaguchi*, lit. "song mouth") is the blowing edge: a notch cut into the rim of the upper end of the tube | **[V]** ja.wikipedia §物理的構造 |
| **The bevel slopes *outward*** — 「尺八の歌口は、外側に向かって傾斜がついている」 ("the shakuhachi's utaguchi is bevelled towards the outside") | **[V]** ja.wikipedia §物理的構造. This is the organologically load-bearing detail — see §1.3 |
| An insert of hard material is set into the edge: **水牛の角** (water-buffalo horn), **象牙** (ivory), **エボナイト** (ebonite / hard rubber). 「基本的には補強用であるが、これによって音質が変わるとする説もある」 — "fundamentally it is for reinforcement, though there is also a view that it changes the tone quality" | **[V]** ja.wikipedia §物理的構造 |
| Heibonsha adds that the insert's **shape varies by school** (流派), and that the utaguchi is placed at the hard, closely-noded upper end of the tube | **[V, kotobank summary]** |
| Wolfe & Smith independently describe it as "a sharp edge of horn or ivory (or a synthetic substitute) which is set into a notch bevelled into the cylindrical side" | **[V]** Wolfe & Smith 2000, p. 104-2 |
| Modern plastic/resin instruments use a moulded or plastic insert rather than horn | **[U]** — plausible and consistent with §2.4, but I did not find a source stating it for a named product |

**歌口の角度 (the utaguchi angle).** [U] **I could not source a numerical bevel angle, edge
width, or notch depth from any reference-grade source.** ja.wikipedia cites a maker's page,
泉州尺八工房 "歌口研究2" (`senshu-shakuhachi.com/utakuchi2.html`), as the locus of a dispute over
whether material affects tone; I did not fetch it, and it is a **COMMERCIAL** maker's site in any
case. The figures sometimes quoted in English sources (e.g. "a 30° bevel") are, as far as I can
establish, **unsourced**. This is a real gap.

### 1.3 The outward bevel is the key organological fact — and a common English error

The shakuhachi's utaguchi is bevelled **outward** (away from the bore). The Chinese *xiao* and the
*gagaku* shakuhachi are bevelled the other way, **inward**. [V] ja.wikipedia §歴史: 「その後中国
では、歌口の傾斜が管の外側にあるタイプの縦笛は断絶し」 — "subsequently in China, the type of
vertical flute whose utaguchi bevel is on the *outside* of the tube died out" (cited there to
月渓恒子, 『日本の音楽・アジアの音楽』 ch. 16 「尺八楽」, p. 384). My translation.

Two consequences, both real:

1. The outward bevel plus the chin-seal geometry is what gives the instrument its very large
   pitch-bend range (§5.3). [V] implied by Wolfe & Smith 2000 p. 104-5 — see §5.
2. Describing the shakuhachi in English as "like a recorder" is wrong in the most important way.
   A recorder is a **fipple** flute: the windway and labium are built into the instrument, so the
   jet geometry is fixed. ja.wikipedia makes exactly this contrast [V]: 「リコーダー（いわゆる
   「縦笛」）は歌口の構造（フィップル、ブロック）によって初心者でも簡単に音が出せるが、尺八・
   フルートで音を出すには熟練が必要である」 — "on the recorder (the so-called *tatebue*) the
   construction of the mouthpiece (fipple, block) lets even a beginner get a note out easily,
   whereas producing a sound on the shakuhachi or the flute requires skill." The shakuhachi is an
   **air-reed/edge-tone** instrument like the transverse flute, with the jet formed by the
   player's lips, not by the instrument.

### 1.4 手孔 *tekō* — the finger holes

- The holes are called **手孔** (*tekō*, "hand holes"); ja.wikipedia glosses them as 指孔
  (*shikō*, "finger holes") and links both to the article 音孔. [V] ja.wikipedia §奏法, §物理的構造.
- **Four front + one back = five.** [V] all sources agree: ja.wikipedia (「前面に4つ、背面に1つ」),
  Heibonsha (「指孔は前面4、背面1、計5孔」, verbatim quote), Nipponica, マイペディア, 音楽用語ダス,
  山川日本史小辞典 [V, kotobank summary].
- **Which digit covers which hole**, lowest to highest (Heibonsha) [V, kotobank summary]: right
  ring finger, right index, left ring, left index, **left thumb** (the back hole). So the back
  hole is the *highest* hole and is the thumb hole. Note this is an unusual assignment — the
  middle fingers are not used on a five-hole instrument.
- **Multi-hole variants** [V] ja.wikipedia §物理的構造: six-, seven- and nine-hole shakuhachi were
  developed from the Meiji period onward under the influence of Western music; all can be made by
  drilling additional holes in an existing five-hole instrument. Of these the **seven-hole** is
  the most widely used, though still not mainstream against the five-hole. 「手孔の数が増えれば
  その分安定して出せる音が増えるが、使用する指の数も増えるため運指上の制約も多くなる」 — more
  holes give more stably-producible notes but impose more fingering constraints. Six-hole
  instruments feel almost identical to five-hole, so some players convert after starting on five.
- Attributions for the multi-hole instruments [V] ja.wikipedia §流派: the seven-hole shakuhachi in
  current use originates with **上田芳憧** (Ueda Hōdō), who founded 上田流 in 1917 and also tried
  to introduce staff notation; **村治虚憧** (Muraji Kodō, 上田流, founded 村治流 in 1928) developed
  a 純律六孔尺八 ("just-intonation six-hole shakuhachi") in 1952, designed so that the 筒音 and the
  third hole form an exact fifth — described there as having had a large influence on later
  shakuhachi tuning. The multi-hole (mostly 7-hole) instruments were further developed and spread
  by **宮田耕八朗** (Miyata Kōhachirō) from the 1960s in the 日本音楽集団 circle.

### 1.5 節 *fushi* — the nodes, and the seven-node convention

This is where my best source contradicts itself, so I report the disagreement rather than
resolving it.

| Statement | Where | Status |
|---|---|---|
| "generally made so as to **include seven bamboo nodes**" (「7個の竹の節を含むようにして作るものが一般的である」) | ja.wikipedia §概要 (lead), rev. 2026-09-19 | **[V]** |
| "the current shakuhachi is a **五孔三節** (five-hole, *three*-node) instrument made from the root of madake" (「現行の尺八は、真竹の根元を使用して作る五孔三節のものである。」) | ja.wikipedia §物理的構造, same revision | **[V] — and it contradicts the lead** |
| "nodes are removed, and the whole tube usually contains **seven nodes**, with the root end thick and densely noded" | 改訂新版 世界大百科事典 (Heibonsha) | **[V, kotobank summary]** |
| 普化尺八 has **seven nodes** overall | 日本大百科全書 (Nipponica) | **[V, kotobank summary]** |
| The *ancient/gagaku* shakuhachi is **六孔三節** (six-hole, three-node) — the Shōsōin instruments | ja.wikipedia §歴史: 「正倉院には六孔三節の尺八」 | **[V]** |

**My reading of the conflict** [U]: two independent printed encyclopedias (Heibonsha, Nipponica)
and the Wikipedia lead all say **seven nodes** for the modern 普化尺八, and "三節" is the standard
description of the *ancient* instrument. The most economical explanation is that 「五孔三節」 in
the §物理的構造 paragraph is **an error or a contamination from the gagaku-shakuhachi
description**. I could not confirm this — it would need a maker's or organological monograph. **Do
not repeat "three nodes" for a modern shakuhachi without checking.** The seven-node convention is
the well-supported one.

Why nodes matter physically: the node (節) is a solid internal diaphragm in living bamboo. Making
a shakuhachi requires **removing** the internal diaphragms; what remains visible externally are
the seven node rings, and what remains internally is a ridge at each node position unless it too
is worked away. [V] ja.wikipedia §物理的構造: 「現行の尺八の管の内部は、管の内側に残った節を
削り取り…」 — "in the interior of the current shakuhachi, the nodes remaining on the inside of the
tube are shaved away…". This is exactly the *jinashi*/*jiari* distinction (§3).

### 1.6 中継ぎ *nakatsugi* — the mid-joint, and why instruments are two-piece

[V] ja.wikipedia §物理的構造, transcribed exactly: 「古くは一本の竹を切断せずに制作する延管
（のべかん）を作っていたが、現在では一本の竹を中間部で上下に切断してジョイントできるように
加工したものが主流である。これは製造時に中の構造をより細密に調整できる、一本の竹材にこだわらず
複数の竹から良い部分を組み合わせられるなどの理由からだが、結果として持ち運びにも便利になった。」

My translation: "In former times instruments were made as 延管 (*nobekan*), produced without
cutting the single piece of bamboo; today the mainstream is bamboo cut into upper and lower halves
at the middle section and worked so that it can be jointed. The reasons are that the internal
structure can be adjusted more finely during making, and that good parts from several pieces of
bamboo can be combined rather than being committed to a single piece — and as a result it also
became convenient to carry."

So the ordered reasons are: **(1) bore adjustment, (2) material selection across billets,
(3) portability as a side-effect.** The commonly repeated English claim that the joint exists
"so it fits in a bag" inverts the priority — portability is explicitly the *consequence*, not the
motive. [V]

- 延管 *nobekan* = the one-piece instrument. [V] same passage. Note: *nobekan* is a term you will
  also meet in the *jinashi* world (e.g. 地無し延管), where it signals an uncut, natural-bore
  instrument.
- The joint itself: [U] I did **not** verify the standard construction of the *nakatsugi* — the
  usual description is a tenon-and-socket fitted with a metal (often silver or nickel-silver)
  sleeve, with the joint positioned between the 3rd and 4th holes. **I found no reference-grade
  source for the sleeve material or the joint's exact position.** Flagging as unverified.

### 1.7 管尻 *kanjiri*, the root end, and 根曲がり *nemagari*

- The instrument is made from **the root end** of the bamboo — 「真竹の根元を使い」 / 「竹の根元
  部分から作られており」. [V] ja.wikipedia §概要 and §普化尺八; also Heibonsha, Nipponica,
  Britannica Japan, マイペディア [V, kotobank summary].
- The root end becomes the **bottom** of the instrument (the foot), and the utaguchi is at the
  opposite, upper end — i.e. the instrument is played "root downward". [V] 精選版日本国語大辞典 via
  kotobank describes 普化尺八 as made from the root end of thick bamboo 「with the mouthpiece at
  the far end」 [V, kotobank summary].
- Why the root: the root section is **thick-walled and densely noded** (Heibonsha: root end thick
  and densely noded) [V, kotobank summary], and it flares, giving the characteristic bell. The
  wall thickness is also what makes the deep *jinashi* bore possible (§3).
- **管尻 *kanjiri*** — the term for the bottom end / foot of the tube. **[U]** I did not find
  管尻 in either ja.wikipedia 尺八 or the kotobank entries. It is standard player/maker vocabulary
  but **I could not verify it from a reference source**, and I cannot confirm from a source whether
  it denotes the bottom rim specifically or the whole foot section.
- **根曲がり *nemagari*** — "root bend", bamboo whose root section curves, prized for instruments.
  **[U]** Likewise **not found** in ja.wikipedia 尺八 or the kotobank entries I read. I can neither
  confirm the term's currency nor the usual claim that *nemagari* is specifically sought for long
  instruments. **This is an unverified gap.**

### 1.8 内径 — the bore

[V, kotobank summary] 改訂新版 世界大百科事典 (Heibonsha) gives the only dimensioned bore
description I obtained from a reference source:

| Dimension | Value | Source |
|---|---|---|
| Outer diameter at the middle | **about 3.5–4 cm** | Heibonsha [V, kotobank summary] |
| Outer diameter (普化尺八, average) | **about 4 cm** | Britannica Japan and ja.wikipedia §普化尺八 「直径4cm」 [V] |
| **Inner diameter at the top** | **about 2 cm** | Heibonsha [V, kotobank summary] |
| **Inner diameter at the bottom** | **about 1.5 cm** | Heibonsha [V, kotobank summary] |
| Overall bore shape | **逆円錐 — an inverted cone**, i.e. narrowing towards the foot | Heibonsha [V, kotobank summary] |
| Bore finish | smoothed and lacquered black or vermilion | Heibonsha [V, kotobank summary] |

Two important notes:

1. **The bore narrows towards the foot.** The bore is *wider at the blowing end* (~20 mm) than at
   the open foot (~15 mm). This is the opposite of the intuition that a flute's bore widens to a
   bell, and it is a frequent English error. The external flare of the root end is **not** a bore
   flare. [V]
2. **"Approximately cylindrical" vs "inverted cone" is a genuine disagreement in emphasis.**
   Wolfe & Smith 2000 p. 104-2 call it "an approximately cylindrical instrument" [V] — a fair
   acoustic idealisation for a 20→15 mm taper over ~540 mm. Heibonsha's 逆円錐 is the correct
   maker's description. Both are defensible; they are describing the same object at different
   tolerances. Report both.
3. [U] I found **no** published bore profile (diameter as a function of distance along the tube)
   for any shakuhachi. Wolfe & Smith measured impedance, not geometry. Sudo et al. 2025 (§5.6)
   generated 3D models from CT images, which implies real bore profiles exist in that paper; I
   could not obtain it.

## 2. Materials

### 2.1 真竹 *madake* — and the species name is wrong in most English sources

**Headline correction.** English (and much Japanese popular) writing gives madake as
*Phyllostachys bambusoides* Siebold & Zucc. That name is a **synonym**. The currently accepted
name is ***Phyllostachys reticulata*** (Rupr.) K.Koch (1873).

| Name | Status | Evidence |
|---|---|---|
| *Phyllostachys reticulata* (Rupr.) K.Koch | **ACCEPTED** — GBIF usageKey 5677245, exact match, confidence 99 | **[V]** GBIF species-match API, `api.gbif.org/v1/species/match?name=Phyllostachys%20reticulata&strict=true`, fetched 2026-11-13 |
| *Phyllostachys bambusoides* Siebold & Zucc. | **SYNONYM**, acceptedUsageKey 5677245 (i.e. resolves to *P. reticulata*) | **[V]** same API, same date |
| *Phyllostachys edulis* (Carrière) J.Houz. | **ACCEPTED** — a **different** species, usageKey 5290168. This is 孟宗竹 *mōsōchiku* / moso | **[V]** same API, same date |

Corroboration [V]: ja.wikipedia マダケ, raw wikitext via API, revision timestamp
**2026-07-05T03:03:41Z**. Its taxobox gives 学名 = *Phyllostachys reticulata* (Rupr.) K.Koch
(1873), citing **YList** (the standard Japanese plant-name list, `id=5905`, "マダケ（標準）"), and
lists *Phyllostachys bambusoides* Siebold et Zucc. (1843) explicitly under シノニム (synonyms),
citing YList `id=35095` "マダケ（シノニム）". The article also cites **POWO (Kew)** for
*P. reticulata*. Note the article's *prose* opening still says 「学名: *Phyllostachys
bambusoides*」 — an internal inconsistency in the article itself [V].

So: **madake is *P. reticulata*, syn. *P. bambusoides*; it is NOT *P. edulis*.** The user's
suspicion that there is confusion with moso is confirmed, and the mix-up is real and consequential
in Japan — see §2.3.

I attempted to confirm against POWO's own API directly; the endpoint returned non-JSON and I did
not retrieve it [U]. The GBIF result plus ja.wikipedia's YList/POWO citations are, I judge,
sufficient, but **the primary POWO record is a check I did not personally complete**.

Other names [V] ja.wikipedia マダケ: 和名 マダケ（真竹）; also called タケ, **ニガタケ（苦竹）**
"bitter bamboo" (cited to the 農林水産省 / MAFF page `maff.go.jp/j/pr/aff/1301/spe1_02.html`),
真柄竹. Chinese name 剛竹 (alias 桂竹). English: Madake, Giant Timber Bamboo, Japanese Timber
Bamboo.

### 2.2 Why madake specifically

[V] ja.wikipedia マダケ §素材としての利用 and §形態, rev. 2026-07-05. The relevant mechanical
properties, in the article's own terms:

| Property | Japanese | Why it matters for a shakuhachi |
|---|---|---|
| Internodes are long: **30–40 cm** between nodes | 「節の間は30 - 40 cmと長いのが特徴」 (cited to 宮内泰之 監修 2023, p. 43) | A ~540 mm tube containing 7 nodes needs the nodes close-spaced at the root end and the long internodes above; madake's geometry suits the length |
| Culm grows straight and vertical, **10–20 m tall, up to 10 cm thick** | 「稈はまっすぐに垂直に伸びて、高さは…10 m - 20 m…太さは10 cmに達する」 (辻井達一 2006, p. 221) | Straightness and adequate diameter |
| **Elastic / resilient** and strong, with a **low taper rate** from root to tip, yet **thin-walled**, so it works easily | 「竹の根元から先端部にかけての細り率が低く強靭でありながら肉厚は薄いため細工しやすい」 | Low taper = a nearly cylindrical bore without heroic reaming |
| **Dimensionally stable** — little shrink/swell, little change with temperature or humidity, almost no warping, which is why madake is used for 竹尺 (bamboo measuring rules) | 「伸縮が小さく、温度や湿度による変化も小さく狂いが殆どおこらないことから物差しや…竹尺にも用いられている」 | **This is the property that matters most for a wind instrument**, and it is the one English sources never mention |

Note the **tension** here [V]: madake is *thin-walled* (肉厚は薄い) in the culm generally, yet the
shakuhachi needs the *thick-walled* root section (§1.7). Both are true — the root is the atypical
part of the plant. This is exactly why the root end is used and why good shakuhachi bamboo is
scarce. **[U]** I did not find a source that states this reasoning explicitly; the inference is
mine from two verified facts.

### 2.3 Harvesting, curing and ageing

Shakuhachi-specific, from a commercial page — **COMMERCIAL** [V]: `shakuhachi-kaitori.info/how-to-make/`
(a shakuhachi *buying/appraisal* business, i.e. trade-practitioner but not scholarly), fetched
2026-11-13:

| Step | Detail |
|---|---|
| Species | 真竹 madake; the bamboo should be dry / low in moisture |
| **Age at harvest** | **5+ years** — 「生えてから5年以上経過した硬くて古い物」; younger bamboo is soft and may warp after becoming an instrument |
| **Season** | Harvested **in the cold of midwinter**, when the air is dry |
| Oil removal (油抜き) | The bamboo is **heated over fire** to draw out the oil |
| Straightening (矯め) | Warps corrected with a vice or a saw-file; done again before cutting, because naturally grown bamboo always warps |
| **Ageing** | Sun-dried, then **「1～3年寝かせる」 — rested 1 to 3 years** in a shaded, well-ventilated place, so it dries fully and resists deformation |

This is **one commercial source**; treat the 5-year / midwinter / 1–3-year figures as
trade-reported, not scholarly [V as to what the page says, U as to whether the figures are
standard]. I did not find them corroborated in a reference source.

Generic madake curing practice, which contextualises the above [V] ja.wikipedia マダケ
§素材としての利用: madake circulates as 青竹 (green bamboo, freshly cut — easy to get but poor
durability), **晒し竹** (oil removed either **dry**, 火であぶる, by scorching over flame, or **wet**,
苛性ソーダで煮沸, by boiling in caustic soda), **炭化竹** (partially carbonised), bamboo left to
dry naturally **for several months to several years**, and **煤竹 *susudake*** — bamboo smoked for
**decades** in the roof space of a house over an *irori* hearth or a kitchen stove, which is hard,
very durable, has a distinctive colour (煤竹色), and is **difficult to obtain**. [U] *susudake*
is prized for shakuhachi in player lore; **I did not verify that specifically**, only that it is a
prized bamboo material in general.

**Supply context — a genuinely important and little-known fact** [V] ja.wikipedia マダケ §開花:
madake flowers gregariously on a cycle of **about 120 years** and **dies after flowering**. The
last mass flowering and die-off began in **1962**; by **1966 about 40,000 hectares — one third of
Japan's madake forest — had died**. Restoration was attempted but planting mother culms proved
difficult, and only 2,000 ha had been begun by 1970 (cited there to 社団法人国土緑化推進委員会,
『国土緑化20年の歩み』, 1970, p. 180). As a result, in the later Shōwa period **the area ratio of
madake to moso forest in Japan inverted**, and the Japanese bamboo industry shifted to
**moso**-centred material and to **imported Chinese** moso. If the 120-year cycle holds, the next
flowering is expected **around 2090**.

Two consequences:
1. The madake/moso confusion is not merely a naming error — the Japanese bamboo trade genuinely
   became moso-centred, so "bamboo" in a Japanese craft context often *does* mean moso. The
   shakuhachi is one of the holdouts that still needs madake. **[U]** — the inference is mine;
   the Wikipedia article does not mention shakuhachi.
2. Madake is listed by the Ministry of the Environment and MAFF as a **産業管理外来種**
   ("industrially-managed alien species") because its spread damages the *satoyama* environment
   [V] ja.wikipedia マダケ lead, citing a 森林総合研究所 press release of 2017-10-18. So the raw
   material is simultaneously a scarce craft input and a managed invasive.

### 2.4 The oiling / sealing question

**[U] — I could not resolve this, and I want to be plain about it.**

What I verified: in the *making* process the **interior** is coated with 漆 (urushi) [V]
`shakuhachi-kaitori.info/how-to-make/`, and in a *jiari* instrument the whole bore is covered with
*ji* and then lacquered (§3). Heibonsha says the bore is "smoothed and lacquered black or
vermilion" [V, kotobank summary]. The madake article confirms oil is deliberately **removed**
(油抜き) from craft bamboo during curing [V].

What I could **not** verify from any reference-grade source: the widespread player practice of
periodically oiling the bore of a finished instrument, the oil used (camellia oil / 椿油 is the
usual claim), the frequency, or whether it is recommended for *jiari* instruments at all (a fully
lacquered bore arguably does not need it). **I found no reference-grade source either way, and I
deliberately did not fill the gap from memory.** Note the apparent tension worth investigating:
curing removes the bamboo's own oil, and then players are said to add oil back.

### 2.5 Non-bamboo materials

[V] ja.wikipedia 尺八 §物理的構造, transcribed exactly: 「材質は真竹が主流であるが、木製の木管
尺八やプラスチックなどの合成樹脂でできた安価な尺八が開発され、おもに初心者の普及用などの用途で
使用されている。更に近年では3Dプリンターによって制作された尺八や、アルミニウム合金製の「メタル
尺八」なども開発されている。」

My translation: "Madake is the mainstream material, but **wooden *mokkan* shakuhachi** (木管尺八)
and **cheap shakuhachi made of plastic and other synthetic resins** have been developed, used
mainly for beginners and popular diffusion. Further, in recent years **3D-printed** shakuhachi and
**aluminium-alloy "metal shakuhachi"** (メタル尺八) have also been developed."

So the verified non-bamboo list is: **wood, synthetic resin/plastic, 3D-printed polymer, aluminium
alloy.** [V]

**Does material affect tone?** [V] ja.wikipedia states the question has been contested:
「尺八の音色と材質は科学的には無関係とされているが…関係があるとする論争もあった」 — "the
shakuhachi's tone and its material are held to be scientifically unrelated, though there has also
been a dispute claiming they are related." The two cited sources are both **COMMERCIAL /
practitioner** web pages: 大橋鯛山, 「尺八の物理」 (`ohashi-taizan.net`) for the "unrelated"
position, and 泉州尺八工房, 「歌口研究2」 (`senshu-shakuhachi.com/utakuchi2.html`) for "related".
I did not fetch either. **[U]** No peer-reviewed study on shakuhachi wall material was found.

### 2.6 Verified branded non-bamboo instruments and prices

**All of this section is COMMERCIAL.** Prices as listed on **2026-11-13**.

**悠 "Yuu" — VERIFIED to exist as a product.** [V]

- Faber Corporation (株式会社ファベル), product page
  `fabercorporation.com/product-page/プラスティック尺八-悠-shakuhachi-yuu`, fetched 2026-11-13
  **[V, COMMERCIAL]**: listed as **プラスティック尺八「悠」／Plastic Shakuhachi "YUU"**, regular
  price **¥16,500**, sale price **¥15,180**, flat ¥500 domestic shipping, shown **out of stock**.
  Description: 「高品質なプラスチック製で、耐久性に優れ、お手入れも簡単。」 and 「成型プラスティック
  管であるため、調律および音質にばらつきがありません。」 (my translation: "made of high-quality
  plastic, excellent durability, easy to maintain" / "because it is a **moulded** plastic tube,
  there is no variation in tuning or tone quality").
- **Important caveat on "ABS":** the Faber page I actually opened says only
  「高品質なプラスチック製」 / 「成型プラスティック管」 — **it does not name ABS** [V]. The ABS
  attribution comes from a Rakuten listing seen **only as a search snippet**
  (`item.rakuten.co.jp/mishimaya3408/90200/`, "【尺八】悠 1尺8寸 ABSプラスチック製") [U — snippet
  only, page not opened]. So: **"Yuu" is verified; "cast ABS" is plausible and snippet-supported
  but not verified from a page I read.** "Moulded" (成型) is verified; "cast" is a reasonable gloss.
- Neither page I opened names the designer or manufacturer. **[U]**

Yuu price spread across retailers, **all from Yahoo! Japan search snippets only** — I did not open
these pages, so treat as indicative [U, COMMERCIAL]:

| Retailer | Item | Listed price (2026-11-13) |
|---|---|---|
| Faber Corporation (page opened) | プラスティック尺八「悠」 | **¥16,500** list / **¥15,180** sale **[V]** |
| 和楽器家 wagakkiya | プラスチック尺八 悠, 1尺8寸 | ¥16,800 incl. tax (list ¥17,600) [U, snippet] |
| my-best ranking page | 入門尺八「悠」オリジナルセット, 1尺8寸, 5-hole | ¥18,980 reference price [U, snippet] |
| Rakuten | 悠 1尺8寸 ABS plastic | ¥19,250, free shipping [U, snippet] |
| 価格.com, via あぽろんYahoo!店 | **全音 (Zen-On) 入門尺八 悠** | ¥25,850 [U, snippet] |
| 映像と音の友社 eizo-oto | 入門セット「悠」 | ¥39,200 excl. tax / ¥43,120 incl. tax [U, snippet; set contents unknown] |

The 価格.com snippet attributing a 入門尺八 悠 to **全音 / Zen-On** is interesting — it would make
Zen-On the brand owner — but **I could not confirm the material or the maker from any page I
opened. [U]**

**Other branded student instruments: I could NOT verify any.** A 和楽器家 snippet mentions
「胡蝶宝 尺八 楓」 (Kochōhō, model "Kaede", 都山流, 1尺8寸) but gives no material [U, snippet
only]. **I found no verification for any other named plastic/ABS student shakuhachi brand.**

## 3. 地無し *jinashi* vs 地有り *jiari* — the central organological distinction

### 3.1 The distinction itself

[V] ja.wikipedia 尺八 §物理的構造, transcribed exactly — the two adjacent paragraphs:

> 現行の尺八の管の内部は、管の内側に残った節を削り取り、漆の地（じ）を塗り重ねることで管の内径を
> 精密に調整する。これにより音が大きくなり、正確な音程が得られる。
>
> これに対し「古管」あるいは「地無し管」と呼ぶ古いタイプの尺八は、管の内側に節による突起を残し、
> 漆地も塗らない。正確な音程が得られないため、奏者が音程の補正をする必要がある。古典的な本曲の
> 吹奏では、このひとつひとつの尺八のもつ個性もその魅力となっている。

My translation:

> "In the interior of the current shakuhachi, the nodes remaining on the inside of the tube are
> shaved away and the **urushi *ji*** (漆の地) is applied in **successive coats**, thereby
> adjusting the tube's inner diameter **precisely**. By this means the sound becomes **louder**
> and **accurate intonation is obtained**.
>
> By contrast, the older type of shakuhachi called **「古管」(*kokan*, "old tube") or 「地無し管」
> (*jinashi-kan*)** leaves the **protrusions formed by the nodes** on the inside of the tube and
> **does not apply urushi *ji*** either. Because accurate intonation cannot be obtained, **the
> player must correct the intonation**. In the playing of **classical *honkyoku***, the
> **individuality** that each single shakuhachi possesses is itself part of its appeal."

Three things to take from this [V]:

1. *Ji* is a **built-up ground layer that re-shapes the bore**, applied in coats — not a varnish
   or a finish. The adjustment target is the 内径 (inner diameter).
2. The stated acoustic payoff of *ji* is **two** things: **more volume** and **accurate
   intonation**. That is the whole case for *jiari*.
3. ***jinashi* is explicitly tied to *honkyoku*,** and the virtue claimed for it is per-instrument
   **individuality** — not "better tone" in the abstract. This is the right frame.

Note also that 地無し and 古管 are presented as near-synonyms in this source [V] — i.e. in standard
Japanese usage "jinashi" and "old instrument" substantially overlap, because *ji* construction is
the modern norm. That is worth knowing: a Japanese player saying 古管 may mean "jinashi".

### 3.2 What *ji* (地) is actually made of

This is the question most English sources get vague about. The answer is a **lacquer-bound mineral
filler paste** — the same family of technique as *urushi* ground-coats in Japanese lacquerware.

| Recipe | Source | Status |
|---|---|---|
| **漆 (urushi) + 砥石の粉 (whetstone powder) + 水 (water)**, mixed to a paste: 「漆と砥石の粉を水で混ぜ合わせたもの」 | `shakuhachi-kaitori.info/how-to-make/`, fetched 2026-11-13 | **[V, COMMERCIAL]** |
| **砥の粉 (tonoko, polishing/whetstone powder) + 漆** only — the author's own workshop practice, which other makers tell him is **rare** | 遠藤鈴匠 (Endō Reishō), 尺八演奏家・制管師 (performer and bore-maker), 遠藤晏弘尺八工房; blog post 「尺八の下地の真相」, `ameblo.jp/4anglers/entry-12584345884.html`, fetched 2026-11-13 | **[V, practitioner blog]** |
| **石膏 (gypsum/plaster)** — stated to be the **most common** material among other makers today, often blended with 砥の粉 and 漆 | same Endō post | **[V, practitioner blog]** |
| **カシュー下地 (cashew-lacquer ground)** — a coating that uses **no urushi** | same Endō post | **[V, practitioner blog]** |
| **樹脂 (synthetic resin)** grounds | same Endō post | **[V, practitioner blog]** |
| 地の粉 (*jinoko*, the fired-clay ground powder of standard lacquerware) as a distinct ingredient | — | **[U] — not found in any source I read.** The sources say 砥の粉 / 砥石の粉, not 地の粉. Do not assume the lacquerware term transfers |

**A historical claim worth carrying, with its caveat** [V as to what Endō says, U as to truth]:
Endō's post states that classic 銘管 (*meikan*, celebrated old instruments) used **砥の粉** grounds;
that the switch to **石膏 and resin** came with the shakuhachi and *min'yō* booms, when
quick-drying, thickly-appliable materials let makers produce instruments fast for sale; and that
after the booms ended makers **did not return** to 砥の粉, because the older method is far more
laborious and needs different skill. This is one named practitioner's account of his own trade's
history. It is **not independently corroborated** and he has a professional interest in the claim
(his workshop is the rare one still using 砥の粉). Report it as his position.

### 3.3 半地無し *han-jinashi* — the third category everyone omits

[V, COMMERCIAL] `shakuhachi-kaitori.info/how-to-make/`, fetched 2026-11-13: the *ji* coating is
described in **three** grades, not two —

- **地入り** (*ji-iri*, = 地有り): the coating covers the **whole** interior.
- **半地無し** (*han-jinashi*, "half-jinashi"): *ji* goes **only into the sunken node areas** — i.e.
  the depressions are filled to even out the bore, but the bore is not wholly rebuilt.
- **地無し** (*jinashi*): **no *ji* at all.**

**This matters.** The English literature usually presents a binary, but the real continuum is
natural bore → node depressions filled → bore fully rebuilt in *ji*. Most instruments sold as
"jinashi" in practice have *some* intervention; the fully untouched bore is the extreme case. [V
for the three-way taxonomy; U for my claim about what is usually sold]

### 3.4 Acoustic and playing consequences

Verified consequences of **地有り / 地塗り**:

| Consequence | Source |
|---|---|
| **Louder** (音が大きくなる) | **[V]** ja.wikipedia §物理的構造 |
| **Accurate intonation** (正確な音程が得られる) | **[V]** ja.wikipedia §物理的構造 |
| Bore can be adjusted **precisely** (精密に) and iteratively — the maker carves and re-applies *ji* repeatedly until satisfied | **[V]** ja.wikipedia; and `shakuhachi-kaitori.info` §調律: after 地付け, the tone is adjusted by carving the interior and reapplying *ji* repeatedly |
| Note is **easier to produce**; easier for the maker to adjust by coating | **[V, practitioner blog]** 尺八修理工房幻海 blog, 「地無しと地塗り」, 3 Dec 2012, `shakuhatchi.seesaa.net/article/304973409.html`, fetched 2026-11-13 |
| Tone somewhat **harder/stiffer** (「音色はやや硬い」 in the fetched paraphrase) | **[V, practitioner blog]** same post — but see the caveat below |
| **Longer to dry** in making | **[V, practitioner blog]** same post |

Verified consequences of **地無し**:

| Consequence | Source |
|---|---|
| **Intonation must be corrected by the player** | **[V]** ja.wikipedia §物理的構造 |
| Each instrument has marked **individuality**, valued in *honkyoku* | **[V]** ja.wikipedia §物理的構造 |
| **Softer tone**; needs more careful tuning; **limited volume** | **[V, practitioner blog]** 幻海 post |
| **More sensitive** to the bamboo itself and to the player's technique | **[V, practitioner blog]** 幻海 post |
| Can be finished in about **1–2 weeks** (vs. the long drying of a *ji* bore) | **[V, practitioner blog]** 幻海 post |
| A rougher tone, and **less common today** | **[V, snippet only]** `wagakki-hiroba.com/about_shakuhachi/` — snippet, page not opened |

**Caveat on the 幻海 post** [V]: the fetched page was **badly garbled by a character-encoding
error**, and the summariser flagged parts of its reading as a best guess, and could not read the
author's name. So treat the 幻海 rows as **weakly** sourced — directionally right, consistent with
everything else, but not quotable.

**What I could NOT verify** [U]: any **measured** acoustic difference between *jinashi* and *jiari*
— no sound-pressure levels, no spectra, no impedance comparisons, no intonation-deviation
measurements in cents. **Every claim above is qualitative and tradition-internal.** The
"louder"/"softer" contrast is universally asserted and, as far as I can find, **never measured**.
This is the single largest evidential hole in the whole topic.

### 3.5 Which repertoire and which schools prefer which

Verified:

- ***jinashi* ↔ classical *honkyoku*.** [V] ja.wikipedia §物理的構造: 「古典的な本曲の吹奏では、
  このひとつひとつの尺八のもつ個性もその魅力となっている」 (*honkyoku* playing values the
  per-instrument individuality).
- ***jiari* ↔ ensemble and modern music.** [V, kotobank summary] 日本大百科全書 (Nipponica)
  distinguishes **地無し**, suited to classical *honkyoku*, from **地塗り**, suited to **ensemble
  and modern music**. This is a printed-encyclopedia statement, which makes it the strongest
  sourcing in this subsection.

**Why this is the natural split** — the reasoning, which follows directly from §3.4 [V premises, my
inference]: ensemble playing (*sankyoku* with koto and shamisen, modern composed music, Western-pitch
contexts) demands **reliable intonation against other instruments** and **volume to balance
them** — exactly the two things *ji* delivers. Solo *honkyoku* has neither constraint: there is
nothing to tune against, and no one to be drowned out by. What it rewards instead is timbral
individuality and a wide bend range, which an unrebuilt bore supplies. The *komusō* repertoire is
solo religious music (the Edo-period legal framing and the *komusō* themselves are **covered
elsewhere**), so the organology and the repertoire point the same way.

**A caution against over-reading this split, from a parallel research strand** [U — reported to me
by a parallel strand on this project, not independently verified by me]: the Peters score of
Takemitsu's *November Steps* specifies an **ordinary 2尺3寸 "A" instrument**, and **Riley Lee
argues in print against the claim that *jinashi* instruments are superior** — so the strong
*jinashi* preference often attributed to the Watazumi/Yokoyama line may be **largely a Western
accretion**. This is consistent with what I found independently: note how **unromantic** the
Japanese reference framing of *jinashi* is (§3.1) — nodes left protruding, unlacquered, **does not
give accurate pitch so the player must correct it**, with per-instrument individuality offered as
the *compensating aesthetic virtue in honkyoku playing*, **not** as acoustic superiority. Nothing
in any Japanese source I read claims *jinashi* sounds better. Treat "jinashi is the real thing" as
an English-language position, not a Japanese one.

**Not verified** [U]: a school-by-school mapping. ja.wikipedia names 琴古流, 都山流, 明暗流, 上田流,
村治流 and the regional *honkyoku* lineages, but **does not state which schools prefer jinashi or
jiari**. The common English claim that 明暗 (Myōan) lineages favour *jinashi* while 都山 (Tozan)
is *jiari* is **plausible and consistent with the repertoire split, but I could not source it.**
Do not assert it.

### 3.6 法竹 *hotchiku* — the contested term

Reading: **ほっちく** *hotchiku* (also romanised *hochiku*). [V]

**What I verified** [V] via Yahoo! Japan search, fetched 2026-11-13 (titles and snippets; I opened
no page in full, so this subsection is snippet-level):

- The term is **tightly bound to 海童道 *Watazumidō*** and its founder **海童道祖 *Watazumido
  Shuso*** (also styled 海童道宗祖 / 海童道老師). In 海童道, the instrument is called **法竹
  (ホッチク)** or **定具** (*jōgu*, "blowing-discipline implement"). Recordings are titled simply
  「法竹」 (e.g. a 1968 release), and a record 「法竹と尺八」 ("Hotchiku and Shakuhachi") exists —
  the title itself **contrasts** hotchiku with shakuhachi.
- A **maker explicitly equates the terms**: 遠藤健二 (Endō Kenji), Shimo-Ina, Nagano,
  `otomoribeat.wixsite.com/chikuon`, headlines his business
  「法竹"ほっちく"（地無し尺八）製作販売」 — "hotchiku (= *jinashi* shakuhachi), made and sold". His
  stated route in was encountering **Watazumidō's hotchiku recordings in 1995**.
- One product description glosses hotchiku as **a plainer thing than a shakuhachi — "just a tube
  of natural bamboo"** — with lengths ranging from **about 30 cm up to roughly a child's height**.
  [V, snippet] That length range is far wider than the shakuhachi's (§4).

**The contest, stated carefully.** The evidence supports exactly the user's caution:

1. *hotchiku* is a **lineage term**, originating in and belonging to 海童道 — not a neutral
   organological category. [V, snippet-level]
2. It has nonetheless **leaked into general use as a near-synonym for "heavy jinashi
   instrument"** — demonstrated by Endō Kenji's own business copy, which parenthesises it as
   「地無し尺八」. [V]
3. Whether other lineages accept the term, **I could not determine** — the fetch explicitly
   reported that the snippets do not settle it. **[U]**
4. The 海童道 position was reportedly that these are **not shakuhachi at all** (hence 定具,
   "implement", and the 「法竹と尺八」 contrast). **[U] — inferred from titles and snippets; I did
   not read a statement of doctrine.**

**Practical guidance for the skill:** use 地無し *jinashi* as the organological term. Use 法竹
*hotchiku* only when describing 海童道 or a maker who self-describes that way, and say that it is a
lineage term. Do **not** present *hotchiku* as simply "long jinashi shakuhachi".

**Addendum from a parallel research strand** [U — reported to me by a parallel strand on this
project, not independently verified by me, but it **sharpens rather than contradicts** what I found
above]: **法竹 is Watazumi Dōso's own coinage, made in order to refuse the word 尺八** — part of a
consistent refusal-vocabulary alongside **道曲 *dōkyoku*** (refusing 本曲 *honkyoku*) and **道具
*dōgu*** for his instruments. On that account the term is not a neutral organological category at
all; it is **one man's refusal-vocabulary, later generalised in English**. This fits my point 4
above exactly, and it explains the 定具 / 「法竹と尺八」 evidence: the contrast was the point.

## 4. Length, pitch, and the naming system

### 4.1 The units, verified exactly

**[V]** ja.wikipedia 寸 (rev. **2026-06-18T19:38:03Z**) and 尺 (rev. **2026-09-27T14:14:52Z**), raw
wikitext via API, fetched 2026-11-13:

| Unit | Definition | SI value |
|---|---|---|
| **1 尺 (*shaku*)**, 曲尺 *kanejaku* — the ordinary carpenter's shaku | **exactly 10/33 m**, fixed in the Meiji period | **≈ 303.030 mm** |
| **1 寸 (*sun*)** | **exactly 1/33 m = 1/10 尺** | **≈ 30.303 mm = 3.0303 cm** |
| 1 分 (*bu*) | 1/10 寸 | ≈ 3.03 mm |

Legal basis cited there [V]: 計量法施行法 (Law 208 of 1951), Art. 4(1). Shakkanhō was abolished as
a system of legal measurement units by the 計量法 of **1958**, and its use in commerce was
prohibited from **1 April 1966** — yet the shakuhachi still names itself in it [V].

**So the user's figures are confirmed: 1 尺 = 30.3 cm, 1 寸 = 3.03 cm.** Be precise that this is
the **曲尺 kanejaku**. There is also the **鯨尺 *kujirajaku*** (the cloth shaku), legally 25/66 m
≈ **378.788 mm**, which is 1.25× the kanejaku [V]. A shakuhachi measured in *kujirajaku* would be
68.2 cm — so naming the right shaku matters.

### 4.2 Why 尺八 means "one shaku eight sun" — and the 54.5 cm arithmetic

My computation from the verified unit values:

> 1 尺 8 寸 = 303.030 mm + (8 × 30.303 mm) = 303.030 + 242.424 = **545.45 mm = 54.545 cm**

which rounds to the **54.5 cm** every Japanese source gives. [V for the units; the arithmetic is
mine] — and it is worth noting explicitly that **54.5 cm is not an empirical measurement of
instruments, it is the modern kanejaku converted.**

**The etymology** [V] ja.wikipedia 尺八 §概要: 「名称は、標準の管長が一尺八寸であったことに由来し」
— the name derives from the standard tube length having been 1 shaku 8 sun. The leading account
(有力な説) is from the 「呂才伝」 in the 『旧唐書』 (*Jiu Tang shu*, Old Book of Tang): the
early-7th-century Tang court musician **呂才 (Lü Cai)**, when making vertical flutes whose 筒音
were tuned to the **十二律**, found that **the one producing 黄鐘 — the Chinese standard pitch,
which in the Japanese twelve-*ritsu* system is 壱越 *ichikotsu*, i.e. Western D — was one shaku
eight sun**. Cited there to 久保田敏子, 『よくわかる箏曲地歌の基礎知識』 (当道音楽会 ed.), p. 212,
ISBN 9784560036846, and to 月渓恒子, ch. 16 「尺八楽」, p. 384. My translation.

**A trap: 黄鐘 has two different referents.** In the Chinese *lü* system 黄鐘 *huangzhong* is the
foundational pitch, mapped here to **D**. In the Japanese 十二律, 黄鐘 *ōshiki* is **A** — and
indeed the length table below gives 一尺一寸管 and 二尺三寸管 as 「A（黄鐘）」 [V]. Same characters,
different note. Do not conflate them.

**A lovely ancillary fact** [V] ja.wikipedia 尺: the unit 尺 itself was **originally defined from a
pitch pipe**. The 律暦志 of the 『漢書』 defines the 分 as the width of one grain of black millet,
taking 90 grains laid in a row as "the length of the *huangzhong*" (the pipe sounding the
foundational pitch); 10 分 = 1 寸, 10 寸 = 1 尺. Quoted there from the 漢書:
「以子穀秬黍中者、一黍之広、度之九十分、黄鐘之長。一為一分、十分為寸、十寸為尺…」. So 尺八 is a
length named after a pitch, in a unit that was itself named after a pitch.

### 4.3 Resolving the 54.5 cm vs 43.7 cm discrepancy

The kotobank encyclopedias disagree, and the resolution is units, not fact.

| Source | Figure | |
|---|---|---|
| 改訂新版 世界大百科事典, 精選版日本国語大辞典, デジタル大辞泉, ブリタニカ Japan, マイペディア, 音楽用語ダス, 日本文化いろは事典 | **about 54.5 cm** | [V, kotobank summary] |
| **日本大百科全書 (Nipponica)** | **about 43.7 cm**, attributing the name to the **Tang-era 律尺 (*lüchi*) foot** | [V, kotobank summary] |
| ja.wikipedia 尺八, with an explicit warning | 「ただし時代と国によって「尺」の単位の実際の長さが違うので注意が必要であり、日本の江戸時代の普化尺八では約54.5 cmである。」 — "the actual length of the unit 尺 differs by era and country, so caution is needed; for the Edo-period Japanese *fuke* shakuhachi it is **about 54.5 cm**." | **[V]** |

**My resolution** [V premises, inference mine]: Nipponica is measuring 1.8 shaku in the **Tang
shaku**, not the modern Japanese kanejaku. 43.7 cm ÷ 1.8 = **24.3 cm per shaku**, which matches the
**Tang 小尺 (small shaku), given as about 24.6 cm** in ja.wikipedia 尺 [V]. So the two figures are
the *same* 1.8 shaku expressed in two different historical feet. The 54.5 cm applies to the modern
and Edo-period instrument; ~43–44 cm is the ancient/Chinese measure. (ja.wikipedia separately gives
the surviving 古代尺八 an average length of **40 cm** [V] — also in the right region, and note
Britannica Japan gives "about 40 cm" too [V, kotobank summary].) **This is a reconciliation, not a
contradiction, and English sources that report "43.7 cm" for a modern shakuhachi have simply
mis-transcribed Nipponica.**

### 4.4 The standard instrument and D4 — verified

| Claim | Status |
|---|---|
| The standard instrument is the **一尺八寸管** (*isshaku-hassun-kan*), whose **筒音 *tsutsune*** (the note with all finger holes closed, = its lowest note) is **壱越 *ichikotsu* = D4** | **[V]** ja.wikipedia §筒音: 「標準の尺八は、日本の十二律で壱越（D4）の筒音を持つ一尺八寸管である。」 Corroborated by the §正律 table and by Heibonsha/Nipponica [V, kotobank summary] |
| **筒音** is the technical term for the all-closed note, and it is the instrument's lowest note | **[V]** ja.wikipedia §筒音: 「尺八の手孔をすべて塞いだときの音を筒音と呼ぶ。これはその尺八で出すことのできる最低音である。」 |
| The lowest note is called **ロ *ro*** in both 琴古流 and 都山流 notation | **[V]** ja.wikipedia §音域・音階 (notation itself: covered elsewhere) |
| **D4 ≈ 294 Hz measured** — Wolfe & Smith's Fig. 2 upper pair compares "the lowest notes (named D4 and *ro*) on the two instruments, which are quite similar in pitch", with the flute note labelled **D4, 294 Hz** | **[V]** Wolfe & Smith 2000, p. 104-4. (D4 in equal temperament at A=440 is 293.665 Hz, so 294 Hz is the expected value — my arithmetic) |

So **D4 is verified**, from Japanese reference sources, Japanese Wikipedia, and an acoustics paper
that measured an actual instrument of standard length.

### 4.5 The full length/pitch table

**[V]** transcribed directly from the ja.wikipedia 尺八 §正寸と正律 wikitable, rev. 2026-09-19. The
"筒音（乙ロ）" column is the all-closed low-register note; 別名 is the pitch-name alias.

| 正律 (length) | Decimal shaku | Computed length (kanejaku), mine | 筒音 (乙ロ) | 十二律 name | Alias |
|---|---|---|---|---|---|
| 一尺一寸管 | 1.1 | 33.3 cm | **A4** | 黄鐘 | A管（黄鐘管） |
| 一尺二寸管 | 1.2 | 36.4 cm | **A♭4** | 鳧鐘 | A♭管（鳧鐘管） |
| 一尺三寸管 | 1.3 | 39.4 cm | **G4** | 双調 | G管（双調管） |
| 一尺四寸管 | 1.4 | 42.4 cm | **F♯4** | 下無 | F♯管（下無管） |
| 一尺五寸管 | 1.5 | 45.5 cm | **F4** | 勝絶 | F管（勝絶管） |
| **一尺六寸管** | 1.6 | 48.5 cm | **E4** | 平調 | E管（平調管） |
| 一尺七寸管 | 1.7 | 51.5 cm | **E♭4** | 断金 | E♭管（断金管） |
| **一尺八寸管 — the standard** | **1.8** | **54.5 cm** | **D4** | 壱越 | **D管（壱越管）** |
| 一尺九寸管 | 1.9 | 57.6 cm | **C♯4** | 上無 | C♯管（上無管） |
| 二尺管 | 2.0 | 60.6 cm | **C4** | 神仙 | C管（神仙管） |
| 二尺一寸管 | 2.1 | 63.6 cm | **B3** | 盤渉 | B管（盤渉管） |
| 二尺二寸管 | 2.2 | 66.7 cm | **B♭3** (see note) | 鸞鏡 | B♭管（鸞鏡管） |
| **二尺三寸管** | 2.3 | 69.7 cm | **A3** | 黄鐘 | A管（黄鐘管） |

**Error in the source, corrected** [V]: the Wikipedia table prints 二尺二寸管 as **"Bb4"**. That
must be **B♭3** — it sits between B3 (二尺一寸) and A3 (二尺三寸) in a strictly descending
semitone series. **An octave typo in the source.** (一尺一寸管 = A4 is *correct*: 7 sun shorter
than 1.8 shaku = 7 semitones above D4 = A4.)

**The rule** [V] ja.wikipedia §筒音 and 音楽用語ダス via kotobank: lengths run **in 1-sun steps**,
and **each sun is one semitone** — 「長さのバリエーションは、半音分ずつ寸刻みで」. Heibonsha says
the same: a 1-sun change shifts the pitch by about a semitone [V, kotobank summary]. (The physics:
one semitone is a factor of 2^(1/12) ≈ 1.0595 in frequency, so from 54.5 cm one semitone down needs
+5.95% length ≈ +3.24 cm, against 1 sun = 3.03 cm. **The sun-per-semitone rule is an approximation
that is about 7% short, and it drifts across the range** — which is precisely why 正寸 and 正律
diverge. That computation and inference are mine [U as published claim].)

**Range of lengths actually made.** The sources disagree on the extremes, which is itself worth
reporting:

| Range given | Source |
|---|---|
| **一尺一寸 to 二尺三寸** (1.1–2.3) in 1-sun steps | **[V]** ja.wikipedia §筒音 and §正寸と正律 table |
| **about 1 尺 2 寸 up to about 3 尺** (≈1.2–3.0) | 改訂新版 世界大百科事典 (Heibonsha) [V, kotobank summary] |
| **about 1 尺 3 寸 to 3 尺** (1.3–3.0) | 日本大百科全書 (Nipponica) [V, kotobank summary] |
| 1 尺 1 寸 to 2 尺 3 寸, per the printed dictionaries' "short and long variants" | デジタル大辞泉 mentions short and long variants without numbers [V, kotobank summary] |

So the **well-attested span is roughly 1.1–3.0 shaku (≈33–91 cm)**, with Wikipedia's table stopping
at 2.3 and the printed encyclopedias reaching 3.0. **[U]** The user's "3.0+" — instruments longer
than 3 shaku — **I could not verify from any source**; they exist in the *jinashi*/*hotchiku* world
(where one snippet described lengths "up to roughly a child's height", §3.6) but I have no citable
figure. [U] I also found **no** source giving the pitch of a 3.0-shaku instrument; by the semitone
rule it would be ~F♯3 (12 sun below 1.8 shaku = one octave below D4 would be 3.0 shaku exactly
→ **D3**; by the table's logic 3 尺 = 2.3 shaku + 7 sun = A3 − 7 semitones = **D3**. My arithmetic,
unverified against any source).

### 4.6 Which lengths are used for what

**[V]** ja.wikipedia §筒音, transcribed: 「標準の尺八は…一尺八寸管である。次いで、春の海などで
使用される一尺六寸管（筒音:平調（E4））や、二尺三寸管（筒音:黄鐘（A3））などが使用される。…
一尺八寸管・一尺六寸管以外のものはそれに比べ使用頻度ははるかに少なく、一尺二寸管や二尺二寸管
などはめったに用いられない。」

My translation and the resulting hierarchy:

1. **1.8 shaku (D) — the standard, and the ensemble standard.** [V]
2. **1.6 shaku (E) — the clear second**, specifically named as the instrument used in 『春の海』
   (*Haru no Umi*, Miyagi Michio, 1929 — the single most-played piece in the modern repertoire).
   [V]
3. **2.3 shaku (A)** — the named third. [V]
4. Everything else is **"far less frequent"**, and **1.2 and 2.2 shaku are "rarely used"**. [V]

The practical reading: **1.8 and 1.6 are the two instruments a working player owns**; the rest are
repertoire-specific. [V]

**Why 1.8 is the ensemble standard** [U as a sourced claim; the premises are V]: in 三曲合奏
(*sankyoku*, with shamisen and koto) the shakuhachi replaced the 胡弓 after the Meiji Restoration
and now normally takes that part [V, ja.wikipedia §三曲合奏 — genre detail is **covered
elsewhere**]. The D-fundamental instrument fits the common koto tunings. **I did not find a source
stating the tuning reason**, so do not assert it.

### 4.7 正寸 vs 正律 — the distinction that makes the naming system coherent

This is the most useful thing in §4 and it is almost entirely absent from English writing.

**[V]** ja.wikipedia §正寸と正律, transcribed and translated by me:

> 「基本的に尺八の長さと筒音の音程は対応しているが、内径の構造によっては正確に対応しない場合も
> 多くある。…「正寸」は文字通り「長さに正確」なので、「正寸一尺八寸管」と示された場合、それは
> 正しく一尺八寸の長さである反面、筒音が正確に壱越(D)である保証は無い。対して「正律」は「音律に
> 正確」なので、「正律一尺八寸管」と示された場合筒音は正しく壱越(D)であり、長さが正確に一尺八寸
> とはなっていない可能性もある。現在は正律で示すのが主流となっており、より明瞭にするため、筒音
> によって「D管」「E管」「A管」という呼び方をされることもある。」

> "Basically the length of a shakuhachi and the pitch of its *tsutsune* correspond, but depending
> on the structure of the **bore** there are many cases where they do not correspond exactly. …
> **正寸 *seisun*** means literally 'exact in length': an instrument labelled 正寸一尺八寸管 is
> correctly 1 shaku 8 sun long, but **there is no guarantee its *tsutsune* is exactly 壱越 (D)**.
> By contrast **正律 *seiritsu*** means 'exact in pitch': an instrument labelled 正律一尺八寸管 has
> a *tsutsune* correctly at 壱越 (D), but **its length may not be exactly 1 shaku 8 sun**.
> **At present labelling by 正律 is mainstream**, and for extra clarity instruments are sometimes
> called 「D管」「E管」「A管」 after their *tsutsune*."

Consequences for the skill:

- **"1.8 shaku" on a modern instrument is a pitch name, not a measurement.** A modern 正律 1.8 may
  be a centimetre or two off 54.5 cm. This is the single most common English mis-statement about
  shakuhachi dimensions. [V]
- **Why they diverge: the bore.** The source names 内径 structure as the cause [V]. Physically, a
  bore built up with *ji* has different end-correction and taper than a natural bore, so length and
  pitch decouple — which is *exactly* the *jinashi*/*jiari* axis of §3. The two distinctions are
  the same fact seen twice. [V premises, my inference]
- **The convention the user asked about — "2.4 in B".** The verified Japanese convention is
  **length + pitch-letter**: 「二尺三寸管 / A管」. [V] A **2.4-shaku** instrument is **not in the
  Wikipedia table at all**, and would by the semitone rule be A♭3/G♯3, not B. "2.4 in B" does
  **not** follow from the table. **[U]** I could not verify "2.4 in B" or any English-market naming
  convention of that shape, and I suspect either a different length-pitch mapping in the
  English-language *jinashi* market or a transcription slip. **Flagging rather than guessing.**

### 4.8 A=440 vs older pitch standards

**[U] — I could not source this for the shakuhachi, and it is a real gap.**

- ja.wikipedia 尺八 gives the pitch system entirely in Western note names (D4, E4, A3) and the
  Japanese 十二律 names, and **never states a reference frequency** [V that it is absent].
- The only A=440 statement I found in a measured source concerns the **flute** they compared
  against, not the shakuhachi: Wolfe & Smith note their classical flute's "scale has been adjusted
  to play at A = 440 Hz" [V, p. 104-3]. Their shakuhachi's low note is labelled in a figure shared
  with a 294 Hz flute D4, which **implies** A≈440 but does not state it. [V/U]
- **What I could not establish:** whether Japanese makers cut to A=440, A=442 (common in Japanese
  orchestral practice) or some other reference; whether *sankyoku* ensembles use a different
  standard; or what pitch standard pre-Meiji instruments were made to. **No source found either
  way. Do not assert a figure.**
- One thing *is* safe to say and matters [V]: because 正律 labelling means the maker tunes to a
  pitch rather than a length, **the pitch standard is baked into the instrument at making time** —
  so the question of *which* standard is not academic. A 正律 1.8 is only "D" relative to some
  reference.

## 5. Acoustics

### 5.1 What exists in the literature, honestly

I searched Crossref systematically (`api.crossref.org/works?query.bibliographic=…`, fetched
2026-11-13) on *shakuhachi acoustics*, *Yoshikawa shakuhachi*, *Yoshikawa air-reed instruments*,
*shakuhachi impedance*, and *shakuhachi pitch bend meri*. The complete set of quantitative
acoustics items that exists, as far as Crossref knows:

| Item | Type | Did I read it? |
|---|---|---|
| **Wolfe, Joe & Smith, John, "Acoustics of the air-jet family of instruments", *Proc. WESTPRAC VII*, Kumamoto, 3–5 Oct 2000, pp. 575–580.** PDF: `newt.phys.unsw.edu.au/jw/WOLFE.pdf` | Full conference paper with measurements | **YES — all 6 pages [V].** This is the backbone of this section |
| Wolfe, J. & Smith, J., "Some acoustics of the shakuhachi—and of the shakuhachi player's face", *JASA* **108**(5 Suppl.) (Nov 2000): 2552, DOI **10.1121/1.4743469** | **Meeting abstract only** | Metadata via Crossref [V]; abstract text and method via the UNSW project pages `/jw/shakuhachiresults.html` and `/jw/ASA.html` [V]. **The record is an abstract; there is no full paper** |
| **Yoshikawa, Shigeru & Kajiwara, Kazue, "Cross fingerings and associated intonation anomaly in the shakuhachi", *Acoustical Science and Technology* 36(4) (2015): 314–325.** DOI **10.1250/ast.36.314**. Both at the Graduate School of Design, Kyushu University | **Full 12-page journal paper** | **NO — [U].** J-STAGE returned **HTTP 500** on every route I tried (`/_article`, `/_article/-char/en`, `/_pdf`, `/_pdf/-char/ja`, `/_html/-char/en`), with a browser user-agent and without, on retry. Crossref holds **no abstract** for it. **This is the most important thing I could not get**, and its title alone tells you cross-fingering intonation anomaly is a measured, published problem |
| Yoshikawa, S., "Changes in acoustical design from ancient shakuhachi to modern shakuhachi", *JASA* **131**(4 Suppl.) (Apr 2012): 3297, DOI **10.1121/1.4708326** | **Meeting abstract only** | Metadata only [U]. **Directly on this file's topic** (it is literally about the *gagaku*→modern design change, i.e. §7) and I could not obtain even the abstract text |
| Ziemer, Tim, "Sound Radiation Characteristic of a Shakuhachi with different Playing Techniques", *Proc. ISMA*, pp. 549–555, DOI **10.25366/2020.08** | Conference paper | Metadata only [U]. Crossref holds no abstract, no full-text link. A LinkedIn snippet pointed to `conforg.fr/isma2014/cdrom/data/articles/000121.pdf` which **404s**. Note the Crossref deposit date (2020-04-27) and the "ISMA-14" container conflict with the conforg path's "isma2014" — **I cannot even confirm the year**. Would be the source for directivity/radiation data |
| Sudo, S., Nakao, M., Mizuno, A. & Takahashi, Y., "3D model generation from CT images via morphological operations for reproduction of a shakuhachi by additive manufacturing", *Proceedings of Meetings on Acoustics* **60** (2025): 035008, DOI **10.1121/2.0002426** (189th ASA / ASJ joint meeting) | Conference proceedings | Metadata only [U]. `pubs.aip.org` redirected to a Silverchair CDN URL that **served a completely different article** (a phase-change-material fluid-dynamics paper). **This is the likely source of a real measured bore profile** (CT-derived) and I could not get it |
| Seltzer, "Shakuhachi pitch and intonation: Application to computer music composition", *JASA* (Nov 1983), DOI 10.1121/1.2020840 | Meeting abstract | Metadata only [U] |

**Plainly: the published quantitative shakuhachi acoustics literature is thin — on the order of one
full measured paper (Wolfe & Smith 2000) plus one full journal paper I could not open (Yoshikawa &
Kajiwara 2015) plus a handful of abstracts.** There is nothing resembling the literature on the
Western flute or clarinet. Every number below therefore comes from Wolfe & Smith 2000 or from
ja.wikipedia.

Also noted and **not** usable: the Routledge volume *Flute and Shakuhachi* (DOI
10.4324/9781315077192, 2020) contains a dozen relevant chapters including Tukitani Tuneko, Seyama
Tōru & Simura Satosi, "The Shakuhachi: The Instrument and its Music, Change and
Diversification" (pp. 103–129) and Castellengo & Fabre, "The Contemporary Transverse Flute and the
Shakuhachi: Convergences" (pp. 217–237) — **Castellengo and Fabre are serious flute acousticians**,
so that chapter is very likely the best organology/acoustics synthesis in English. **I have
Crossref metadata only; Taylor & Francis is inaccessible. [U]** Flagging as the top acquisition
priority. (Tukitani Tsuneko is the same 月渓恒子 cited throughout ja.wikipedia.)

### 5.2 The end-blown air-reed mechanism, and the one fact that organises everything

**[V]** Wolfe & Smith 2000, pp. 104-1 to 104-2:

- The shakuhachi belongs to the **air-jet family** with the transverse flute, recorder, quena,
  syrinx, ocarina and organ pipe. "The spontaneous wave produced by the air-jet striking an edge
  excites a column of air in a long, thin bore. Under appropriate conditions of jet speed and
  length, the jet can be deflected alternately into and out of the embouchure hole so as to excite
  large oscillations at one or more of the resonant frequencies of the bore."
- **The instrument is OPEN at the excitation point.** "The air jet is open to the radiation field,
  so at the mouth end of the instrument, the boundary condition imposed on the standing waves is a
  large acoustic flow with relatively little variation in the acoustic pressure."
- **Therefore it operates at the MINIMA of the acoustic input impedance Z(f)**, not the maxima.
  "For air-jet instruments, stable oscillation régimes (the ordinary notes of the instruments)
  occur at frequencies for which Z(f) is a minimum." Reed and lip-reed instruments are the
  opposite: the player's mouth closes the input aperture, giving high pressure and low flow, so
  they work at Z maxima.
- "Since the jet is not sinusoidal, such regimes usually depend upon **minima in Z(f) occurring at
  or near harmonics of the fundamental frequency** of oscillation."

**Measured dynamic range of Z(f): "Z(f) can vary over 60-70 dB"** and elsewhere "Our acoustic
impedance varies over some 70 dB" [V]. This is why shakuhachi impedance measurements are rare:
minima are *small* pressure signals, and acoustic flow is "virtually impossible to measure
accurately", so a very large dynamic range is needed. [V]

**Why this fact organises everything else:** because the instrument is open at the blowing end, the
**radiation load at the blowing end is part of the resonator**, and the player's face is sitting in
that radiation load. That is the whole mechanism of *meri*/*kari* (§5.3). On a transverse flute the
embouchure hole is a small aperture in a closed head joint; on the shakuhachi the entire tube end
is open and the chin is the stopper. [V]

### 5.3 *Meri*/*kari* as acoustics, not just technique

**The player's side** [V] ja.wikipedia 尺八 §奏法, transcribed:
「唇と歌口の鋭角部（エッジ）との距離を変化させることで、音高（音程）を変化させる。音高を下げる
ことを**メリ**、上げることを**カリ**と呼ぶ。メリ、カリの範囲は開放管（指で手孔を押さえない）の
状態に近いほど広くなり、メリでは最大で半音4個ぶん以上になる。通常の演奏に用いる範囲はメリで2半音、
カリで1半音程度）。奏者の動作としては楽器と下顎（下唇よりやや下）との接点を支点にして顎を引く
（沈める）と「メリ」になり、顎を浮かせると「カリ」になる。」

My translation: "Pitch is changed by varying **the distance between the lips and the sharp-angled
part (the edge) of the utaguchi**. Lowering the pitch is called **meri**, raising it **kari**. The
range of meri and kari **widens the closer the instrument is to the open-tube state** (no fingers
on the holes); **in meri it reaches a maximum of more than 4 semitones**. The range used in normal
playing is **about 2 semitones of meri and about 1 semitone of kari**. In terms of the player's
action, taking the chin in (sinking it), pivoting on the contact point between the instrument and
the lower jaw (slightly below the lower lip), gives *meri*; floating the chin gives *kari*."

**These are the quantitative pitch-bend figures the user asked for** [V]:

| Quantity | Value |
|---|---|
| **Maximum *meri*** (downward bend) | **more than 4 semitones** |
| ***Meri* in normal playing** | **~2 semitones** |
| ***Kari* in normal playing** | **~1 semitone** |
| Dependence on fingering | **Bend range widens as the tube approaches fully open** |

For comparison, a Western flute's embouchure bend is on the order of a semitone or less in
practice; **>4 semitones from a single hole position is extraordinary** and is the single most
distinctive acoustic property of the instrument. [V for the shakuhachi figure; **[U]** for the
flute comparison — I did not source a flute bend figure.]

**The acoustic explanation, measured** [V] Wolfe & Smith 2000, pp. 104-5 to 104-6, plus
`/jw/ASA.html`. They explicitly call this "'Lipping up or down' — the effect of the radiation
impedance at the embouchure", and the mechanism has **three** components, all of which **increase
the radiation impedance and so lower the frequencies of the minima in Z(f)**:

1. It **shortens the length of the jet**.
2. It **partially occludes** the blowing aperture with the lower lip.
3. It **reduces the solid angle available for radiation**, because the face acts as a **baffle**.

Quoting the mechanism for the shakuhachi specifically [V, p. 104-5]: "In shakuhachi performance,
pitch control by embouchure is sometimes a more prominent feature of performance. **The fact that
the chin closes the pipe means that the area which links the bore to the radiation field, and the
solid angle available, can be controlled by movements of the head and arms.** Although these
parameters are difficult to measure directly, we expect that they have a substantial effect on the
impedance minima and thus on the pitch and timbre of notes played."

So: **chin position changes the effective radiation geometry at the open blowing end, which shifts
the impedance minima, which changes the pitch.** This is exactly the user's framing — *meri*/*kari*
as an acoustic fact about blowing-edge/radiation geometry, not merely a technique. [V]

**Their quantification of the radiation load** [V, p. 104-5/6]: for a baffled pipe of radius *a*,
the radiation impedance "nearly equals that of an ideal tube with a length about **0.85a**". With
*g* the open fraction of the hole and *h*2π steradians the radiation solid angle,

> Z_rad = 0.85·a·jωρ / (√g · h · S_emb)

They simulated the radiation load with a short coupling pipe: **6 mm** long for the flute and
**9 mm** long for the shakuhachi, both **7.8 mm** in diameter. For the flute, with S_emb = 90 mm²,
this gives **h√g = 0.3** — "a little less than the value when g = h = 0.5". For the shakuhachi they
state the embouchure geometry "is more complicated and the area through which the bore radiates is
more difficult to define", so they used the flute-equivalent 6 mm load for plotting. [V]

**How they measured the face effect** [V] `/jw/ASA.html`, fetched 2026-11-13: they measured the
instrument's acoustic impedance alone, then measured how the player's face baffles it, by **cutting
a plastic shakuhachi so an impedance probe could sit inside it**. The player was **Riley Lee**.
Their finding: "**More obstruction by the lips and face lowers the resonance frequencies. The
results matched how much players know they can flatten pitch**, and they helped explain timbre
differences between notes." [V — note this is a *qualitative* validation of the player's bend
range; **they publish no cents figure** [U]].

**A caveat on the measured instrument** [V, p. 104-3]: the shakuhachi studied was a **Bei Shu model
(Nagano Ken, Japan)** of standard length, with "a bamboo body, but **the bore itself is
synthetic**. This is an advantage for scientific purposes, as it allows a greater degree of
reproducibility." **So the only well-measured shakuhachi impedance spectra in the literature are of
an instrument with a synthetic bore** — which is a *jiari*-like controlled bore, not a natural one.
That is a real limitation on generalising to *jinashi* instruments, and it compounds the gap noted
in §3.4.

### 5.4 The registers 乙 *otsu* / 甲 *kan* / 大甲 *dai-kan*

**The nomenclature and extent** [V] ja.wikipedia §音域・音階, transcribed: 「基本的には音域は
2オクターブ強（一尺八寸管でC4-E6）である。1オクターブ目を乙、2オクターブ目を甲という。用いられる
頻度は少ないが、倍音を用いてその上の約1オクターブの音を出すことができ、3オクターブ目を大甲という。」

My translation: "The range is basically a little over **2 octaves** (**C4–E6** on a 1.8-shaku
instrument). The first octave is called **乙 *otsu***, the second **甲 *kan***. Used less
frequently, **harmonics** can be used to produce notes about one octave above that, and the third
octave is called **大甲 *dai-kan***."

| Fact | Status |
|---|---|
| Normal range on 1.8 shaku: **C4–E6**, "a little over two octaves" | **[V]** ja.wikipedia |
| Note that **C4 is below the D4 *tsutsune*** — the extra semitones at the bottom come from **大メリ** (the fingering table gives C4 as 乙 ロ大 in Kinko, 乙 (ロ)メ in Tozan). **So the "lowest note" of a 1.8 shaku is D4 as a tube but C4 as an instrument**, via a ~2-semitone *meri* — consistent with §5.3 | **[V]** ja.wikipedia fingering table, §音域・音階 |
| 大甲 reaches **up to about E7-equivalent** on 1.8 shaku with advanced technique | **[V]** ja.wikipedia: 「高度の技術によれば一尺八寸管のE7相当程度まで可能であり」 |
| **One single note is extremely difficult: F6-equivalent on 1.8 shaku** (「全音域中で、一尺八寸管のF6相当の1音だけは演奏が極めて困難である」) | **[V]** ja.wikipedia. A delightfully specific fact, and clearly a register-crossing artefact |
| Heibonsha gives the range as **about two and a half octaves**, with first octave 呂 *ro* **or** 乙 *otsu*, second 甲, third 大甲 — note **呂** as an alternative name for the low register | **[V, kotobank summary]**; 音楽用語ダス agrees on about two and a half octaves [V, kotobank summary] |

**How the registers are produced — the measured mechanism** [V] Wolfe & Smith 2000, p. 104-4: with
all tone holes closed, "the instruments most closely resemble a simple pipe, and their impedance
spectra qualitatively resemble those of an open pipe. **The first several minima in Z(f) are very
nearly harmonic.** When the lowest note is sounded, harmonics of the note coincide with each of
these minima. Further, **the notes corresponding to the first several minima can be sounded on
their own by changing the length and speed of the jet.**"

That last sentence **is** the register mechanism: 乙 → 甲 → 大甲 is the player selecting
successively higher (near-harmonic) impedance minima by **changing jet length and jet speed** — i.e.
by lip aperture, blowing pressure and the lip-to-edge distance. It is overblowing, and it works
cleanly only because the minima of a nearly-cylindrical open pipe are nearly harmonic. [V]

**And the measured reason the top register is hard** [V, p. 104-5]: "An array of such holes
(fingerings for the higher notes) produces **a filter which transmits higher frequencies. This
reduces the standing waves and thus the playability of higher notes.**" The open finger holes
behave as a high-pass filter, so for high fingerings the standing wave — and with it the usable
impedance minimum — is weakened. Also: with holes open, "**fewer of the notes corresponding to
minima are playable**", and after opening even one hole "only the first few impedance minima are
now harmonic". [V]

### 5.5 Cross-fingerings, and why holes are not where you would cut the tube

**[V]** Wolfe & Smith 2000, p. 104-2 — a measured-instrument explanation of something usually
presented as mere fingering lore:

- "Beginning with all the tone holes closed, successive opening of the holes from the end remote
  from the mouthpiece shortens the effective length of the tube. **The standing wave, however, does
  not fall to zero at the first open hole, but penetrates considerably further down the tube. Thus
  a tone hole must be drilled at a position rather closer to the embouchure than the point at which
  the tube would need to be cut.**" (cited there to Benade 1960, *JASA* 32, 1591–1608)
- "If the tone holes are small relative to the bore, this extension of the standing wave past the
  first open tone hole may be substantially affected by subsequent toneholes. **The closing of such
  subsequent tone holes in order to flatten the note is called a cross fingering.**"
- Measured magnitude [V, p. 104-5]: opening the most distant tone hole (ro → tsu, i.e. D4 → E4)
  shortens the effective length such that "**the first few minima [occur] at frequencies increased
  by approximately 12%, and so the corresponding note rises by about a tone**." (A whole tone is
  a factor of 2^(2/12) ≈ 1.1225, i.e. +12.2% — so the measurement matches theory to within the
  quoted precision. Arithmetic mine.)
- With more holes open, "the section of the tube downstream from the first open hole has its own
  resonances, and so imposes on the upper tube an acoustic load more complicated than that of an
  open pipe, hence the more complicated series of resonances", with complications "appearing at
  successively lower frequencies as the downstream length increases". [V]
- Wolfe & Smith note the shakuhachi is like the **classical (conical) 18th/early-19th-century
  flute** in having "rather fewer than the twelve tone holes required for a Western chromatic
  scale", and so **both "use cross fingerings extensively"** [V, p. 104-3]. The shakuhachi's
  five holes "suggest a pentatonic scale, but cross fingerings, partial closing of the holes and
  the adjustment of the embouchure permit not only a Western chromatic scale over two octaves, but
  **microtonal divisions as well**." [V]

This is also exactly the subject of **Yoshikawa & Kajiwara 2015**, "Cross fingerings and associated
**intonation anomaly**" — so there is a documented, measured anomaly here that I could not read.
**[U]** (§5.1.)

### 5.6 Why the instrument is loud and breathy

**The "breathy" part is verified and has a precise cause** [V] Wolfe & Smith 2000, p. 104-3: "This
flexibility, plus **the relative prominence of the broadband sound of the jet in the timbre of the
instrument**, give it great expressive range, and it is often used to suggest natural sounds
including those of birds, wind and water."

So the breathiness is the **broadband (noise) component of the air jet itself** being unusually
prominent in the radiated timbre. [V] The structural reason follows from §5.2: the blowing end is
wide open, with no narrow embouchure chimney to load it, so the jet noise radiates directly rather
than being filtered. [V premises, my inference]

**Two measured structural differences from the flute that shape the spectrum** [V, p. 104-5]:

1. On the flute, "the closed tube upstream from the embouchure hole is in parallel with the rest of
   the bore, **which adds approximately 6 dB per octave at high frequencies**." **The shakuhachi has
   no upstream resonator at all**, so it lacks this.
2. On the flute, "the embouchure hole itself is a relatively narrow chimney whose larger impedance
   **reduces the magnitude of both the maxima and minima in Z(f) at high frequencies**." **The
   shakuhachi has no chimney**, so its high-frequency minima stay deep.

The JASA abstract states the same two absences [V] `/jw/shakuhachiresults.html`: "Unlike Western
flutes, the shakuhachi has neither a narrow chimney nor a short upstream resonator. These
differences shape its overall Z(f)."

**The "loud" part: [U].** I found **no sound-pressure-level measurement** of a shakuhachi, and no
measured comparison with any other instrument. ja.wikipedia says *ji* makes an instrument **louder**
than *jinashi* (§3.4) [V], and that the 普化尺八 has **greater volume** than the 一節切 [V, §7], but
these are relative and unmeasured. Timbral control is verified [V] ja.wikipedia §奏法: 「口腔内の
形状変化や流量変化等により、倍音構成は…適宜変化させることができる」 — the harmonic content can be
varied at will by changing the shape of the oral cavity and the flow rate. **Note this implies a
vocal-tract contribution**, and the UNSW group has published vocal-tract-tuning work on saxophone
and soprano voice [V, their site index] — **but nothing on shakuhachi vocal-tract tuning that I
could find. [U] A clear open research question.**

### 5.7 ユリ *yuri* — vibrato as a pitch-geometry effect

Worth recording because it follows directly from §5.3 [V] ja.wikipedia §奏法: vibrato is produced
by the *meri*/*kari* action itself — vertical jaw motion (**縦ユリ** *tate-yuri*) or side-to-side
head motion (**横ユリ** *yoko-yuri*), collectively **ユリ** (or あごユリ, "jaw yuri"). The source
notes this is **unlike** the flute's breath-flow vibrato and gives "a distinctive lustre"
(独特の艶); breath-flow vibrato is also used and is called **息ユリ** *iki-yuri*. So the shakuhachi
has **two physically distinct vibrato mechanisms**: a *radiation-geometry* vibrato and a
*flow* vibrato. [V] (Technique as such: covered elsewhere — recorded here because the mechanism is
acoustic.)

## 6. Buying, prices, maintenance, and the legal position

Everything in §6.1–6.3 is **COMMERCIAL**. Prices were as listed on **2026-11-13**; the yen figures
are nominal and undated-for-inflation beyond that.

### 6.1 Price tiers — the best source is a Japanese shop's own published ladder

**邦星堂和楽器店 (Hōseidō Wagakki-ten)**, `ohashi-taizan.net/商品`, fetched 2026-11-13 **[V,
COMMERCIAL]**. This is the single most useful pricing artefact I found, because the shop publishes a
named tier ladder rather than a list of individual instruments. **All prices 税別 (tax
excluded).** (Note: the proprietor is 大橋鯛山 *Ōhashi Taizan*, who is also the author of the
「尺八の物理」 page cited by ja.wikipedia in §2.5 — so this is a maker/retailer with a technical
bent, not a generic shop.)

| Tier | Price (excl. tax) | Lengths offered | What distinguishes it |
|---|---|---|---|
| **普及管** (popular/budget) | **¥29,800** | 1尺6寸 and 1尺8寸 only | Built from broken 標準管 stock and 六節竹 (six-node bamboo — i.e. **not** the seven-node ideal of §1.5) |
| **標準管** (standard) | **¥39,000–50,000** | 1尺1寸 to 2尺5寸 | The full length range — note 2尺5寸, beyond the Wikipedia table (§4.5) |
| **中級管** (intermediate) | **¥60,000–80,000** | 1尺4寸 to 2尺3寸 | Made from bamboo "purchased at high cost" (高額で購入した竹材) |
| **上級管** (advanced) | **¥80,000–100,000** | not stated | Single maker, end-to-end production |
| **高級管** (high grade) | **¥100,000–200,000** | not stated | Higher-grade bamboo than the tier below; single-maker production |
| **貴品管** (finest) | **up to ¥500,000** | not stated | — |

**The shop's ladder does not use the words 初心者用 or 銘管**, and **does not label any tier
jiari/jinashi** [V]. Read it as a *bamboo jiari* ladder — which, given §3, is what an ordinary
Japanese shop sells.

**和楽器一番 (Wagakki Ichiba)**, `wagakki-ichiba.com/shakuhati1.htm`, fetched 2026-11-13 **[V,
COMMERCIAL]** — page title reads 「尺八の大特価販売 初心者用～演奏会用まで（木管・合竹）」, i.e.
**beginner through performance grade, in 木管 (wood) and 合竹 (laminated/composite bamboo)**. The
page's Japanese is mis-encoded so the per-item material fields were unreadable, but the prices and
lengths were legible:

| Item code | Lengths | Shop price | Web price |
|---|---|---|---|
| WKT-2011 | 1.8 / 1.6 shaku | — | **¥26,125** |
| WKT-2013 | 1.8 / 1.6 shaku | ¥38,500 | **¥34,650** |
| WKT-2015 | 1.8 / 1.6 shaku | ¥74,800 | **¥67,320** |
| WKT-2017 | 1.8 / 1.6 shaku | ¥85,800 | **¥77,220** |

**[U]** Which of these are 木管 and which 合竹, I could not determine — the encoding defeated it.
Worth re-fetching with an explicit Shift_JIS decode.

**Mejiro (目白)**, `mejiro-japan.com/en/…`, fetched 2026-11-13 **[V, COMMERCIAL]** — the main
English-facing Tokyo shop. Its category structure confirms the market segmentation even where I
could not open the pages (several returned 403):

| Item | Price |
|---|---|
| 1.8 Kinko **Daiho** bamboo, pre-owned | **¥82,500** |
| 1.8 Kinko **Yozan** bamboo, pre-owned | **¥129,800** |
| 1.6-E Tozan **Shinzan** bamboo, pre-owned | **¥242,000** |
| **2.4 (A)** Kinko-Tozan **Takusan** bamboo | **¥300,000** |
| Komusō set with rattan *tengai* hat (5 items — accessories, not an instrument) | ¥57,500 |
| Shakuhachi **utaguchi adapter / mouthpiece for beginners** (A4015) | ¥3,630 |

Mejiro's category list includes a **"New Jinashi Shakuhachi for Sale"** section and separate "New
Shakuhachi for Sale" sections split **1.1–1.7 / 1.8 / 1.9-and-longer** [V] — independent
confirmation of the §4.6 hierarchy (1.8 gets its own category). **I could not open the jinashi
category (404/403), so I have NO verified price for a new jinashi instrument. [U]**

**Synthesis of the tiers**, in round numbers (my synthesis, each premise [V]):

| Tier | Typical price | Notes |
|---|---|---|
| Moulded plastic student | **¥15,000–20,000** | Yuu 悠 (§2.6) |
| Wood / laminated-bamboo student | **¥26,000–39,000** | Wagakki Ichiba; Hōseidō 普及管 ¥29,800 |
| Standard bamboo | **¥39,000–50,000** | Hōseidō 標準管 |
| Intermediate bamboo | **¥60,000–85,000** | Hōseidō 中級管; Wagakki Ichiba WKT-2015/2017 |
| Professional bamboo | **¥80,000–200,000** | Hōseidō 上級管/高級管; Mejiro pre-owned ¥82,500–242,000 |
| Top / collector | **¥200,000–500,000+** | Hōseidō 貴品管 "up to ¥500,000"; Mejiro 2.4 at ¥300,000 |

**A dating note the user should want:** the glaring gap in this ladder is that **a handmade jinashi
by a named maker has no verified price anywhere in my sources.** I looked and failed. [U]

### 6.2 Named makers and makers' vocabulary

**The vocabulary first** [V] ja.wikipedia 尺八 §製作 (via the fetched summary of the same article):
making a shakuhachi is **製管** (*seikan*), and a maker is a **製管師** (*seikanshi*). Traditionally
a player was reckoned fully qualified only when able both to play and to make one; **full-time
makers appeared only from the Meiji period onward**. Some makers are tied to particular schools;
some players make instruments as a hobby. [V]

Makers and workshops I actually verified exist (as opposed to names I have only seen in passing):

| Name | Evidence | What for |
|---|---|---|
| **大橋鯛山 / 邦星堂和楽器店** | **[V]** own site fetched; also cited in ja.wikipedia for 「尺八の物理」 | Maker-retailer; published tier ladder (§6.1) |
| **遠藤鈴匠 (Endō Reishō), 遠藤晏弘尺八工房** | **[V]** own blog fetched; self-describes as 尺八演奏家・制管師 | Rare 砥の粉-only *ji* ground (§3.2) |
| **遠藤健二 (Endō Kenji)**, 下伊那郡, Nagano | **[V, snippet]** `otomoribeat.wixsite.com/chikuon` | 法竹/地無し尺八 maker (§3.6) |
| **尺八工房 筦山 (Kanzan)**, Gunma (谷川, Minakami-machi; Numata) | **[V]** repair price page fetched | Making and repair (§6.3) |
| **尺八工房 慈庵 (Jian)** | **[V, snippet]** `jianshakuhachi.com` | Repair/maintenance |
| **容山銘尺八 / 引地 (Hikichi)**, Ōtsuka | **[V, snippet]** `yozan-hikichi.co.jp` | Named 銘 line; warns against DIY crack glue |
| **泉州尺八工房 (Senshū)** | **[V]** cited by ja.wikipedia for 「歌口研究2」 | Utaguchi research (§1.2) |
| **米澤浩 (Yonezawa Hiroshi)** | **[V, snippet]** `yonezawa.art.coocan.jp` Q&A on cracks | Player/maker Q&A |
| **林雅寛 (鈴麟) Hayashi Masahiro / "Reirin"** | **[V]** named on the Hōseidō page | Designer of the **3D-printed 烽火 (Hōka) series**, which he **hand-tunes after printing** — a verified, named, 3D-printed production instrument, which pins down the ja.wikipedia claim in §2.5 |
| **"Bei Shu"**, Nagano Ken | **[V]** Wolfe & Smith 2000, p. 104-3 | The model used for the published impedance measurements — bamboo body, **synthetic bore** |
| **Tom Deaver** | **[V]** acknowledged in Wolfe & Smith 2000 and linked from the UNSW page as "shakuhachi maker" | Supplied instruments/advice to the UNSW study |
| **"Daiho", "Yozan", "Shinzan", "Takusan"** (大法/容山/信山/琢山 — kanji unconfirmed) | **[V, as names on Mejiro's listings]** | Maker 銘 appearing on instruments for sale |

**"Schools of making": [U].** ja.wikipedia says only that *some* makers are tied to particular
schools [V]. I found **no** source describing distinct lineages or regional traditions of
*making* (as opposed to playing). If such a taxonomy exists I did not find it.

**Second-hand market** [V, COMMERCIAL]: it is a real, organised market. Mejiro runs a dedicated
**"Pre-Owned Bamboo Flutes"** category [V], with the three instruments priced ¥82,500–¥242,000
above — i.e. **pre-owned professional instruments sell at professional-tier prices, not at a
discount tier.** There is also a dedicated **buying/appraisal trade**: `shakuhachi-kaitori.info`
(the making-process source in §2.3) is a 尺八買取 (shakuhachi purchase) business, and it publishes a
page 「尺八が壊れてしまった…売る前に修理できないか確認してみよう！」 — "your shakuhachi has broken…
check whether it can be repaired before selling" [V]. The existence of a specialist appraisal trade
implies meaningful resale value and that **condition (especially cracks) drives it**.

### 6.3 Maintenance — cracks are the whole problem

**Cause: dryness.** [V, practitioner] 邦星堂和楽器店 blog 「割れ止め」,
`houseidou.blog.fc2.com/blog-entry-135.html` — snippet only, states that in low humidity cracks
occur 「非常な高確率で」 ("with very high probability"). [V, snippet]

**Verified repair price list — 尺八工房 筦山 (Kanzan)**, `kanzan108.co.jp/shakuhati/business/repair/`,
fetched 2026-11-13 **[V, COMMERCIAL]**. Prices in yen, tax status not stated; 最短納期 = minimum
turnaround:

| Work | Price from | Min. turnaround |
|---|---|---|
| **割れ止め** (crack arrest), 1 spot, **small** | ¥2,000 | 5 days |
| 割れ止め, 1 spot, **medium** | ¥3,000 | 5 days |
| 割れ止め, 1 spot, **large** | ¥4,000 | 5 days |
| **籐巻き *tomaki*** (rattan binding) — **the standard finish for a crack arrest** | **included in the 割れ止め price** | 5 days |
| 中継ぎ漆塗り (re-lacquering the mid-joint) | ¥3,000 | 2 days |
| **中継ぎ入れ替え** (replacing the mid-joint) | ¥10,000 | 5 days |
| **金環・銀環の入れ替え** (replacing the **gold or silver ring**) | ¥15,000 | 5 days |
| 唄口の入れ替え (replacing the utaguchi inlay) | ¥5,000 | 3 days |
| **唄口のアゴ調整** (adjusting the utaguchi "chin") | ¥5,000 | 2 days |
| 音程調整 (intonation adjustment) | ¥10,000 | 5 days |
| **再調律（改作）** (full retuning / remaking) | **¥50,000** | **3 months** |
| 孔あけ (drilling an extra hole, multi-hole conversion), per hole | ¥5,000 | 3 days |

Also offered without separate prices: 籐巻き漆塗り仕上げ (rattan binding with urushi finish) and
かつ糸漆塗り仕上げ (thread-and-urushi finish). Multi-hole conversion is **free** for instruments
bought from the workshop. [V] 尺八工房 慈庵 quotes **about ¥3,000 per external crack repair**
[V, snippet].

**Two incidental findings of real value:**

1. **籐巻き is not decoration, it is the standard crack repair.** Kanzan lists it as
   「割れ止めの基本仕上げ」 — *the basic finish of a crack arrest* — and includes it in the crack
   price [V]. English sources routinely treat *tomaki* as ornament or as reinforcement bands
   applied at making time. It is primarily a **repair and prophylaxis** technique. **Correction.**
2. **The mid-joint has a metal ring.** 「金環・銀環の入れ替え」 — gold-ring or silver-ring
   replacement — at ¥15,000 [V]. This **retroactively verifies the metal sleeve** I had to flag as
   [U] in §1.6, and tells you the materials are gold and silver. (The joint's exact position
   remains [U].)

**Repair technique, as described by practitioners** [V, snippet-level — these are search snippets,
not pages I opened]:

- The **wet-towel method**: wrap the cracked area in a wet towel so the bamboo **swells and the
  crack temporarily closes**, then seal. [V, snippet] — sources `run-maru.com`,
  `houseidou.blog.fc2.com`, `shakuhachi-kaitori.info`
- The **external binding method**: cut shallow **grooves above and below the crack**, wrap with
  **nylon thread**, then wrap with **rattan**; adhesive over the thread can adjust the height so
  the binding sits flush. [V, snippet] — `jianshakuhachi.com`, and a DIY video
- **Do not glue a crack yourself.** 容山銘尺八 warns that filling a crack with adhesive makes
  proper later repair harder. [V, snippet]
- After sealing, the bamboo dries and **the crack may widen slightly**; 米澤浩's Q&A says this is
  usually not a cause for concern. [V, snippet]

**Humidity and storage** [V, snippet]: the Sound House staff blog recommends **placing a cup of
water near the instrument during the dry winter months**, and notes that **bamboo instruments risk
cracking while wooden ones do not** — which is the practical argument for a 木管 instrument.
(I attempted to open this page in full; the fetch **timed out**, so this remains snippet-level.)

**Oiling: still [U].** Not one of the ten maintenance results mentioned oiling — the fetch
explicitly reported "None of the snippets mention oiling". Combined with §2.4, **I have now failed
twice to source the shakuhachi oiling practice at all.** My tentative conclusion, flagged as
inference: **oiling may be much less central to shakuhachi care than the English-language
literature implies** — the Japanese maintenance discourse I sampled is overwhelmingly about
*humidity and cracks*, not oil. **This deserves a dedicated check before the skill asserts
anything about oiling.**

**Travel: [U].** I found **no** source on travelling with a shakuhachi — cabin vs hold, pressure,
or climate change on arrival. The inference from everything above (two-piece construction §1.6;
dryness causes cracks) is that the instrument travels well mechanically and badly climatically, but
that is unsourced.

### 6.4 Legal: CITES and plant import

#### Madake is NOT CITES-listed — verified, not assumed

**[V] — and this is a strong verification.** I read the **official Japanese government edition of
the CITES flora appendices**: 経済産業省 (METI), 「ワシントン条約附属書（植物界）」,
`meti.go.jp/policy/external_economy/trade_control/02_exandim/06_washington/download/appendix_flora.pdf`,
23 pages, **version as of 2026年3月5日時点版（2026年3月27日修正）**, downloaded and text-extracted
2026-11-13.

The document lists every CITES-listed plant taxon by family in alphabetical order, in three columns
(附属書Ⅰ / Ⅱ / Ⅲ). My checks:

- Full-text search for **Poaceae, Gramineae, Phyllostachys, Bambusa, Guadua, Chusquea, イネ科, タケ,
  竹**: **zero hits.** [V]
- Positional confirmation, since alphabetical order makes absence provable: the family sequence runs
  **… PEDALIACEAE → PINACEAE (p. 18) → PODOCARPACEAE → PORTULACACEAE → PRIMULACEAE → RANUNCULACEAE
  → ROSACEAE (p. 19) …**. **POACEAE would fall between PINACEAE and PODOCARPACEAE, and it is not
  there.** [V — I read those pages]

**Conclusion: no grass (Poaceae) is listed in any CITES Appendix, therefore no bamboo is, therefore
*Phyllostachys reticulata* (madake) is not.** The user's assumption is correct, and it is now
verified rather than assumed. A bamboo shakuhachi, as bamboo, is outside CITES entirely.

#### Ivory utaguchi inlay on older instruments IS a CITES Appendix I problem

**[V]** 経済産業省, 「ワシントン条約附属書（動物界）」, same page, same version date (2026年3月5日
時点版, 2026年3月27日修正), 123 pages, downloaded and text-extracted 2026-11-13, PROBOSCIDEA /
ELEPHANTIDAE entry at p. 38:

| Taxon | Listing |
|---|---|
| ***Elephas maximus*** アジアゾウ (Asian / Indian elephant) | **Appendix I** |
| ***Loxodonta* spp.** アフリカゾウ属 | **Appendix I**, 「附属書Ⅱに掲げるボツワナ、ナミビア、南アフリカ及びジンバブエの個体群を除く」 — excluding the Botswana, Namibia, South Africa and Zimbabwe populations, which are in Appendix II |
| ***Loxodonta africana*** サバンナゾウ | **Appendix II**, but **limited to** the Botswana / Namibia / South Africa / Zimbabwe populations; annotation **A11** |

Annotation **A11** [V, my translation]: for those Appendix-II populations, trade is permitted
**only** for (a) non-commercial hunting trophies, (b) live animals to appropriate and acceptable
destinations, (c) hides, (d) hair products, (e) leather goods, and (f) **for Namibia only, the
non-commercial trade in *ekipa* — individually marked and certified worked-ivory ornaments — and
for Zimbabwe only, the non-commercial trade in ivory carvings.** The note closes:
「他のすべての標本は、附属書Ⅰに掲げる種の標本とみなされ…」 — **all other specimens are deemed
specimens of an Appendix-I species** and regulated as such.

**So, for a shakuhachi with an ivory utaguchi inlay:**

- Ivory on a Japanese instrument is **overwhelmingly likely to be Asian or non-exempt African
  elephant**, hence **Appendix I**. [V on the listings; [U] on which species any given inlay is —
  and note that **identifying the species of a small worked inlay is itself hard**, which is a
  practical problem, not a legal one]
- **The US personal-effects exemption does not help you.** 50 CFR 23.15(d)(2) [V, eCFR API,
  2025-01-01 edition, fetched 2026-11-13]: the exemption applies only if "**No specimen from an
  Appendix-I species is included**, except for certain worked African elephant ivory as provided in
  paragraph (f)".
- **The one narrow escape route**, 50 CFR 23.15(f) [V]: a **US resident** may export and re-import
  **worked African elephant ivory** as a personal effect without a CITES document if all of:
  (1) it meets the personal/household-effect conditions and you owned it before leaving the US;
  (2) **it is pre-Convention** — and the regulation states the date: **"The African elephant was
  first listed in CITES on February 26, 1976."**; (3) **you may not sell or transfer it while
  abroad**; (4) the ivory is **substantially worked and not raw** (a shakuhachi inlay plainly
  qualifies as worked); and (5) you can show records that it is pre-Convention **and that you
  registered it before leaving**, via one of: a **US CITES pre-Convention certificate**, an **FWS
  Form 3-177** declaration, or a **CBP Form 4457** Certificate of Registration for Personal
  Effects Taken Abroad. **Note this route is African-elephant-only; it does not cover Asian
  elephant ivory at all.** [V]
- **Pre-Convention certificates generally**, 50 CFR 23.45 [V]: the pre-Convention date is **the date
  the species was first listed under CITES**, regardless of later Appendix transfers; for a
  pre-Convention Appendix-I specimen **no CITES import permit is required**; the US application is
  **Form 3-200-23** (wildlife). The exemption works only if **the importing country will accept a
  pre-Convention certificate**. [V]
- **Stricter national measures override all of this** [V, 50 CFR 23.15(b)]: the personal-effects
  exemption "does not apply if a country prohibits or restricts the import, export, or re-export of
  the item". Several jurisdictions have near-total domestic ivory bans stricter than CITES.
  **[U]** I did not research any specific national ivory ban (US ESA 4(d) rule, UK Ivory Act 2018,
  EU measures, Japan's domestic registration regime) — **a real gap, and the practically decisive
  one for a player.**

**Practical upshot** [V premises, my synthesis]: **buy or specify water-buffalo horn or ebonite,
not ivory.** Both are verified standard utaguchi materials (§1.2), and 唄口の入れ替え — replacing
the inlay — is a routine ¥5,000 job (§6.3). An ivory inlay on an older instrument is a genuine
cross-border liability with a narrow, documentation-heavy escape route that does not exist at all
for Asian elephant ivory.

#### Does a Musical Instrument Certificate apply?

**Partly verified, and the answer is "it exists, but probably not for your shakuhachi".**

- **It exists.** [V] UK Government guidance, `gov.uk/guidance/cites-imports-and-exports`, fetched
  2026-11-13: where a CITES specimen is a musical instrument and the movement is **not for
  commercial purposes**, you may "instead apply for a **musical instrument certificate**". **There
  is no fee.** The page does **not** state the Resolution number, the validity period, or whether
  pre-Convention status or legal acquisition are conditions. It notes that the **3-year validity
  belongs to travelling-exhibition certificates, not to musical instrument certificates.** [V]
- **The Resolution: [U].** cites.org returned **HTTP 403 on every route** I tried (the appendices
  page, the appendices PDF, and `/eng/res/16/16-08.php`), with and without browser headers. **I
  could not verify the Resolution number, the certificate's validity period, or its conditions
  from the CITES primary text.** The user's prompt and general knowledge point to **Resolution
  Conf. 16.8** — I **did not verify this** and it should not be stated as verified.
- **An unexpected finding: the certificate is not in the US CITES regulations.** [V] I downloaded
  the **entire** 50 CFR Part 23 (the US CITES implementing regulations) via the eCFR API,
  2025-01-01 edition, ~275,000 characters, and searched it. The word **"musical" does not occur**,
  and "instrument" occurs **only** in the phrase "instrument of ratification". The part does have
  explicit sections for **personal and household effects (§23.15)**, **pre-Convention specimens
  (§23.45)** and **travelling exhibitions (§23.49)** — but **no musical instrument certificate
  section.** So in the US the applicable instruments are the pre-Convention certificate and the
  personal-effects exemption, not a musical-instrument certificate. **[V as to the regulation's
  contents; [U] as to whether FWS nonetheless issues such certificates under some other
  authority — it may, and I did not establish it; `fws.gov` returned 404 on the page I tried.**
- **Does it apply to a shakuhachi at all?** [V premises, my conclusion]: **a plain bamboo
  shakuhachi with horn or ebonite is not a CITES specimen** (§6.4 first part), so **no CITES
  document of any kind is needed and the question does not arise.** The certificate only becomes
  relevant if the instrument contains an ivory inlay or some other listed material.

#### Phytosanitary / plant-import rules for raw bamboo

**[U] — I did not research this and will not guess.** The question is real and separate from CITES:
many jurisdictions regulate the import of **unprocessed plant material** (and especially **bamboo**,
as a host for pests) under phytosanitary rather than wildlife law. The relevant regimes would be
IPPC/ISPM, and nationally e.g. USDA APHIS and the EU plant-health regulation. What I can say from
verified material is only that **madake itself is officially treated in Japan as a
産業管理外来種 — an "industrially-managed alien species"** whose spread is a problem (§2.3) [V],
which is suggestive of exactly the kind of species that attracts import controls elsewhere.
**A finished, heat-cured, lacquered instrument is a different category from raw culm**, and I did
not verify how any jurisdiction classifies either. **Flag loudly; do not fill from memory.**

## 7. Related instruments — enough to place the modern shakuhachi

Organological only. The **history** of the *gagaku* shakuhachi and the *hitoyogiri* is **covered
elsewhere**; what follows is bore, holes, length, construction and blowing-edge geometry.

### 7.1 Comparison table

All figures **[V]** from the sources named in the following subsections.

| Instrument | Length | Holes | Nodes | Material | **Utaguchi bevel** |
|---|---|---|---|---|---|
| **普化尺八** (the modern shakuhachi) | **54.5 cm** (1.8 shaku) standard; 1.1–3.0 shaku range | **4 front + 1 back = 5** | **7** (but see §1.5) | 真竹 madake, **root end** | **OUTWARD** |
| **古代尺八 / 雅楽尺八** (gagaku) | **~40 cm** | **5 front + 1 back = 6** | **3** | bamboo | **outward** (disputed — §7.2) |
| **一節切 *hitoyogiri*** | **33.6 cm** (= 1尺1寸1分 kanejaku); dia. ~3 cm | **4 front + 1 back = 5** | **1** | 真竹 madake, **middle of the culm** | **OUTWARD** |
| **天吹 *tempuku*** | **~30 cm** | **4 front + 1 back = 5** | **3** | **布袋竹 *hoteichiku*** (not madake), root end | **INWARD** (*dòngxiāo* type), mainly |
| **洞簫 / 簫 *xiao*** (China) | **~80 cm**; Qing court type **54 cm** | **5 front + 1 back = 6**; modern types 6 or 8 | — | bamboo; also **jade and porcelain** | **INWARD**, and shallower |
| **南簫 / 南曲 *dòngxiāo*** (Fujian *nanguan*) | **~56 cm**, "as thick as a shakuhachi" | — | — | bamboo | inward |
| **短簫** (China, short type) | **42 cm** | **4 front + 1 back = 5** | — | bamboo | inward |
| **洞簫 *tungso*** (Korea) | — | **5 front + 1 back = 6**, sometimes plus a **清孔** membrane hole | — | bamboo | inward |
| **短簫 *danso/tanso*** (Korea) | — | **4 front + 1 back = 5** | — | bamboo | inward |

### 7.2 古代尺八 / 雅楽尺八 — the gagaku shakuhachi

**[V]** ja.wikipedia 尺八 §歴史, rev. 2026-09-19, and the kotobank encyclopedias:

- Tang origin, transmitted to Japan as a **gagaku** instrument from the late 7th to early 8th
  century; **extinct as a gagaku instrument by the mid-Heian period, the 10th century**. [V]
- **正倉院 (Shōsōin) at Tōdai-ji holds 六孔三節 shakuhachi** — six-hole, three-node. [V] Nipponica
  counts **nine surviving examples: eight at the Shōsōin and one at Hōryū-ji.** [V, kotobank
  summary]
- **Average length 40 cm; finger-hole diameter 2 cm; 5 holes front + 1 back.** [V] ja.wikipedia:
  「平均の長さは40cm、指穴の直径は2cm、前5、後1の6つの指穴がある」. Britannica Japan agrees:
  6 holes, tube about 40 cm, hole diameter just over 2 cm [V, kotobank summary].
- **No notation survives**, so playing method and scale are unknown: 「古台尺八に関連する楽譜の
  記録がないため、演奏方法や音階などの詳細は不明である」 [V]. (The *sic* is in the source — it
  prints 古台 for 古代.)
- **Note how different this is from the modern instrument**: 6 holes not 5, 3 nodes not 7, 40 cm not
  54.5, and **not made from the root end**. The two instruments share a name and little else. [V]
- **A genuine disagreement on the bevel** [V both sides]: ja.wikipedia 簫 (citing 小学館) says 「日本
  の正倉院に伝わる雅楽尺八も、洞簫の一種である」 — "the gagaku shakuhachi handed down in Japan's
  Shōsōin is also a kind of *dòngxiāo*", which implies an **inward** bevel. But ja.wikipedia 一節切
  (citing 国史大辞典) says the outward-cut utaguchi 「この形は古代尺八や普化尺八と共通する」 — "this
  shape is **common to the 古代尺八 and the 普化尺八**", i.e. the ancient instrument was bevelled
  **outward**. **I cannot resolve this and report both.** It bears directly on §1.3 and on
  Yoshikawa's 2012 abstract title "Changes in acoustical design from ancient shakuhachi to modern
  shakuhachi" (§5.1) — which I could not read, and which is very likely the paper that settles it.

### 7.3 一節切 *hitoyogiri*

**[V]** ja.wikipedia 一節切, raw wikitext via API, rev. **2026-06-14T07:36:47Z**, fetched
2026-11-13 — a well-footnoted article citing 国史大辞典, 日本国語大辞典, 世界大百科事典, 日本大百科
全書 and デジタル大辞泉.

- Also written 一重切, 一簡切, 一節截; read **ひとよぎり** or **ひとえぎり**; classified as
  **一節切尺八**, i.e. **a kind of shakuhachi**. [V]
- **Made from the middle of the madake culm** (真竹の幹の中ほど), **containing exactly one node**,
  which is what the name means. **Thinner, shorter and straighter** than the modern instrument. [V]
- **Standard length 1尺1寸1分 in kanejaku ≈ 33.6 cm**; diameter about **3 cm**. [V] (My check:
  1.11 shaku × 303.03 mm = 336.4 mm. The 33.6 cm figure is exactly the kanejaku conversion.)
- **4 front + 1 back = 5 holes — the same count and arrangement as the 普化尺八**, but 「孔間比は
  微妙に異なる」, **the ratios of the inter-hole spacings differ subtly**. [V] This is a precise and
  useful organological statement.
- **Two blowing-end differences from the modern shakuhachi** [V]:
  1. The utaguchi is cut diagonally away from the upper end **on the outside** — a form **shared
     with the 古代尺八 and 普化尺八**, and **different from the Chinese 洞簫 and the Korean 短簫**.
  2. **The utaguchi is at the end *nearer the root***: 「根に近い方を歌口にする点でも普化尺八と
     異なる」 — "it also differs from the 普化尺八 in that the end nearer the root is made the
     utaguchi." **The hitoyogiri is blown from the root end; the shakuhachi is blown from the far
     end with the root as the foot.** This is a sharp, concrete difference that English accounts
     almost never mention.
- **Lengths and pitches** [V]: before the early 17th century there were **five** lengths, each named
  for its 筒音 — **壱越切 (D), 平調切 (E), 双調切 (G), 黄鐘切 (A), 盤渉切 (B)**. Subsequently the
  **黄鐘切 (A)** became the standard. So the hitoyogiri had its own length-naming system, built on
  the same 十二律 names the shakuhachi uses (§4.5), but naming the *cut* (切) rather than the *tube*
  (管).
- **Performance limits, stated plainly** [V]: basic technique is close to the 普化尺八, but it is
  **unsuited to complex technique and is inferior in both volume and range** (「複雑な技法には向か
  ず、音量・音域も普化尺八に劣った」). ja.wikipedia 尺八 says the same from the other side: the
  普化尺八 is **larger in volume, wider in range and superior** to the 一節切 [V].
- Trajectory: in use by the 14th–15th century at latest, general by the 16th, **peak in the later
  17th century, then rapid decline — scarcely played from the 18th century**, displaced by the
  普化尺八. [V] (History: covered elsewhere.)

### 7.4 天吹 *tempuku*

**[V]** kotobank 天吹 (`kotobank.jp/word/天吹-1570456`), fetched 2026-11-13, serving 日本大百科全書,
改訂新版 世界大百科事典 and ブリタニカ国際大百科事典. **Note: Japanese Wikipedia has no article —
天吹 is a redirect to 笛 [V].** So kotobank is the source of record here.

- **Different bamboo species.** Made from **布袋竹 / ホテイチク *hoteichiku*** — Nipponica
  specifies the part near the **root** of a flattened, curved hoteichiku; Heibonsha says thin
  hoteichiku. **Not madake.** [V] ([U] I did not verify the scientific name of hoteichiku; it is
  conventionally *Phyllostachys aurea*, and given §2.1 that attribution should itself be checked.)
- **Length about 30 cm.** Nipponica gives an **outer circumference of 7–8 cm** (≈ 22–25 mm outer
  diameter — my conversion); Britannica gives an **inner diameter of 7–8 mm**. Heibonsha notes
  makers **size it by finger width**, so dimensions vary. [V] **This is a much narrower bore than
  the shakuhachi's ~15–20 mm (§1.8) — the tempuku is a thin pipe, not a scaled-down shakuhachi.**
- **4 front + 1 back = 5 holes, 3 nodes** (Nipponica, Heibonsha). **Britannica's "4 front, 5 back"
  conflicts with both and is almost certainly an error** [V as to the disagreement].
- **The distinctive construction feature**: **the first node near the bottom is NOT removed — a
  small hole is bored through it instead.** [V] Nipponica and Heibonsha both. Nothing in the
  shakuhachi family does this, and it is a partially-closed-end configuration with real acoustic
  consequences. **[U]** I found no acoustic analysis of it.
- **The utaguchi is mainly the 洞簫 type** — cut so that only the skin edge remains and the inside
  is hollowed out, i.e. **bevelled inward**, Chinese-style. A shakuhachi-style utaguchi was also
  made but was not the main form; Britannica says both types exist. [V] **So the tempuku is
  Chinese on the one feature that most distinguishes the shakuhachi (§1.3).**
- A **folk instrument of Kagoshima / Satsuma**; origin unknown; tradition has Satsuma samurai
  playing it in the 16th century; declined after Meiji; **白岡国俊 of Kajiki (now Aira) is named as
  the last known practitioner.** [V] (History: covered elsewhere.)
- Placement: Nipponica calls it very similar in appearance to the shakuhachi and likewise
  reed-less, and says **it may be an early form of the modern shakuhachi**, but that the
  bottom-node hole and the mouthpiece differ markedly; Heibonsha treats it as **a variant of the
  shakuhachi**, and the Heibonsha shakuhachi entry lists **一節切尺八, 古代尺八 and 天吹** together
  as "shakuhachi in the broad sense". [V]

### 7.5 The Chinese 尺八 *chiba*, and 簫 / 洞簫 *xiao*

**The Chinese 尺八 as a name** [V] ja.wikipedia 尺八 §歴史, with a verifiable primary quotation: the
Song-dynasty 陳暘 (Chen Yang), 『楽書』 vol. 148, gives 尺八管 as **an alternative name for 簫管**.
The article quotes it directly, with an archive.org link to the scanned text:

> 「簫管之制、六孔旁一孔。加竹膜焉。足黄鐘一均声。或謂之尺八管、或謂之竪籧、或謂之中管。尺八、
> 其長数也。」

My translation: "The construction of the *xiaoguan*: six holes, with one hole at the side. A bamboo
membrane is added to it. It completes one *jun* of pitches of the *huangzhong*. Some call it
*chiba-guan* (the 'one-shaku-eight pipe'), some the *shuqu*, some the *zhongguan*. '*Chiba*' is its
length-number." [V that the article quotes this; the translation is mine. Note the **bamboo
membrane** — a feature of neither the shakuhachi nor the ordinary *xiao*, but compare the Korean
清孔 in §7.6.]

So **尺八 in Chinese was a descriptive length-name for a kind of *xiaoguan***, not a distinct
instrument tradition — and "尺八、其長数也" ("*chiba* is its length-number") is the earliest
explicit statement of the etymology in §4.2. **[U]** The modern Chinese *chiba* **revival** — the
reconstruction movement that re-imports the Japanese instrument — I did **not** research at all.

**簫 / 洞簫 *xiao* / *dòngxiāo*** [V] ja.wikipedia 簫, raw wikitext, rev. **2025-06-25T11:54:21Z**,
citing 世界大百科事典 (Heibonsha), 音楽之友社 and 小学館:

- 簫 is an East Asian **vertical, reed-less bamboo flute**; there are **single-tube** and **panpipe**
  types, and from the **Song dynasty onward the single-tube type is generally called 洞簫**. [V]
  (The panpipe 簫 is out of scope here.)
- **Length about 80 cm, 5 front + 1 back holes.** Mostly bamboo, but also made of **jade (玉) and
  porcelain (磁器)**. [V]
- **THE defining contrast, and it verifies §1.3 from the Chinese side** [V], transcribed:
  「歌口は、管壁の外側を削る尺八と異なり、管壁の内側を斜めにえぐっており、えぐり方も小さい」 —
  "the utaguchi, **unlike the shakuhachi which shaves the *outside* of the tube wall, gouges the
  *inside* of the tube wall diagonally, and the gouge is also smaller.**" So the difference is
  twofold: **direction** (inside vs outside) **and depth** (shallower).
- **出音孔**: the *xiao* has **2–4 "sound-exit holes" at the lower end on the back side** [V] — a
  feature the shakuhachi entirely lacks.
- Lineage [V]: derived from the 羌笛 (*Qiang* flute), called 篴 in the Han — a 3–4-hole reed pipe of
  the Gansu/Sichuan minority peoples — with **京房 (Jing Fang) adding a sixth hole on the back in
  the 1st century BC to make 5 front + 1 back.** The **Qing-dynasty court-music 洞簫 was 54 cm with
  5 front + 1 back** — i.e. **almost exactly the shakuhachi's length, with a different hole count
  and the opposite bevel.** A useful calibration.
- Modern Chinese types [V]: **鳳凰簫** dia. ~2.2 cm, 6 holes; **玉屏簫** dia. ~1.05 cm, 6 holes,
  pale-yellow bamboo with the nodes shaved, known from south-west Guizhou; **琴簫 (雅簫)** dia.
  ~1.7–1.8 cm, 8 holes, made of **紫竹** (purple bamboo).
- **短簫** (Chinese short type) [V]: **42 cm, 4 front + 1 back**, used in 郷楽 and in 正楽 chamber
  music.
- **The *nanxiao* contrast the user asked for** [V]: 「福建の南曲では、尺八のように太い、長さ56
  センチメートルほどの竹製の洞簫が使われる」 — "in the 南曲 (*nanqu* / *nanguan*) of **Fujian**, a
  bamboo *dòngxiāo* **as thick as a shakuhachi**, about **56 cm** long, is used." **This is the
  closest living relative of the shakuhachi in dimensional terms** — same length class, same thick
  bore — and the difference reduces almost entirely to the **bevel direction and the hole count**.
  (The article calls it 洞簫, not 南簫; the name *nanxiao* is the common one in the *nanguan* world
  — **[U]** I did not verify the term 南簫 itself.)

### 7.6 Korea: 洞簫 *tungso* and 短簫 *danso*

**[V]** ja.wikipedia 簫, same revision:

- The **洞簫 was transmitted to Korea in the Goryeo period** and is used in both **雅楽** and folk
  music. It likewise has **5 front + 1 back** holes, and **some have a 清孔 — an extra hole covered
  with 竹紙 (bamboo paper / membrane) to give a buzzing, "numbed" timbre** (しびれた音色). [V]
  **The membrane is the feature with no shakuhachi parallel** — and note it echoes the 竹膜 in the
  Song-dynasty 楽書 description in §7.5.
- **短簫 *danso* (タンソ)** [V]: a Korean single-tube instrument with 簫 in its name, **4 front +
  1 back**, described as **popular in Korean traditional music — taught even in South Korean
  primary schools.** It is the Korean counterpart of the recorder-as-school-instrument, which is a
  useful cultural calibration against the shakuhachi's status.
- ja.wikipedia 一節切 independently notes that the outward-cut utaguchi distinguishes the Japanese
  instruments **from the Korean 短簫** as well as the Chinese 洞簫 [V] — so the inward bevel is the
  continental norm and the outward bevel is the Japanese divergence.

### 7.7 What places the modern shakuhachi

Drawing the table together — the modern 普化尺八 is distinguished from **everything** else in the
family by a short list of features, all verified above:

1. **The outward-bevelled utaguchi** — shared with the *hitoyogiri* and (disputedly) the *gagaku*
   shakuhachi; **not** with any Chinese or Korean instrument, nor mainly with the *tempuku*. This is
   the Japanese divergence. [V]
2. **Five holes (4+1), not six.** The continental norm is 5+1 = six. [V]
3. **Made from the root end, thick-walled, seven nodes.** The *hitoyogiri* uses mid-culm; the
   *gagaku* instrument has three nodes; the *xiao* is a thin tube. [V]
4. **A bore built up with *ji*** — an intervention nothing else in the family shares as a norm
   (§3). [V]
5. **Blown from the end away from the root**, where the *hitoyogiri* is blown from the root end. [V]

And the thing it is **not** distinguished by: **length.** At 54.5 cm it sits right on top of the
Qing court *dòngxiāo* (54 cm) and the Fujian *nanguan* *dòngxiāo* (~56 cm). The "one shaku eight
sun" is a shared East Asian pipe length, not a Japanese invention. [V]

## 8. Corrections to the common English account, and open questions

### 8.1 Corrections — numbered, each with its evidence

1. **Madake's scientific name is *Phyllostachys reticulata* (Rupr.) K.Koch, not *P. bambusoides*.**
   *P. bambusoides* Siebold & Zucc. is a **synonym**. And it is certainly **not** *P. edulis*,
   which is a different accepted species (moso, 孟宗竹). **[V]** GBIF species-match API + YList/POWO
   via ja.wikipedia マダケ. See §2.1. Bonus: ja.wikipedia マダケ contradicts *itself* on this, giving
   the synonym in its prose and the accepted name in its taxobox.

2. **The utaguchi is bevelled OUTWARD, away from the bore — and that is the single most important
   organological fact about the instrument.** The Chinese *xiao* and the Korean *tungso*/*danso*
   are bevelled **inward**, and the gouge is shallower. The outward bevel is the Japanese
   divergence, it is what makes the enormous pitch bend possible, and English sources that describe
   the shakuhachi as "notched like a recorder" get it exactly backwards (a recorder is a **fipple**
   flute with fixed jet geometry; the shakuhachi is an **air-reed** instrument like the transverse
   flute). **[V]** §1.2, §1.3, §7.5.

3. **"1.8 shaku" on a modern instrument is a PITCH name, not a measurement.** Japanese makers
   distinguish **正寸** (accurate in length) from **正律** (accurate in pitch), and **正律 is now
   the mainstream labelling** — so a "正律一尺八寸管" is guaranteed to sound D, and is **not**
   guaranteed to be 54.5 cm. The cause of the divergence is the **bore**, which is the
   *jinashi*/*jiari* axis seen from another angle. **[V]** §4.7. Almost no English source has this.

4. **The 54.5 cm vs 43.7 cm "contradiction" is a units problem, not a factual one.** 54.5 cm is 1.8
   shaku in the modern 曲尺 (10/33 m); Nipponica's ~43.7 cm is 1.8 shaku in the **Tang 小尺**
   (~24.6 cm). Same instrument-name, two historical feet. ja.wikipedia says so explicitly.
   **[V]** §4.3.

5. **The bore narrows towards the foot — it is an inverted cone (逆円錐), ~20 mm at the top and
   ~15 mm at the bottom.** The external flare of the root end is **not** a bore flare. **[V]**
   Heibonsha via kotobank, §1.8. English writing routinely implies the opposite.

6. **The two-piece construction exists primarily for BORE ADJUSTMENT and material selection;
   portability is explicitly the side-effect.** ja.wikipedia lists the reasons in that order and
   then says "and as a result it also became convenient to carry". **[V]** §1.6.

7. **籐巻き *tomaki* is primarily a crack repair, not ornament.** A working Japanese repair shop
   lists rattan binding as 「割れ止めの基本仕上げ」 — *the basic finish of a crack arrest* — and
   includes it in the crack-repair price. **[V]** §6.3.

8. **The mid-joint carries a metal ring, in gold or silver.** Verified indirectly but decisively by
   a repair price list that quotes 「金環・銀環の入れ替え」 at ¥15,000. **[V]** §6.3, filling the
   gap I had flagged in §1.6.

9. **There is a THIRD bore category, 半地無し *han-jinashi*, where *ji* fills only the node
   depressions.** The real continuum is natural bore → node depressions filled → bore fully rebuilt.
   The English binary is a simplification. **[V]** §3.3.

10. ***Ji* (地) is a lacquer-bound mineral filler paste, and the recipes are contested and
    historically contingent**: 漆 + 砥の粉 (+水) classically; **石膏 (gypsum) is the commonest base
    today**, with カシュー (non-urushi cashew lacquer) and plain 樹脂 also in use. A named maker
    attributes the shift to the post-war shakuhachi/*min'yō* booms and fast production. 地の粉
    (*jinoko*) — the standard lacquerware term — did **not** appear in any source I read. **[V]**
    §3.2.

11. ***jinashi* is not claimed to sound better in Japanese sources.** The Japanese reference framing
    is that *jinashi* **does not give accurate pitch, so the player must correct it**, with
    per-instrument individuality offered as the compensating aesthetic virtue *in honkyoku*. The
    verified case for *jiari* is **louder + accurate intonation**. "Jinashi is the real thing" is
    an English-language position. **[V]** §3.1, §3.5.

12. **法竹 *hotchiku* is a lineage term, not an organological category.** It belongs to 海童道
    and 海童道祖, where the instrument is called 法竹 or 定具 — and a record titled 「法竹と尺八」
    exists precisely to contrast them. It has leaked into general use as "heavy jinashi", including
    in one maker's own business copy, but it should be used with its provenance attached. **[V]**
    §3.6.

13. **The shakuhachi operates at the MINIMA of its input impedance, not the maxima** — because it is
    **open at the blowing end**. That one fact explains the pitch bend, the breathiness, the
    register mechanism and the absence of the flute's high-frequency features. Reed instruments work
    at maxima; air-jet instruments do not. **[V]** Wolfe & Smith 2000, §5.2.

14. **Meri can reach more than 4 semitones** from a single hole position (normal playing: ~2
    semitones of *meri*, ~1 of *kari*), and the bend range **widens as the tube approaches fully
    open**. These are the real figures and they are rarely quoted. **[V]** ja.wikipedia §奏法, §5.3.

15. **The "breathy" timbre has a specific published cause**: the unusual prominence of the
    **broadband noise of the air jet itself** in the radiated sound. **[V]** Wolfe & Smith 2000,
    §5.6. (The "loud" claim, by contrast, is **unmeasured anywhere** — see §8.2.)

16. **The registers 乙/甲/大甲 are overblowing to successively higher near-harmonic impedance
    minima, selected by changing jet length and speed** — and the top register is hard because the
    array of open finger holes acts as a **high-pass filter** that weakens the standing wave.
    **[V]** Wolfe & Smith 2000, §5.4.

17. **Madake is NOT CITES-listed, and this is now verified rather than assumed**: no Poaceae appears
    anywhere in the official CITES flora appendices, provable positionally because the family list
    runs PINACEAE → PODOCARPACEAE with no POACEAE between. **[V]** METI 附属書（植物界）, version
    2026年3月5日 (rev. 2026年3月27日), §6.4.

18. **An ivory utaguchi inlay is a hard Appendix-I problem with only one narrow escape route, and
    that route does not cover Asian elephant ivory at all.** *Elephas maximus* is Appendix I;
    *Loxodonta* spp. is Appendix I except four southern-African populations. The US personal-effects
    exemption excludes Appendix-I specimens **except certain worked African elephant ivory**, which
    must be **pre-26 February 1976**, registered before departure, and not sold abroad. **[V]** METI
    附属書（動物界）+ 50 CFR 23.15, 23.45, §6.4.

19. **A Musical Instrument Certificate exists but almost certainly does not apply to a shakuhachi** —
    because a bamboo instrument with horn or ebonite is **not a CITES specimen at all**, so no CITES
    document is needed. And notably, **the certificate does not appear anywhere in the US CITES
    regulations**: the word "musical" does not occur in the whole of 50 CFR Part 23. **[V]** §6.4.

20. **The *hitoyogiri* is blown from the end NEARER the root**, the opposite of the shakuhachi,
    and is made from the **middle** of the culm with exactly one node. It has the same 4+1 hole
    count but **subtly different inter-hole spacing ratios**. **[V]** ja.wikipedia 一節切, §7.3.

21. **The *tempuku* is made from a different bamboo (布袋竹 *hoteichiku*, not madake), has a
    Chinese-style INWARD bevel, a much narrower bore (~7–8 mm internal), and — uniquely — leaves
    the lowest node in place with a small hole bored through it.** It is not a small shakuhachi.
    **[V]** kotobank 天吹, §7.4.

22. **54.5 cm is not a Japanese invention.** The Qing court *dòngxiāo* was **54 cm** and the Fujian
    *nanguan* *dòngxiāo* is **~56 cm and as thick as a shakuhachi**. "One shaku eight sun" is a
    shared East Asian pipe length. The Chinese 尺八 was a **descriptive length-name** for a kind of
    *xiaoguan*, and the Song 『楽書』 says so outright: 「尺八、其長数也」. **[V]** §7.5.

23. **The seven-node convention is the well-supported one, but my best source contradicts itself**
    — ja.wikipedia's lead says seven nodes (as do Heibonsha and Nipponica) while its 物理的構造
    section says 五孔三節, "five holes, three nodes". "Three nodes" is the standard description of
    the *ancient* instrument. **Do not repeat "three nodes" for a modern shakuhachi.** **[V]**
    §1.5.

24. **ja.wikipedia's length table has an octave typo**: 二尺二寸管 is printed "Bb4" and must be
    **B♭3**, between B3 (2.1) and A3 (2.3). **[V]** §4.5.

25. **"Sun per semitone" is an approximation that is about 7% short and drifts across the range.**
    One semitone needs +5.95% of length (≈3.24 cm at 54.5 cm) against 1 sun = 3.03 cm — which is
    precisely why 正寸 and 正律 diverge. [V premises; the arithmetic is mine.] §4.5.

### 8.2 Open questions I could not resolve

Ranked by how much they matter.

1. **No measured acoustic comparison of *jinashi* vs *jiari* exists that I could find.** No SPL, no
   spectra, no impedance curves, no intonation deviations in cents. The entire central
   organological distinction rests on qualitative, tradition-internal claims. **And the one
   well-measured shakuhachi in the literature had a *synthetic* bore** (Wolfe & Smith's Bei Shu),
   so it cannot even stand in for a natural one. §3.4, §5.3.

2. **Yoshikawa & Kajiwara (2015), *Acoustical Science and Technology* 36(4): 314–325, "Cross
   fingerings and associated intonation anomaly in the shakuhachi", DOI 10.1250/ast.36.314.**
   A full 12-page journal paper by a reliable author, on a core topic. **J-STAGE returned HTTP 500
   on every route**, with and without browser headers, on retry. Crossref holds no abstract. **The
   highest-value single acquisition target.** §5.1.

3. **Castellengo & Fabre, "The Contemporary Transverse Flute and the Shakuhachi: Convergences", in
   *Flute and Shakuhachi* (Routledge, 2020), pp. 217–237, DOI 10.4324/9781315077192-10.** Two
   serious flute acousticians writing in English on exactly this comparison. Taylor & Francis
   inaccessible. Likewise Tukitani, Seyama & Simura, "The Shakuhachi: The Instrument and its Music,
   Change and Diversification", pp. 103–129 — by the same 月渓恒子 who is ja.wikipedia's main
   scholarly citation. **Probably the best English organology that exists.** §5.1.

4. **No published bore profile.** Nobody has published diameter-versus-position for any shakuhachi
   that I could obtain. Sudo et al. (2025), *Proc. Meetings on Acoustics* 60: 035008, DOI
   10.1121/2.0002426, generated 3D models **from CT images** for additive reproduction — so real
   profiles exist in that paper. `pubs.aip.org` redirected to a CDN URL that **served a completely
   different article**. §1.8, §5.1.

5. **The oiling question is unresolved, and I now suspect the English account is wrong.** I looked
   twice — in the making literature and in the maintenance literature — and found **nothing** about
   oiling a finished instrument. The Japanese maintenance discourse I sampled is overwhelmingly
   about **humidity and cracks**. Note also the tension: curing deliberately **removes** the
   bamboo's oil (油抜き), and a *jiari* bore is fully lacquered. **Check before asserting anything
   about camellia oil.** §2.4, §6.3.

6. **The utaguchi's geometry has no sourced numbers.** No bevel angle, no edge width, no notch
   depth, from any reference-grade source. The "30°" figures in circulation appear to be
   unsourced. §1.2.

7. **"2.4 in B" does not follow from any verified mapping.** The Japanese table has no 2.4 entry;
   by the semitone rule 2.4 shaku is A♭3/G♯3. **Mejiro, however, sells a "2.4 (A)"** — so the
   English/retail market labels 2.4 as **A**, which the strict table assigns to 2.3. There is a
   real offset between the strict 正律 table and market labelling, and I could not characterise it.
   §4.5, §6.1.

8. **No pitch standard is stated anywhere.** A=440 vs A=442 vs pre-Meiji standards: not one source
   gave a reference frequency for the shakuhachi. Since 正律 labelling means makers tune **to a
   pitch**, this is not academic. §4.8.

9. **No verified price for a handmade *jinashi* by a named maker.** Mejiro has a "New Jinashi
   Shakuhachi for Sale" category; it 403/404'd. Every price I verified is for *jiari* bamboo,
   plastic, or wood. §6.1.

10. **Phytosanitary / plant-import rules for raw bamboo: entirely unresearched.** Separate from
    CITES, real, and likely to differ between raw culm and a finished lacquered instrument.
    Relatedly, **no specific national ivory ban** (US ESA 4(d), UK Ivory Act 2018, EU measures,
    Japan's domestic registration regime) was researched — and for a player those are the
    practically decisive rules, stricter than CITES. §6.4.

11. **cites.org is entirely inaccessible (HTTP 403 on every route).** I therefore could **not**
    verify the Musical Instrument Certificate's **Resolution number** (reputedly Conf. 16.8), its
    validity period, or its conditions from the primary text. UK guidance confirms the certificate
    exists, is non-commercial, and is free of charge — and that the 3-year validity belongs to
    *travelling-exhibition* certificates, not to this one. §6.4.

12. **管尻 *kanjiri* and 根曲がり *nemagari* are unverified terms.** Neither appears in
    ja.wikipedia 尺八 nor in the kotobank entries I read. They are standard player vocabulary but I
    could not source them, and I could not confirm the usual claim that *nemagari* bamboo is sought
    specifically for long instruments. §1.7.

13. **The *nakatsugi*'s exact position** (conventionally between the 3rd and 4th holes) remains
    unverified, even though the metal ring is now confirmed. §1.6, §6.3.

14. **Was the *gagaku* shakuhachi bevelled inward or outward?** ja.wikipedia 簫 (citing 小学館) calls
    the Shōsōin instrument "a kind of *dòngxiāo*" (implying inward); ja.wikipedia 一節切 (citing
    国史大辞典) says the outward cut is "common to the 古代尺八 and the 普化尺八". **Unresolved, and
    it matters** — it decides whether the outward bevel is a Nara-period import or a later Japanese
    innovation. Yoshikawa's 2012 JASA abstract, "Changes in acoustical design from ancient
    shakuhachi to modern shakuhachi", is very likely the paper that answers it, and it is an
    abstract I could not obtain. §7.2, §5.1.

15. **No study of wall material vs tone.** ja.wikipedia reports the question as contested between
    two practitioner web pages and says tone and material are "held to be scientifically
    unrelated". There is no peer-reviewed study either way. Likewise **no work on vocal-tract
    tuning in shakuhachi playing**, despite the UNSW group having done exactly that for saxophone
    and voice, and despite ja.wikipedia stating that oral-cavity shape changes alter the harmonic
    content. §2.5, §5.6.

16. **Travel with the instrument: no source at all.** §6.3.

17. **The modern Chinese *chiba* revival: unresearched.** §7.5. Also unverified: the term 南簫
    *nanxiao* itself (the Japanese source calls the Fujian instrument 洞簫), and the scientific name
    of 布袋竹 *hoteichiku* — which, after correction 1, should not be taken on trust either. §7.4.

### 8.3 Method notes for whoever picks this up

What worked, for the record: **Yahoo! Japan search** (when DuckDuckGo-class engines are walled);
**raw wikitext via the MediaWiki API** (`action=query&prop=revisions&rvslots=main`) rather than
rendered pages — this is how the internal contradictions in §1.5 and §2.1 became visible at all;
**kotobank** for the printed encyclopedias; **api.crossref.org** for bibliography; **GBIF's
`species/match` API** for taxonomy; **the eCFR API** (needs `Accept-Encoding` permitting
compression) when `ecfr.gov` web redirects away; **METI's Japanese-language mirrors of the CITES
appendices** when `cites.org` 403s — these need a **Referer header** from the parent page or they
403 too; and **`pdftotext`**, present at `/opt/homebrew/bin/pdftotext`, which makes PDF appendix
searches exact rather than eyeballed.

What failed: `cites.org` (403, everything), `jstage.jst.go.jp` for `ast/36/4/36_314` (500,
everything), `speciesplus.net` API without a token (returns a fixed 25-record demo, so **it cannot
support a negative claim**), `pubs.aip.org` (redirect served the wrong article), Taylor & Francis,
and `eur-lex.europa.eu` (TLS SNI mismatch, then connection failure).
