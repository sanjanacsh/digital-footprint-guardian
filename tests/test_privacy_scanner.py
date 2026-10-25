import unittest
from privacy_scanner import scan_text, redact_text

class PrivacyScannerTests(unittest.TestCase):
    def test_email_is_detected(self):
        result = scan_text("Reach me at learner@example.com")
        self.assertTrue(any(item["type"] == "Email address" for item in result["findings"]))
        self.assertGreater(result["score"], 0)

    def test_password_like_assignment_is_detected(self):
        result = scan_text("password = demoSecret123")
        self.assertTrue(any(item["type"] == "Password-like assignment" for item in result["findings"]))

    def test_redaction_hides_email(self):
        result = redact_text("Email: learner@example.com")
        self.assertNotIn("learner@example.com", result)
        self.assertIn("[REDACTED: Email address]", result)

    def test_empty_text_has_zero_score(self):
        result = scan_text("")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["findings"], [])

if __name__ == "__main__":
    unittest.main()
