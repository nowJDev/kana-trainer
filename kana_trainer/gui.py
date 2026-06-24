# 터미널풍 GUI로 가나 학습 세션을 실행한다.
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, replace
from tkinter import font, scrolledtext, ttk
from typing import Callable

from .cli import DEFAULT_QUESTION_COUNT, KANA_QUESTION_COUNT, MAIN_MENU_OPTIONS, default_history_path, default_store_path
from .kana import (
    KanaEntry,
    get_beginner_patterns,
    get_confusing_pairs,
    get_kana,
    get_kana_level_label,
    get_particles,
    get_reading_examples,
    get_sokuon_examples,
    pair_by_romaji,
)
from .quiz import (
    ConfusingItem,
    ExampleItem,
    KANA_GAME_LIVES,
    KanaGameState,
    StudyHistoryStore,
    WrongAnswerStore,
    advance_kana_game_state,
    build_confusing_question_items,
    build_example_question_items,
    build_kana_question_items,
    build_multiple_choice,
    build_particle_meaning_choice,
    build_particle_question_items,
    build_romaji_question_items,
    collect_confusing_items,
    collect_example_items,
    find_entry_by_romaji,
    is_correct_romaji,
    kana_level_mode,
)
from .resources import resource_path
from .settings import MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, AppSettings, SettingsStore, clamp_font_size, window_geometry

InputHandler = Callable[[str], None]
MenuOption = tuple[str, str]
DISPLAY_FONT_CANDIDATES = ("나눔고딕", "NanumGothic", "Nanum Gothic", "Yu Gothic UI", "Meiryo", "Yu Gothic", "MS Gothic")
GLASS_THEME = {
    "background": "#070A0F",
    "surface": "#111824",
    "surface_soft": "#0B111A",
    "surface_lifted": "#162131",
    "border": "#203246",
    "border_glow": "#65D9FF",
    "glow_cool": "#9FE7FF",
    "glow_warm": "#FFE6A3",
    "glow_good": "#B5FFCA",
    "glow_bad": "#FF8FA3",
    "glow_input": "#B1FFF2",
    "text": "#EAF6FF",
    "muted": "#8FA3B7",
    "selection": "#1E4056",
}
REFERENCE_MENU_OPTIONS: tuple[MenuOption, ...] = (
    ("1", "히라가나 헷갈리는 쌍/예문"),
    ("2", "가타카나 헷갈리는 쌍/예문"),
    ("3", "조사와 바로 쓰는 문장"),
    ("4", "일본어.md 원문 전체 보기"),
    ("0", "돌아가기"),
)
COLOR_TAGS = {
    "muted": GLASS_THEME["muted"],
    "good": GLASS_THEME["glow_good"],
    "bad": GLASS_THEME["glow_bad"],
    "input": GLASS_THEME["glow_input"],
    "menu": GLASS_THEME["glow_cool"],
    "question": GLASS_THEME["glow_warm"],
    "kana": GLASS_THEME["glow_cool"],
    "answer": GLASS_THEME["glow_warm"],
    "result": "#D9C2FF",
    "title": GLASS_THEME["text"],
}


def choose_display_font(available_fonts: tuple[str, ...]) -> str:
    available = set(available_fonts)
    for family in DISPLAY_FONT_CANDIDATES:
        if family in available:
            return family
    return DISPLAY_FONT_CANDIDATES[-1]


def choose_ui_font_family(display_font: str) -> str:
    return display_font


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
    question_entries: tuple[KanaEntry, ...] = ()
    confusing_items: tuple[ConfusingItem, ...] = ()
    current_hint: str = ""
    particle_items: tuple[dict[str, object], ...] = ()
    example_items: tuple[ExampleItem, ...] = ()
    lives: int | None = None


class KanaTrainerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.store = WrongAnswerStore(default_store_path())
        self.history_store = StudyHistoryStore(default_history_path())
        self.handler: InputHandler = self.handle_menu_input
        self.session: QuizSession | None = None
        self.focus_after_id: str | None = None

        self.root.title("Kana Trainer")
        self.root.geometry(window_geometry(self.settings))
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.configure(bg=GLASS_THEME["background"])

        display_font = choose_display_font(font.families(root))
        ui_font_family = choose_ui_font_family(display_font)
        self.text_font = font.Font(family=display_font, size=self.settings.font_size)
        self.emphasis_font = font.Font(family=display_font, size=self.settings.font_size, weight="bold")
        self.ui_font = font.Font(family=ui_font_family, size=11, weight="normal")
        self.title_font = font.Font(family=ui_font_family, size=16, weight="bold")
        self._build_layout()
        self._bind_events()
        self.show_main_menu()

    def _build_layout(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Kana.TButton",
            background=GLASS_THEME["surface_lifted"],
            bordercolor=GLASS_THEME["border"],
            darkcolor=GLASS_THEME["surface"],
            focuscolor=GLASS_THEME["border_glow"],
            font=self.ui_font,
            foreground=GLASS_THEME["text"],
            lightcolor=GLASS_THEME["border_glow"],
            padding=(14, 8),
            relief=tk.FLAT,
        )
        style.map(
            "Kana.TButton",
            background=[
                ("pressed", GLASS_THEME["surface_soft"]),
                ("active", GLASS_THEME["surface_lifted"]),
            ],
            bordercolor=[
                ("focus", GLASS_THEME["border_glow"]),
                ("active", GLASS_THEME["border_glow"]),
            ],
            foreground=[
                ("pressed", GLASS_THEME["glow_warm"]),
                ("active", GLASS_THEME["glow_cool"]),
            ],
            lightcolor=[("active", GLASS_THEME["border_glow"])],
        )
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = tk.Frame(
            self.root,
            bg=GLASS_THEME["surface"],
            highlightbackground=GLASS_THEME["border"],
            highlightcolor=GLASS_THEME["border_glow"],
            highlightthickness=1,
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))

        title = tk.Label(
            header,
            text="かな Trainer",
            bg=GLASS_THEME["surface"],
            fg=GLASS_THEME["glow_cool"],
            font=self.title_font,
            padx=16,
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
            bg=GLASS_THEME["surface_soft"],
            fg=GLASS_THEME["text"],
            highlightbackground=GLASS_THEME["border"],
            highlightcolor=GLASS_THEME["border_glow"],
            highlightthickness=1,
            insertbackground=GLASS_THEME["glow_input"],
            selectbackground=GLASS_THEME["selection"],
            relief=tk.FLAT,
            borderwidth=0,
            padx=18,
            pady=18,
            font=self.text_font,
            state=tk.DISABLED,
            height=1,
        )
        self.output.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.configure_output_tags()

        self.option_frame = tk.Frame(
            self.root,
            bg=GLASS_THEME["surface"],
            highlightbackground=GLASS_THEME["border"],
            highlightcolor=GLASS_THEME["border_glow"],
            highlightthickness=1,
            padx=10,
            pady=8,
        )
        self.option_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        for column in range(2):
            self.option_frame.columnconfigure(column, weight=1)

        input_row = tk.Frame(
            self.root,
            bg=GLASS_THEME["surface"],
            highlightbackground=GLASS_THEME["border"],
            highlightcolor=GLASS_THEME["border_glow"],
            highlightthickness=1,
        )
        input_row.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))
        input_row.columnconfigure(1, weight=1)

        prompt = tk.Label(
            input_row,
            text=">",
            bg=GLASS_THEME["surface"],
            fg=GLASS_THEME["glow_warm"],
            font=self.text_font,
            padx=12,
        )
        prompt.grid(row=0, column=0, sticky="w")

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            input_row,
            textvariable=self.entry_var,
            bg=GLASS_THEME["surface_soft"],
            fg=GLASS_THEME["text"],
            highlightbackground=GLASS_THEME["border"],
            highlightcolor=GLASS_THEME["border_glow"],
            highlightthickness=1,
            insertbackground=GLASS_THEME["glow_input"],
            relief=tk.FLAT,
            font=self.text_font,
        )
        self.entry.grid(row=0, column=1, sticky="ew", ipady=8, pady=10)

        submit = ttk.Button(input_row, text="Enter", style="Kana.TButton", command=self.submit_input)
        submit.grid(row=0, column=2, padx=10)

        self.status_var = tk.StringVar(value="Enter 제출 | Esc 메뉴 | Ctrl+휠 글자 크기")
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            bg=GLASS_THEME["background"],
            fg=GLASS_THEME["muted"],
            font=self.ui_font,
            padx=12,
            pady=6,
        )
        status.grid(row=4, column=0, sticky="ew")

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda _event: self.submit_input())
        self.root.bind("<Escape>", lambda _event: self.show_main_menu())
        self.root.bind("<Control-MouseWheel>", self.handle_ctrl_wheel)
        self.root.bind("<Destroy>", self.cancel_pending_focus, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.focus_after_id = self.root.after(100, self.focus_entry)

    def cancel_pending_focus(self, event: tk.Event) -> None:
        if event.widget is not self.root or self.focus_after_id is None:
            return
        try:
            self.root.after_cancel(self.focus_after_id)
        except tk.TclError:
            pass
        self.focus_after_id = None

    def focus_entry(self) -> None:
        self.focus_after_id = None
        try:
            self.entry.focus_set()
        except tk.TclError:
            pass

    def handle_ctrl_wheel(self, event: tk.Event) -> None:
        delta = 2 if event.delta > 0 else -2
        self.change_font_size(delta)

    def change_font_size(self, delta: int) -> None:
        next_size = clamp_font_size(self.settings.font_size + delta)
        self.settings = replace(self.settings, font_size=next_size)
        self.settings_store.save(self.settings)
        self.text_font.configure(size=next_size)
        self.emphasis_font.configure(size=next_size)
        self.status_var.set(f"폰트 크기 {next_size} | Enter 제출 | Esc 메뉴 | Ctrl+휠 글자 크기")

    def save_window_size(self) -> None:
        try:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = self.root.winfo_x()
            y = self.root.winfo_y()
        except tk.TclError:
            return
        self.settings = replace(self.settings, window_width=width, window_height=height, window_x=x, window_y=y)
        self.settings_store.save(self.settings)

    def close(self) -> None:
        self.save_window_size()
        self.root.destroy()

    def clear_output(self) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)

    def write(self, text: str = "", tag: str | None = None) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def write_segments(self, segments: tuple[tuple[str, str | None], ...]) -> None:
        self.output.configure(state=tk.NORMAL)
        for text, tag in segments:
            self.output.insert(tk.END, text, tag)
        self.output.insert(tk.END, "\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def configure_output_tags(self) -> None:
        for tag, color in COLOR_TAGS.items():
            self.output.tag_configure(tag, foreground=color)
        for tag in ("answer", "kana", "menu", "question", "result", "title"):
            self.output.tag_configure(tag, font=self.emphasis_font)
        self.output.tag_configure("prompt", foreground=COLOR_TAGS["input"])

    def submit_input(self) -> None:
        value = self.entry_var.get().strip()
        self.entry_var.set("")
        self.submit_value(value)

    def submit_value(self, value: str) -> None:
        if value:
            self.write(f"> {value}", "input")
        self.handler(value)
        try:
            should_focus = bool(self.root.winfo_exists() and self.entry.winfo_exists())
        except tk.TclError:
            should_focus = False
        if should_focus:
            self.focus_entry()

    def set_option_buttons(self, options: tuple[MenuOption, ...]) -> None:
        for child in self.option_frame.winfo_children():
            child.destroy()
        if not options:
            self.option_frame.grid_remove()
            return

        self.option_frame.grid()
        for index, (value, label) in enumerate(options):
            button = ttk.Button(
                self.option_frame,
                text=f"{value}. {label}" if value else label,
                style="Kana.TButton",
                command=lambda selected=value: self.submit_value(selected),
            )
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=4, pady=4)

    def show_main_menu(self) -> None:
        self.session = None
        self.handler = self.handle_menu_input
        self.clear_output()
        self.write("かな Trainer", "title")
        self.write("")
        for number, label in MAIN_MENU_OPTIONS:
            self.write_menu_item(number, label)
        self.write("")
        self.write("메뉴 번호를 입력하거나 버튼을 누르세요.", "muted")
        self.set_option_buttons(MAIN_MENU_OPTIONS)
        self.status_var.set("메뉴 | 버튼 선택 | Enter 제출 | Esc 메뉴 | Ctrl+휠 글자 크기")

    def write_menu_item(self, number: str, label: str) -> None:
        self.write_segments(((f"{number}. ", "menu"), (label, None)))

    def handle_menu_input(self, value: str) -> None:
        if value == "1":
            self.show_kana_level_menu("hiragana", "히라가나", "romaji")
        elif value == "2":
            self.show_kana_level_menu("katakana", "가타카나", "romaji")
        elif value == "3":
            self.show_kana_level_menu("matching", "히라가나-가타카나 매칭", "matching")
        elif value == "4":
            self.show_kana_level_menu("hiragana", "히라가나 4지선다", "choice")
        elif value == "5":
            self.start_particle_meaning_quiz()
        elif value == "6":
            self.start_confusing_character_quiz()
        elif value == "7":
            self.start_wrong_answer_review()
        elif value == "8":
            self.show_wrong_answer_summary()
        elif value == "9":
            self.show_study_history_summary()
        elif value == "10":
            self.show_reference_menu()
        elif value == "0":
            self.close()
        else:
            self.write("메뉴 번호를 다시 입력하세요.", "bad")

    def show_kana_level_menu(self, script: str, label: str, quiz_kind: str) -> None:
        self.handler = lambda value: self.handle_kana_level_input(script, label, quiz_kind, value)
        self.clear_output()
        self.write(f"{label} 레벨 선택", "title")
        self.write("")
        if quiz_kind == "matching":
            unlocked_level = min(self.history_store.unlocked_kana_level("hiragana"), self.history_store.unlocked_kana_level("katakana"))
        else:
            unlocked_level = self.history_store.unlocked_kana_level(script)
        options: list[MenuOption] = []
        for level in (1, 2, 3):
            status = "해금" if level <= unlocked_level else "잠김"
            label_text = f"Lv.{level} {get_kana_level_label(level)} ({status})"
            self.write_menu_item(str(level), label_text)
            options.append((str(level), label_text))
        self.write_menu_item("0", "돌아가기")
        options.append(("0", "돌아가기"))
        self.set_option_buttons(tuple(options))

    def handle_kana_level_input(self, script: str, label: str, quiz_kind: str, value: str) -> None:
        if value == "0":
            self.show_main_menu()
            return
        if not value.isdigit() or int(value) not in (1, 2, 3):
            self.write("레벨 번호를 다시 입력하세요.", "bad")
            return
        level = int(value)
        if quiz_kind == "matching":
            unlocked_level = min(self.history_store.unlocked_kana_level("hiragana"), self.history_store.unlocked_kana_level("katakana"))
        else:
            unlocked_level = self.history_store.unlocked_kana_level(script)
        if level > unlocked_level:
            self.write("아직 잠긴 레벨입니다. 이전 레벨에서 80% 이상 정답을 기록하면 해금됩니다.", "bad")
            return

        level_label = get_kana_level_label(level)
        if quiz_kind == "choice":
            self.start_choice_quiz(
                f"{label} Lv.{level} {level_label}",
                get_kana(script, level=level),
                mode=kana_level_mode(script, level, mode="choice"),
            )
        elif quiz_kind == "matching":
            self.start_matching_quiz(level=level, mode=f"matching:level{level}")
        else:
            self.start_romaji_quiz(
                f"{label} Lv.{level} {level_label}",
                get_kana(script, level=level),
                mode=kana_level_mode(script, level),
            )

    def start_romaji_quiz(self, title: str, entries: tuple[KanaEntry, ...], *, mode: str = "romaji") -> None:
        question_count = min(KANA_QUESTION_COUNT, len(entries))
        questions = tuple(build_kana_question_items(entries, count=question_count))
        self.session = QuizSession(
            title=title,
            mode=mode,
            entries=entries,
            count=question_count,
            question_entries=questions,
            lives=KANA_GAME_LIVES,
        )
        self.handler = self.handle_romaji_answer
        self.clear_output()
        self.set_option_buttons(())
        self.write(title)
        self.write(f"목표: {question_count}문제 전부 돌파", "muted")
        self.write(f"목숨: {KANA_GAME_LIVES}/{KANA_GAME_LIVES}", "muted")
        self.next_romaji_question()

    def next_romaji_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        symbol, romaji = session.question_entries[session.index - 1]
        session.expected_symbol = symbol
        session.expected_romaji = romaji
        self.write("")
        if session.lives is None:
            self.write(f"문제 {session.index}/{session.count}", "question")
        else:
            self.write(f"문제 {session.index}/{session.count} | 목숨 {session.lives}/{KANA_GAME_LIVES}", "question")
        self.write_segments(((symbol, "kana"), (" 의 읽는 법은?", "question")))

    def handle_romaji_answer(self, value: str) -> None:
        session = self.require_session()
        is_correct = is_correct_romaji(value, session.expected_romaji)
        if session.lives is not None:
            self.handle_romaji_game_answer(value, is_correct)
            return

        if is_correct:
            session.correct += 1
            session.streak += 1
            session.best_streak = max(session.best_streak, session.streak)
            self.write("정답.", "good")
            self.write(f"연속 정답: {session.streak}", "muted")
        else:
            session.streak = 0
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_romaji, "answer"), (".", "bad")))
        self.next_romaji_question()

    def handle_romaji_game_answer(self, value: str, is_correct: bool) -> None:
        session = self.require_session()
        state = KanaGameState(
            total=session.count,
            lives=session.lives or 0,
            correct=session.correct,
            answered=session.index - 1,
            streak=session.streak,
            best_streak=session.best_streak,
        )
        state = advance_kana_game_state(state, is_correct=is_correct)
        session.correct = state.correct
        session.streak = state.streak
        session.best_streak = state.best_streak
        session.lives = state.lives
        if is_correct:
            self.write("정답.", "good")
            self.write(f"연속 정답: {session.streak}", "muted")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_romaji, "answer"), (".", "bad")))
            self.write(f"남은 목숨: {session.lives}/{KANA_GAME_LIVES}", "bad" if session.lives <= 1 else "muted")
        if state.finished:
            self.finish_session()
            return
        self.next_romaji_question()

    def start_choice_quiz(self, title: str, entries: tuple[KanaEntry, ...], *, mode: str = "choice") -> None:
        questions = tuple(build_romaji_question_items(entries, count=KANA_QUESTION_COUNT))
        self.session = QuizSession(
            title=title,
            mode=mode,
            entries=entries,
            count=KANA_QUESTION_COUNT,
            question_entries=questions,
        )
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
        _symbol, romaji = session.question_entries[session.index - 1]
        expected_symbol, _expected_romaji = find_entry_by_romaji(romaji, session.entries)
        session.expected_symbol = expected_symbol
        session.expected_romaji = romaji
        session.choices = build_multiple_choice(romaji, session.entries)
        self.set_option_buttons(tuple((str(index), symbol) for index, (symbol, _romaji) in enumerate(session.choices, start=1)))
        self.write("")
        self.write_segments(((f"문제 {session.index}/{session.count}: ", "question"), (romaji, "answer"), (" 에 해당하는 문자는?", "question")))
        for index, (symbol, _choice_romaji) in enumerate(session.choices, start=1):
            self.write_segments(((f"{index}. ", "menu"), (symbol, "kana")))

    def handle_choice_answer(self, value: str) -> None:
        session = self.require_session()
        if self.is_expected_choice(value, session):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_romaji, "answer"), (".", "bad")))
        self.next_choice_question()

    def start_matching_quiz(self, *, level: int | None = None, mode: str = "matching") -> None:
        pairs = pair_by_romaji(level=level)
        entries = tuple((item[0], romaji) for romaji, item in pairs.items())
        questions = tuple(build_romaji_question_items(entries, count=KANA_QUESTION_COUNT))
        title = "히라가나-가타카나 매칭"
        if level is not None:
            title = f"{title} Lv.{level} {get_kana_level_label(level)}"
        self.session = QuizSession(
            title=title,
            mode=mode,
            entries=entries,
            count=KANA_QUESTION_COUNT,
            question_entries=questions,
        )
        self.handler = self.handle_matching_answer
        self.clear_output()
        self.write(title)
        self.next_matching_question()

    def next_matching_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        pairs = pair_by_romaji(level=self.matching_level_from_mode(session.mode))
        _symbol, romaji = session.question_entries[session.index - 1]
        hiragana, katakana = pairs[romaji]
        katakana_entries = tuple((item[1], key) for key, item in pairs.items())
        session.expected_symbol = katakana
        session.expected_romaji = romaji
        session.choices = build_multiple_choice(romaji, katakana_entries)
        self.set_option_buttons(tuple((str(index), symbol) for index, (symbol, _romaji) in enumerate(session.choices, start=1)))
        self.write("")
        self.write_segments(((f"문제 {session.index}/{session.count}: ", "question"), (hiragana, "kana"), (" 와 같은 소리의 가타카나는?", "question")))
        for index, (symbol, _choice_romaji) in enumerate(session.choices, start=1):
            self.write_segments(((f"{index}. ", "menu"), (symbol, "kana")))

    def handle_matching_answer(self, value: str) -> None:
        session = self.require_session()
        if self.is_expected_choice(value, session, compare_symbol=True):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_symbol, "answer"), (".", "bad")))
        self.next_matching_question()

    def matching_level_from_mode(self, mode: str) -> int | None:
        prefix = "matching:level"
        if not mode.startswith(prefix):
            return None
        try:
            return int(mode.removeprefix(prefix))
        except ValueError:
            return None

    def start_particle_meaning_quiz(self) -> None:
        entries = tuple((str(item["particle"]), str(item["meaning"])) for item in get_particles())
        questions = tuple(build_particle_question_items(get_particles(), count=DEFAULT_QUESTION_COUNT))
        self.session = QuizSession(title="조사 뜻 맞히기", mode="particle", entries=entries, particle_items=questions)
        self.handler = self.handle_particle_answer
        self.clear_output()
        self.write("조사 뜻 맞히기")
        self.next_particle_question()

    def next_particle_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        item = session.particle_items[session.index - 1]
        particle = str(item["particle"])
        reading = str(item["reading"])
        meaning = str(item["meaning"])
        session.expected_symbol = particle
        session.expected_romaji = meaning
        session.choices = build_particle_meaning_choice(meaning, get_particles())
        self.set_option_buttons(tuple((str(index), choice_meaning) for index, (_particle, choice_meaning) in enumerate(session.choices, start=1)))
        self.write("")
        self.write_segments(((f"문제 {session.index}/{session.count}: ", "question"), (particle, "kana"), (f"({reading})의 뜻은?", "question")))
        for index, (_choice_particle, choice_meaning) in enumerate(session.choices, start=1):
            self.write_segments(((f"{index}. ", "menu"), (choice_meaning, None)))

    def handle_particle_answer(self, value: str) -> None:
        session = self.require_session()
        if self.is_expected_choice(value, session):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_romaji, "answer"), (".", "bad")))
        self.next_particle_question()

    def start_example_romaji_quiz(self) -> None:
        questions = tuple(build_example_question_items(collect_example_items(), count=DEFAULT_QUESTION_COUNT))
        entries = tuple(
            (word, romaji)
            for _category, _script_label, word, romaji, _reading, _meaning in questions
        )
        self.session = QuizSession(title="예문 로마자 입력", mode="example", entries=entries, example_items=questions)
        self.handler = self.handle_example_answer
        self.clear_output()
        self.set_option_buttons(())
        self.write("예문 로마자 입력")
        self.next_example_question()

    def next_example_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        category, script_label, word, romaji, reading, meaning = session.example_items[session.index - 1]
        session.expected_symbol = word
        session.expected_romaji = romaji
        self.write("")
        self.write_segments(
            (
                (f"문제 {session.index}/{session.count}: ", "question"),
                (f"[{script_label} {category}] ", "menu"),
                (word, "kana"),
            )
        )
        self.write(f"읽기 힌트: {reading}", "muted")
        self.write(f"뜻: {meaning}", "muted")

    def handle_example_answer(self, value: str) -> None:
        session = self.require_session()
        if is_correct_romaji(value, session.expected_romaji):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_romaji, "answer"), (".", "bad")))
        self.next_example_question()

    def start_confusing_character_quiz(self) -> None:
        questions = tuple(build_confusing_question_items(collect_confusing_items(), count=DEFAULT_QUESTION_COUNT))
        entries = tuple(
            (symbol, romaji)
            for _script_label, symbol, romaji, _other_symbol, _other_romaji, _note in questions
        )
        self.session = QuizSession(title="헷갈리는 문자 선택", mode="confusing", entries=entries, confusing_items=questions)
        self.handler = self.handle_confusing_answer
        self.clear_output()
        self.write("헷갈리는 문자 선택")
        self.next_confusing_question()

    def next_confusing_question(self) -> None:
        session = self.require_session()
        if session.index >= session.count:
            self.finish_session()
            return
        session.index += 1
        script_label, symbol, romaji, other_symbol, other_romaji, note = session.confusing_items[session.index - 1]
        session.expected_symbol = symbol
        session.expected_romaji = romaji
        session.current_hint = note
        session.choices = build_kana_question_items(((symbol, romaji), (other_symbol, other_romaji)), count=2)
        self.set_option_buttons(
            tuple(
                (str(index), choice_symbol)
                for index, (choice_symbol, _choice_romaji) in enumerate(session.choices, start=1)
            )
        )
        self.write("")
        self.write_segments(
            (
                (f"문제 {session.index}/{session.count}: ", "question"),
                (f"[{script_label}] ", "menu"),
                (romaji, "answer"),
                (" 에 해당하는 문자는?", "question"),
            )
        )
        for index, (choice_symbol, _choice_romaji) in enumerate(session.choices, start=1):
            self.write_segments(((f"{index}. ", "menu"), (choice_symbol, "kana")))

    def handle_confusing_answer(self, value: str) -> None:
        session = self.require_session()
        if self.is_expected_choice(value, session, compare_symbol=True):
            session.correct += 1
            self.write("정답.", "good")
        else:
            self.store.record(session.expected_symbol, session.expected_romaji, value)
            self.write_segments((("오답. ", "bad"), ("정답은 ", "bad"), (session.expected_symbol, "answer"), (".", "bad")))
        self.write(f"힌트: {session.current_hint}", "muted")
        self.next_confusing_question()

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
        if session.lives is not None:
            self.write("")
            if session.lives > 0 and session.index >= session.count:
                self.write("게임 승리. 모든 문제를 끝까지 돌파했습니다.", "good")
            else:
                self.write("게임 종료. 목숨이 모두 사라졌습니다.", "bad")
            self.write(
                f"결과: {session.correct}/{session.count} 정답, 남은 목숨 {session.lives}/{KANA_GAME_LIVES}, 최고 연속 정답 {session.best_streak}.",
                "result",
            )
        elif session.mode.startswith("romaji"):
            self.write("")
            self.write(f"결과: {session.correct}/{session.count} 정답, 최고 연속 정답 {session.best_streak}.", "result")
        else:
            self.write("")
            self.write(f"결과: {session.correct}/{session.count} 정답.", "result")
        self.history_store.record_session(session.title, session.mode, correct=session.correct, total=session.count)
        self.write("")
        self.write("메뉴로 돌아가려면 Enter 또는 Esc를 누르세요.", "muted")
        self.set_option_buttons((("", "메뉴로 돌아가기"),))
        self.handler = lambda _value: self.show_main_menu()

    def start_wrong_answer_review(self) -> None:
        entries = self.store.as_entries()
        if not entries:
            self.clear_output()
            self.set_option_buttons((("", "메뉴로 돌아가기"),))
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
            question_entries=tuple(
                build_kana_question_items(entries, count=min(DEFAULT_QUESTION_COUNT, len(entries)))
            ),
        )
        self.handler = self.handle_romaji_answer
        self.clear_output()
        self.set_option_buttons(())
        self.write("오답 복습")
        self.next_romaji_question()

    def show_wrong_answer_summary(self) -> None:
        self.clear_output()
        self.set_option_buttons((("", "메뉴로 돌아가기"),))
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

    def show_study_history_summary(self) -> None:
        self.clear_output()
        self.set_option_buttons((("", "메뉴로 돌아가기"),))
        for line in self.history_store.summary_lines():
            self.write(line, "result" if line == "학습 기록" else None)
        self.write("")
        self.write("메뉴로 돌아가려면 Enter 또는 Esc를 누르세요.", "muted")
        self.handler = lambda _value: self.show_main_menu()

    def show_reference_menu(self) -> None:
        self.handler = self.handle_reference_input
        self.clear_output()
        self.write("참고 자료")
        self.write("")
        for number, label in REFERENCE_MENU_OPTIONS:
            self.write_menu_item(number, label)
        self.set_option_buttons(REFERENCE_MENU_OPTIONS)

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
        markdown_path = resource_path("일본어.md")
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
        self.set_option_buttons((("", "참고 자료 메뉴로 돌아가기"),))
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
