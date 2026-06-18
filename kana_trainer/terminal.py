# 터미널 화면 정리와 입력 프롬프트 형식을 관리한다.
from __future__ import annotations

import os
import sys
from typing import TextIO

CLEAR_SCREEN = "\033[2J\033[H"


def input_prompt(question: str) -> str:
    return f"{question}\n> "


def should_clear_screen(*, is_interactive: bool, no_clear: bool) -> bool:
    return is_interactive and not no_clear


def clear_screen(stream: TextIO | None = None) -> None:
    output = stream or sys.stdout
    no_clear = os.environ.get("KANA_TRAINER_NO_CLEAR") == "1"
    if should_clear_screen(is_interactive=output.isatty(), no_clear=no_clear):
        output.write(CLEAR_SCREEN)
        output.flush()


def pause_if_interactive(message: str = "계속하려면 Enter를 누르세요.") -> None:
    if sys.stdin.isatty() and sys.stdout.isatty():
        input(input_prompt(message))
