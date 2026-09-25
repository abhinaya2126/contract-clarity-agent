"""Small, model-aware client for Amazon Bedrock Runtime."""

from __future__ import annotations

import json
import os
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv


class BedrockConfigurationError(RuntimeError):
    """Raised when the local Bedrock configuration is incomplete."""


class BedrockInvocationError(RuntimeError):
    """Raised when Bedrock cannot produce a usable model response."""


def invoke_bedrock(prompt: str, document_text: str) -> str:
    """Send a document-grounded prompt to the configured Bedrock model.

    The request and response adapters are kept here so callers do not need to
    know a model family's native ``InvokeModel`` schema.
    """
    load_dotenv()
    region = os.getenv("AWS_REGION", "").strip()
    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
    if not region:
        raise BedrockConfigurationError(
            "AWS_REGION is not set. Add it to your environment or .env file."
        )
    if not model_id:
        raise BedrockConfigurationError(
            "BEDROCK_MODEL_ID is not set. Add a Bedrock model ID to your environment or .env file."
        )

    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(_build_request(model_id, prompt, document_text)),
            contentType="application/json",
            accept="application/json",
        )
    except NoCredentialsError as error:
        raise BedrockConfigurationError(
            "AWS credentials were not found. Configure credentials that can invoke Bedrock."
        ) from error
    except (ClientError, BotoCoreError) as error:
        raise BedrockInvocationError(f"Bedrock invocation failed: {error}") from error

    return _parse_response(model_id, response)


def _build_request(model_id: str, prompt: str, document_text: str) -> dict[str, Any]:
    """Build the native InvokeModel body for supported Bedrock model families."""
    message = f"{prompt}\n\nDocument:\n{document_text}"
    if model_id.startswith("anthropic."):
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": message}],
        }
    if model_id.startswith("amazon.nova"):
        return {
            "messages": [{"role": "user", "content": [{"text": message}]}],
            "inferenceConfig": {"maxTokens": 1024},
        }
    if model_id.startswith("meta.llama") or model_id.startswith("mistral."):
        return {"prompt": message, "max_gen_len": 1024, "temperature": 0}
    raise BedrockConfigurationError(
        "Unsupported BEDROCK_MODEL_ID. Supported model families are anthropic., "
        "amazon.nova, meta.llama, and mistral."
    )


def _parse_response(model_id: str, response: dict[str, Any]) -> str:
    """Extract text from a native InvokeModel response."""
    try:
        body = response["body"].read()
        payload = json.loads(body)
    except (KeyError, AttributeError, TypeError, json.JSONDecodeError) as error:
        raise BedrockInvocationError("Bedrock returned a malformed response body.") from error

    text: Any = None
    if model_id.startswith("anthropic."):
        content = payload.get("content")
        if isinstance(content, list) and content and isinstance(content[0], dict):
            text = content[0].get("text")
    elif model_id.startswith("amazon.nova"):
        output = payload.get("output")
        if isinstance(output, dict):
            message = output.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, list) and content and isinstance(content[0], dict):
                    text = content[0].get("text")
    elif model_id.startswith("meta.llama"):
        text = payload.get("generation")
    elif model_id.startswith("mistral."):
        outputs = payload.get("outputs")
        if isinstance(outputs, list) and outputs and isinstance(outputs[0], dict):
            text = outputs[0].get("text")

    if not isinstance(text, str) or not text.strip():
        raise BedrockInvocationError("Bedrock returned a response without model text.")
    return text.strip()
