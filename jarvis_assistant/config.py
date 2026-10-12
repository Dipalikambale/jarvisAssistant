import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    music_dir: Path | None = None

    @classmethod
    def from_environment(cls) -> "Settings":
        from dotenv import load_dotenv

        project_root = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=project_root / ".env")
        api_key = os.getenv("GOOGLE_API_KEY", "").strip() or None
        model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
        music_dir_value = os.getenv("MUSIC_DIR", "").strip()
        music_dir = Path(music_dir_value).expanduser() if music_dir_value else None
        return cls(
            api_key=api_key,
            gemini_model=model or "gemini-3.8-flash",
            music_dir=music_dir,
        )
