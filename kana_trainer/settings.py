# GUI 앱의 사용자 설정을 저장하고 불러온다.
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

MIN_FONT_SIZE = 12
MAX_FONT_SIZE = 72
DEFAULT_FONT_SIZE = 24


@dataclass(frozen=True)
class AppSettings:
    font_size: int = DEFAULT_FONT_SIZE


def default_settings_path() -> Path:
    return Path.home() / ".kana-trainer" / "settings.json"


def clamp_font_size(value: int) -> int:
    return max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, value))


class SettingsStore:
    def __init__(self, path: Path | None = None):
        self.path = path or default_settings_path()

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return AppSettings()
        if not isinstance(data, dict):
            return AppSettings()
        try:
            font_size = int(data.get("font_size", DEFAULT_FONT_SIZE))
        except (TypeError, ValueError):
            font_size = DEFAULT_FONT_SIZE
        return AppSettings(font_size=clamp_font_size(font_size))

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"font_size": clamp_font_size(settings.font_size)}
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
