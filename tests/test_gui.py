# GUI 표시 폰트 선택 정책을 검증한다.
import unittest

from kana_trainer.gui import choose_display_font


class GuiFontTests(unittest.TestCase):
    def test_choose_display_font_prefers_yu_gothic_ui(self):
        available = ("MS Gothic", "Meiryo", "Yu Gothic UI")

        self.assertEqual(choose_display_font(available), "Yu Gothic UI")

    def test_choose_display_font_falls_back_to_meiryo_then_ms_gothic(self):
        self.assertEqual(choose_display_font(("MS Gothic", "Meiryo")), "Meiryo")
        self.assertEqual(choose_display_font(("Arial", "MS Gothic")), "MS Gothic")


if __name__ == "__main__":
    unittest.main()
