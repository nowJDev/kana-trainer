# 터미널에서 가나 퀴즈 메뉴와 학습 세션을 실행한다.
from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path

from .kana import (
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
from .terminal import clear_screen, input_prompt, pause_if_interactive

DEFAULT_QUESTION_COUNT = 10


def configure_stdio() -> None:
    for stream in (sys.stdin, sys.stdout):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def default_store_path() -> Path:
    configured = os.environ.get("KANA_TRAINER_WRONG_PATH")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".kana-trainer" / "wrong-answers.json"


def ask_question(symbol: str, romaji: str, store: WrongAnswerStore) -> bool:
    answer = input(input_prompt(f"{symbol} 의 읽는 법은?"))
    if is_correct_romaji(answer, romaji):
        print("정답.")
        return True
    print(f"오답. 정답은 {romaji}.")
    store.record(symbol, romaji, answer)
    return False


def run_romaji_quiz(
    title: str,
    entries: tuple[tuple[str, str], ...],
    store: WrongAnswerStore,
    *,
    count: int = DEFAULT_QUESTION_COUNT,
) -> None:
    print(f"\n{title}")
    correct = 0
    best_streak = 0
    streak = 0

    for index in range(1, count + 1):
        prompt = random_prompt(entries)
        print(f"\n문제 {index}/{count}")
        if ask_question(prompt.symbol, prompt.romaji, store):
            correct += 1
            streak += 1
            best_streak = max(best_streak, streak)
            print(f"연속 정답: {streak}")
        else:
            streak = 0

    print(f"\n결과: {correct}/{count} 정답, 최고 연속 정답 {best_streak}.")


def run_choice_quiz(
    title: str,
    entries: tuple[tuple[str, str], ...],
    store: WrongAnswerStore,
    *,
    count: int = DEFAULT_QUESTION_COUNT,
) -> None:
    print(f"\n{title}")
    correct = 0

    for index in range(1, count + 1):
        _symbol, romaji = random.choice(entries)
        expected_symbol, _expected_romaji = find_entry_by_romaji(romaji, entries)
        choices = build_multiple_choice(romaji, entries)
        print(f"\n문제 {index}/{count}: {romaji} 에 해당하는 문자는?")
        for choice_index, (symbol, _choice_romaji) in enumerate(choices, start=1):
            print(f"{choice_index}. {symbol}")

        answer = input("> ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            picked_symbol, picked_romaji = choices[int(answer) - 1]
            if picked_romaji == romaji:
                print("정답.")
                correct += 1
                continue
        store.record(expected_symbol, romaji, answer)
        print(f"오답. 정답은 {romaji}.")

    print(f"\n결과: {correct}/{count} 정답.")


def run_matching_quiz(store: WrongAnswerStore, *, count: int = DEFAULT_QUESTION_COUNT) -> None:
    pairs = pair_by_romaji()
    romaji_values = list(pairs.keys())
    print("\n히라가나-가타카나 매칭")
    correct = 0

    for index in range(1, count + 1):
        romaji = random.choice(romaji_values)
        hiragana, katakana = pairs[romaji]
        katakana_entries = tuple((item[1], key) for key, item in pairs.items())
        choices = build_multiple_choice(romaji, katakana_entries)
        print(f"\n문제 {index}/{count}: {hiragana} 와 같은 소리의 가타카나는?")
        for choice_index, (symbol, _choice_romaji) in enumerate(choices, start=1):
            print(f"{choice_index}. {symbol}")

        answer = input("> ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            picked_symbol, picked_romaji = choices[int(answer) - 1]
            if picked_symbol == katakana:
                print("정답.")
                correct += 1
                continue
        store.record(katakana, romaji, answer)
        print(f"오답. 정답은 {katakana}.")

    print(f"\n결과: {correct}/{count} 정답.")


def run_wrong_answer_review(store: WrongAnswerStore) -> None:
    entries = store.as_entries()
    if not entries:
        print("\n아직 오답 기록이 없습니다.")
        return
    run_romaji_quiz("오답 복습", entries, store, count=min(DEFAULT_QUESTION_COUNT, len(entries)))


def print_wrong_answer_summary(store: WrongAnswerStore) -> None:
    data = store.load()
    if not data:
        print("\n오늘 복습할 오답이 없습니다.")
        return

    print("\n오답 기록")
    for symbol, item in sorted(data.items(), key=lambda pair: int(pair[1]["count"]), reverse=True):
        print(f"- {symbol}: {item['romaji']} ({item['count']}회, 마지막 입력 {item['last_answer']})")


def print_reference_for_script(script: str) -> None:
    label = "히라가나" if script == "hiragana" else "가타카나"
    print(f"\n{label} 헷갈리는 쌍")
    for left, right, note in get_confusing_pairs(script):
        print(f"- {left} / {right}: {note}")

    print(f"\n{label} 촉음 예문")
    for word, romaji, reading, meaning in get_sokuon_examples(script):
        print(f"- {word}: {romaji}, {reading}, {meaning}")

    print(f"\n{label} 읽기 예문")
    for word, romaji, reading, meaning in get_reading_examples(script):
        print(f"- {word}: {romaji}, {reading}, {meaning}")


def print_particle_reference() -> None:
    print("\n조사")
    for item in get_particles():
        print(f"- {item['particle']} ({item['reading']}): {item['meaning']}")
        print(f"  {item['note']}")
        for example in item["examples"]:
            print(f"  예: {example}")

    print("\n초보용 바로 써먹는 세트")
    for pattern in get_beginner_patterns():
        print(f"- {pattern}")


def print_original_markdown() -> None:
    markdown_path = Path(__file__).resolve().parents[1] / "일본어.md"
    if not markdown_path.exists():
        print("\n일본어.md 파일을 찾을 수 없습니다.")
        return
    print("\n일본어.md 원문")
    print(markdown_path.read_text(encoding="utf-8"))


def run_reference_menu() -> None:
    while True:
        clear_screen()
        print("\n참고 자료")
        print("1. 히라가나 헷갈리는 쌍/예문")
        print("2. 가타카나 헷갈리는 쌍/예문")
        print("3. 조사와 바로 쓰는 문장")
        print("4. 일본어.md 원문 전체 보기")
        print("0. 돌아가기")
        choice = input("> ").strip()

        if choice == "1":
            print_reference_for_script("hiragana")
            pause_if_interactive()
        elif choice == "2":
            print_reference_for_script("katakana")
            pause_if_interactive()
        elif choice == "3":
            print_particle_reference()
            pause_if_interactive()
        elif choice == "4":
            print_original_markdown()
            pause_if_interactive()
        elif choice == "0":
            return
        else:
            print("메뉴 번호를 다시 입력하세요.")


def run_demo() -> None:
    print("かな Trainer 데모")
    print("문제: し 의 읽는 법은?")
    print("> shi")
    print("정답.")
    print("문제: ka 에 해당하는 문자는?")
    choices = build_multiple_choice("ka", get_kana("hiragana"), rng_seed=7)
    for index, (symbol, _romaji) in enumerate(choices, start=1):
        print(f"{index}. {symbol}")


def run_menu() -> None:
    configure_stdio()
    store = WrongAnswerStore(default_store_path())

    while True:
        clear_screen()
        print("\nかな Trainer")
        print("1. 히라가나 보고 로마자 입력")
        print("2. 가타카나 보고 로마자 입력")
        print("3. 로마자 보고 히라가나 선택")
        print("4. 히라가나-가타카나 매칭")
        print("5. 오답 복습")
        print("6. 오답 기록 보기")
        print("7. 일본어.md 참고 자료 보기")
        print("0. 종료")
        choice = input("> ").strip()

        if choice == "1":
            run_romaji_quiz("히라가나 연습", get_kana("hiragana"), store)
        elif choice == "2":
            run_romaji_quiz("가타카나 연습", get_kana("katakana"), store)
        elif choice == "3":
            run_choice_quiz("히라가나 4지선다", get_kana("hiragana"), store)
        elif choice == "4":
            run_matching_quiz(store)
        elif choice == "5":
            run_wrong_answer_review(store)
        elif choice == "6":
            print_wrong_answer_summary(store)
        elif choice == "7":
            run_reference_menu()
        elif choice == "0":
            print("다음에 또 연습해요.")
            return
        else:
            print("메뉴 번호를 다시 입력하세요.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="히라가나와 가타카나를 연습하는 CLI 학습 앱.")
    parser.add_argument("--demo", action="store_true", help="입력 없이 데모 출력을 보여준다.")
    parser.add_argument("--gui", action="store_true", help="터미널풍 GUI 앱으로 실행한다.")
    args = parser.parse_args(argv)

    if args.gui:
        from .gui import run_gui

        return run_gui()

    if args.demo:
        configure_stdio()
        run_demo()
        return 0

    run_menu()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
