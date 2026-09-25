"""Deterministic document-clause analysis used by the MCP tool."""

from __future__ import annotations

import re


ClauseRule = tuple[str, str, str, str, re.Pattern[str]]

CLAUSE_RULES: tuple[ClauseRule, ...] = (
    (
        "early_cancellation",
        "Early cancellation",
        "This clause may require payment or impose other consequences for ending the agreement early.",
        "high",
        re.compile(r"\bearly\s+(?:cancellation|termination)\b", re.IGNORECASE),
    ),
    (
        "auto_renewal",
        "Automatic renewal",
        "This clause may renew the agreement unless you cancel before the stated deadline.",
        "medium",
        re.compile(
            r"\b(?:auto(?:matic(?:ally)?)?[-\s]?renewal|automatically\s+(?:renew|extend))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "late_payment",
        "Late payment",
        "This clause may add a fee, interest, or other consequence when payment is late.",
        "medium",
        re.compile(r"\b(?:late\s+(?:payment|fee)|overdue\s+payment)\b", re.IGNORECASE),
    ),
    (
        "security_deposit",
        "Security deposit",
        "This clause describes money held to cover damage, unpaid amounts, or other obligations.",
        "medium",
        re.compile(r"\bsecurity\s+deposit\b", re.IGNORECASE),
    ),
    (
        "termination",
        "Termination",
        "This clause describes how or when the agreement can end.",
        "high",
        re.compile(r"\b(?:termination|terminate|notice\s+to\s+terminate)\b", re.IGNORECASE),
    ),
)


def analyze_document(document_text: str, document_type: str = "document") -> dict[str, object]:
    """Return recognized clause information for a document's plain text."""
    normalized_type = document_type.strip() or "document"
    text = document_text.strip()

    if not text:
        return {
            "document_type": normalized_type,
            "summary": "No document text was provided.",
            "key_items": [],
        }

    source_segments = _split_source_segments(text)
    key_items = [_build_key_item(rule, source_segments) for rule in CLAUSE_RULES]
    recognized_items = [item for item in key_items if item is not None]

    if not recognized_items:
        summary = f"No recognized clauses were found in this {normalized_type}."
    else:
        summary = (
            f"Found {len(recognized_items)} recognized clause(s) in this {normalized_type}."
        )

    return {
        "document_type": normalized_type,
        "summary": summary,
        "key_items": recognized_items,
    }


def _split_source_segments(text: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", text) if segment.strip()]


def _build_key_item(
    rule: ClauseRule, source_segments: list[str]
) -> dict[str, str] | None:
    category, title, explanation, severity, pattern = rule
    source_text = next((segment for segment in source_segments if pattern.search(segment)), None)

    if source_text is None:
        return None

    return {
        "category": category,
        "title": title,
        "explanation": explanation,
        "severity": severity,
        "source_text": source_text,
    }
