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
    StudyHistoryStore,
    WrongAnswerStore,
    build_example_question_items,
    build_multiple_choice,
    build_particle_meaning_choice,
    build_particle_question_items,
    collect_example_items,
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


def default_history_path() -> Path:
    configured = os.environ.get("KANA_TRAINER_HISTORY_PATH")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".kana-trainer" / "study-history.json"


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
    history_store: StudyHistoryStore | None = None,
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
    if history_store is not None:
        history_store.record_session(title, "romaji", correct=correct, total=count)


def run_choice_quiz(
    title: str,
    entries: tuple[tuple[str, str], ...],
    store: WrongAnswerStore,
    *,
    history_store: StudyHistoryStore | None = None,
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
    if history_store is not None:
        history_store.record_session(title, "choice", correct=correct, total=count)


def run_matching_quiz(
    store: WrongAnswerStore,
    *,
    history_store: StudyHistoryStore | None = None,
    count: int = DEFAULT_QUESTION_COUNT,
) -> None:
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
    if history_store is not None:
        history_store.record_session("히라가나-가타카나 매칭", "matching", correct=correct, total=count)


def run_particle_meaning_quiz(
    *,
    history_store: StudyHistoryStore | None = None,
    count: int = DEFAULT_QUESTION_COUNT,
) -> None:
    particles = get_particles()
    questions = build_particle_question_items(particles, count=count)
    print("\n조사 뜻 맞히기")
    correct = 0

    for index, item in enumerate(questions, start=1):
        particle = str(item["particle"])
        reading = str(item["reading"])
        meaning = str(item["meaning"])
        choices = build_particle_meaning_choice(meaning, particles)
        print(f"\n문제 {index}/{count}: 조사 {particle}({reading})의 뜻은?")
        for choice_index, (_choice_particle, choice_meaning) in enumerate(choices, start=1):
            print(f"{choice_index}. {choice_meaning}")

        answer = input("> ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            _picked_particle, picked_meaning = choices[int(answer) - 1]
            if picked_meaning == meaning:
                print("정답.")
                correct += 1
                continue
        print(f"오답. 정답은 {meaning}.")

    print(f"\n결과: {correct}/{count} 정답.")
    if history_store is not None:
        history_store.record_session("조사 뜻 맞히기", "particle", correct=correct, total=count)


def run_example_romaji_quiz(
    store: WrongAnswerStore,
    *,
    history_store: StudyHistoryStore | None = None,
    count: int = DEFAULT_QUESTION_COUNT,
) -> None:
    questions = build_example_question_items(collect_example_items(), count=count)
    print("\n예문 로마자 입력")
    correct = 0

    for index, (category, script_label, word, romaji, reading, meaning) in enumerate(questions, start=1):
        print(f"\n문제 {index}/{count}: [{script_label} {category}] {word}")
        print(f"읽기 힌트: {reading}")
        print(f"뜻: {meaning}")
        answer = input("> ").strip()
        if is_correct_romaji(answer, romaji):
            print("정답.")
            correct += 1
        else:
            print(f"오답. 정답은 {romaji}.")
            store.record(word, romaji, answer)

    print(f"\n결과: {correct}/{count} 정답.")
    if history_store is not None:
        history_store.record_session("예문 로마자 입력", "example", correct=correct, total=count)


def run_wrong_answer_review(store: WrongAnswerStore, *, history_store: StudyHistoryStore | None = None) -> None:
    entries = store.as_entries()
    if not entries:
        print("\n아직 오답 기록이 없습니다.")
        return
    run_romaji_quiz("오답 복습", entries, store, history_store=history_store, count=min(DEFAULT_QUESTION_COUNT, len(entries)))


def print_wrong_answer_summary(store: WrongAnswerStore) -> None:
    data = store.load()
    if not data:
        print("\n오늘 복습할 오답이 없습니다.")
        return

    print("\n오답 기록")
    for symbol, item in sorted(data.items(), key=lambda pair: int(pair[1]["count"]), reverse=True):
        print(f"- {symbol}: {item['romaji']} ({item['count']}회, 마지막 입력 {item['last_answer']})")


def print_study_history_summary(history_store: StudyHistoryStore) -> None:
    print()
    for line in history_store.summary_lines():
        print(line)


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
    history_store = StudyHistoryStore(default_history_path())

    while True:
        clear_screen()
        print("\nかな Trainer")
        print("1. 히라가나 보고 로마자 입력")
        print("2. 가타카나 보고 로마자 입력")
        print("3. 로마자 보고 히라가나 선택")
        print("4. 히라가나-가타카나 매칭")
        print("5. 조사 뜻 맞히기")
        print("6. 예문 로마자 입력")
        print("7. 오답 복습")
        print("8. 오답 기록 보기")
        print("9. 학습 기록 보기")
        print("10. 일본어.md 참고 자료 보기")
        print("0. 종료")
        choice = input("> ").strip()

        if choice == "1":
            run_romaji_quiz("히라가나 연습", get_kana("hiragana"), store, history_store=history_store)
        elif choice == "2":
            run_romaji_quiz("가타카나 연습", get_kana("katakana"), store, history_store=history_store)
        elif choice == "3":
            run_choice_quiz("히라가나 4지선다", get_kana("hiragana"), store, history_store=history_store)
        elif choice == "4":
            run_matching_quiz(store, history_store=history_store)
        elif choice == "5":
            run_particle_meaning_quiz(history_store=history_store)
        elif choice == "6":
            run_example_romaji_quiz(store, history_store=history_store)
        elif choice == "7":
            run_wrong_answer_review(store, history_store=history_store)
        elif choice == "8":
            print_wrong_answer_summary(store)
        elif choice == "9":
            print_study_history_summary(history_store)
        elif choice == "10":
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
