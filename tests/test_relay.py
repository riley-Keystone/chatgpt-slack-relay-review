import unittest

from scripts.send_to_slack import split_text
from scripts.validate_issue import validate


class RelayTests(unittest.TestCase):
    def test_short_text_is_unchanged(self):
        self.assertEqual(split_text("hello", 100), ["hello"])

    def test_long_text_is_split_without_loss(self):
        source = "alpha " * 100
        chunks = split_text(source, 100)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))
        self.assertEqual("".join(chunks).replace(" ", ""), source.replace(" ", ""))

    def test_approved_report_issue(self):
        validate({
            "number": 1,
            "title": "Chain & Wallet Compatibility Report | 2026-09-16",
            "body": "Report body",
            "state": "open",
        })

    def test_unapproved_issue_is_rejected(self):
        with self.assertRaises(ValueError):
            validate({"title": "Unrelated issue", "body": "spam", "state": "open"})


if __name__ == "__main__":
    unittest.main()
