# 가나 퀴즈의 정답 판정과 오답 기록을 관리한다.
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .kana import KanaEntry, get_confusing_pairs, get_kana, get_reading_examples, get_sokuon_examples

ConfusingItem = tuple[str, str, str, str, str, str]
ExampleItem = tuple[str, str, str, str, str, str]
ParticleMeaningChoice = tuple[str, str]
ParticleItem = dict[str, object]
KANA_LEVEL_UNLOCK_ACCURACY = 80.0
KANA_GAME_LIVES = 3

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


@dataclass(frozen=True)
class KanaGameState:
    total: int
    lives: int = KANA_GAME_LIVES
    correct: int = 0
    answered: int = 0
    streak: int = 0
    best_streak: int = 0

    @property
    def won(self) -> bool:
        return self.total > 0 and self.answered >= self.total and self.lives > 0

    @property
    def lost(self) -> bool:
        return self.lives <= 0

    @property
    def finished(self) -> bool:
        return self.won or self.lost


@dataclass(frozen=True)
class StudySessionRecord:
    title: str
    mode: str
    correct: int
    questions: int
    created_at: str

    @property
    def accuracy(self) -> float:
        if self.questions <= 0:
            return 0.0
        return round(self.correct / self.questions * 100, 1)


@dataclass(frozen=True)
class StudyTitleSummary:
    sessions: int
    correct: int
    questions: int

    @property
    def accuracy(self) -> float:
        if self.questions <= 0:
            return 0.0
        return round(self.correct / self.questions * 100, 1)


@dataclass(frozen=True)
class StudyHistorySummary:
    total_sessions: int
    total_correct: int
    total_questions: int
    by_title: dict[str, StudyTitleSummary]
    recent: tuple[StudySessionRecord, ...]

    @property
    def accuracy(self) -> float:
        if self.total_questions <= 0:
            return 0.0
        return round(self.total_correct / self.total_questions * 100, 1)


def normalize_romaji(value: str) -> str:
    return value.strip().lower()


def kana_level_mode(script: str, level: int, *, mode: str = "romaji") -> str:
    return f"{mode}:{script.strip().lower()}:level{level}"


def is_correct_romaji(answer: str, expected: str) -> bool:
    normalized_answer = normalize_romaji(answer)
    normalized_expected = normalize_romaji(expected)
    accepted = ROMAJI_ALIASES.get(normalized_expected, {normalized_expected})
    return normalized_answer in accepted


def advance_kana_game_state(state: KanaGameState, *, is_correct: bool) -> KanaGameState:
    answered = state.answered + 1
    if is_correct:
        streak = state.streak + 1
        return KanaGameState(
            total=state.total,
            lives=state.lives,
            correct=state.correct + 1,
            answered=answered,
            streak=streak,
            best_streak=max(state.best_streak, streak),
        )
    return KanaGameState(
        total=state.total,
        lives=max(0, state.lives - 1),
        correct=state.correct,
        answered=answered,
        streak=0,
        best_streak=state.best_streak,
    )


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


def build_kana_question_items(
    entries: Iterable[KanaEntry],
    *,
    count: int,
    rng_seed: int | None = None,
) -> list[KanaEntry]:
    pool = list(entries)
    if count < 0:
        raise ValueError("question count must be zero or greater")
    if count <= len(pool):
        return random.Random(rng_seed).sample(pool, count)

    rng = random.Random(rng_seed)
    questions = pool[:]
    rng.shuffle(questions)
    questions.extend(rng.choice(pool) for _index in range(count - len(pool)))
    return questions


def build_romaji_question_items(
    entries: Iterable[KanaEntry],
    *,
    count: int,
    rng_seed: int | None = None,
) -> list[KanaEntry]:
    by_romaji: dict[str, KanaEntry] = {}
    for entry in entries:
        by_romaji.setdefault(entry[1], entry)
    return build_kana_question_items(by_romaji.values(), count=count, rng_seed=rng_seed)


def build_particle_meaning_choice(
    expected_meaning: str,
    particles: Iterable[dict[str, object]],
    *,
    rng_seed: int | None = None,
) -> list[ParticleMeaningChoice]:
    pool = [(str(item["particle"]), str(item["meaning"])) for item in particles]
    if len(pool) < 4:
        raise ValueError("at least four particles are required")

    answer_candidates = [entry for entry in pool if entry[1] == expected_meaning]
    if not answer_candidates:
        raise ValueError(f"unknown particle meaning: {expected_meaning}")

    rng = random.Random(rng_seed)
    answer = answer_candidates[0]
    distractors = [entry for entry in pool if entry != answer]
    choices = [answer, *rng.sample(distractors, 3)]
    rng.shuffle(choices)
    return choices


def build_particle_question_items(
    particles: Iterable[ParticleItem],
    *,
    count: int,
    rng_seed: int | None = None,
) -> list[ParticleItem]:
    pool = list(particles)
    if count < 0:
        raise ValueError("question count must be zero or greater")
    if count <= len(pool):
        return random.Random(rng_seed).sample(pool, count)

    rng = random.Random(rng_seed)
    questions = pool[:]
    rng.shuffle(questions)
    questions.extend(rng.choice(pool) for _index in range(count - len(pool)))
    return questions


def collect_example_items() -> tuple[ExampleItem, ...]:
    examples: list[ExampleItem] = []
    for script, script_label in (("hiragana", "히라가나"), ("katakana", "가타카나")):
        examples.extend(
            ("읽기", script_label, word, romaji, reading, meaning)
            for word, romaji, reading, meaning in get_reading_examples(script)
        )
        examples.extend(
            ("촉음", script_label, word, romaji, reading, meaning)
            for word, romaji, reading, meaning in get_sokuon_examples(script)
        )
    return tuple(examples)


def build_example_question_items(
    examples: Iterable[ExampleItem],
    *,
    count: int,
    rng_seed: int | None = None,
) -> list[ExampleItem]:
    pool = list(examples)
    if count < 0:
        raise ValueError("question count must be zero or greater")
    if count <= len(pool):
        return random.Random(rng_seed).sample(pool, count)

    rng = random.Random(rng_seed)
    questions = pool[:]
    rng.shuffle(questions)
    questions.extend(rng.choice(pool) for _index in range(count - len(pool)))
    return questions


def collect_confusing_items() -> tuple[ConfusingItem, ...]:
    items: list[ConfusingItem] = []
    for script, script_label in (("hiragana", "히라가나"), ("katakana", "가타카나")):
        romaji_by_symbol = dict(get_kana(script))
        for left, right, note in get_confusing_pairs(script):
            left_romaji = romaji_by_symbol[left]
            right_romaji = romaji_by_symbol[right]
            items.append((script_label, left, left_romaji, right, right_romaji, note))
            items.append((script_label, right, right_romaji, left, left_romaji, note))
    return tuple(items)


def build_confusing_question_items(
    items: Iterable[ConfusingItem],
    *,
    count: int,
    rng_seed: int | None = None,
) -> list[ConfusingItem]:
    pool = list(items)
    if count < 0:
        raise ValueError("question count must be zero or greater")
    if count <= len(pool):
        return random.Random(rng_seed).sample(pool, count)

    rng = random.Random(rng_seed)
    questions = pool[:]
    rng.shuffle(questions)
    questions.extend(rng.choice(pool) for _index in range(count - len(pool)))
    return questions


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


class StudyHistoryStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, dict):
            return []
        sessions = data.get("sessions", [])
        if not isinstance(sessions, list):
            return []
        return [item for item in sessions if isinstance(item, dict)]

    def record_session(
        self,
        title: str,
        mode: str,
        *,
        correct: int,
        total: int,
        created_at: str | None = None,
    ) -> None:
        sessions = self.load()
        sessions.append(
            {
                "title": title,
                "mode": mode,
                "correct": max(0, int(correct)),
                "questions": max(0, int(total)),
                "created_at": created_at or datetime.now().isoformat(timespec="seconds"),
            }
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump({"sessions": sessions}, file, ensure_ascii=False, indent=2)

    def summary(self, *, recent_limit: int = 5) -> StudyHistorySummary:
        records = tuple(self._record_from_item(item) for item in self.load())
        total_correct = sum(record.correct for record in records)
        total_questions = sum(record.questions for record in records)
        by_title_values: dict[str, StudyTitleSummary] = {}
        for record in records:
            current = by_title_values.get(record.title, StudyTitleSummary(sessions=0, correct=0, questions=0))
            by_title_values[record.title] = StudyTitleSummary(
                sessions=current.sessions + 1,
                correct=current.correct + record.correct,
                questions=current.questions + record.questions,
            )
        recent = tuple(reversed(records[-recent_limit:]))
        return StudyHistorySummary(
            total_sessions=len(records),
            total_correct=total_correct,
            total_questions=total_questions,
            by_title=by_title_values,
            recent=recent,
        )

    def summary_lines(self) -> tuple[str, ...]:
        summary = self.summary()
        if summary.total_sessions == 0:
            return ("아직 학습 기록이 없습니다.",)

        lines = [
            "학습 기록",
            f"전체 정답률: {summary.total_correct}/{summary.total_questions} ({summary.accuracy:.1f}%)",
            f"총 학습 세션: {summary.total_sessions}회",
            "",
            "모드별 정답률",
        ]
        for title, item in sorted(summary.by_title.items()):
            lines.append(f"- {title}: {item.correct}/{item.questions} ({item.accuracy:.1f}%), {item.sessions}회")

        lines.extend(["", "최근 기록"])
        for record in summary.recent:
            lines.append(f"- {record.created_at} {record.title}: {record.correct}/{record.questions} ({record.accuracy:.1f}%)")
        return tuple(lines)

    def unlocked_kana_level(self, script: str) -> int:
        normalized_script = script.strip().lower()
        unlocked = 1
        records = tuple(self._record_from_item(item) for item in self.load())
        for level in (1, 2):
            required_mode = kana_level_mode(normalized_script, level)
            if any(record.mode == required_mode and record.accuracy >= KANA_LEVEL_UNLOCK_ACCURACY for record in records):
                unlocked = level + 1
        return unlocked

    def _record_from_item(self, item: dict[str, object]) -> StudySessionRecord:
        return StudySessionRecord(
            title=str(item.get("title", "알 수 없는 학습")),
            mode=str(item.get("mode", "")),
            correct=self._safe_int(item.get("correct")),
            questions=self._safe_int(item.get("questions")),
            created_at=str(item.get("created_at", "")),
        )

    def _safe_int(self, value: object) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0
