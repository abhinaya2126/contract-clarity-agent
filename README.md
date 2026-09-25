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

3. Copy the environment template and set your Bedrock configuration:

   ```bash
   cp .env.example .env
   ```

   Set `AWS_REGION` and `BEDROCK_MODEL_ID` in `.env`. For example:

   ```dotenv
   AWS_REGION=us-east-1
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
   ```

   Real AWS credentials with permission to invoke the selected Bedrock model are
   required for the Bedrock-backed tools. Credentials are read through the normal
   AWS credential provider chain and must not be committed.

4. Run the MCP server with Streamable HTTP:

   ```bash
   python server.py
   ```

## Available MCP tools

`analyze_document(document_text, document_type="document")` uses deterministic
rules to identify early-cancellation, automatic-renewal, late-payment,
security-deposit, and termination clauses. It returns the document type, a
summary, and structured key items with source text and severity. It does not
use Amazon Bedrock or any other LLM.

`analyze_document_with_bedrock(document_text, document_type="document")` retains
the deterministic result and adds a concise, document-grounded Bedrock
explanation. Its `deterministic_findings` field has the same structure returned
by `analyze_document`; `llm_explanation` is useful for plain-English context.

`ask_document(document_text, question)` asks Bedrock a follow-up question using
only the supplied document. The prompt instructs the model to say when an answer
is not stated rather than inventing a detail. It returns the answer and the
source document text.

The deterministic tool is predictable rule-based clause detection. The Bedrock
tools add concise natural-language explanation, but require Bedrock model access
and AWS credentials.
