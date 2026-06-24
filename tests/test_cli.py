# CLI 로마자 입력 게임 흐름을 검증한다.
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from kana_trainer.cli import run_romaji_game
from kana_trainer.quiz import StudyHistoryStore, WrongAnswerStore


class CliRomajiGameTests(unittest.TestCase):
    def test_run_romaji_game_caps_stage_to_unique_entries_and_wins(self):
        entries = (("あ", "a"), ("い", "i"))
        with tempfile.TemporaryDirectory() as temp_dir:
            store = WrongAnswerStore(Path(temp_dir) / "wrong.json")
            history_store = StudyHistoryStore(Path(temp_dir) / "history.json")
            output = io.StringIO()

            with (
                patch("kana_trainer.cli.build_kana_question_items", return_value=list(entries)),
                patch("builtins.input", side_effect=["a", "i"]),
                redirect_stdout(output),
            ):
                run_romaji_game("히라가나 Lv.1 기본", entries, store, history_store=history_store, count=20)

            summary = history_store.summary()

        self.assertIn("목표: 2문제", output.getvalue())
        self.assertIn("게임 승리", output.getvalue())
        self.assertNotIn("문제 3/", output.getvalue())
        self.assertEqual(summary.total_correct, 2)
        self.assertEqual(summary.total_questions, 2)

    def test_run_romaji_game_stops_when_lives_reach_zero(self):
        entries = (("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"))
        with tempfile.TemporaryDirectory() as temp_dir:
            store = WrongAnswerStore(Path(temp_dir) / "wrong.json")
            history_store = StudyHistoryStore(Path(temp_dir) / "history.json")
            output = io.StringIO()

            with patch("builtins.input", side_effect=["x", "x", "x"]), redirect_stdout(output):
                run_romaji_game("히라가나 Lv.1 기본", entries, store, history_store=history_store, count=4)

            misses = store.load()
            summary = history_store.summary()

        self.assertIn("게임 종료", output.getvalue())
        self.assertIn("문제 3/4", output.getvalue())
        self.assertNotIn("문제 4/4", output.getvalue())
        self.assertEqual(len(misses), 3)
        self.assertEqual(summary.total_correct, 0)
        self.assertEqual(summary.total_questions, 4)


if __name__ == "__main__":
    unittest.main()
