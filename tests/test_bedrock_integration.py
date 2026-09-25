"""Tests for Bedrock configuration, invocation, and grounded analysis paths."""

import io
import json
import os
import unittest
from unittest.mock import Mock, patch

from tools.bedrock_analysis import ask_document
from tools.bedrock_client import (
    BedrockConfigurationError,
    BedrockInvocationError,
    invoke_bedrock,
)


class BedrockClientTests(unittest.TestCase):
    def test_requires_region_and_model_id(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(BedrockConfigurationError, "AWS_REGION"):
                invoke_bedrock("prompt", "document")

        with patch.dict(os.environ, {"AWS_REGION": "us-east-1"}, clear=True):
            with self.assertRaisesRegex(BedrockConfigurationError, "BEDROCK_MODEL_ID"):
                invoke_bedrock("prompt", "document")

    @patch("tools.bedrock_client.boto3.client")
    def test_invokes_anthropic_model_and_returns_text(self, mock_client_factory: Mock) -> None:
        client = Mock()
        client.invoke_model.return_value = {
            "body": io.BytesIO(json.dumps({"content": [{"text": "Clear explanation."}]}).encode())
        }
        mock_client_factory.return_value = client
        environment = {
            "AWS_REGION": "us-east-1",
            "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
        }

        with patch.dict(os.environ, environment, clear=True):
            result = invoke_bedrock("Use only this document.", "Payment is due Friday.")

        self.assertEqual(result, "Clear explanation.")
        request = json.loads(client.invoke_model.call_args.kwargs["body"])
        self.assertIn("Payment is due Friday.", request["messages"][0]["content"])
        self.assertEqual(mock_client_factory.call_args.kwargs["region_name"], "us-east-1")

    @patch("tools.bedrock_client.boto3.client")
    def test_rejects_malformed_model_response(self, mock_client_factory: Mock) -> None:
        mock_client_factory.return_value.invoke_model.return_value = {"body": io.BytesIO(b"{}")}
        environment = {"AWS_REGION": "us-east-1", "BEDROCK_MODEL_ID": "anthropic.test"}

        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(BedrockInvocationError, "without model text"):
                invoke_bedrock("prompt", "document")


class GroundedAnalysisTests(unittest.TestCase):
    @patch("tools.bedrock_analysis.invoke_bedrock", return_value="It is not stated in the document.")
    def test_ask_document_uses_grounded_prompt(self, mock_invoke: Mock) -> None:
        result = ask_document("Payment is due Friday.", "What is the late fee?")

        self.assertEqual(result["answer"], "It is not stated in the document.")
        self.assertEqual(result["source_text"], "Payment is due Friday.")
        self.assertIn("Use only information present", mock_invoke.call_args.args[0])
        self.assertIn("not stated", mock_invoke.call_args.args[0])

if __name__ == "__main__":
    unittest.main()
