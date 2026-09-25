"""Document-grounded Bedrock analysis paths built on deterministic findings."""

from __future__ import annotations

from tools.bedrock_client import invoke_bedrock
from tools.document_analysis import analyze_document


ANALYSIS_PROMPT = """Explain this document concisely in plain English. Use only information
present in the supplied document. Do not invent terms, penalties, dates, fees, or
obligations. If an important detail is absent, say it is not stated. Preserve brief
source evidence from the document when possible."""


def analyze_document_with_bedrock(
    document_text: str, document_type: str = "document"
) -> dict[str, object]:
    """Combine stable rule-based findings with a grounded Bedrock explanation."""
    deterministic_findings = analyze_document(document_text, document_type)
    explanation = invoke_bedrock(ANALYSIS_PROMPT, document_text)
    return {
        "document_type": deterministic_findings["document_type"],
        "summary": deterministic_findings["summary"],
        "deterministic_findings": deterministic_findings,
        "llm_explanation": explanation,
    }


def ask_document(document_text: str, question: str) -> dict[str, str]:
    """Answer a question only from the supplied document text."""
    prompt = f"""Answer this question about the document: {question}

Use only information present in the supplied document. Do not invent terms,
penalties, dates, fees, or obligations. If the document does not contain enough
information to answer, explicitly say that it is not stated in the document.
Give a concise plain-English answer and preserve brief source evidence when possible."""
    return {"answer": invoke_bedrock(prompt, document_text), "source_text": document_text}
