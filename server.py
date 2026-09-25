"""Minimal Streamable HTTP MCP server entry point."""

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
