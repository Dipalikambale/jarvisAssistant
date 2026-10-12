import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from google.genai.errors import APIError

from jarvis_assistant.gemini_client import (
    _format_api_error,
    _generate_with_503_retry,
)


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

    def test_503_error_explains_temporary_overload(self) -> None:
        error = SimpleNamespace(code=503, message="backend busy")
        message = _format_api_error(error, "secret-key")
        self.assertIn("temporarily overloaded", message)
        self.assertIn("try again", message)

    def test_503_retries_then_returns_success(self) -> None:
        generate = Mock(
            side_effect=[
                APIError(503, {"error": {"message": "busy"}}),
                SimpleNamespace(text="Recovered response"),
            ]
        )
        sleep = Mock()

        response = _generate_with_503_retry(
            generate,
            model="test-model",
            contents="hello",
            sleep=sleep,
        )

        self.assertEqual(response.text, "Recovered response")
        self.assertEqual(generate.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_non_503_api_error_is_not_retried(self) -> None:
        error = APIError(429, {"error": {"message": "quota"}})
        generate = Mock(side_effect=error)
        sleep = Mock()

        with self.assertRaises(APIError):
            _generate_with_503_retry(
                generate,
                model="test-model",
                contents="hello",
                sleep=sleep,
            )

        generate.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
