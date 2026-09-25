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

## Available MCP tool

`analyze_document(document_text, document_type="document")` uses deterministic
rules to identify early-cancellation, automatic-renewal, late-payment,
security-deposit, and termination clauses. It returns the document type, a
summary, and structured key items with source text and severity. It does not
use Amazon Bedrock or any other LLM.
