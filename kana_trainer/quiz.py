# 가나 퀴즈의 정답 판정과 오답 기록을 관리한다.
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .kana import KanaEntry

ROMAJI_ALIASES: dict[str, set[str]] = {
    "shi": {"shi", "si"},
    "chi": {"chi", "ti"},
    "tsu": {"tsu", "tu"},
    "fu": {"fu", "hu"},
    "wo": {"wo", "o"},
}


@dataclass(frozen=True)
class Prompt:
    symbol: str
    romaji: str


def normalize_romaji(value: str) -> str:
    return value.strip().lower()


def is_correct_romaji(answer: str, expected: str) -> bool:
    normalized_answer = normalize_romaji(answer)
    normalized_expected = normalize_romaji(expected)
    accepted = ROMAJI_ALIASES.get(normalized_expected, {normalized_expected})
    return normalized_answer in accepted


def build_multiple_choice(
    expected_romaji: str,
    entries: Iterable[KanaEntry],
    *,
    rng_seed: int | None = None,
) -> list[KanaEntry]:
    pool = list(entries)
    if len(pool) < 4:
        raise ValueError("at least four kana entries are required")

    answer_candidates = [entry for entry in pool if entry[1] == expected_romaji]
    if not answer_candidates:
        raise ValueError(f"unknown romaji: {expected_romaji}")

    rng = random.Random(rng_seed)
    answer = answer_candidates[0]
    distractors = [entry for entry in pool if entry != answer]
    choices = [answer, *rng.sample(distractors, 3)]
    rng.shuffle(choices)
    return choices


def find_entry_by_romaji(expected_romaji: str, entries: Iterable[KanaEntry]) -> KanaEntry:
    for entry in entries:
        if entry[1] == expected_romaji:
            return entry
    raise ValueError(f"unknown romaji: {expected_romaji}")


def random_prompt(entries: Iterable[KanaEntry]) -> Prompt:
    symbol, romaji = random.choice(list(entries))
    return Prompt(symbol=symbol, romaji=romaji)


class WrongAnswerStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict[str, dict[str, object]]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            return {}
        return data

    def record(self, symbol: str, romaji: str, answer: str) -> None:
        data = self.load()
        current = data.get(symbol, {})
        count = int(current.get("count", 0)) + 1
        data[symbol] = {
            "romaji": romaji,
            "count": count,
            "last_answer": answer,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()

    def as_entries(self) -> tuple[KanaEntry, ...]:
        data = self.load()
        return tuple((symbol, str(item["romaji"])) for symbol, item in data.items())
