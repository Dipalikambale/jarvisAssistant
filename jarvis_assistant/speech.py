import logging
from io import BytesIO
from typing import BinaryIO

logger = logging.getLogger(__name__)


def transcribe_audio_file(audio_file: BinaryIO) -> str:
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError as error:
        raise ValueError("I couldn't understand that recording. Please try again.") from error
    except sr.RequestError as error:
        logger.exception("Speech recognition request failed", extra={"event": "speech_error"})
        raise RuntimeError(
            "Google Speech Recognition is unavailable. Check your internet connection."
        ) from error
    except (OSError, ValueError) as error:
        logger.exception("Could not read audio recording", extra={"event": "audio_error"})
        raise ValueError("I couldn't read that audio recording. Please try WAV audio.") from error


def listen_microphone(timeout: int = 5, phrase_time_limit: int = 12) -> str:
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )
        return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        raise
    except sr.UnknownValueError as error:
        raise ValueError("I couldn't understand that. Please try again.") from error
    except sr.RequestError as error:
        logger.exception("Speech recognition request failed", extra={"event": "speech_error"})
        raise RuntimeError(
            "Google Speech Recognition is unavailable. Check your internet connection."
        ) from error
    except (AssertionError, AttributeError, ImportError, OSError) as error:
        logger.exception("Microphone is unavailable", extra={"event": "microphone_error"})
        raise RuntimeError(
            "I couldn't access a microphone. CLI microphone input requires PyAudio; "
            "install it with 'pip install -r requirements-cli.txt' and check that "
            "a microphone is connected."
        ) from error


def speak_local(text: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def synthesize_speech(text: str) -> bytes:
    from gtts import gTTS
    from gtts.tts import gTTSError

    output = BytesIO()
    try:
        gTTS(text=text, lang="en").write_to_fp(output)
    except (gTTSError, OSError) as error:
        logger.exception("Text-to-speech request failed", extra={"event": "tts_error"})
        raise RuntimeError("Google Text-to-Speech could not create audio.") from error
    return output.getvalue()
