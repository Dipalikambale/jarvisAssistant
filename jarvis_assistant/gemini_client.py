import logging
from collections.abc import Sequence

from jarvis_assistant.config import Settings

logger = logging.getLogger(__name__)


def _format_api_error(error: Exception, api_key: str) -> str:
    status = getattr(error, "code", None) or getattr(error, "status", None)
    try:
        status = int(status)
    except (TypeError, ValueError):
        pass
    message = getattr(error, "message", None) or str(error)
    message = str(message).replace(api_key, "[REDACTED]").strip()
    if len(message) > 300:
        message = f"{message[:297]}..."

    if status in (401, 403):
        return (
            "Gemini rejected the API key or denied access. Check that the key is "
            "valid, the Generative Language API is enabled for its project, and "
            "the key has no restrictive API or referrer settings."
        )
    if status == 404:
        detail = f" Google reported: {message}" if message else ""
        return (
            "Google returned 404 Not Found. Check that GEMINI_MODEL is an available "
            f"model for this API key and API version.{detail}"
        )
    if status == 429:
        return (
            "Gemini quota or rate limit reached. Check the API project's quota "
            "and billing settings, then try again."
        )
    if status == 400:
        detail = f" Google reported: {message}" if message else ""
        return f"Gemini rejected the request as invalid.{detail}"
    if isinstance(status, int) and status >= 500:
        return f"Google Gemini is temporarily unavailable (HTTP {status}). Try again later."
    if message and message != str(error):
        return f"Gemini request failed: {message}"
    return "Gemini request failed. Check the API key, model, and network connection."


class GeminiClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise RuntimeError(
                "Gemini is not configured. Add GOOGLE_API_KEY to your .env file "
                "or use a built-in command."
            )

        from google import genai

        self._client = genai.Client(api_key=settings.api_key)
        self._api_key = settings.api_key
        self._model = settings.gemini_model

    def reply(
        self,
        prompt: str,
        history: Sequence[dict[str, str]] = (),
    ) -> str:
        conversation = [
            f"{'User' if item['role'] == 'user' else 'Assistant'}: {item['content']}"
            for item in history[-10:]
            if item.get("role") in {"user", "assistant"}
        ]
        conversation.append(f"User: {prompt}")
        contents = (
            "You are JARVIS, a helpful and concise voice assistant. "
            "Answer the latest user message clearly.\n\n"
            + "\n".join(conversation)
            + "\nAssistant:"
        )
        import httpx
        from google.genai.errors import APIError

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
            )
        except (APIError, httpx.HTTPError) as error:
            logger.error(
                "Gemini request failed (%s)",
                type(error).__name__,
                extra={"event": "gemini_error"},
            )
            if isinstance(error, APIError):
                message = _format_api_error(error, self._api_key)
            else:
                message = (
                    "Could not reach Google Gemini. Check your internet connection "
                    "and try again."
                )
            raise RuntimeError(message) from error

        text = response.text
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()
