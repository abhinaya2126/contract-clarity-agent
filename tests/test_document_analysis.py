"""Tests for deterministic document analysis."""

import unittest

from tools.document_analysis import analyze_document


class AnalyzeDocumentTests(unittest.TestCase):
    def test_detects_common_clauses(self) -> None:
        document = (
            "An early cancellation fee of $200 applies. "
            "This lease will automatically renew each year. "
            "A late payment fee applies after five days. "
            "The security deposit will be returned after inspection. "
            "Either party may terminate with 30 days' notice."
        )

        result = analyze_document(document, "lease")

        self.assertEqual(result["document_type"], "lease")
        self.assertEqual(len(result["key_items"]), 5)
        self.assertEqual(
            [item["category"] for item in result["key_items"]],
            [
                "early_cancellation",
                "auto_renewal",
                "late_payment",
                "security_deposit",
                "termination",
            ],
        )
        self.assertEqual(result["key_items"][0]["severity"], "high")
        self.assertIn("early cancellation", result["key_items"][0]["source_text"].lower())

    def test_detects_automatic_renewal_verb_forms(self) -> None:
        for document in (
            "This agreement automatically renews each year.",
            "This agreement renews automatically each year.",
        ):
            with self.subTest(document=document):
                result = analyze_document(document, "agreement")

                self.assertEqual(len(result["key_items"]), 1)
                self.assertEqual(result["key_items"][0]["category"], "auto_renewal")

    def test_returns_empty_result_for_empty_document(self) -> None:
        result = analyze_document("   ")

        self.assertEqual(result["document_type"], "document")
        self.assertEqual(result["summary"], "No document text was provided.")
        self.assertEqual(result["key_items"], [])

    def test_returns_empty_result_when_no_clause_is_recognized(self) -> None:
        result = analyze_document("The office is open Monday through Friday.", "notice")

        self.assertEqual(result["document_type"], "notice")
        self.assertEqual(result["summary"], "No recognized clauses were found in this notice.")
        self.assertEqual(result["key_items"], [])


if __name__ == "__main__":
    unittest.main()
