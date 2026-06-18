# 가나 학습 로직의 핵심 동작을 검증한다.
import tempfile
import unittest
from pathlib import Path

from kana_trainer.kana import (
    get_beginner_patterns,
    get_confusing_pairs,
    get_kana,
    get_particles,
    get_reading_examples,
    get_sokuon_examples,
    pair_by_romaji,
)
from kana_trainer.quiz import (
    WrongAnswerStore,
    build_multiple_choice,
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


if __name__ == "__main__":
    unittest.main()
