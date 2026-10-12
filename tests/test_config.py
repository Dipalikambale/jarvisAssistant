import os
import unittest
from unittest.mock import patch

from jarvis_assistant.config import Settings


class SettingsTests(unittest.TestCase):
    def test_streamlit_secrets_override_environment(self) -> None:
        secrets = {
            "GOOGLE_API_KEY": "cloud-key",
            "GEMINI_MODEL": "cloud-model",
            "MUSIC_DIR": "cloud-music",
        }
        with patch.dict(
            os.environ,
            {
                "GOOGLE_API_KEY": "local-key",
                "GEMINI_MODEL": "local-model",
                "MUSIC_DIR": "local-music",
            },
        ):
            settings = Settings.from_environment(streamlit_secrets=secrets)

        self.assertEqual(settings.api_key, "cloud-key")
        self.assertEqual(settings.gemini_model, "cloud-model")
        self.assertEqual(str(settings.music_dir), "cloud-music")

    def test_missing_model_uses_default(self) -> None:
        settings = Settings.from_environment(streamlit_secrets={})
        self.assertEqual(settings.gemini_model, "gemini-3.8-flash")

    def test_non_string_secret_is_reported(self) -> None:
        with self.assertRaisesRegex(ValueError, "GOOGLE_API_KEY"):
            Settings.from_environment(streamlit_secrets={"GOOGLE_API_KEY": 123})


if __name__ == "__main__":
    unittest.main()
