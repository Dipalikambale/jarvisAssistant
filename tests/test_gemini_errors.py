import unittest
from types import SimpleNamespace

from jarvis_assistant.gemini_client import _format_api_error


class GeminiErrorTests(unittest.TestCase):
    def test_authentication_error_gives_key_checks(self) -> None:
        error = SimpleNamespace(code=403, message="Permission denied")
        message = _format_api_error(error, "secret-key")
        self.assertIn("rejected the API key", message)
        self.assertNotIn("secret-key", message)

    def test_missing_model_gives_model_setting_hint(self) -> None:
        error = SimpleNamespace(
            code=404,
            message="models/invalid-model is not found for API version v1beta",
        )
        message = _format_api_error(error, "secret-key")
        self.assertIn("GEMINI_MODEL", message)
        self.assertIn("invalid-model", message)

    def test_not_found_detail_redacts_api_key(self) -> None:
        error = SimpleNamespace(code=404, message="Resource secret-key was not found")
        message = _format_api_error(error, "secret-key")
        self.assertIn("[REDACTED]", message)
        self.assertNotIn("secret-key", message)

    def test_quota_error_gives_quota_hint(self) -> None:
        error = SimpleNamespace(code="429", message="Quota exceeded")
        self.assertIn("quota", _format_api_error(error, "secret-key").casefold())

    def test_invalid_request_message_is_preserved_without_key(self) -> None:
        error = SimpleNamespace(code=400, message="Invalid API key secret-key")
        message = _format_api_error(error, "secret-key")
        self.assertIn("[REDACTED]", message)
        self.assertNotIn("secret-key", message)


if __name__ == "__main__":
    unittest.main()
