import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc)
            .isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        event = getattr(record, "event", None)
        if event is not None:
            entry["event"] = event
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=True)


def configure_logging(log_dir: Path | None = None) -> None:
    destination = log_dir or Path("logs")
    destination.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    if any(getattr(handler, "_jarvis_handler", False) for handler in root_logger.handlers):
        return

    handler = RotatingFileHandler(
        destination / "application.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(JsonFormatter())
    handler._jarvis_handler = True  # type: ignore[attr-defined]
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
