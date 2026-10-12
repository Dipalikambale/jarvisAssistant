import logging
import os
import platform
import random
import shutil
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

_APP_COMMANDS = {
    "calculator": {"Windows": ["calc.exe"], "Darwin": ["open", "-a", "Calculator"]},
    "notepad": {"Windows": ["notepad.exe"], "Darwin": ["open", "-a", "TextEdit"]},
    "command prompt": {"Windows": ["cmd.exe"]},
}
_MUSIC_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}


def open_system_app(app_name: str) -> str:
    app_key = app_name.casefold().strip()
    commands = _APP_COMMANDS.get(app_key)
    if commands is None:
        raise ValueError(f"'{app_name}' is not an allowed application.")

    command = commands.get(platform.system())
    if command is None:
        raise RuntimeError(f"Opening {app_name} is not supported on this platform.")
    if platform.system() != "Windows" and shutil.which(command[0]) is None:
        raise RuntimeError(f"The {app_name} application is not installed.")

    try:
        subprocess.Popen(command)
    except OSError as error:
        logger.exception("Could not open system app", extra={"event": "app_open_error"})
        raise RuntimeError(f"I couldn't open {app_name}.") from error
    logger.info("Opened system app", extra={"event": "app_opened"})
    return f"Opening {app_name}."


def open_website(url: str, description: str) -> str:
    opened = webbrowser.open(url)
    if not opened:
        raise RuntimeError(f"I couldn't open {description} in a browser.")
    logger.info("Opened website", extra={"event": "website_opened"})
    return f"Opening {description}."


def search_google(query: str) -> str:
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    return open_website(url, "Google search")


def play_random_track(music_dir: Path | None) -> str:
    if music_dir is None or not music_dir.is_dir():
        raise ValueError("Set MUSIC_DIR in .env to a folder containing your music.")

    tracks = [
        path
        for path in music_dir.iterdir()
        if path.is_file() and path.suffix.casefold() in _MUSIC_EXTENSIONS
    ]
    if not tracks:
        raise ValueError(f"No supported audio files were found in {music_dir}.")

    track = random.choice(tracks)
    try:
        if os.name == "nt":
            os.startfile(track)  # type: ignore[attr-defined]
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(track)])
        else:
            subprocess.Popen(["xdg-open", str(track)])
    except OSError as error:
        logger.exception("Could not play music", extra={"event": "music_play_error"})
        raise RuntimeError("I couldn't open the selected music track.") from error
    logger.info("Started local music playback", extra={"event": "music_started"})
    return f"Playing {track.name}."
