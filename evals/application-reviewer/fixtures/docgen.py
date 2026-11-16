#!/usr/bin/env python3
"""Minimal PDF and DOCX writers, standard library only.

The eval suite needs CVs that break in specific ways: a two-column layout, an
email that only exists in the page header, white-on-white keyword stuffing,
text positioned off the page, a scan with no text layer. Those cannot be
written by hand in a text editor and there is no PDF library in this repo's
dependency set, so this module emits the files directly.

It writes PDFs the hard way, as object graphs and content streams, which is
both why it is standard-library-only and why it is exactly reproducible: the
same call produces the same bytes on any machine. ``build.py`` uses it to
generate the fixtures, and the extract tests use it to generate throwaway ones.

It is not a general PDF library. It writes single-font text at absolute
coordinates and nothing else.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["Item", "Page", "write_pdf", "write_docx", "DocxPara", "DocxRun"]

PAGE_WIDTH = 612.0   # US Letter at 72 dpi, the default CV page size
PAGE_HEIGHT = 792.0

# pdftotext -bbox-layout reports coordinates with the origin at the top left,
# while PDF content streams put it at the bottom left. Everything in this
# module uses PDF coordinates; the extractor does the flipping.


@dataclass
class Item:
    """One run of text placed at an absolute position on a page."""

    text: str
    x: float
    y: float
    size: float = 11.0
    #: Fill colour as (r, g, b) in 0..1. (1, 1, 1) is the white-on-white trick.
    color: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class Page:
    items: list[Item] = field(default_factory=list)
    #: A filled grey box, which is how a page gets visible marks but no text,
    #: i.e. what a scanned CV looks like to a text extractor.
    filled_box: tuple[float, float, float, float] | None = None

    def add(self, text: str, x: float, y: float, size: float = 11.0,
            color: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> "Page":
        self.items.append(Item(text=text, x=x, y=y, size=size, color=color))
        return self

    def column(self, lines: list[str], x: float, top: float, size: float = 11.0,
               leading: float = 14.0) -> "Page":
        """Add a block of lines downward from ``top``.

        Writing one whole column and then the other is what makes the content
        stream order differ from the visual reading order, which is the signal
        the multi-column check looks for.
        """
        y = top
        for line in lines:
            self.add(line, x, y, size=size)
            y -= leading
        return self


def _pdf_escape(text: str) -> bytes:
    """Encode a string for a PDF literal, in WinAnsi so accents survive."""
    try:
        raw = text.encode("cp1252")
    except UnicodeEncodeError:
        raw = text.encode("cp1252", errors="replace")
    out = bytearray()
    for byte in raw:
        ch = bytes([byte])
        if ch in b"()\\":
            out += b"\\" + ch
        elif byte < 32 or byte > 126:
            out += f"\\{byte:03o}".encode("ascii")
        else:
            out += ch
    return bytes(out)


def _content_stream(page: Page) -> bytes:
    parts: list[bytes] = []
    if page.filled_box:
        x, y, w, h = page.filled_box
        parts.append(f"0.8 0.8 0.8 rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f".encode("ascii"))
    for item in page.items:
        r, g, b = item.color
        parts.append(
            b"BT /F1 " + f"{item.size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg "
            f"{item.x:.2f} {item.y:.2f} Td ".encode("ascii")
            + b"(" + _pdf_escape(item.text) + b") Tj ET"
        )
    return b"\n".join(parts) + b"\n"


def write_pdf(path: str | Path, pages: list[Page]) -> Path:
    """Write a PDF with one Helvetica font and absolutely positioned text."""
    path = Path(path)
    objects: list[bytes] = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    # Object numbers are allocated up front so the page tree can reference the
    # pages and the pages can reference their parent.
    catalog_num = 1
    pages_num = 2
    objects.append(b"")  # placeholder for the catalog
    objects.append(b"")  # placeholder for the page tree
    font_num = add(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding >>"
    )

    page_nums: list[int] = []
    for page in pages:
        stream = _content_stream(page)
        content_num = add(
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
            + stream + b"endstream"
        )
        page_nums.append(add(
            b"<< /Type /Page /Parent " + str(pages_num).encode("ascii") + b" 0 R "
            b"/MediaBox [0 0 " + f"{PAGE_WIDTH:.0f} {PAGE_HEIGHT:.0f}".encode("ascii") + b"] "
            b"/Resources << /Font << /F1 " + str(font_num).encode("ascii") + b" 0 R >> >> "
            b"/Contents " + str(content_num).encode("ascii") + b" 0 R >>"
        ))

    kids = b" ".join(f"{n} 0 R".encode("ascii") for n in page_nums)
    objects[pages_num - 1] = (
        b"<< /Type /Pages /Kids [" + kids + b"] /Count "
        + str(len(page_nums)).encode("ascii") + b" >>"
    )
    objects[catalog_num - 1] = (
        b"<< /Type /Catalog /Pages " + str(pages_num).encode("ascii") + b" 0 R >>"
    )

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("ascii") + body + b"\nendobj\n"

    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (
        b"trailer\n<< /Size " + str(len(objects) + 1).encode("ascii")
        + b" /Root " + str(catalog_num).encode("ascii") + b" 0 R >>\nstartxref\n"
        + str(xref_at).encode("ascii") + b"\n%%EOF\n"
    )

    path.write_bytes(bytes(out))
    return path


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------


@dataclass
class DocxRun:
    text: str
    #: Hex colour, e.g. "FFFFFF" for the white-text trick.
    color: str | None = None
    #: Font size in half-points, so 4 is 2pt: small enough to be invisible.
    half_points: int | None = None
    vanish: bool = False


@dataclass
class DocxPara:
    runs: list[DocxRun]
    #: When set, the paragraph is wrapped in a text box, which many CV parsers
    #: skip entirely.
    in_text_box: bool = False

    @classmethod
    def of(cls, text: str, **kw) -> "DocxPara":
        return cls(runs=[DocxRun(text=text, **kw)])


_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>
"""

_ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

_DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdHdr" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
  <Relationship Id="rIdFtr" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>
"""

_W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
_WPS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:v="urn:schemas-microsoft-com:vml"'
)


def _esc(text: str) -> str:
    return (
        str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def _run_xml(run: DocxRun) -> str:
    props = []
    if run.color:
        props.append(f'<w:color w:val="{run.color}"/>')
    if run.half_points is not None:
        props.append(f'<w:sz w:val="{run.half_points}"/><w:szCs w:val="{run.half_points}"/>')
    if run.vanish:
        props.append("<w:vanish/>")
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f'{rpr}<w:t xml:space="preserve">{_esc(run.text)}</w:t>'


def _para_xml(para: DocxPara) -> str:
    runs = "".join(f"<w:r>{_run_xml(r)}</w:r>" for r in para.runs)
    if para.in_text_box:
        # A real text box nests a whole body fragment inside the drawing.
        return (
            "<w:p><w:r><w:pict><v:shape><v:textbox><w:txbxContent>"
            f"<w:p>{runs}</w:p>"
            "</w:txbxContent></v:textbox></v:shape></w:pict></w:r></w:p>"
        )
    return f"<w:p>{runs}</w:p>"


def write_docx(
    path: str | Path,
    paragraphs: list[DocxPara],
    *,
    header: list[DocxPara] | None = None,
    footer: list[DocxPara] | None = None,
) -> Path:
    """Write a DOCX with optional header and footer parts."""
    path = Path(path)
    body = "".join(_para_xml(p) for p in paragraphs)
    sect = (
        '<w:sectPr><w:headerReference w:type="default" r:id="rIdHdr"/>'
        '<w:footerReference w:type="default" r:id="rIdFtr"/></w:sectPr>'
    ) if (header or footer) else "<w:sectPr/>"
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<w:document {_WPS} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<w:body>{body}{sect}</w:body></w:document>"
    )

    def part(tag: str, paras: list[DocxPara]) -> str:
        inner = "".join(_para_xml(p) for p in paras)
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f"<w:{tag} {_WPS}>{inner}</w:{tag}>"
        )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        # Fixed timestamps keep the archive byte-identical across runs.
        def put(name: str, text: str) -> None:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text)

        put("[Content_Types].xml", _CONTENT_TYPES)
        put("_rels/.rels", _ROOT_RELS)
        put("word/_rels/document.xml.rels", _DOC_RELS)
        put("word/document.xml", document)
        put("word/header1.xml", part("hdr", header or []))
        put("word/footer1.xml", part("ftr", footer or []))
    return path
