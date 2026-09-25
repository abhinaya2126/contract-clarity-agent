# Contract/Bill Clarity Agent

A minimal, self-hosted MCP server foundation for the Contract/Bill Clarity Agent.

## Development setup

1. Create and activate a Python 3.11+ virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Optionally copy the environment template and adjust non-secret settings:

   ```bash
   cp .env.example .env
   ```

4. Run the MCP server with Streamable HTTP:

   ```bash
   python server.py
   ```

The initial server intentionally has no document-analysis tools yet.
