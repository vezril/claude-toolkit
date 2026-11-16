# The Shamisen: Scholarly Sources and Bibliographic Verification

Compiled by the coordinating agent, 2026-11-13, to fill the one gap the four research agents all
reported: **no general web search was reachable, and Brill / Taylor & Francis / Project MUSE /
Scholarly Publishing Collective all returned HTTP 403**, so the agents could verify books as
objects but could not find or cite the journal literature.

Every item below was retrieved from a **structured metadata API** rather than a web page, which is
why these worked when search did not:

- **Crossref REST API** (`api.crossref.org`) — authoritative for DOI, title, subtitle, author,
  container, volume, issue, pagination, publisher, ISBN, issue date.
- **OpenLibrary search API** (`openlibrary.org/search.json`) — publisher, year, ISBN, page count.
- **OSF API** (`api.osf.io/v2/preprints/<id>/`) — preprint abstracts in full, verbatim.

**What this file is and is not.** Every citation here is **[V] as a bibliographic object** — the
metadata is from the publisher's own Crossref deposit. **Content was not read** except where a
verbatim abstract is quoted, which is marked. Do not attribute an argument to any of these works on
the strength of this file alone.

---

## 1. The reference-work entries (start here)

- **Malm, William P., and David W. Hughes. "Japan, §VII: Instruments and instrumental genres —
  'Shamisen'." *Grove Music Online* / Oxford Music Online. Oxford University Press, 2001.**
  DOI `10.1093/omo/9781561592630.013.90000382380`. **[V]** — note the **two** authors: the standard
  Grove treatment is Malm *with* Hughes, who is the leading Anglophone authority on Japanese folk
  song. Citing "Malm in Grove" alone is incomplete.
- **"Shamisen." *Grove Music Online*, 2001.** DOI `10.1093/gmo/9781561592630.article.25576`
  (unsigned in the Crossref record). **[V]**
- **Johnson, Henry. "Yanagawa shamisen." *Grove Music Online*. Oxford University Press,
  2015-05-28.** DOI `10.1093/gmo/9781561592630.article.l2281939`. **[V]** — establishes Johnson as
  Grove's contributor on the instrument, which is the reason his 2010 monograph carries weight.
- **Mitsui, Tōru. "Shamisen." *Bloomsbury Encyclopedia of Popular Music of the World*, 2003.**
  DOI `10.5040/9781501329234-007053`. **[V]** — the popular-music-studies framing, distinct from the
  ethnomusicological one.

## 2. The two articles that answer questions the encyclopedias do not

These are the highest-value finds in this pass. Both are directly on points the research files had
to leave unsourced.

- **Sakata, Lorraine. "The Comparative Analysis of *Sawari* on the Shamisen." *Ethnomusicology*
  10, no. 2 (May 1966): 141–.** DOI `10.2307/924695`. **[V]**
  This is the scholarly article on the sawari, and it is sixty years old and apparently still the
  only one. Its existence matters for how the sawari section should be written: the biwa-derivation
  story and the Indian-*javari* story are both **hypotheses in the popular literature**, and the one
  piece of actual comparative analysis in the Anglophone record is this. Obtain it before asserting
  either origin.
- **Tokita, Alison McQueen. "Mode and Scale, Modulation and Tuning in Japanese Shamisen Music:
  The Case of Kiyomoto Narrative." *Ethnomusicology* 40, no. 1 (1996): 1–.**
  DOI `10.2307/852434`. **[V]**
  The scholarly treatment of exactly the cluster the technique file had to reconstruct from
  Kotobank: mode vs scale, *why* tuning changes mid-piece, and what modulation means on a fretless
  three-string instrument. Tokita is also the author of the *Naniwa-bushi* chapter in the Brill
  Handbook (§5) and a reviewer of Groemer (§4), i.e. a central figure. **If one paywalled item is
  to be obtained, make it this one** — it is the authority for the whole tuning-and-scale section,
  and it is specifically about a *narrative* genre, where the English literature is thinnest.

## 3. The monographs

- **Johnson, Henry. *The Shamisen: Tradition and Diversity*. Brill, 2010.**
  ISBN 978-90-04-18137-3 / 90-04-18137-7, 145 pp. **[V]** (OpenLibrary; Brill's own site 403s.)
  Two **reviews**, which are the fastest route to a critical read and are themselves citable:
  - **Prescott, Anne.** *Ethnomusicology* 57, no. 1 (2013): 133–135. DOI
    `10.5406/ethnomusicology.57.1.0133`. **[V]**
  - **Hughes, David W.** (SOAS). *Ethnomusicology Forum* 25, no. 3 (Sept 2016): 371–373. DOI
    `10.1080/17411912.2016.1234939`. **[V]** — a **joint** review of Johnson's shamisen and
    shakuhachi books. Hughes is the Grove co-author (§1); this is the review to read.
- **Adriaansz, Willem. *Introduction to Shamisen Kumiuta*. Frits Knuf, 1978, 127 pp.** **[V]**
  (OpenLibrary.) The monograph on the oldest art repertoire — the genre the history file identifies
  as the hinge of the whole tradition and for which it could find no English source at all.
  Reviewed by **Tokumaru Yosihiko**, *Ethnomusicology* 25, no. 1 (1981): 156, DOI `10.2307/850999`;
  and by **Jeremy Montagu**, *Galpin Society Journal* 33 (1980): 142, DOI `10.2307/841845`. **[V]**
- **Groemer, Gerald. *The Spirit of Tsugaru: Blind Musicians, Tsugaru-jamisen, and the Folk Music
  of Northern Japan. With the Autobiography of Takahashi Chikuzan*. Harmonie Park Press / Tsugaru
  Shobō, 1999, 321 pp.** ISBN 0-89990-085-2 / 978-0-89990-085-8. **[V]**
  **The subtitle is now verified.** OpenLibrary's record omits it, which is why an earlier pass
  flagged it unverified; it is confirmed by **three** independent review titles in Crossref:
  - **Fritsch, Ingrid.** *Monumenta Nipponica* 55, no. 2 (2000): 312. DOI `10.2307/2668443`
  - **Halliwell, Patrick.** *Asian Folklore Studies* 60, no. 1 (2001): 158. DOI `10.2307/1178707`
  - **Tokita, Alison McQueen.** *Ethnomusicology* 50, no. 1 (2006): 157–159. DOI `10.2307/20174433`
  All three review titles carry the full subtitle including "With the Autobiography of Takahashi
  Chikuzan," which also confirms that the Chikuzan autobiography is **inside this book** — it is not
  a separate publication.
- **Daijō Kazuo, Suda Naoyuki, and Anthony Rausch. *The Birth of Tsugaru Shamisen Music: The Origin
  and Development of a Japanese Folk Performing Art*. Aomori University Press, 1998, 219 pp.**
  ISBN 4-900027-00-6 / 978-4-900027-00-8. **[V]** (OpenLibrary gives Daijō as author and the 1998
  Aomori University Press imprint; the full subtitle comes from the *Japanese Sociological Review*
  review title.)
  **This is the book that makes Nitabō the founder of the genre, in English** — and therefore the
  book Groemer disputes. Having both on the shelf is the whole point: the Nitabō question is a
  live disagreement between two obtainable English-language sources, not a settled fact.
  Reviews: *Contemporary Sociological Studies* (Hokkaido Sociological Association) 12 (1999):
  88–93, DOI `10.7129/jject.12.88`; *Japanese Sociological Review* (Japan Sociological Society) 51,
  no. 1 (2000): 182–184, DOI `10.4057/jsr.51.182`. **[V]**
- **Rausch, Anthony S. *Cultural Commodities in Japanese Rural Revitalization: Tsugaru Nuri
  Lacquerware and Tsugaru Shamisen*. Brill, 2010, 232 pp.** ISBN 978-90-04-17996-7 /
  978-90-474-4426-8. DOI `10.1163/ej.9789004179967.i-232`. **[V]**
  The political economy of tsugaru-shamisen as a **regional-revitalization commodity** — the
  dimension the romantic account omits entirely. Chapter pagination (all **[V]** from Crossref):
  ch. 2 "The Tsugaru District of Aomori Prefecture" 15–32; ch. 3 "Culture in Revitalization" 33–61;
  ch. 4 "Tsugaru Revitalization Policy and Cultural Commodities" 63–98; ch. 5 "**The Production of
  Tsugaru Cultural Commodities**" 99–142; ch. 6 "**The Consumption of Tsugaru Cultural
  Commodities**" 143–182; ch. 7 "Cultural Commodities and Local Revitalization" 183–208;
  Appendices 209–219; References 221–229.
  Four reviews exist, which is unusual for a Brill monograph and indicates it landed:
  *Journal of Cultural Economics* 35, no. 1 (2011): 77–80, DOI `10.1007/s10824-010-9132-0`;
  *Asian Journal of Social Science* 39, no. 4 (2011): 553–555, DOI `10.1163/156853111x598098`;
  *Journal of Modern Craft* 4, no. 2 (July 2011): 221–223, DOI
  `10.2752/174967811x13050332209486`; and one more in the same cluster. **[V]**
- **Matsue, Jennifer Milioto. *Focus: Music in Contemporary Japan*. Routledge, 2015/2016, 275 pp.**
  ISBN 978-1-138-79140-7 / 978-1-138-79138-5 / 978-1-315-76285-2. **[V]**
  Contains a feature that is hard to find anywhere else and is exactly what the notation section
  needs: **the same piece, "Echigojishi," printed in two different shamisen notations side by
  side** — "Echigojishi" (**Yoshizumi Kojūrō-fu**) at p. 255, DOI `10.4324/9781315762852-26`, and
  "Echigojishi" (**Kineya bunkafu**) at p. 256, DOI `10.4324/9781315762852-27`. **[V]**
  Note what this confirms independently of the NDL catalogue work in the technique file: the
  bunkafu is attributed to **Kineya** (杵家), and a **separate, competing** publisher/school
  notation under the name Yoshizumi Kojūrō exists and was in print.
- **Malm, William P. *Traditional Japanese Music and Musical Instruments*. Kodansha International,
  2000.** ISBN 4-7700-2395-2. **[V]** (OpenLibrary.) The revised successor to his 1959 *Japanese
  Music and Musical Instruments*. English Wikipedia's shamisen-origins footnote points at p. 213 of
  this, and **Malm supplies only "the 16th century" and "Sakai" — not the year 1562.** That matters:
  the 1562 date cannot be laundered through Malm.
- **Arisawa, Shino(?). *Transmission of Japanese Jiuta Sōkyoku for Shamisen and Koto*. Routledge,
  forthcoming 2026-04-29.** DOI `10.4324/9781003727316`. **[V] as a forthcoming object only** —
  flagged because, if it appears, it will be the first English monograph on jiuta transmission and
  will supersede part of the jiuta section.

## 4. Keisuke Yamada — the leading living Anglophone scholar on this instrument

None of the four research files found him, and he is the single most important omission. Four works,
all **[V]**:

- **"Rethinking Iemoto: Theorizing Individual Agency in the Tsugaru Shamisen Oyama-ryū."
  *Asian Music* 48, no. 1 (2017): 28–57.** DOI `10.1353/amu.2017.0002`.
  The scholarly treatment of the iemoto question *specifically inside the tsugaru world* — i.e.
  precisely the question "does the iemoto system even apply to tsugaru-jamisen?" that both the
  history and technique files had to answer from Japanese encyclopedias and a school's own website.
- **"*Shamisen* skin on the verge of extinction: musical sustainability and non-scalability of
  cultural loss." *Ethnomusicology Forum* 26, no. 3 (2017): 373–396.**
  DOI `10.1080/17411912.2018.1423575`.
  **The citation for the skin crisis.** The dog-and-cat-skin question is otherwise handled in the
  English-language record only by newspapers, forum posts and dealers' blogs, which is why the
  research files had to flag the whole causal story as unsourced. This is a peer-reviewed treatment
  of it as a *sustainability* problem.
- **"The Political Economy of Nonlife: Biopower, Ontosecurity, and the *Shamisen* Skin Trade in
  Japan." In *The Oxford Handbook of Economic Ethnomusicology*. Oxford University Press,
  2020-07-09.** DOI `10.1093/oxfordhb/9780190859633.013.35`.
  The companion piece, on the **trade** rather than the instrument.
- **"Rethinking the Evolution of Japanese Music: Kunimoto Takeharu and Katō Kinji's Electric
  Shamisen." In *Handbook of Japanese Music in the Modern Era*, 372–385. Brill, 2023.**
  DOI `10.1163/9789004687172_024`. The electric-shamisen and modernization thread.

## 5. *Handbook of Japanese Music in the Modern Era*, ed. Henry Johnson. Brill, 2023

ISBN 978-90-04-68717-2. **[V]** — the current state-of-the-field reference, published after every
book the research files cite, and **not mentioned in any of them**. Full verified table of contents
for the chapters bearing on this topic (pagination from Crossref deposits):

| pp. | chapter | author(s) |
|---|---|---|
| 1–18 | Introduction: Japanese Music in the Modern Era | Johnson |
| 70–84 | The "Heike Brothers" and the 800-Year Transmission and Reception of Heike Musical Narrative | Komoda, Tokita |
| 119–136 | Getting into Min'yō: Online and Offline Access to Japanese Folk Song | Greenland |
| **137–155** | **Traditional Folk Music in Contemporary Japan: Case Studies of Standardization and Diversification in Tsugaru Shamisen and Folk Song** | **Chiba, Savage** |
| 156–172 | Naniwa-bushi: A Musical Narrative Born in Modern Japan | Tokita |
| 173–187 | An Innovative Conservative: Satsuma-biwa Practice and the Legacy of Fumon Yoshinori | de Ferranti, Marshall |
| 301–316 | Ryukyuan Uta-sanshin in Modern Japan: The Influence of Government Institutions on Teaching and Performing | Gillan, Endō |
| 317–334 | Koto Modernities in the Twenty-First Century | Johnson |
| **356–371** | **The Innate Hybridity of the Shamisen within Contemporary Music: The Physical, Musical, and Socio-Cultural** | **Schmuckal** |
| **372–385** | **Rethinking the Evolution of Japanese Music: Kunimoto Takeharu and Katō Kinji's Electric Shamisen** | **Yamada** |

Also useful for the 20th-century section: 237–253 "Learning Musical Instruments in Japanese
Schools" (Hebert, Matsunobu) and 286–300 "The Suzuki Method, Yamaha System, and Japanese
Traditional Music" (Kubo) — both bear on *why the koto entered school music education and the
shamisen did not*, which the history file identifies as an open question.

Related: **Regan, "Shamisen Works by Colleen Christina Schmuckal: Performed by Tetsuya Nozawa,"
*Asian Music* 53, no. 1 (2022): 160–165**, DOI `10.1353/amu.2022.0008` **[V]** — a review of new
concert repertoire, by the author of the Handbook's hybridity chapter.

## 6. The one quantitative study of the tsugaru competition circuit — with real numbers

The competition circuit is where the English-language account turns most confidently cynical
("competitions standardized and sterilized the music"). There is an actual experiment, it is open
access, and **its result is more interesting than the cynical claim**.

**Chiba, Gakuto, Yuto Ozaki, Shinya Fujii, and Patrick E. Savage. "Sight vs. Sound Judgments of
Music Performance Depend on Relative Performer Quality: Cross-cultural Evidence From Classical
Piano and Tsugaru Shamisen Competitions." *Collabra: Psychology* 9, no. 1 (2023).**
DOI `10.1525/collabra.73641`. A **Stage 2 Registered Report** — i.e. the predictions were
preregistered before the data were seen, which is why the partial disconfirmation below is
trustworthy rather than a post-hoc story. Open-access preprint: `10.31234/osf.io/xky4j`. **[V]**

Design and results, **quoted from the abstract retrieved verbatim via the OSF API** (so **[V]** for
content, unusually for this file):

- **n = 155 participants**, Japanese.
- **40 performers total, from 10 piano and 10 shamisen competitions**: in 5 competitions of each
  kind, participants chose between the 1st- and 2nd-placing performers; in 5 others, between the
  1st-place and a low-ranking performer.
- Stimuli were **6-second excerpts**, presented **video-only vs audio-only**.
- Three preregistered predictions, each tested twice (piano, shamisen): (1) an interaction between
  domain and variance in quality; (2) visuals trump sound when quality variance is low; (3) sound
  trumps visuals when quality variance is high.
- **Result: prediction (1) confirmed for both** piano and shamisen — "suggesting that this
  interaction is cross-culturally general." **Prediction (2) was supported only for piano.**
  **Prediction (3) was supported only for shamisen** — "suggesting culturally dependent factors in
  the specific balance between sight and sound in the judgment of musical performance."

**How to use this.** It does **not** show that tsugaru competitions are judged on looks. It shows
the opposite asymmetry from piano: in the shamisen condition, **sound** dominated where the quality
gap was wide, and the visual-dominance effect that shows up at the top of piano competitions did
**not** replicate for shamisen. Any claim that the competition circuit rewards showmanship over
sound needs to reckon with this, and the honest version is that the one controlled study points
the other way. Cite the preregistration status — it is what makes the null results meaningful.

Companion chapter, same authors, qualitative: **Chiba and Savage, "Traditional folk music in
contemporary Japan: Case studies of standardization and diversification in Tsugaru shamisen and
folk song,"** preprint DOI `10.31234/osf.io/mwb2z` (2022-09-05), published as ch. 10 of the Brill
Handbook, pp. 137–155, DOI `10.1163/9789004687172_010`. **[V]** Abstract retrieved verbatim via the
OSF API: it is **two autoethnographic case studies, one by each author**, describing their own
experience performing the music, explicitly offered as "a more qualitative perspective" on the
"melodic evolution" and "audiovisual interactions" they had published quantitatively elsewhere.
**It is not a quantitative standardization study** — do not cite it as measuring standardization.

## 7. Gerald Groemer's wider work — the context for the blind-musician sections

Groemer is the authority for the social history, and *The Spirit of Tsugaru* is only the most
obvious of his relevant publications. All **[V]**:

- ***Goze: Women, Musical Performance, and Visual Disability in Traditional Japan*. Oxford
  University Press, 2016.** ISBN 978-0-19-025903-7 / 0-19-025903-5 / 978-0-19-025906-8.
  DOI `10.1093/acprof:oso/9780190259037.001.0001`.
  The monograph on the **goze**, and the single most important source for that section. Verified
  chapter structure and pagination: Preface xv–xxvi; 1 Introduction 1–14; 2 **The Production of
  Visual Disability** 15–36; 3 The Development of Echigo *Goze* Associations 37–82; 4 Learning the
  *Goze* Art and Way of Life 83–119; 5 Touring and Performing in Echigo 120–187; 6 Endings 188–204;
  7 After the End 205–218; Appendix 219–236.
  Note chapter 2's title. Groemer's frame is that visual disability was **produced** by social and
  medical conditions, not simply suffered — which is the analytical move that distinguishes his
  account from the romantic one, and it applies equally to the *bosama* of Tsugaru.
- **"The Guild of the Blind in Tokugawa Japan." *Monumenta Nipponica* 56, no. 3 (2001): 349–.**
  DOI `10.2307/3096791`. **The citation for the 当道座 tōdōza.**
- ***Street Performers and Society in Urban Japan, 1600–1900*. Routledge, 2016.** ISBN
  978-1-317-40990-8. DOI `10.4324/9781315684680`. The context for *kadozuke* / door-to-door
  performance, i.e. what the bosama actually did for a living.
- **"Visual disability and musical culture in Edo-period Japan." In *The Tokugawa World*, 543–559.
  Routledge, 2021.** DOI `10.4324/9781003198888-38`. The short, current, citable synthesis — the
  best single thing to read first.
- **"Who Benefits? Religious Practice, Blind Women (Goze), Harugoma, and Manzai." *Japanese Journal
  of Religious Studies* 41, no. 2 (2014): 347–386.** DOI `10.18874/jjrs.41.2.2014.347-386`.
  Open access (JJRS is).
- **"A Short History of the Gannin: Popular Religious Performers in Tokugawa Japan." *Japanese
  Journal of Religious Studies* 27, no. 1–2 (2000): 41–72.** DOI
  `10.18874/jjrs.27.1-2.2000.41-72`. Open access.
- **"Fifteen Years of Folk Song Collection in Japan: Reports and Recordings of the 'Emergency Folk
  Song Survey'." *Asian Folklore Studies* 53, no. 2 (1994): 199–.** DOI `10.2307/1178643`.
  The guide to the 緊急民俗芸能調査 recordings — i.e. **where the primary audio evidence for
  regional min'yō actually is**.
- **"Singing the News: *Yomiuri* in Japan During the Edo and Meiji Periods." *Harvard Journal of
  Asiatic Studies* 54, no. 1 (June 1994): 233–.** DOI `10.2307/2719392`.
- **"Outcast status in historical Japan." In *Handbook of Buraku Studies*, 20–35. Routledge,
  2026.** DOI `10.4324/9781003756507-2`. Relevant to the 河原者 / 非人 material: the 1580
  *Oyudono no ue no nikki* player and the people whose instruments were burned in 1842.
- Review: **Groemer on Wei Yu Wayne Tan, *Blind in Early Modern Japan: Disability, Medicine, and
  Identity*. *Monumenta Nipponica* 77, no. 2 (2022): 334–340.** DOI `10.1353/mni.2022.0055`.
  Tan's book (University of Michigan Press, 2022) is the newest monograph on blindness in Japan and
  Groemer's assessment of it is the place to start on whether it supersedes him.

## 8. The woods, verified as species — and the CITES position

The CITES status of the shamisen woods was a specific question. Here is what is verifiable and
what is not. The **species identifications matter more than the trade law**, because the trade law
changes and the species constrain what is physically available.

- **紅木 kōki = *Pterocarpus santalinus*** (red sanders / red sandalwood). **[V]**
  - **CITES Appendix II.** **[V]** (English Wikipedia, *Pterocarpus santalinus*, read 2026-11-13;
    no listing date given there.) **[U]** on the listing date and on which annotation applies.
  - **IUCN status is genuinely contradictory in the record**: the article's infobox gives
    **Endangered**, citing a **13 November 2021** assessment, while its conservation-status section
    says the species was "later reclassified to **Near Threatened** in 2018." The page does not
    resolve this. **Report the conflict; do not pick a side.**
  - **Endemic to the southern Eastern Ghats of South India.** **[V]** This is the point with real
    consequences: the premium shamisen wood is a **single-region endemic** of a country that
    restricts its export, which is why kōki supply is a structural problem for the instrument and
    not a market fluctuation.
- **花梨 karin = *Pterocarpus indicus*** (amboyna / Burmese rosewood). **[V]**
  - **Not CITES-listed** per the English Wikipedia article (read 2026-11-13) — **[U]**, an absence
    of mention is weak evidence; verify against Species+ before stating it.
  - **IUCN Endangered**; "many populations are seriously threatened"; **extinct in Vietnam** and
    possibly in Peninsular Malaysia and Sri Lanka. **[V]**
  - Native range **includes the Ryukyu Islands** **[V]** — a pleasing detail given the instrument's
    transmission route. Explicitly "used for … musical instruments." **[V]**
- **紫檀 shitan = *Dalbergia* spp.** **[V]**
  - **All *Dalbergia* are CITES-listed: Appendix II except *D. nigra*, which is Appendix I.**
    **[V]** (English Wikipedia, *Dalbergia*, read 2026-11-13, citing the CITES appendices.)

**SUPERSEDED — defer to `instrument.md` on the annotations.** This section was written before
`references/instrument.md` landed, flagging the annotation numbers and CoP history as
unverifiable because cites.org, speciesplus.net, FWS and NAMM all refused me. **The instrument reference got them**,
by a route I had not tried: the **League of American Orchestras / industry-coalition document of
April 2021**, which quotes **Annotation #15 verbatim**, plus Kew's *CITES and Timber* and a CITES
SC74 document on red sanders. Its §10 table and verification notes are the authority; read those
and not this. Three things from it are worth carrying forward here because they change the answer:

1. **Finished instruments are exempt under #15(c)** — "finished musical instruments, finished
   musical instrument parts, and finished musical instrument accessories" — alongside a **10 kg
   per shipment** allowance for other finished products. So the common case is *not* controlled,
   which is the opposite of the cautious formulation I had written.
2. ***Dalbergia cochinchinensis* (Siamese rosewood) is expressly excluded from #15** and falls
   under **Annotation #4, which has no instrument exception**. Since the Japanese trade name
   **紫檀 is loose**, an owner may not know which species their instrument is. The instrument reference calls this
   the nastiest wrinkle in the topic and is right.
3. **Kōki (*P. santalinus*) is Appendix II under Annotation #7** — only **logs, wood chips, powder
   and extracts** are controlled — so a **finished** kōki instrument is not CITES-controlled
   either. The instrument reference flags **[U]** on the *number*, because Kew's edition calls it **#12**; the
   substance is triply attested. It also notes that the Japanese trade claim that kōki "is banned
   from import" is **overstated**, and that India's own export controls on red sanders are the
   likelier cause of scarcity — which fits the endemism point above.

The one point here that still stands, and that `instrument.md` also lists as an open question, is **karin**:
no CITES listing for *Pterocarpus indicus* was found by either pass, and both are arguing from
absence. Given that African *Pterocarpus* spp. were added to Appendix II effective **25 November
2024**, that deserves a direct check against the current appendices before anyone ships a dō.

## 8b. The acoustics chapter — full citation, and the erratum nobody cites

The instrument reference's quantitative backbone is one chapter, read in full, and it is the only quantitative
shamisen acoustics in the literature either of us could find. Its full verified citation:

> **Yoshikawa, Shigeru. "Plucked String Instruments in Asia." Chapter 11 in Thomas D. Rossing (ed.),
> *The Science of String Instruments*, 173–195. Springer New York, 2010.**
> ISBN 978-1-4419-7109-8 / 978-1-4419-7110-4. DOI `10.1007/978-1-4419-7110-4_11`. **[V]**
> (Crossref, 2026-11-13.)

**There is an erratum, and it should be cited alongside the chapter. [V]**

> **Yoshikawa, Shigeru. "Erratum to: Plucked String Instruments in Asia." In *The Science of String
> Instruments*, E1–E3. Springer New York, 2010.** DOI `10.1007/978-1-4419-7110-4_24`.

I read the erratum's notices (via a three-hop `idp.springer.com` cookie redirect, which is the only
way through Springer's paywall shell). **Good news for `instrument.md`: the erratum does not touch any
shamisen number.** Its four corrections are **[V]**, read verbatim:

1. **Fig. 11.5** "should consist of 16 parts, from (a) to (p) as shown."
2. **p. 184, line 8 from the bottom:** "in Fig. 11.5d, e," should read "in **Fig. 11.4**d, e,".
3. **Fig. 11.6** "should consist of two parts (a) and (b) as shown."
4. **Table 11.2 caption:** the source line should read "**(Takasawa 1993)**."

So the sawari-as-energy-transfer argument, the 700 Hz spectral peak, the 25 dB/oct low-end roll-off
and the bridge-mass sensitivity all stand unamended. Two things to carry forward anyway:

- Correction 2 means a **figure cross-reference in the published chapter is wrong**, so anyone
  following the chapter's own pointers from p. 184 will land on the wrong figure. Worth knowing
  before quoting anything keyed to Fig. 11.5.
- Correction 4 **confirms an attribution `instrument.md` already makes**, which is worth recording
  because it is the kind of thing that decays into folklore. That file's only skin-tension figure
  (**2,000 N/m**, with surface density 0.040 kg/m² and membrane wave speed 220 m/s on a
  0.16 × 0.16 m square) is cited there as **Yoshikawa 2010, Table 11.2, from Takasawa 1993** — and
  the erratum's corrected caption independently fixes Table 11.2's source line as
  **"(Takasawa 1993)."** So the number is **Takasawa's finite-difference model as reported by
  Yoshikawa**, not Yoshikawa's own measurement, and the published caption needed an erratum to say
  so. Since this appears to be the only quantitative datum on shamisen skin tension in existence,
  cite it through both names.

**A live lead on the sawari acoustics, which `instrument.md` lists as an open question.** Crossref surfaced:

> **Kemp, J. "The Effects of Vibrational Energy Transmitted to Sections of String Outside the Main
> Sounding Length in Plucked String Instruments." *Acoustics 2023*, Institute of Acoustics,
> 2023-10-23.** DOI `10.25144/16593`. **[V] as a bibliographic record only** — the IoA catalogue
> page 404'd and the abstract was not read.

The title describes **exactly the sawari mechanism** — energy transmitted into the length of string
*beyond* the sounding length — which is the physics behind both the shamisen's sawari and the
sitar's *jawari*. If it treats either instrument, it is **thirteen years newer than Yoshikawa and
fifty-seven years newer than Sakata 1966**, and it would be the first modern acoustic work on the
question. **Chase this one** — it is the highest-value unread item for §2.3 and §2.6 of `instrument.md`.

## 8c. The tsugaru-shamisen literature in English — four articles and a dissertation

The Tsugaru tradition has a small, concentrated Anglophone literature, almost all of it in one
journal. All records **[V]** from Crossref, 2026-11-13; **content not read** unless stated.

- **McGoldrick, Gerald Thomas. "Tsugaru Shamisen and Modern Japanese Identity." PhD dissertation,
  York University, 2017. 305 pp.** `hdl.handle.net/10315/33622` → the YorkSpace record resolves to
  `yorkspace.library.yorku.ca/items/de46b733-7be5-432f-b451-2c15e2ea480b`; date issued
  **2017-07-27**; PDF `McGoldrick_Gerald_T_2017_PhD.pdf`, 4.99 MB; filed under the Music
  collection; keyword "Asian studies". **[V]** — and **open access, and read in full** for the
  `tsugaru-shamisen` skill, which is why that skill's Groemer citations are page-cited at all.
  The abstract traces the music from the *bosama* through the 1970s and 2000s revivals, using
  discourse analysis plus the author's own participation, engaging 1930s Japanese thinkers on
  modernity and tradition, and examining **how national contests have shaped the genre** — the
  dissertation is itself a competition ethnography. Its thesis, in its own words, concerns
  "a Japanese identity that is modern but still essentially Japanese."
  **This is the single most useful English-language source on the subject and it is free.**
- **Johnson, Henry Mabley. "Tsugaru Shamisen: From Region to Nation (and Beyond) and Back Again."
  *Asian Music* 37, no. 1 (March 2006): 75–100.** DOI `10.1353/amu.2006.0005`. **[V]**
  Paywalled. By the author of the Brill monograph and of Grove's "Yanagawa shamisen" entry (§1),
  which makes him the obvious authority on the region-to-nation framing.
- **Peluse, Michael S. "Not Your Grandfather's Music: Tsugaru Shamisen Blurs the Lines Between
  'Folk,' 'Traditional,' and 'Pop'." *Asian Music* 36, no. 2 (June 2005): 57–80.**
  DOI `10.1353/amu.2005.0024`. **[V]** — full subtitle confirmed from the Crossref deposit.
  Paywalled. The genre-category question, which is exactly the one the commercial era raises.
- **Yamada, Keisuke. "Rethinking Iemoto…" *Asian Music* 48, no. 1 (2017): 28–57** — see §4.
  Note the year: **Crossref's deposit says 2017**, and secondary citations giving 2016 are wrong.
- **Groemer, Gerald. 「津軽三味線における即興演奏的要素の分析」 ("An analysis of improvisatory
  elements in tsugaru-shamisen"), *Tōyō Ongaku Kenkyū* 東洋音楽研究 57 (1993): 41–61.**
  **[U — identified, not read, and not located in Crossref.]** The only study of **improvisation**
  in the tradition, and the one that would answer what *kyokubiki* actually consists of.
- **Barsky, Jacob. "Shaping a Music Genre through Competition and Virtuosity." MA thesis,
  University of Hawaiʻi at Mānoa, 2013.** **[U — repository behind a Cloudflare challenge.]**

**One bibliographic point worth flagging.** Groemer's *The Spirit of Tsugaru* has **two editions**:
the 1999 Harmonie Park Press / Tsugaru Shobō first edition (§3) and a **revised second edition,
Tsugaru Shobō, 2012**. McGoldrick cites **the 2012 revision** by page throughout. Page references
taken from McGoldrick therefore point at the 2012 text, not the 1999 one, and the two should not be
mixed. (This also resolves the double ISBN in the OpenLibrary record at §3: the 978-4-806602-20-0
number is the Japanese publisher's.)

## 9. What the Japanese reference works actually say about tsugaru-jamisen

Fetched from **kotobank.jp** (which aggregates the printed Japanese dictionaries and encyclopedias
and, unlike the publishers' own sites, serves readable pages), 2026-11-13. All **[V]** as reports of
those entries. This section exists because the result is sharply corrective of the standard English
narrative.

### 9.1 The headline: Nipponica's entry on 津軽三味線 does not mention Nitabō *or* bosama

**[V]** The entry on 津軽三味線 at `kotobank.jp/word/津軽三味線` collates **デジタル大辞泉**,
**精選版 日本国語大辞典**, and **日本大百科全書 (Nipponica)**, the longest of the three.
**Neither 仁太坊 nor 坊様 appears in any of them.**

The lineage Nipponica names for the style as it now exists is **梅田豊月 Umeda Hōgetsu, 白川軍八郎
Shirakawa Gunpachirō, 木田林松栄 Kida Rinshōei, and 高橋竹山 Takahashi Chikuzan** — performers who
"added showy solo pieces." That is a **20th-century** lineage, and it starts one generation *after*
the figure the English literature treats as the founder.

This does not refute the Nitabō account (see §9.3, where he has his own entry). It establishes
something more useful: the standard Japanese encyclopedia treatment of the genre is organised
around the **20th-century professionalisation**, not around a founding individual. Any write-up that
opens with Nitabō is adopting Daijō Kazuo's framing (§3), not the reference literature's.

### 9.2 Three hard facts from Nipponica that change the shape of the story

**(a) The genre name is post-war — c. 1956. [V]** Nipponica states that the name **津軽三味線**
became common **around 1956**, beginning with a stage show featuring **三橋美智也 Mihashi Michiya**
(a major popular *min'yō*-trained singer) and **木田林松栄 Kida Rinshōei**. The *music* is older than
the *name*, and the name comes out of the commercial entertainment industry. Write the periodisation
accordingly: it is not that a 19th-century genre was later commercialised, but that the category
itself was assembled in the mid-1950s around existing players.

**(b) The mechanism of its spread was rōkyoku, not solitary genius. [V]** Nipponica gives **three**
reasons the style spread — **geography, performance conditions, and the influence of 浪花節
(naniwa-bushi / rōkyoku)** — and states that the 津軽三つ物 (below) became popular as **stand-ins
for 浪花節** from late Meiji to early Shōwa, which is what added the show element to performances.
This connects directly to the genre taxonomy: rōkyoku is the *other* futozao narrative genre, and it
was the competitor whose audience tsugaru-jamisen captured. The virtuoso solo idiom is a response to
a market, and the reference work says so.

**(c) 津軽三つ物 — the canonical three. [V]** Nipponica names the **津軽三つ物** (*Tsugaru
mitsumono*) as **じょんがら Jongara, よされ Yosare, and おはら Ohara**. Use this term; it is the
Japanese canon-forming label, and it specifies three, not the longer lists that circulate in English.

**(d) Real numbers on the instrument. [V]** Nipponica gives string gauges for tsugaru as **30, 18,
12** for the 一の糸 / 二の糸 / 三の糸, against **15, 13, 12** for the thinner nagauta shamisen, and
says the body is **slightly larger than a standard futozao**. Note what the comparison shows: the
third string is **identical** (12) and the difference is concentrated almost entirely in the first
string, which is **double** the nagauta gauge. That is precisely consistent with the technique —
the first string is what gets struck with full force to carry the rhythm. Daijisen and Seisen both
give the neck as **太棹**, so the futozao classification is unanimous.

**(e) Technique, in the reference works' own words. [V]** Seisen describes playing with the bachi
「たたくようにして」 ("as if striking"). Nipponica describes striking the **一の糸** with a thick,
heavy bachi 「力いっぱいたたいて」 ("with full force") **to set the rhythm**, with **スクイバチ**
(*sukui-bachi*, scooping upstroke) on the **三の糸** as ornamentation. So *tataki* is not a
decorative flourish in the reference account — it is the **rhythm-generating function**, assigned to
a specific string, with ornament assigned to a different one.

**(f) A notable absence of hedging. [V]** Unlike the origin-story material in `history.md` — where the
Japanese dictionaries are conspicuously thick with 「という」「とされる」「説」 — **none of these
hedges appears in the 津軽三味線 entries.** They use plain passives (〜られる). The Japanese
reference literature is *more* confident about the 20th-century history than about the Edo origins,
which is the opposite of how the English popular account distributes its confidence.

### 9.3 The biographical entries, with dates

All from **`新撰 芸能人物事典 明治～平成`** (Nichigai Associates, 2010) via kotobank, 2026-11-13.
Note that this is a **single printed reference** in each case — these are not multiply-attested
dates, and the dictionary is a performing-arts *who's-who*, not a scholarly biography.

**仁太坊 Nitabō [V]**
- Real name **秋元仁太郎 Akimoto Nitarō**. Born **Ansei 4 = 1857**, in **Kanagi, Mutsu Province**
  (now Aomori Prefecture). Died **2 January 1928** (Shōwa 3).
- **Born to a mother who was herself a blind shamisen player.**
- Lost his sight to **smallpox at age 8** — note, **smallpox**, not the measles that blinded
  Chikuzan; the two are routinely conflated. Lost both parents at 11.
- Around then he **met goze (瞽女), the wandering blind female musicians, and learned their art by
  following them** — the entry hedges this with **「という」**. This is the most important line in
  the entry and the English account drops it: the Tsugaru tradition is connected by its own
  reference literature to the **Echigo goze tradition**, which is exactly the subject of Groemer's
  2016 Oxford monograph (§7). The two bodies of material are not separate topics.
- By **Meiji 4 = 1871**, aged 14, already a skilled player.
- Earned his living as a street performer known as **坊様 bosama** — so *bosama* is attested here
  even though it is absent from the genre entry (§9.1).
- Credited with: breaking older convention by developing a **forceful striking technique on the
  futozao**; creating **八人芸 hachinin-gei**, a one-man act presenting eight people's parts; and
  being the point the modern lineage **「行き着くとされる」** ("is held to be traced back to").
  The founder claim is **hedged in the dictionary itself**.

**白川軍八郎 Shirakawa Gunpachirō (初代, first of the name) [V]**
- Born **23 January 1909** (Meiji 42), **Kanagi-machi, Kita-Tsugaru-gun, Aomori** — now
  **Goshogawara City**; the *same town as Nitabō*. Died **18 May 1962** (Shōwa 37).
- Lost his sight at **age 4**.
- Became a pupil of **Nitabō** — whom this entry calls the **始祖** ("progenitor") of
  tsugaru-shamisen, again with **「とされる」** — and the entry says he soon surpassed his teacher.
  **[U] on the arithmetic:** the entry gives his age at entry as 9 but prints the year as 1914,
  which does not reconcile with a 1909 birth (9 would give 1917–18). Report the relationship, not
  the year.
- **Self-taught** the **太田長作 Ōta Chōsaku** and **梅田豊月 Umeda Hōgetsu** styles — note Umeda is
  the first name in Nipponica's lineage (§9.1), so the two accounts interlock here.
- At **15** created the **軍八郎手 Gunpachirō-de** ("Gunpachirō's hand").
- Credited with establishing **曲弾き kyokubiki** — tsugaru-shamisen as a **solo** art — and with
  raising the instrument's status to **parity with the voice**. Nicknamed **津軽三味線の神様**,
  "the god of tsugaru-shamisen" (「と呼ばれる」, i.e. common usage, not a title).
- **This is the figure to credit with the solo idiom**, not Nitabō. Nitabō's credited innovation is
  the *striking technique*; Shirakawa's is *kyokubiki*.

**木田林松栄 Kida Rinshōei [V]** (sources: the 2010 dictionary above **plus**
`20世紀日本人名事典`, Nichigai Associates, 2004 — so two references, unlike the others)
- Real name **田中林次郎 Tanaka Rinjirō**. Born **Hiraka-machi, Minami-Tsugaru-gun, Aomori**
  (no birth date given in either entry — **[U]**). Died **1 January 1979** (Shōwa 54).
- Began shamisen at **10**, stage debut at **19**. Known for an earthy, intense style.
- **Performed at Expo 67 in Montreal**, and on many overseas tours. **[V]**
  This is the concrete internationalisation datum the English account usually lacks, and it dates
  the instrument's first major Western exposure to **1967** — eleven years after the genre acquired
  its name (§9.2a) and three decades before the Yoshida Brothers.

**高橋竹山 Takahashi Chikuzan [V]** (from English Wikipedia, read 2026-11-13, which is
better-sourced than usual here)
- Born **18 June 1910**, Nakahiranai, Aomori; died **5 February 1998**, Hiranai, Aomori, aged 87.
- Real name **高橋定蔵 Takahashi Sadazō**.
- Lost his sight at about **age two, from measles** (contrast Nitabō's smallpox at 8).
- **His teacher was 戸田重次郎**, a tsugaru-jamisen performer near his hometown, with whom he was a
  live-in apprentice — **not Nitabō.** The frequent English claim that Chikuzan studied under
  Nitabō is wrong; he is two steps removed. (Give the name's reading with care: 重 takes both
  readings, English Wikipedia romanises it **Toda Jūjirō**, and the `tsugaru-shamisen` skill's
  sources give **Toda Shigejirō**. Both appear in print.) That skill also places his birth at
  **Kominato on Mutsu Bay**, not on the Tsugaru plain.
- Spent many years touring Tōhoku and Hokkaidō "playing before doorsteps."
- Post-war he became known first as **accompanist to the singer 成田雲竹 Narita Unchiku, who gave
  him the name "Chikuzan,"** and only later as a solo performer. The stage name is the singer's gift
  — the 竹 is from 雲竹.
- Performed for years at **渋谷ジャンジャン Shibuya Jean-Jean**, where his long solo improvisations
  were called **「岩木」 Iwaki**.
- His best-known disciple performs as **高橋竹山二代目 Takahashi Chikuzan II**, a woman.

### 9.3b Kobayashi Haru, and the designation that is routinely misreported

**小林ハル Kobayashi Haru** — the last of the Echigo *goze*, and the figure through whom most people
encounter the tradition. **[V]** from `ja.wikipedia.org/wiki/小林ハル` (revision 111678015), read
2026-11-13.

- Born **24 January 1900** (Meiji 33), **井栗村 Ikuri village, 南蒲原郡 Minami-Kanbara district,
  Niigata** — now **三条市 Sanjō City**. Died **25 April 2005** of 老衰, **aged 105**, in
  **黒川村 Kurokawa village, 北蒲原郡 Kita-Kanbara** — now **胎内市 Tainai City**, where she is
  buried.
- **Blind from about three months old**, following cataracts.
- Began goze training at **age 5, in 1905**, under **樋口フジ Higuchi Fuji**. First tour **late
  1908**, aged about 8. Changed teachers more than once — **初次サワ Hatsuji Sawa** in 1915, then
  **酒井ツル Sakai Tsuru** in 1921 — and later led tours herself.
- **Retired from performing 28 May 1973**, on entering a nursing home; the article says this ended
  the **Nagaoka lineage** of goze activity. **Resumed after 1977**, having moved to the
  **胎内やすらぎの家 Tainai Yasuragi no Ie** home, where she was recorded and broadcast and took new
  students.

**The designation, and the correction.** The history reference flags that she was **not** a Living National
Treasure in the legal sense, and that is right. The precise form:

> **瞽女唄** (goze-uta) was selected as a **記録作成等の措置を講ずべき無形文化財** — "an intangible
> cultural property requiring the taking of measures such as **record-making**" — and she was
> recognised as its **holder on 25 March 1978**. **[V]**

That is a **different legal instrument** from **重要無形文化財保持者**, the designation that makes
someone a Living National Treasure. Japanese Wikipedia states explicitly that she is **sometimes
called** a 人間国宝 *because of* this recognition, and that the label is **informal**, not an
official designation of the kind the national system grants. **[V]** So the popular claim is a
misattribution derived from a real but different honour.

**The category name is worth a sentence in its own right.** The state's instrument for goze-uta was
**record-making** — an acknowledgement that the tradition was ending, with documentation rather
than transmission as the policy response. That is a sharper and sadder point than "she was
honoured," and it is the designation's actual content.

Her other honours, dated **[V]**: **黄綬褒章** (Yellow Ribbon Medal), **29 April 1979**; honorary
citizen of Sanjō City, **6 September 2001**; **36th 吉川英治文化賞** (Yoshikawa Eiji Culture
Prize), **2002**.

### 9.3c The modern scene: tataki vs hiki, the competition circuit, and the tunings-to-pieces map

**[V]** from `ja.wikipedia.org/wiki/津軽三味線`, read 2026-11-13. (The article's critique
paragraph is tagged 要出典 in the article itself, so it is marked **[U]** below.)

**The correction that matters most: Chikuzan represents the minority style. [V]**
The article distinguishes **叩き *tataki*** — the percussive style that strikes the strings with
the bachi — from **弾き *hiki***, the plucking-based style. It states that **tataki "shaped the
tradition and is the lineage of most current players,"** while **hiki, which it associates
specifically with 高橋竹山 Takahashi Chikuzan, is "much rarer."**

The player best known in the West is therefore an exponent of the **minority** technique. Any
account that treats Chikuzan as the archetype of tsugaru-jamisen playing has the field backwards.
This also explains something otherwise puzzling: Chikuzan's reputation abroad rests on long
contemplative solo improvisations (the 「岩木」 *Iwaki*, §9.3), which is not what the competition
circuit rewards or what most players do.

**A terminological note. [V]** 曲弾き *kyokubiki* **does not appear in this article at all.** The
term comes from the biographical literature on **白川軍八郎** (§9.3), which credits him with
establishing it. So *kyokubiki* is a term *about* Shirakawa rather than one of the genre's own
organising categories — do not present it as the latter.

**Tunings mapped to actual pieces. [V]** This closes a gap `scales-notation-and-pedagogy.md` explicitly lists as unresolved:

| Tuning | Intervals as given | Pieces |
|---|---|---|
| **二上り** niagari | Do–So–Do | **津軽じょんから節**, **津軽よされ節** |
| **本調子** honchōshi | Do–Fa–Do | **津軽小原節** |
| **三下り** sansagari | Do–Fa–Ti♭ | **津軽三下がり** |

Note that two of the three **津軽三つ物** (§9.2c) sit in **niagari** and the third in honchōshi.
And two further practical facts: the **一の糸 is adjusted to match the singer's voice**, and
**absolute pitch is referenced to the shakuhachi or the shinobue** — the concrete answer to how a
fretless, non-fixed-pitch instrument gets pitched in practice.

**The competition circuit. [V]** There is **no single national championship**; there are at least
eight competing annual events, which is itself the finding. The article also names venues in Tokyo,
Osaka, Kobe, Kyushu and Kagawa beyond those tabulated.

| Competition | Organiser | Venue | Since |
|---|---|---|---|
| **津軽三味線世界大会** (World; formerly 全国大会, National) | 津軽三味線全国・世界大会実行委員会 | **Hirosaki, Aomori** | **1982** — the oldest |
| 津軽三味線全日本金木大会 | 津軽三味線会館 | **Kanagi, Goshogawara** | 1989 |
| 津軽三味線コンクール全国大会 | 公益財団法人日本民謡協会 | Asakusa, Tokyo | 1998 |
| 津軽三味線日本一決定戦 | exec. cttee + 津軽三味線全国協議会 (NPO) + Aomori City Board of Education + Aomori City Cultural and Sports Promotion Foundation | Aomori City | 2007 |
| 本場津軽民謡全国大会 | 津軽伝承工芸館 | Kuroishi, Aomori | 2012 |
| 津軽三味線・津軽民謡全国大会 in びわ湖 | NPO法人日本伝承芸能舞台芸術振興会 | Ōtsu, Shiga | 2013 |
| 〃 in 倉敷 / in 岡山 | same body | Kurashiki, Okayama | 2016 |
| 岡山県民謡全国大会 | same body | Kurashiki, Okayama | 2017 |

Plus a **津軽三味線甲子園** in Tokyo, tied to the manga **『ましろのおと』 *Mashiro no Oto*** — a
competition created in the slipstream of a comic, which is a fact about how the tradition now
reproduces itself.

**Kanagi is worth noticing:** the 1989 competition is sited in **Nitabō's and Shirakawa
Gunpachirō's birthplace** (§9.3), i.e. the circuit has physically installed itself on the origin
myth, and the 津軽三味線会館 (Tsugaru Shamisen Hall) that runs it is a municipal heritage
institution. That is Rausch's cultural-commodity thesis (§3) in concrete form.

**The critique, as the scene states it. [U] — the article tags all of this 要出典:**
judging criteria are **vague**; **repeat top finishers dominate**, so newcomers rarely place high;
and **each competition has its own judging style, which shifts over the years**. The article frames
competitions as **judged on merit, in contrast to the iemoto system** — that contrast is the
circuit's own justification and should be reported as such.

**Set this against §6.** The "vague criteria reward showmanship" charge is **unsourced folklore in
the article itself**, while the one controlled study (Chiba, Ozaki, Fujii & Savage 2023) found
**sound** dominating for shamisen where quality varied widely and found **no** visual-dominance
effect at the top of the field. The honest write-up reports the critique as the scene's own
self-criticism and the experiment as the only evidence, pointing the other way.

**Geography, which complicates the regional story. [V]** Most top players moved from **Tsugaru
*and Hakodate*** to **Tokyo**, so **Tokyo now has more depth than Aomori**. Hakodate (Hokkaidō) as
a second historical centre is routinely omitted in English accounts.

**The roster. [V]** Far wider than the two or three names that reach the West — useful both for a
listening list and for showing the field's actual size.
- *Established, Tokyo:* 二代目小山貢, 五錦竜二, 澤田勝秋, 高橋祐次郎, 福居典大, 福士豊秋
- *Established, Aomori:* 工藤まんじ, 長谷川裕二, 福士豊勝, 渋谷和生, 山上進, 多田あつし, 小山内薫.
  *Osaka:* 長谷川一義. *Niigata:* 木田林松次
- *Younger:* **上妻宏光 Agatsuma Hiromitsu**, 浅野祥, 木乃下真市, 高橋竹童, 山中信人, 踊正太郎,
  **吉田兄弟** (吉田良一郎 / 吉田健一), 柴田三兄妹, 藤井黎元, 大塚晴也
- *Women:* **二代目高橋竹山**, 工藤菊江, 市川竹女, 駒田早代, 福居典美, はなわちえ, 白藤ひかり,
  武田佳泉, 松原ひろ子, 山田里千美, 蜷川べに

**Two biographical anchors for the commercial era.** Both from English Wikipedia, read 2026-11-13;
**both articles carry citation-needed banners, so [U] on specifics.**

- **Yoshida Brothers:** 吉田良一郎 b. **26 July 1977**; 吉田健一 b. **16 December 1979**. Debuted
  **1999** with ***Ibuki***, **Domo Records**; first album **sold over 100,000 copies**. Teachers:
  **足立コカ Adachi Koka** from age five (min'yō-shamisen), then **佐々木孝 Sasaki Takashi** from
  about **1989** (tsugaru-jamisen). **"Kodo (Inside the Sun Remix)" used in Nintendo Wii
  commercials in North America from November 2006** — which is, for a great many Westerners, the
  actual first encounter with the instrument.
- **Agatsuma Hiromitsu:** b. **27 July 1973, Hitachi, Ibaraki** — **not from Aomori**, which
  matters for the regional-authenticity framing. Top prize at the All-Japan Tsugaru-jamisen
  Competition **1988, aged 14**; top honours at the Tsugaru-jamisen National Competition **1995 and
  1996**. Major-label debut **2001**, self-titled *Agatsuma* on Toshiba EMI, named **Traditional
  Japanese Music Album of the Year at the 16th Japan Gold Disc Awards**. *Beams (Agatsuma 2)* 2002,
  released in the US by **Domo Records, January 2003**, with a five-concert East Coast tour.
  *Classics (Agatsuma 3)* 2003, partly recorded live in a New York church. Collaborations with
  **Marcus Miller, Larry Coryell, Naná Vasconcelos**.

**One loop worth closing.** Nipponica attributes the spread of tsugaru-jamisen partly to **rōkyoku**
(§9.2b). **国本武春 Kunimoto Takeharu** was a **rōkyoku-trained** performer who took the shamisen
into **bluegrass**, and is the subject of Yamada's Brill chapter (§4, §5: pp. 372–385, DOI
`10.1163/9789004687172_024`). The genre's 20th-century expansion and its late-century
cross-over both run through rōkyoku, a century apart.

### 9.4 How to write the origin paragraph, given all of the above

The three accounts are reconcilable and the honest version names all three:

1. **Daijō Kazuo's account** (§3, obtainable in English as Daijō/Suda/Rausch 1998) makes **Nitabō**
   the founder, dating his acquisition and modification of a shamisen to **1877**.
2. **Groemer** (§3, 1999) argues that account may not be accurate, because the documentation is
   thin — and English Wikipedia reports the resulting dispute, together with the position that "the
   specific developers of tsugaru-jamisen are not known with certainty" and that "some consensus is
   that the style was developed by homeless and blind individuals called **bosama**."
3. **The Japanese reference literature** (§9.1) sidesteps the question: its entry on the genre
   begins in the 20th century, and its entry on Nitabō hedges the founder claim with 「とされる」.

So: *a plural, undocumented bosama milieu, out of which the tradition's own lineages trace
themselves to Nitabō, whose founder status the Japanese dictionaries themselves mark as
traditional attribution; the identifiable innovations are separable — the futozao striking
technique to Nitabō, kyokubiki to Shirakawa Gunpachirō — and the genre as a named, marketed
category dates from about 1956.*

## 10. Three supplements to the scale-theory section of `scales-notation-and-pedagogy.md`

The performance reference reconstructed Koizumi's theory from the Japan Arts Council's educational pages and flagged
two things as unverified. Two of them can be upgraded, and a third hazard should be added.

**(a) The *kakuon* attribution can be upgraded from [U] to [V].** The performance reference inferred that the frame
tones of each tetrachord are Koizumi's nuclear tones and marked that inference **[U] as an
attribution to Koizumi**. The inference is correct and there is a citation for it. English
Wikipedia's *In scale* article attributes to Koizumi precisely the view that scales are understood
through **"nuclear tones a fourth apart, with notes between them,"** and cites:

> **Koizumi Fumio. 『日本の音楽』 (*Nihon no ongaku*, "Japanese music"), p. 76. Tokyo: National
> Theatre of Japan, 1974.**

**[V]** as a citation present in that article (read 2026-11-13); **[U]** as to whether p. 76 says
exactly this, since the book was not read. Note this is a **different and later** Koizumi
publication from the one `scales-notation-and-pedagogy.md` names (『日本伝統音楽の研究』 vol. 1, Ongaku no Tomo Sha, 1958) —
the 1974 National Theatre volume is the compact statement and the likelier thing to obtain. The
same Wikipedia article also supplies the corroborating detail that under Koizumi's analysis the
**miyako-bushi scale** used in koto and shamisen music has pitches equivalent to the **in scale**,
example `1-♭2-4-5-♭6` on D — which matches `scales-notation-and-pedagogy.md`'s own worked transposition (D – E♭ – G – A – B♭)
exactly. Two independently derived statements agreeing is worth recording.

**(b) The scholarly authority for the whole tuning-and-scale section is Tokita 1996** (§2 above),
and it bears directly on `scales-notation-and-pedagogy.md`'s open questions. **Tokita, "Mode and Scale, Modulation and Tuning
in Japanese Shamisen Music: The Case of Kiyomoto Narrative," *Ethnomusicology* 40, no. 1 (1996): 1–,
DOI `10.2307/852434`.** Note the convergence: `scales-notation-and-pedagogy.md`'s best source for *why* the shamisen bends time
for the voice is a **Kiyomoto** example (*Michitose*) from the Bunka Digital Library, and Tokita's
article is a study of **Kiyomoto narrative** specifically. Her title also names the exact pair `scales-notation-and-pedagogy.md`
had to argue about from dictionaries — **"mode and scale"** — so she is very likely the Anglophone
source for the mode-vs-scale correction that `scales-notation-and-pedagogy.md` could only source to Heibonsha's *Mypedia*.
Obtain this before finalising the scale-theory section.

**(c) An additional hazard `scales-notation-and-pedagogy.md` does not cover: *hirajōshi* and friends are not Japanese scales.**
The names **hirajōshi, kumoijōshi and kokinjōshi** circulate in Western guitar and synth culture as
"Japanese scales." English Wikipedia's *Hirajoshi scale* article states that these "'scales' are
**Western derivations of the koto tunings of the same names**," citing **Speed (2008), p. 15**, and
documents that published transcriptions **flatly disagree with each other** about the pitches —
Burrows (1999, *How to Read Music*, p. 90) gives C–E–F♯–G–B; Slonimsky (1947, *Thesaurus of Scales
and Musical Patterns*, p. 160) gives C–D♭–F–G♭–B♭; Kostka & Payne (1995, *Tonal Harmony*, p. 484)
and Speed give C–D–E♭–G–A♭. All are hemitonic pentatonics and all are described as modes of the same
2–1–4–1–4 semitone pattern. **[V]** as a report of that article (read 2026-11-13).

Two consequences worth stating. First, *hirajōshi* is a **koto tuning**, not a shamisen scale, and
it belongs nowhere in a shamisen scale list. Second, the three mutually inconsistent Western
transcriptions are a cleaner illustration of `scales-notation-and-pedagogy.md`'s point than anything in the Japanese sources:
when the Western literature reifies a tuning into a "scale," it cannot even agree what the notes
are. That is the same error as the yō/in framework, committed one step further downstream.

**Method note for whoever revises this.** The pattern across this whole pass is that
**structured APIs are reachable where web pages are not**. Crossref, OpenLibrary and OSF all
answered immediately while publisher sites, search engines and even cites.org refused. When a
source seems unreachable, look for its API before concluding the fact is unverifiable — and
conversely, note that CITES has no open API, which is exactly why its annotations stayed unverified
here.
