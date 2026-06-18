# 터미널풍 GUI로 가나 학습 세션을 실행한다.
from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import font, scrolledtext, ttk
from typing import Callable

from .cli import DEFAULT_QUESTION_COUNT, default_store_path
from .kana import (
    KanaEntry,
    get_beginner_patterns,
    get_confusing_pairs,
    get_kana,
    get_particles,
    get_reading_examples,
    get_sokuon_examples,
    pair_by_romaji,
)
from .quiz import (
    WrongAnswerStore,
    build_multiple_choice,
    find_entry_by_romaji,
    is_correct_romaji,
    random_prompt,
)
from .settings import AppSettings, SettingsStore, clamp_font_size

InputHandler = Callable[[str], None]
DISPLAY_FONT_CANDIDATES = ("Yu Gothic UI", "Meiryo", "Yu Gothic", "MS Gothic")


def choose_display_font(available_fonts: tuple[str, ...]) -> str:
    available = set(available_fonts)
    for family in DISPLAY_FONT_CANDIDATES:
        if family in available:
            return family
    return DISPLAY_FONT_CANDIDATES[-1]


@dataclass
class QuizSession:
    title: str
    mode: str
    entries: tuple[KanaEntry, ...]
    count: int = DEFAULT_QUESTION_COUNT
    index: int = 0
    correct: int = 0
    streak: int = 0
    best_streak: int = 0
    expected_symbol: str = ""
    expected_romaji: str = ""
    choices: list[KanaEntry] | None = None


class KanaTrainerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.store = WrongAnswerStore(default_store_path())
        self.handler: InputHandler = self.handle_menu_input
        self.session: QuizSession | None = None

        self.root.title("Kana Trainer")
        self.root.geometry("920x680")
        self.root.minsize(680, 460)
        self.root.configure(bg="#111111")

        display_font = choose_display_font(font.families(root))
        self.text_font = font.Font(family=display_font, size=self.settings.font_size)
        self.ui_font = font.Font(family="Segoe UI", size=10)
        self._build_layout()
        self._bind_events()
        self.show_main_menu()

    def _build_layout(self) -> None:
        style = ttk.Style()
        style.configure("Kana.TButton", font=self.ui_font, padding=(10, 5))

        header = tk.Frame(self.root, bg="#1b1b1b")
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="かな Trainer",
            bg="#1b1b1b",
            fg="#f2f2f2",
            font=("Segoe UI", 15, "bold"),
            padx=14,
            pady=10,
        )
        title.pack(side=tk.LEFT)

        for label, delta in (("A-", -2), ("A+", 2)):
            button = ttk.Button(
                header,
                text=label,
                style="Kana.TButton",
                command=lambda amount=delta: self.change_font_size(amount),
            )
            button.pack(side=tk.RIGHT, padx=(0, 8), pady=8)

        self.output = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg="#0c0c0c",
            fg="#e8e8e8",
            insertbackground="#e8e8e8",
            selectbackground="#345d7e",
            relief=tk.FLAT,
            borderwidth=0,
            padx=18,
            pady=18,
            font=self.text_font,
            state=tk.DISABLED,
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        self.output.tag_configure("muted", foreground="#9ca3af")
        self.output.tag_configure("good", foreground="#7ddc9b")
        self.output.tag_configure("bad", foreground="#ff8a8a")
        self.output.tag_configure("prompt", foreground="#f7d774")

        input_row = tk.Frame(self.root, bg="#1b1b1b")
        input_row.pack(fill=tk.X)

        prompt = tk.Label(input_row, text=">", bg="#1b1b1b", fg="#f7d774", font=self.text_font, padx=12)
        prompt.pack(side=tk.LEFT)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            input_row,
            textvariable=self.entry_var,
            bg="#101010",
            fg="#f2f2f2",
            insertbackground="#f2f2f2",
            relief=tk.FLAT,
            font=self.text_font,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, pady=10)

        submit = ttk.Button(input_row, text="Enter", style="Kana.TButton", command=self.submit_input)
        submit.pack(side=tk.RIGHT, padx=10)

        self.status_var = tk.StringVar(value="Enter 제출 | Esc 메뉴 | Ctrl+휠 글자 크기")
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            bg="#111111",
            fg="#9ca3af",
            font=self.ui_font,
            padx=12,
            pady=6,
        )
        status.pack(fill=tk.X)

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda _event: self.submit_input())
        self.root.bind("<Escape>", lambda _event: self.show_main_menu())
        self.root.bind("<Control-MouseWheel>", self.handle_ctrl_wheel)
        self.root.after(100, self.entry.focus_set)

    def handle_ctrl_wheel(self, event: tk.Event) -> None:
        delta = 2 if event.delta > 0 else -2
        self.change_font_size(delta)

    def change_font_size(self, delta: int) -> None:
        next_size = clamp_font_size(self.settings.font_size + delta)
        self.settings = AppSettings(font_size=next_size)
        self.settings_store.save(self.settings)
        self.text_font.configure(size=next_size)
        self.status_var.set(f"폰트 크기 {next_size} | Enter 제출 | Esc 메뉴 | Ctrl+휠 글자 크기")

    def clear_output(self) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)

    def write(self, text: str = "", tag: str | None = None) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def submit_input(self) -> None:
        value = self.entry_var.get().strip()
        self.entry_var.set("")
        if value:
            self.write(f"> {value}", "prompt")
        self.handler(value)

    def show_main_menu(self) -> None:
        self.session = None
        self.handler = self.handle_menu_input
        self.clear_output()
        self.write("かな Trainer")
        self.write("")
        self.write("1. 히라가나 보고 로마자 입력")
        self.write("2. 가타카나 보고 로마자 입력")
        self.write("3. 로마자 보고 히라가나 선택")
        self.write("4. 히라가나-가타카나 매칭")
        self.write("5. 오답 복습")
        self.write("6. 오답 기록 보기")
        self.write("7. 일본어.md 참고 자료 보기")
        self.write("0. 종료")
        self.write("")
        self.write("메뉴 번호를 입력하세요.", "muted")
        self.status_var.set("메뉴 | Enter 제출 | Esc 메뉴 | Ctrl+휠 글자 크기")

    def handle_menu_input(self, value: str) -> None:
        if value == "1":
            self.start_romaji_quiz("히라가나 연습", get_kana("hiragana"))
        elif value == "2":
            self.start_romaji_quiz("가타카나 연습", get_kana("katakana"))
        elif value == "3":
            self.start_choice_quiz("히라가나 4지선다", get_kana("hiragana"))
        elif value == "4":
            self.start_matching_quiz()
        elif value == "5":
            self.start_wrong_answer_review()
        elif value == "6":
            self.show_wrong_answer_summary()
        elif value == "7":
            self.show_reference_menu()
        elif value == "0":
            self.root.destroy()
        else:
            self.write("메뉴 번호를 다시 입력하세요.", "bad")

    def start_romaji_quiz(self, title: str, entries: tuple[KanaEntry, ...]) -> None:
        self.session = QuizSession(title=title, mode="romaji", entries=entries)
        self.handler = self.handle_romaji_answer
        self.clear_output()
        self.write(title)
        self.next_romaji_question()

    def next_romaji_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        prompt = random_prompt(session.entries)
        session.expected_symbol = prompt.symbol
        session.expected_romaji = prompt.romaji
        self.write("")
        self.write(f"문제 {session.index}/{session.count}")
        self.write(f"{prompt.symbol} 의 읽는 법은?")

    def handle_romaji_answer(self, value: str) -> None:
        session = self.require_session()
        if is_correct_romaji(value, session.expected_romaji):
            session.correct += 1
            session.streak += 1
            session.best_streak = max(session.best_streak, session.streak)
            self.write("정답.", "good")
            self.write(f"연속 정답: {session.streak}", "muted")
        else:
            session.streak = 0
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write(f"오답. 정답은 {session.expected_romaji}.", "bad")
        self.next_romaji_question()

    def start_choice_quiz(self, title: str, entries: tuple[KanaEntry, ...]) -> None:
        self.session = QuizSession(title=title, mode="choice", entries=entries)
        self.handler = self.handle_choice_answer
        self.clear_output()
        self.write(title)
        self.next_choice_question()

    def next_choice_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        _symbol, romaji = random.choice(session.entries)
        expected_symbol, _expected_romaji = find_entry_by_romaji(romaji, session.entries)
        session.expected_symbol = expected_symbol
        session.expected_romaji = romaji
        session.choices = build_multiple_choice(romaji, session.entries)
        self.write("")
        self.write(f"문제 {session.index}/{session.count}: {romaji} 에 해당하는 문자는?")
        for index, (symbol, _choice_romaji) in enumerate(session.choices, start=1):
            self.write(f"{index}. {symbol}")

    def handle_choice_answer(self, value: str) -> None:
        session = self.require_session()
        if self.is_expected_choice(value, session):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write(f"오답. 정답은 {session.expected_romaji}.", "bad")
        self.next_choice_question()

    def start_matching_quiz(self) -> None:
        pairs = pair_by_romaji()
        entries = tuple((item[0], romaji) for romaji, item in pairs.items())
        self.session = QuizSession(title="히라가나-가타카나 매칭", mode="matching", entries=entries)
        self.handler = self.handle_matching_answer
        self.clear_output()
        self.write("히라가나-가타카나 매칭")
        self.next_matching_question()

    def next_matching_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        pairs = pair_by_romaji()
        romaji = random.choice(list(pairs.keys()))
        hiragana, katakana = pairs[romaji]
        katakana_entries = tuple((item[1], key) for key, item in pairs.items())
        session.expected_symbol = katakana
        session.expected_romaji = romaji
        session.choices = build_multiple_choice(romaji, katakana_entries)
        self.write("")
        self.write(f"문제 {session.index}/{session.count}: {hiragana} 와 같은 소리의 가타카나는?")
        for index, (symbol, _choice_romaji) in enumerate(session.choices, start=1):
            self.write(f"{index}. {symbol}")

    def handle_matching_answer(self, value: str) -> None:
        session = self.require_session()
        if self.is_expected_choice(value, session, compare_symbol=True):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write(f"오답. 정답은 {session.expected_symbol}.", "bad")
        self.next_matching_question()

    def is_expected_choice(self, value: str, session: QuizSession, *, compare_symbol: bool = False) -> bool:
        if not value.isdigit() or session.choices is None:
            return False
        index = int(value) - 1
        if index < 0 or index >= len(session.choices):
            return False
        picked_symbol, picked_romaji = session.choices[index]
        if compare_symbol:
            return picked_symbol == session.expected_symbol
        return picked_romaji == session.expected_romaji

    def finish_session(self) -> None:
        session = self.require_session()
        if session.mode == "romaji":
            self.write("")
            self.write(f"결과: {session.correct}/{session.count} 정답, 최고 연속 정답 {session.best_streak}.")
        else:
            self.write("")
            self.write(f"결과: {session.correct}/{session.count} 정답.")
        self.write("")
        self.write("메뉴로 돌아가려면 Enter 또는 Esc를 누르세요.", "muted")
        self.handler = lambda _value: self.show_main_menu()

    def start_wrong_answer_review(self) -> None:
        entries = self.store.as_entries()
        if not entries:
            self.clear_output()
            self.write("아직 오답 기록이 없습니다.")
            self.write("")
            self.write("메뉴로 돌아가려면 Enter 또는 Esc를 누르세요.", "muted")
            self.handler = lambda _value: self.show_main_menu()
            return
        self.session = QuizSession(
            title="오답 복습",
            mode="romaji",
            entries=entries,
            count=min(DEFAULT_QUESTION_COUNT, len(entries)),
        )
        self.handler = self.handle_romaji_answer
        self.clear_output()
        self.write("오답 복습")
        self.next_romaji_question()

    def show_wrong_answer_summary(self) -> None:
        self.clear_output()
        data = self.store.load()
        if not data:
            self.write("오늘 복습할 오답이 없습니다.")
        else:
            self.write("오답 기록")
            for symbol, item in sorted(data.items(), key=lambda pair: int(pair[1]["count"]), reverse=True):
                self.write(f"- {symbol}: {item['romaji']} ({item['count']}회, 마지막 입력 {item['last_answer']})")
        self.write("")
        self.write("메뉴로 돌아가려면 Enter 또는 Esc를 누르세요.", "muted")
        self.handler = lambda _value: self.show_main_menu()

    def show_reference_menu(self) -> None:
        self.handler = self.handle_reference_input
        self.clear_output()
        self.write("참고 자료")
        self.write("")
        self.write("1. 히라가나 헷갈리는 쌍/예문")
        self.write("2. 가타카나 헷갈리는 쌍/예문")
        self.write("3. 조사와 바로 쓰는 문장")
        self.write("4. 일본어.md 원문 전체 보기")
        self.write("0. 돌아가기")

    def handle_reference_input(self, value: str) -> None:
        if value == "1":
            self.show_script_reference("hiragana")
        elif value == "2":
            self.show_script_reference("katakana")
        elif value == "3":
            self.show_particle_reference()
        elif value == "4":
            self.show_original_markdown()
        elif value == "0":
            self.show_main_menu()
        else:
            self.write("메뉴 번호를 다시 입력하세요.", "bad")

    def show_script_reference(self, script: str) -> None:
        label = "히라가나" if script == "hiragana" else "가타카나"
        self.clear_output()
        self.write(f"{label} 헷갈리는 쌍")
        for left, right, note in get_confusing_pairs(script):
            self.write(f"- {left} / {right}: {note}")

        self.write("")
        self.write(f"{label} 촉음 예문")
        for word, romaji, reading, meaning in get_sokuon_examples(script):
            self.write(f"- {word}: {romaji}, {reading}, {meaning}")

        self.write("")
        self.write(f"{label} 읽기 예문")
        for word, romaji, reading, meaning in get_reading_examples(script):
            self.write(f"- {word}: {romaji}, {reading}, {meaning}")
        self.write_return_hint()

    def show_particle_reference(self) -> None:
        self.clear_output()
        self.write("조사")
        for item in get_particles():
            self.write(f"- {item['particle']} ({item['reading']}): {item['meaning']}")
            self.write(f"  {item['note']}")
            for example in item["examples"]:
                self.write(f"  예: {example}")

        self.write("")
        self.write("초보용 바로 써먹는 세트")
        for pattern in get_beginner_patterns():
            self.write(f"- {pattern}")
        self.write_return_hint()

    def show_original_markdown(self) -> None:
        from pathlib import Path

        markdown_path = Path(__file__).resolve().parents[1] / "일본어.md"
        self.clear_output()
        if not markdown_path.exists():
            self.write("일본어.md 파일을 찾을 수 없습니다.", "bad")
        else:
            self.write("일본어.md 원문")
            self.write(markdown_path.read_text(encoding="utf-8"))
        self.write_return_hint()

    def write_return_hint(self) -> None:
        self.write("")
        self.write("참고 자료 메뉴로 돌아가려면 Enter 또는 Esc를 누르세요.", "muted")
        self.handler = lambda _value: self.show_reference_menu()

    def require_session(self) -> QuizSession:
        if self.session is None:
            raise RuntimeError("active quiz session is required")
        return self.session


def run_gui() -> int:
    root = tk.Tk()
    KanaTrainerApp(root)
    root.mainloop()
    return 0
