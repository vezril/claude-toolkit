#!/usr/bin/env python3
"""S0: turn a CV file into text, and say how likely a parser is to misread it.

This is the deterministic first step of the pipeline. It produces ``parse.json``
(contract in contracts.py) with the extracted text plus a list of parse-health
signals, and the text it produces is the thing every later quote check is
tested against. If the text is wrong here, the whole run is wrong quietly, so
this module prefers to raise rather than guess.

What it checks, and why (design D4, and the parsing section of the research
report):

  * **Multi-column layouts.** ``pdftotext -raw`` gives content-stream order and
    ``-layout`` gives visual order. When those two disagree about the order of
    the words, something on the page is laid out in columns or a sidebar, which
    is the single most common way a CV's reading order comes out scrambled.
  * **Contact details in a page header or footer.** A real and documented
    failure: some parsers never read the margins, so the candidate's email
    disappears. Detected from word bounding boxes in PDFs and from the
    header/footer parts in DOCX.
  * **Hidden text.** White-on-white, near-white, Word's "vanish", and type too
    small to read. About 1% of real resumes carry hidden text. Finding it is
    cheap, and the honest thing to do is tell the user it is there.
  * **No text layer at all**, i.e. a scan or an exported image. That is the one
    case where "an ATS cannot read this" is simply true.
  * **Missing experience heading**, which leaves a parser with nothing to
    anchor the work history to.
  * **Injection text**: lines that address the reading system rather than a
    human. Reported, never obeyed.

Everything is standard library plus ``pdftotext`` from poppler, which is
already on the machine. Note the poppler version in parse.json's ``extractor``
field: layout output does vary between releases.

    extract.py cv.pdf --out out/parse.json --text-out out/cv.txt
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path
from typing import Iterable

import contracts
from edges import find_injection

__all__ = ["extract", "roll_up"]

PDFTOTEXT = "pdftotext"

#: Width of the top and bottom bands of a PDF page treated as header/footer,
#: in points. A CV's real first line sits below this; a running header does not.
MARGIN_BAND_PT = 50.0

#: A word box shorter than this is not meant to be read by a person.
TINY_TEXT_PT = 4.0

#: Word fill colour at or above this on all channels counts as white-on-white.
#: Not 1.0 exactly, because "FEFEFE" is the same trick with deniability.
WHITE_THRESHOLD = 0.93

#: DOCX font size in half-points below which text is unreadable. Design D4 said
#: 4 half-points (2pt); 8 (4pt) is used here because real keyword stuffing uses
#: 1-4pt and 2pt would miss most of it.
TINY_HALF_POINTS = 8

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")

#: Canonical section names and the heading words, English and French, that mean
#: each one. Without the French half every FR CV would look broken (D10).
_SECTION_WORDS: dict[str, tuple[str, ...]] = {
    "experience": (
        "experience", "experiences", "work experience", "professional experience",
        "employment", "employment history", "work history", "career",
        "experience professionnelle", "experiences professionnelles",
        "parcours professionnel", "emplois", "historique d emploi",
    ),
    "education": (
        "education", "academic background", "academic", "qualifications",
        "formation", "formations", "etudes", "scolarite", "diplomes",
    ),
    "skills": (
        "skills", "technical skills", "core skills", "competencies",
        "competences", "competences techniques", "aptitudes", "savoir faire",
    ),
    "certifications": (
        "certifications", "certification", "licences", "licenses",
        "accreditations", "attestations",
    ),
    "languages": ("languages", "langues",),
    "summary": (
        "summary", "profile", "professional summary", "objective", "about",
        "profil", "sommaire", "resume", "objectif",
    ),
    "projects": ("projects", "selected projects", "projets", "realisations",),
}

_FR_MARKERS = {
    "de", "des", "du", "en", "et", "le", "la", "les", "un", "une", "dans",
    "pour", "avec", "ans", "sur", "par", "au", "aux", "ce", "cette", "est",
    "plus", "chez", "ainsi", "afin", "depuis", "sous", "entre",
}

_EN_MARKERS = {
    "and", "the", "of", "in", "with", "for", "to", "on", "at", "as", "by",
    "from", "that", "this", "was", "were", "has", "have", "our", "their",
    "across", "while", "into", "through",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fold(text: str) -> str:
    s = unicodedata.normalize("NFKD", str(text))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def roll_up(codes: Iterable[str]) -> str:
    """Worst severity wins: a fatal signal makes the file unreadable.

    ``info`` signals never move the health, which is what keeps an injection
    finding from being reported as a formatting problem.
    """
    severities = {contracts.PARSE_SIGNALS[c][0] for c in codes if c in contracts.PARSE_SIGNALS}
    if "fatal" in severities:
        return "unreadable"
    if "risk" in severities:
        return "structural_risk"
    return "clean"


class _Signals:
    """Collects signals, keeping them unique and in a stable order."""

    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, code: str, *, detail: str | None = None, evidence: str | None = None) -> None:
        severity, default_detail = contracts.PARSE_SIGNALS[code]
        entry = {
            "code": code,
            "severity": severity,
            "detail": detail or default_detail,
            "evidence": evidence,
        }
        if entry not in self.items:
            self.items.append(entry)

    @property
    def codes(self) -> list[str]:
        return [s["code"] for s in self.items]


def _sections(text: str) -> dict[str, bool]:
    """Which standard sections have a recognisable heading."""
    found = {name: False for name in _SECTION_WORDS}
    for raw_line in text.splitlines():
        line = _fold(raw_line).strip()
        line = re.sub(r"^[#*\-=_\s]+", "", line)
        line = re.sub(r"[:#*\-=_\s]+$", "", line)
        line = re.sub(r"[^a-z0-9 ]+", " ", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line or len(line) > 60:
            continue
        for name, words in _SECTION_WORDS.items():
            if found[name]:
                continue
            for word in words:
                if line == word or line.startswith(word + " ") or line.endswith(" " + word):
                    found[name] = True
                    break
    return found


def _language(text: str) -> str:
    tokens = re.findall(r"[a-z']+", _fold(text))
    fr = sum(1 for t in tokens if t in _FR_MARKERS)
    en = sum(1 for t in tokens if t in _EN_MARKERS)
    if fr >= 2 and en >= 2:
        return "mixed"
    if fr > en:
        return "fr"
    if en > fr:
        return "en"
    return "unknown"


def _contact_strings(text: str) -> set[str]:
    return {m.group(0).strip() for m in _EMAIL.finditer(text)} | {
        m.group(0).strip() for m in _PHONE.finditer(text)
    }


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------


def _pdftotext(path: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            [PDFTOTEXT, *args, str(path), "-"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - environment problem
        raise RuntimeError(
            "pdftotext (poppler) is not on PATH, so PDFs cannot be read"
        ) from exc
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        if "Incorrect password" in stderr or "encrypted" in stderr.lower():
            raise _Encrypted(stderr)
        raise ValueError(f"pdftotext failed on {path.name}: {stderr[:200]}")
    return proc.stdout


class _Encrypted(Exception):
    pass


def _poppler_version() -> str:
    try:
        proc = subprocess.run([PDFTOTEXT, "-v"], capture_output=True, text=True, check=False)
    except FileNotFoundError:  # pragma: no cover
        return "unknown"
    text = (proc.stderr or "") + (proc.stdout or "")
    m = re.search(r"version\s+([0-9.]+)", text)
    return m.group(1) if m else "unknown"


def _pdf_words(path: Path) -> list[dict]:
    """Word boxes from ``-bbox-layout``, with top-left origin coordinates."""
    xml = _pdftotext(path, "-bbox-layout")
    words: list[dict] = []
    page_height = None
    # The output is XHTML with a namespace; a regex is steadier here than a
    # namespace-aware parse of a document poppler formats by hand.
    for page_match in re.finditer(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S):
        page_height = float(page_match.group(2))
        for m in re.finditer(
            r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
            page_match.group(3), re.S,
        ):
            words.append({
                "x_min": float(m.group(1)), "y_min": float(m.group(2)),
                "x_max": float(m.group(3)), "y_max": float(m.group(4)),
                "text": re.sub(r"<[^>]+>", "", m.group(5)).strip(),
                "page_height": page_height,
            })
    return words


def _pdf_white_text(path: Path) -> list[str]:
    """Strings drawn in white or near-white, read off the content streams.

    Design D4 left this open because ``pdftotext`` does not expose fill colour.
    It does not have to: the colour operators are in the content stream, and
    the stream can be pulled out of the file with ``zlib``. No PDF library and
    no new dependency.

    This is deliberately shallow. It walks the colour and text-showing
    operators in order and does not track ``q``/``Q`` graphics-state nesting,
    so a saved-and-restored colour can be attributed to the wrong run. It is a
    risk signal for the user to look at, not a verdict.
    """
    data = path.read_bytes()
    hits: list[str] = []

    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        blob = m.group(1)
        for candidate in (blob, None):
            if candidate is None:
                try:
                    blob = zlib.decompress(m.group(1))
                except zlib.error:
                    continue
            try:
                stream = blob.decode("latin-1")
            except UnicodeDecodeError:  # pragma: no cover
                continue
            hits.extend(_white_runs(stream))
            break

    return hits


_OPS = re.compile(
    r"(?P<rgb>[\d.]+\s+[\d.]+\s+[\d.]+\s+rg)"
    r"|(?P<gray>[\d.]+\s+g(?![a-zA-Z]))"
    r"|(?P<cmyk>[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+k(?![a-zA-Z]))"
    r"|(?P<show>\((?:[^()\\]|\\.)*\)\s*(?:Tj|TJ|'))"
)


def _white_runs(stream: str) -> list[str]:
    white = False
    out: list[str] = []
    for m in _OPS.finditer(stream):
        if m.group("rgb"):
            r, g, b = (float(v) for v in m.group("rgb").split()[:3])
            white = min(r, g, b) >= WHITE_THRESHOLD
        elif m.group("gray"):
            white = float(m.group("gray").split()[0]) >= WHITE_THRESHOLD
        elif m.group("cmyk"):
            c, mm, y, k = (float(v) for v in m.group("cmyk").split()[:4])
            white = max(c, mm, y, k) <= (1 - WHITE_THRESHOLD)
        elif m.group("show") and white:
            text = re.sub(r"\s*(?:Tj|TJ|')$", "", m.group("show")).strip()
            text = text[1:-1] if text.startswith("(") else text
            text = re.sub(r"\\([()\\])", r"\1", text)
            text = re.sub(r"\\(\d{1,3})", lambda mo: chr(int(mo.group(1), 8)), text)
            if text.strip():
                out.append(text.strip())
    return out


def _extract_pdf(path: Path, signals: _Signals) -> str:
    try:
        layout = _pdftotext(path, "-layout")
        raw = _pdftotext(path, "-raw")
    except _Encrypted as exc:
        signals.add("encrypted", evidence=str(exc)[:200])
        return ""

    if not layout.strip() and not raw.strip():
        signals.add("no_text_layer")
        return ""

    raw_words = raw.split()
    layout_words = layout.split()
    if raw_words and layout_words:
        ratio = difflib.SequenceMatcher(None, raw_words, layout_words).ratio()
        if ratio < 0.90:
            signals.add(
                "multi_column_layout",
                detail=(
                    "Content-stream order and visual order disagree "
                    f"(similarity {ratio:.2f}), which suggests columns or a sidebar."
                ),
            )

    words = _pdf_words(path)

    tiny = [w for w in words if (w["y_max"] - w["y_min"]) < TINY_TEXT_PT and w["text"]]
    if tiny:
        signals.add(
            "hidden_tiny_text",
            detail=f"{len(tiny)} word(s) are rendered under {TINY_TEXT_PT:g}pt tall.",
            evidence=" ".join(w["text"] for w in tiny[:12])[:200],
        )

    body_text = "\n".join(w["text"] for w in words if not _in_margin(w))
    for w in words:
        if not _in_margin(w):
            continue
        band = "contact_in_header" if _in_header(w) else "contact_in_footer"
        contacts = _contact_strings(w["text"])
        if contacts and not any(c in body_text for c in contacts):
            signals.add(band, evidence=w["text"][:120])

    white = _pdf_white_text(path)
    if white:
        signals.add(
            "hidden_white_text",
            detail=(
                "Text is drawn in white or near-white. If the page has a dark "
                "background behind it this is a design choice; otherwise it is hidden."
            ),
            evidence=" ".join(white)[:200],
        )

    # -layout is the text the user would read, so it is the text we quote
    # against. Whatever white text exists is part of that output.
    return layout


def _in_header(word: dict) -> bool:
    return word["y_min"] < MARGIN_BAND_PT


def _in_footer(word: dict) -> bool:
    height = word.get("page_height") or 792.0
    return word["y_max"] > height - MARGIN_BAND_PT


def _in_margin(word: dict) -> bool:
    return _in_header(word) or _in_footer(word)


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------


def _docx_part_text(root: ET.Element, signals: _Signals | None = None) -> str:
    """Paragraph text, with runs inside a paragraph joined without a gap.

    Splitting a word across runs is normal in Word output, so joining runs with
    a space would break every verbatim quote that happens to land on one.
    """
    lines: list[str] = []
    for para in root.iter(f"{W_NS}p"):
        pieces: list[str] = []
        for node in para.iter():
            if node.tag == f"{W_NS}t":
                pieces.append(node.text or "")
            elif node.tag == f"{W_NS}tab":
                pieces.append("\t")
            elif node.tag == f"{W_NS}br":
                pieces.append("\n")
        line = "".join(pieces).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def _docx_hidden(root: ET.Element) -> tuple[list[str], list[str]]:
    """Runs that are white/vanished, and runs that are too small to read."""
    white: list[str] = []
    tiny: list[str] = []
    for run in root.iter(f"{W_NS}r"):
        text = "".join(t.text or "" for t in run.iter(f"{W_NS}t")).strip()
        if not text:
            continue
        props = run.find(f"{W_NS}rPr")
        if props is None:
            continue
        colour = props.find(f"{W_NS}color")
        if colour is not None:
            val = (colour.get(f"{W_NS}val") or "").strip().lstrip("#")
            if re.fullmatch(r"[0-9A-Fa-f]{6}", val):
                channels = [int(val[i:i + 2], 16) / 255 for i in (0, 2, 4)]
                if min(channels) >= WHITE_THRESHOLD:
                    white.append(text)
        if props.find(f"{W_NS}vanish") is not None:
            white.append(text)
        size = props.find(f"{W_NS}sz")
        if size is not None:
            try:
                if int(size.get(f"{W_NS}val") or "0") < TINY_HALF_POINTS:
                    tiny.append(text)
            except ValueError:
                pass
    return white, tiny


def _extract_docx(path: Path, signals: _Signals) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            if "word/document.xml" not in names:
                raise ValueError(f"{path.name} is not a Word document (no word/document.xml)")
            doc = ET.fromstring(z.read("word/document.xml"))
            headers = [ET.fromstring(z.read(n)) for n in sorted(names)
                       if re.fullmatch(r"word/header\d*\.xml", n)]
            footers = [ET.fromstring(z.read(n)) for n in sorted(names)
                       if re.fullmatch(r"word/footer\d*\.xml", n)]
    except zipfile.BadZipFile as exc:
        raise ValueError(f"{path.name} is not a readable DOCX: {exc}") from exc
    except ET.ParseError as exc:
        raise ValueError(f"{path.name} has unreadable XML: {exc}") from exc

    body = _docx_part_text(doc)
    header_text = "\n".join(_docx_part_text(h) for h in headers).strip()
    footer_text = "\n".join(_docx_part_text(f) for f in footers).strip()

    for part_text, code in ((header_text, "contact_in_header"), (footer_text, "contact_in_footer")):
        contacts = _contact_strings(part_text)
        if contacts and not any(c in body for c in contacts):
            signals.add(code, evidence=part_text[:120])

    white: list[str] = []
    tiny: list[str] = []
    for root in [doc, *headers, *footers]:
        w, t = _docx_hidden(root)
        white += w
        tiny += t
    if white:
        signals.add("hidden_white_text",
                    detail="Runs are set in white, near-white, or marked hidden.",
                    evidence=" ".join(white)[:200])
    if tiny:
        signals.add("hidden_tiny_text",
                    detail=f"Runs are set under {TINY_HALF_POINTS / 2:g}pt.",
                    evidence=" ".join(tiny)[:200])

    if doc.iter(f"{W_NS}txbxContent") and any(True for _ in doc.iter(f"{W_NS}txbxContent")):
        signals.add("text_box")
    if any(True for _ in doc.iter(f"{W_NS}tbl")):
        signals.add("table_layout")

    # Visual order: a running header reads before the body, a footer after it.
    return "\n".join(part for part in (header_text, body, footer_text) if part)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_SUPPORTED = {".pdf": "pdf", ".docx": "docx", ".md": "md", ".markdown": "md",
              ".txt": "txt", ".text": "txt"}


def extract(path: str | Path) -> dict:
    """Extract ``path`` into the ``parse`` contract."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path}: no such file")
    fmt = _SUPPORTED.get(path.suffix.lower())
    if fmt is None:
        raise ValueError(
            f"{path.name}: unsupported format. Give a PDF, DOCX, Markdown or text file."
        )

    signals = _Signals()
    extractor = {"tool": "python-stdlib", "version": sys.version.split()[0]}

    if fmt == "pdf":
        text = _extract_pdf(path, signals)
        extractor = {"tool": "pdftotext", "version": _poppler_version()}
    elif fmt == "docx":
        text = _extract_docx(path, signals)
        extractor = {"tool": "zipfile+ElementTree", "version": sys.version.split()[0]}
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        signals.add("no_layout_tested")

    if not text.strip():
        signals.add("no_text_layer")

    sections = _sections(text)
    if text.strip() and not sections["experience"]:
        signals.add("no_experience_heading")

    injections = find_injection(text)
    if injections:
        signals.add(
            "injection_text",
            detail=(
                "Text in this file addresses the reading system rather than a "
                "person. It is reported and ignored."
            ),
            evidence="; ".join(injections)[:200],
        )

    return {
        "source_file": str(path),
        "format": fmt,
        "text": text,
        "parse_health": roll_up(signals.codes),
        "signals": signals.items,
        "sections": sections,
        "language": _language(text) if text.strip() else "unknown",
        "extractor": extractor,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="extract.py",
        description="Extract a CV to text and report parse-health signals.",
    )
    parser.add_argument("path", help="the CV file: PDF, DOCX, Markdown or text")
    parser.add_argument("--out", required=True, help="where to write parse.json")
    parser.add_argument("--text-out", help="also write the extracted text here")
    args = parser.parse_args(argv)

    try:
        parse = extract(args.path)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"extract failed: {exc}", file=sys.stderr)
        return 2

    problems = contracts.validate("parse", parse)
    if problems:  # pragma: no cover - a bug in this script, not in the input
        print("extract produced invalid parse.json: " + "; ".join(problems), file=sys.stderr)
        return 3

    Path(args.out).write_text(json.dumps(parse, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.text_out:
        Path(args.text_out).write_text(parse["text"], encoding="utf-8")

    print(f"parse: {parse['parse_health']} ({len(parse['signals'])} signal(s), {parse['language']})")
    for s in parse["signals"]:
        print(f"  - [{s['severity']}] {s['code']}: {s['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
