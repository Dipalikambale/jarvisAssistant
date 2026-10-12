import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    music_dir: Path | None = None

    @classmethod
    def from_environment(
        cls,
        streamlit_secrets: Mapping[str, object] | None = None,
    ) -> "Settings":
        from dotenv import load_dotenv

        project_root = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=project_root / ".env")
        api_key = _setting_value(
            "GOOGLE_API_KEY", streamlit_secrets
        ) or None
        model = _setting_value(
            "GEMINI_MODEL", streamlit_secrets, default="gemini-3.8-flash"
        )
        music_dir_value = _setting_value("MUSIC_DIR", streamlit_secrets)
        music_dir = Path(music_dir_value).expanduser() if music_dir_value else None
        return cls(
            api_key=api_key,
            gemini_model=model,
            music_dir=music_dir,
        )


def _setting_value(
    name: str,
    streamlit_secrets: Mapping[str, object] | None,
    default: str = "",
) -> str:
    if streamlit_secrets is not None and name in streamlit_secrets:
        value = streamlit_secrets[name]
        if not isinstance(value, str):
            raise ValueError(f"{name} must be configured as a string.")
        return value.strip() or default
    return os.getenv(name, default).strip() or default
