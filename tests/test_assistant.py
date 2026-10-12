import unittest
from unittest.mock import patch

from jarvis_assistant.assistant import Assistant
from jarvis_assistant.config import Settings


class AssistantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assistant = Assistant(Settings())

    def test_empty_message_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "enter a message"):
            self.assistant.reply("  ")

    def test_greeting_is_available_without_gemini(self) -> None:
        self.assertEqual(
            self.assistant.reply("Hello!"),
            "Hello! How can I help you?",
        )

    def test_time_command_is_available_without_gemini(self) -> None:
        self.assertRegex(self.assistant.reply("What time is it?"), r"^The time is ")

    @patch("jarvis_assistant.assistant.actions.open_system_app")
    def test_app_command_uses_allowlisted_action(self, open_app: unittest.mock.Mock) -> None:
        open_app.return_value = "Opening calculator."
        self.assertEqual(self.assistant.reply("Open calculator"), "Opening calculator.")
        open_app.assert_called_once_with("calculator")

    def test_unrecognized_request_explains_gemini_setup(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_API_KEY"):
            self.assistant.reply("Explain black holes")

    @patch("jarvis_assistant.assistant.wikipedia_service.summarize")
    def test_wikipedia_command_passes_search_query(
        self, summarize: unittest.mock.Mock
    ) -> None:
        summarize.return_value = "A short article summary."
        self.assertEqual(
            self.assistant.reply("Wikipedia search Ada Lovelace"),
            "A short article summary.",
        )
        summarize.assert_called_once_with("Ada Lovelace")


if __name__ == "__main__":
    unittest.main()
