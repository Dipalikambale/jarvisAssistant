import logging
import re
from collections.abc import Sequence
from datetime import datetime

from jarvis_assistant import actions, wikipedia_service
from jarvis_assistant.config import Settings
from jarvis_assistant.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

_GREETINGS = {
    "hello": "Hello! How can I help you?",
    "hi": "Hi! What can I do for you?",
    "hey": "Hey! How can I help?",
    "how are you": "I'm doing well, thanks for asking. How can I help?",
}
_WIKIPEDIA_PREFIXES = ("wikipedia search ", "search wikipedia for ", "wikipedia ")
_APP_NAMES = ("calculator", "notepad", "command prompt")


class Assistant:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._gemini = GeminiClient(settings) if settings.api_key else None

    def reply(
        self,
        prompt: str,
        history: Sequence[dict[str, str]] = (),
    ) -> str:
        text = prompt.strip()
        normalized = text.casefold().strip(" .!?")
        if not text:
            raise ValueError("Please enter a message.")
        if normalized in {"help", "what can you do"}:
            return (
                "I can tell you the date or time, look up Wikipedia articles, "
                "search Google, open Calculator or Notepad, open Google Calendar "
                "or YouTube, and play music from your configured music folder. "
                "For general questions, configure a Gemini API key."
            )
        if normalized in _GREETINGS:
            return _GREETINGS[normalized]
        if "time" in normalized and any(word in normalized for word in ("what", "current", "tell")):
            return f"The time is {datetime.now().astimezone().strftime('%I:%M %p')}."
        if "date" in normalized and any(word in normalized for word in ("what", "today", "current")):
            return f"Today is {datetime.now().astimezone().strftime('%A, %B %d, %Y')}."

        for app_name in _APP_NAMES:
            if re.search(rf"\b(open|launch|start)\s+(the\s+)?{re.escape(app_name)}\b", normalized):
                return actions.open_system_app(app_name)

        if "google calendar" in normalized:
            return actions.open_website(
                "https://calendar.google.com", "Google Calendar"
            )
        if "youtube" in normalized:
            return actions.open_website("https://www.youtube.com", "YouTube")
        if normalized.startswith(("search google for ", "google search ")):
            query = re.sub(r"^(search google for |google search )", "", text, flags=re.I)
            if query.strip():
                return actions.search_google(query.strip())
            raise ValueError("Tell me what you want to search for.")
        if normalized in {"play music", "play a song", "play music please"}:
            return actions.play_random_track(self._settings.music_dir)

        for prefix in _WIKIPEDIA_PREFIXES:
            if normalized.startswith(prefix):
                query = text[len(prefix):].strip()
                if not query:
                    raise ValueError("Tell me what to search for on Wikipedia.")
                return wikipedia_service.summarize(query)

        if self._gemini is None:
            raise RuntimeError(
                "I don't recognize that as a built-in command. Add GOOGLE_API_KEY "
                "to your .env file to enable Gemini conversations."
            )
        logger.info("Sending a request to Gemini", extra={"event": "gemini_request"})
        return self._gemini.reply(text, history=history)
