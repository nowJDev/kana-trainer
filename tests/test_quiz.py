# 가나 학습 로직의 핵심 동작을 검증한다.
import tempfile
import unittest
from pathlib import Path

from kana_trainer.cli import KANA_QUESTION_COUNT
from kana_trainer.kana import (
    get_kana_level_label,
    get_beginner_patterns,
    get_confusing_pairs,
    get_kana,
    get_particles,
    get_reading_examples,
    get_sokuon_examples,
    pair_by_romaji,
)
from kana_trainer.quiz import (
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
    collect_example_items,
    collect_confusing_items,
    find_entry_by_romaji,
    is_correct_romaji,
)


class KanaDataTests(unittest.TestCase):
    def test_get_kana_returns_basic_hiragana_and_katakana(self):
        hiragana = get_kana("hiragana")
        katakana = get_kana("katakana")

        self.assertIn(("あ", "a"), hiragana)
        self.assertIn(("し", "shi"), hiragana)
        self.assertIn(("ア", "a"), katakana)
        self.assertIn(("ツ", "tsu"), katakana)

    def test_get_kana_includes_japanese_markdown_extended_kana(self):
        hiragana = get_kana("hiragana")
        katakana = get_kana("katakana")

        self.assertIn(("が", "ga"), hiragana)
        self.assertIn(("ぱ", "pa"), hiragana)
        self.assertIn(("きゃ", "kya"), hiragana)
        self.assertIn(("ガ", "ga"), katakana)
        self.assertIn(("パ", "pa"), katakana)
        self.assertIn(("キャ", "kya"), katakana)

    def test_get_kana_level_filters_basic_marks_and_yoon(self):
        self.assertIn(("か", "ka"), get_kana("hiragana", level=1))
        self.assertNotIn(("が", "ga"), get_kana("hiragana", level=1))
        self.assertNotIn(("きゃ", "kya"), get_kana("hiragana", level=1))

        self.assertIn(("が", "ga"), get_kana("hiragana", level=2))
        self.assertNotIn(("きゃ", "kya"), get_kana("hiragana", level=2))
        self.assertIn(("きゃ", "kya"), get_kana("hiragana", level=3))
        self.assertEqual(get_kana_level_label(2), "탁음·반탁음")

    def test_pair_by_romaji_matches_scripts(self):
        pairs = pair_by_romaji()

        self.assertEqual(pairs["ki"], ("き", "キ"))
        self.assertEqual(pairs["n"], ("ん", "ン"))

    def test_reference_material_from_japanese_markdown_is_available(self):
        self.assertIn(("し", "つ", "し는 왼쪽 열림 / つ는 오른쪽 열림"), get_confusing_pairs("hiragana"))
        self.assertIn(("シ", "ツ", "シ는 왼쪽 열림 / ツ는 오른쪽 열림"), get_confusing_pairs("katakana"))
        self.assertIn(("きょう", "kyou", "쿄우", "오늘/오늘날; 今日"), get_reading_examples("hiragana"))
        self.assertIn(("ガッコウ", "gakkou", "가(ㄲ)꼬우", "학교"), get_sokuon_examples("katakana"))

        particles = get_particles()
        self.assertEqual(particles[0]["particle"], "は")
        self.assertEqual(particles[0]["reading"], "wa")
        self.assertEqual(len(particles), 11)
        self.assertIn("わたしは ○○です.", get_beginner_patterns())


class QuizLogicTests(unittest.TestCase):
    def test_kana_session_question_count_is_twenty(self):
        self.assertEqual(KANA_QUESTION_COUNT, 20)

    def test_is_correct_romaji_accepts_case_and_common_aliases(self):
        self.assertTrue(is_correct_romaji("SHI", "shi"))
        self.assertTrue(is_correct_romaji("si", "shi"))
        self.assertTrue(is_correct_romaji("tu", "tsu"))
        self.assertFalse(is_correct_romaji("chi", "shi"))

    def test_build_multiple_choice_contains_answer_once(self):
        choices = build_multiple_choice("ka", get_kana("hiragana"), rng_seed=7)

        self.assertEqual(len(choices), 4)
        self.assertEqual(choices.count(("か", "ka")), 1)
        self.assertEqual(len({symbol for symbol, _romaji in choices}), 4)

    def test_build_kana_question_items_avoids_symbol_repeats(self):
        questions = build_kana_question_items(get_kana("hiragana"), count=20, rng_seed=7)

        self.assertEqual(len(questions), 20)
        self.assertEqual(len({symbol for symbol, _romaji in questions}), 20)

    def test_kana_game_state_tracks_lives_and_consumed_questions(self):
        state = KanaGameState(total=3)

        state = advance_kana_game_state(state, is_correct=True)
        self.assertEqual(state.correct, 1)
        self.assertEqual(state.answered, 1)
        self.assertEqual(state.lives, KANA_GAME_LIVES)
        self.assertFalse(state.finished)

        state = advance_kana_game_state(state, is_correct=False)
        self.assertEqual(state.correct, 1)
        self.assertEqual(state.answered, 2)
        self.assertEqual(state.lives, KANA_GAME_LIVES - 1)
        self.assertFalse(state.finished)

    def test_kana_game_state_loses_at_zero_lives(self):
        state = KanaGameState(total=10, lives=1)

        state = advance_kana_game_state(state, is_correct=False)

        self.assertTrue(state.lost)
        self.assertTrue(state.finished)
        self.assertFalse(state.won)

    def test_kana_game_state_wins_after_all_questions_with_lives_left(self):
        state = KanaGameState(total=2)

        state = advance_kana_game_state(state, is_correct=True)
        state = advance_kana_game_state(state, is_correct=True)

        self.assertTrue(state.won)
        self.assertTrue(state.finished)
        self.assertFalse(state.lost)

    def test_build_romaji_question_items_avoids_prompt_repeats(self):
        questions = build_romaji_question_items(get_kana("hiragana"), count=20, rng_seed=7)

        self.assertEqual(len(questions), 20)
        self.assertEqual(len({romaji for _symbol, romaji in questions}), 20)

    def test_build_particle_meaning_choice_contains_answer_once(self):
        choices = build_particle_meaning_choice("은/는", get_particles(), rng_seed=7)

        self.assertEqual(len(choices), 4)
        self.assertEqual(choices.count(("は", "은/는")), 1)
        self.assertEqual(len({meaning for _particle, meaning in choices}), 4)

    def test_build_particle_question_items_avoids_repeats_within_pool_size(self):
        questions = build_particle_question_items(get_particles(), count=10, rng_seed=7)

        self.assertEqual(len(questions), 10)
        self.assertEqual(len({str(item["particle"]) for item in questions}), 10)

    def test_collect_example_items_includes_reading_and_sokuon_examples(self):
        examples = collect_example_items()

        self.assertEqual(len(examples), 18)
        self.assertIn(("읽기", "히라가나", "きょう", "kyou", "쿄우", "오늘/오늘날; 今日"), examples)
        self.assertIn(("촉음", "가타카나", "ガッコウ", "gakkou", "가(ㄲ)꼬우", "학교"), examples)

    def test_build_example_question_items_avoids_repeats_within_pool_size(self):
        questions = build_example_question_items(collect_example_items(), count=10, rng_seed=7)

        self.assertEqual(len(questions), 10)
        self.assertEqual(len({item[2] for item in questions}), 10)

    def test_collect_confusing_items_builds_questions_for_both_sides(self):
        items = collect_confusing_items()

        self.assertEqual(len(items), 20)
        self.assertIn(("히라가나", "し", "shi", "つ", "tsu", "し는 왼쪽 열림 / つ는 오른쪽 열림"), items)
        self.assertIn(("가타카나", "ツ", "tsu", "シ", "shi", "シ는 왼쪽 열림 / ツ는 오른쪽 열림"), items)

    def test_build_confusing_question_items_avoids_target_repeats(self):
        questions = build_confusing_question_items(collect_confusing_items(), count=10, rng_seed=7)

        self.assertEqual(len(questions), 10)
        self.assertEqual(len({(item[0], item[1]) for item in questions}), 10)

    def test_find_entry_by_romaji_returns_expected_symbol(self):
        self.assertEqual(find_entry_by_romaji("ka", get_kana("hiragana")), ("か", "ka"))
        self.assertEqual(find_entry_by_romaji("tsu", get_kana("katakana")), ("ツ", "tsu"))

    def test_wrong_answer_store_records_and_lists_misses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "wrong.json"
            store = WrongAnswerStore(path)

            store.record("し", "shi", "si")
            store.record("ツ", "tsu", "su")
            store.record("し", "shi", "chi")

            misses = store.load()

        self.assertEqual(misses["し"]["count"], 2)
        self.assertEqual(misses["し"]["romaji"], "shi")
        self.assertEqual(misses["ツ"]["last_answer"], "su")

    def test_study_history_store_records_sessions_and_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "history.json"
            store = StudyHistoryStore(path)

            store.record_session("히라가나 연습", "romaji", correct=8, total=10, created_at="2026-06-19T09:00:00")
            store.record_session("히라가나 연습", "romaji", correct=6, total=10, created_at="2026-06-19T09:10:00")
            store.record_session("히라가나 4지선다", "choice", correct=4, total=5, created_at="2026-06-19T09:20:00")
            summary = store.summary()

        self.assertEqual(summary.total_sessions, 3)
        self.assertEqual(summary.total_correct, 18)
        self.assertEqual(summary.total_questions, 25)
        self.assertEqual(summary.accuracy, 72.0)
        self.assertEqual(summary.by_title["히라가나 연습"].correct, 14)
        self.assertEqual(summary.by_title["히라가나 연습"].questions, 20)
        self.assertEqual(summary.recent[0].title, "히라가나 4지선다")
        self.assertEqual(summary.recent[0].accuracy, 80.0)

    def test_study_history_unlocks_kana_levels_by_accuracy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = StudyHistoryStore(Path(temp_dir) / "history.json")

            self.assertEqual(store.unlocked_kana_level("hiragana"), 1)
            store.record_session("히라가나 Lv.1 기본", "romaji:hiragana:level1", correct=16, total=20)
            self.assertEqual(store.unlocked_kana_level("hiragana"), 2)
            store.record_session("히라가나 Lv.2 탁음·반탁음", "romaji:hiragana:level2", correct=15, total=20)
            self.assertEqual(store.unlocked_kana_level("hiragana"), 2)
            store.record_session("히라가나 Lv.2 탁음·반탁음", "romaji:hiragana:level2", correct=16, total=20)
            self.assertEqual(store.unlocked_kana_level("hiragana"), 3)

    def test_study_history_summary_lines_handles_empty_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = StudyHistoryStore(Path(temp_dir) / "history.json")

            lines = store.summary_lines()

        self.assertEqual(lines, ("아직 학습 기록이 없습니다.",))


if __name__ == "__main__":
    unittest.main()
