#!/usr/bin/env python3
"""The five step contracts, in one place.

This module is the single source of truth for the JSON shapes that pass between
the pipeline's steps. Two things read it:

  * ``edges.py``, which validates each step's output before the next step sees
    it, and
  * ``gen_contracts_doc.py``, which renders
    ``skills/ats-screening/references/contracts.md`` from these definitions.

Keeping the checker and the documentation on one source is the same trick
``brief.py`` plays in delivery-flow: the doc the model reads and the script that
judges the model's output cannot drift apart, because there is only one of them.
If you change a field here, regenerate the doc in the same commit (there is a
test that fails if you forget).

Standard library only.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["CONTRACTS", "STEP_ORDER", "validate", "ValidationError", "enum_of"]

# ---------------------------------------------------------------------------
# Shared vocabularies. These are referenced from several contracts, so they get
# names: a status spelled two different ways in two files is a bug waiting.
# ---------------------------------------------------------------------------

REQUIREMENT_TYPES = [
    "skill", "years", "degree", "cert", "licence", "location", "work_auth",
    "clearance", "language", "title", "other",
]

#: Types the research says employers actually configure as knockout questions.
#: Promoting one of these to a knockout is evidence-backed for the first five
#: and an inference for clearance and language (see design D3).
KNOCKOUT_TYPES = ["work_auth", "location", "years", "degree", "cert", "licence", "clearance", "language"]

STRENGTHS = ["required", "preferred", "unspecified"]

#: What S2 may emit. `ambiguous` is NOT in this list on purpose: only the quote
#: edge creates it, by downgrading a `met` whose quote cannot be found.
MODEL_STATUSES = ["met", "partial", "unmet", "unknown_ask"]

#: What verdict.py may see, i.e. the model's vocabulary plus the edge's.
POST_EDGE_STATUSES = MODEL_STATUSES + ["ambiguous"]

LANGUAGES = ["en", "fr", "mixed", "unknown"]

RECOMMENDATION_KINDS = ["reframe", "ask", "format", "gap"]

PARSE_HEALTH = ["clean", "structural_risk", "unreadable"]

KNOCKOUT_EXPOSURE = ["clear", "at_risk", "unknown_ask"]

AI_TIERS = ["all_required_evidenced", "some_gaps", "major_gaps"]

#: Parse signals extract.py can raise. `severity` is fixed per code so that the
#: roll-up in verdict.py never has to guess how bad a signal is.
PARSE_SIGNALS = {
    "multi_column_layout": ("risk", "Raw and layout extraction disagree on line order, which suggests columns or a sidebar."),
    "contact_in_header": ("risk", "An email or phone number appears only in the page header."),
    "contact_in_footer": ("risk", "An email or phone number appears only in the page footer."),
    "hidden_white_text": ("risk", "Text is set in white or near-white on white."),
    "hidden_tiny_text": ("risk", "Text is rendered below a legible size."),
    "hidden_offpage_text": ("risk", "Text is positioned outside the page box."),
    "text_box": ("risk", "Content sits in a text box or frame, which many parsers skip."),
    "table_layout": ("risk", "Content sits in a table, which can be read in an unexpected order."),
    "no_experience_heading": ("risk", "No recognisable experience or work-history heading was found."),
    "no_text_layer": ("fatal", "The file has no extractable text layer, so it is an image."),
    "no_layout_tested": ("info", "A plain-text source has no layout to test, so layout risks are unknown."),
    "injection_text": ("info", "Text in the file addresses the reading system rather than a human."),
    "encrypted": ("fatal", "The file is encrypted and cannot be read."),
}

SIGNAL_SEVERITIES = ["info", "risk", "fatal"]

RANK_SIGNAL_CODES = [
    "preferred_unmet", "preferred_met", "title_below_posting", "title_above_posting",
    "acronym_only", "full_form_only", "years_near_miss", "skill_listed_not_evidenced",
    "equivalents_allowed", "language_mismatch",
]

REFUSAL_CODES = [
    "hidden_text_request", "fabrication_request", "protected_trait_inference",
    "discrimination_framing", "name_change_request", "multiple_cvs",
    "third_party_cv", "recruiter_framing", "url_fetch_request",
]

FLAG_CODES = ["discriminatory_requirement", "injection_text", "unverifiable_claim"]

_MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"
_ID_PATTERN = r"^[A-Z][0-9]+$"

# ---------------------------------------------------------------------------
# The contracts themselves.
# ---------------------------------------------------------------------------


def _f(type_: str, *, required: bool = True, **kw: Any) -> dict:
    return {"type": type_, "required": required, **kw}


_SIGNAL = {
    "type": "object",
    "fields": {
        "code": _f("string", enum=list(PARSE_SIGNALS), doc="Which signal fired."),
        "severity": _f("string", enum=SIGNAL_SEVERITIES, doc="Fixed per code by PARSE_SIGNALS; never chosen freely."),
        "detail": _f("string", doc="One sentence a human can act on."),
        "evidence": _f("string", required=False, nullable=True, doc="The offending text or coordinates, when there is one."),
    },
}

_FLAG = {
    "type": "object",
    "fields": {
        "code": _f("string", enum=FLAG_CODES, doc="What kind of flag this is."),
        "detail": _f("string", doc="Why it was raised."),
        "source_quote": _f("string", nullable=True, doc="Verbatim text it was raised from, or null."),
    },
}

CONTRACTS: dict[str, dict] = {
    "parse": {
        "file": "parse.json",
        "step": "S0",
        "written_by": "extract.py (deterministic)",
        "purpose": (
            "The CV as text, plus everything we could learn about whether a parser "
            "would read it the way a human does."
        ),
        "root": {
            "type": "object",
            "fields": {
                "source_file": _f("string", doc="Path as given, for the report's provenance line."),
                "format": _f("string", enum=["pdf", "docx", "md", "txt"], doc="Detected from the extension and the file's magic bytes."),
                "text": _f("string", doc="The extracted text. Every later quote check is a substring test against this."),
                "parse_health": _f("string", enum=PARSE_HEALTH, doc="Worst-case roll-up of the signals: any fatal gives unreadable, any risk gives structural_risk."),
                "signals": _f("array", items=_SIGNAL, doc="Zero or more parse signals."),
                "sections": _f("object", free_form=True, doc="Heading name to bool, for the standard sections in EN and FR."),
                "language": _f("string", enum=LANGUAGES, doc="Detected language of the CV text."),
                "extractor": _f("object", free_form=True, doc="Tool and version, because pdftotext layout output varies by poppler release."),
            },
        },
    },
    "requirements": {
        "file": "requirements.json",
        "step": "S1",
        "written_by": "the model",
        "purpose": "The posting decomposed into typed, individually checkable requirements.",
        "root": {
            "type": "object",
            "fields": {
                "posting_language": _f("string", enum=LANGUAGES),
                "requirements": _f("array", min_items=1, items={
                    "type": "object",
                    "fields": {
                        "id": _f("string", pattern=_ID_PATTERN, doc="R1, R2, … Stable within a run; everything downstream refers to these."),
                        "text": _f("string", doc="The requirement in your own words, one per record. Never bundle two."),
                        "type": _f("string", enum=REQUIREMENT_TYPES),
                        "strength": _f("string", enum=STRENGTHS, doc="required / preferred / unspecified, as the posting words it."),
                        "threshold": _f("object", nullable=True, free_form=True, doc='{"years": 5} for a years requirement, else null.'),
                        "knockout_likely": _f("boolean", doc="True when an employer would plausibly ask this as a screening question."),
                        "equivalents_allowed": _f("boolean", doc='True when the posting says "or equivalent experience" or similar.'),
                        "source_quote": _f("string", doc="Verbatim from the posting. Checked as a substring, so do not tidy it."),
                    },
                }),
                "flags": _f("array", items=_FLAG, doc="Discriminatory-looking requirements and injection text found in the posting."),
            },
        },
    },
    "evidence": {
        "file": "evidence.json",
        "step": "S2",
        "written_by": "the model, then amended by the quote edge",
        "purpose": "For each requirement, what the CV actually says about it, quoted.",
        "root": {
            "type": "object",
            "fields": {
                "cv_language": _f("string", enum=LANGUAGES),
                "positions": _f("array", items={
                    "type": "object",
                    "fields": {
                        "id": _f("string", pattern=_ID_PATTERN, doc="P1, P2, …"),
                        "title": _f("string"),
                        "employer": _f("string", nullable=True),
                        "start": _f("string", doc="As written on the CV. years.py parses it; do not normalise."),
                        "end": _f("string", doc="As written, including Present / en cours."),
                        "source_quote": _f("string", doc="Verbatim line the dates came from."),
                    },
                }),
                "findings": _f("array", min_items=1, items={
                    "type": "object",
                    "fields": {
                        "requirement_id": _f("string", pattern=_ID_PATTERN),
                        "status": _f("string", enum=MODEL_STATUSES, doc="ambiguous is not yours to write: the quote edge assigns it."),
                        "evidence_quote": _f("string", nullable=True, doc="Verbatim from the CV text, required for met and partial, null otherwise."),
                        "position_ids": _f("array", items={"type": "string", "pattern": _ID_PATTERN}, doc="Which positions evidence it. years.py unions their ranges."),
                        "note": _f("string", required=False, nullable=True, doc="One clause of reasoning, optional."),
                    },
                }),
                "flags": _f("array", items=_FLAG),
            },
        },
    },
    "verdict": {
        "file": "verdict.json",
        "step": "S3",
        "written_by": "verdict.py (deterministic)",
        "purpose": "The four-part verdict, its reasons, and the years arithmetic.",
        "root": {
            "type": "object",
            "fields": {
                "knockout_exposure": _f("string", enum=KNOCKOUT_EXPOSURE),
                "likely_ai_tier": _f("string", enum=AI_TIERS),
                "parse_health": _f("string", enum=PARSE_HEALTH),
                "rank_signals": _f("array", items={
                    "type": "object",
                    "fields": {
                        "code": _f("string", enum=RANK_SIGNAL_CODES),
                        "requirement_id": _f("string", pattern=_ID_PATTERN, nullable=True),
                        "detail": _f("string"),
                    },
                }),
                "reasons": _f("array", items={
                    "type": "object",
                    "fields": {
                        "component": _f("string", enum=["knockout_exposure", "likely_ai_tier", "parse_health"]),
                        "requirement_id": _f("string", pattern=_ID_PATTERN, nullable=True),
                        "why": _f("string"),
                    },
                }),
                "years": _f("object", free_form=True, doc="Merged ranges, total months, and the per-requirement sums."),
                "downgrades": _f("array", items={
                    "type": "object",
                    "fields": {
                        "requirement_id": _f("string", pattern=_ID_PATTERN),
                        "from": _f("string", enum=POST_EDGE_STATUSES),
                        "to": _f("string", enum=POST_EDGE_STATUSES),
                        "why": _f("string"),
                    },
                }, doc="Every status the edges changed, so the report can show its work."),
            },
        },
    },
    "recommendations": {
        "file": "recommendations.json",
        "step": "S4",
        "written_by": "the model",
        "purpose": "What the candidate can honestly do about the verdict.",
        "root": {
            "type": "object",
            "fields": {
                "recommendations": _f("array", items={
                    "type": "object",
                    "fields": {
                        "id": _f("string", pattern=_ID_PATTERN, doc="C1, C2, …"),
                        "kind": _f("string", enum=RECOMMENDATION_KINDS),
                        "requirement_id": _f("string", pattern=_ID_PATTERN, nullable=True, doc="Required for every kind except format."),
                        "text": _f("string", doc="What to do, addressed to the candidate."),
                        "evidence_quote": _f("string", nullable=True, doc="Required for reframe: the CV text the reframing rests on."),
                        "condition": _f("string", nullable=True, doc="Required for ask: the 'if you have X' the question is conditioned on."),
                    },
                }),
                "refusals": _f("array", items={
                    "type": "object",
                    "fields": {
                        "code": _f("string", enum=REFUSAL_CODES),
                        "detail": _f("string", doc="One line, to the user, saying what was declined and why."),
                    },
                }),
            },
        },
    },
}

STEP_ORDER = ["parse", "requirements", "evidence", "verdict", "recommendations"]


def enum_of(contract: str, *path: str) -> list[str]:
    """Look up an enum by contract and field path, for code that needs the vocabulary."""
    node: Any = CONTRACTS[contract]["root"]
    for key in path:
        node = node["fields"][key] if "fields" in node else node["items"]["fields"][key]
        if node.get("type") == "array" and key != path[-1]:
            node = node["items"]
    return list(node["enum"])


class ValidationError(Exception):
    """Raised with every problem found, not just the first."""

    def __init__(self, contract: str, problems: list[str]):
        self.contract = contract
        self.problems = problems
        super().__init__(f"{contract} failed its contract: " + "; ".join(problems))


def _check(value: Any, spec: dict, path: str, problems: list[str]) -> None:
    expected = spec["type"]

    if value is None:
        if not spec.get("nullable"):
            problems.append(f"{path}: null is not allowed")
        return

    if expected == "object":
        if not isinstance(value, dict):
            problems.append(f"{path}: expected an object, got {type(value).__name__}")
            return
        if spec.get("free_form"):
            return
        fields: dict[str, dict] = spec.get("fields", {})
        for name, fspec in fields.items():
            child = f"{path}.{name}" if path else name
            if name not in value:
                if fspec.get("required", True):
                    problems.append(f"{child}: missing")
                continue
            _check(value[name], fspec, child, problems)
        for name in value:
            if name not in fields:
                problems.append(f"{path}.{name}: unexpected field")
        return

    if expected == "array":
        if not isinstance(value, list):
            problems.append(f"{path}: expected an array, got {type(value).__name__}")
            return
        if len(value) < spec.get("min_items", 0):
            problems.append(f"{path}: needs at least {spec['min_items']} item(s), got {len(value)}")
        item_spec = spec.get("items")
        if item_spec:
            for i, item in enumerate(value):
                _check(item, item_spec, f"{path}[{i}]", problems)
        return

    primitives = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
    }
    want = primitives[expected]
    # bool is an int in Python, which would let `true` pass as an integer.
    if expected in ("integer", "number") and isinstance(value, bool):
        problems.append(f"{path}: expected {expected}, got boolean")
        return
    if not isinstance(value, want):
        problems.append(f"{path}: expected {expected}, got {type(value).__name__}")
        return

    if "enum" in spec and value not in spec["enum"]:
        problems.append(f"{path}: {value!r} is not one of {spec['enum']}")
    if "pattern" in spec and not re.fullmatch(spec["pattern"], value):
        problems.append(f"{path}: {value!r} does not match {spec['pattern']}")
    if expected == "string" and not spec.get("nullable") and not str(value).strip():
        problems.append(f"{path}: must not be blank")


def validate(contract: str, data: Any) -> list[str]:
    """Return a list of problems, empty when ``data`` satisfies ``contract``.

    Every problem is reported, not just the first, so one run of the edge tells
    the model everything it has to fix.
    """
    if contract not in CONTRACTS:
        raise KeyError(f"unknown contract {contract!r}")
    problems: list[str] = []
    _check(data, CONTRACTS[contract]["root"], "", problems)
    return problems
