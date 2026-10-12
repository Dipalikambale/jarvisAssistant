import logging

from jarvis_assistant.assistant import Assistant
from jarvis_assistant.config import Settings
from jarvis_assistant.logging_config import configure_logging
from jarvis_assistant.speech import listen_microphone, speak_local

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    assistant = Assistant(Settings.from_environment())
    print("JARVIS is ready. Say 'help' for commands or 'exit' to quit.")

    while True:
        try:
            prompt = listen_microphone()
        except ValueError as error:
            print(error)
            continue
        except RuntimeError as error:
            print(error)
            logger.error("Voice input failed", extra={"event": "voice_input_error"})
            return

        print(f"You: {prompt}")
        if prompt.strip().casefold() in {"exit", "quit", "stop"}:
            print("JARVIS: Goodbye!")
            return

        try:
            response = assistant.reply(prompt)
        except (RuntimeError, ValueError) as error:
            response = f"Sorry, I couldn't complete that request: {error}"
            logger.warning("Assistant request failed", extra={"event": "assistant_error"})

        print(f"JARVIS: {response}")
        try:
            speak_local(response)
        except (ImportError, OSError, RuntimeError):
            logger.exception("Local speech output failed", extra={"event": "speech_output_error"})
            print("JARVIS: (Text-to-speech is unavailable; see logs/application.log.)")
