"""Minimal Streamable HTTP MCP server entry point."""

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tools.bedrock_analysis import (
    analyze_document_with_bedrock as analyze_document_with_bedrock_content,
)
from tools.bedrock_analysis import ask_document as ask_document_content
from tools.document_analysis import analyze_document as analyze_document_content

load_dotenv()

mcp = FastMCP("Contract/Bill Clarity Agent")


@mcp.tool(
    name="analyze_document",
    description="Identify common contract and bill clauses using deterministic rules.",
)
def analyze_document(
    document_text: str, document_type: str = "document"
) -> dict[str, object]:
    """Analyze text for common document clauses without using an LLM."""
    return analyze_document_content(document_text, document_type)


@mcp.tool(
    name="analyze_document_with_bedrock",
    description="Combine deterministic clause detection with a Bedrock explanation.",
)
def analyze_document_with_bedrock(
    document_text: str, document_type: str = "document"
) -> dict[str, object]:
    """Analyze a document and explain it using a document-grounded Bedrock prompt."""
    return analyze_document_with_bedrock_content(document_text, document_type)


@mcp.tool(
    name="ask_document",
    description="Answer a question using only the text of the supplied document.",
)
def ask_document(document_text: str, question: str) -> dict[str, str]:
    """Ask a document-grounded Bedrock follow-up question."""
    return ask_document_content(document_text, question)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
