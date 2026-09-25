"""Minimal Streamable HTTP MCP server entry point."""

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("Contract/Bill Clarity Agent")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
