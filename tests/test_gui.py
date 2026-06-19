# GUI 표시 폰트 선택 정책을 검증한다.
import unittest

import tkinter as tk

from kana_trainer.gui import COLOR_TAGS, GLASS_THEME, KanaTrainerApp, choose_display_font, choose_ui_font_family


class GuiFontTests(unittest.TestCase):
    def make_root(self):
        try:
            return tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk 초기화 불가: {error}")

    def test_choose_display_font_prefers_nanum_gothic(self):
        available = ("MS Gothic", "Meiryo", "Yu Gothic UI", "나눔고딕")

        self.assertEqual(choose_display_font(available), "나눔고딕")

    def test_choose_display_font_falls_back_to_yu_gothic_then_meiryo(self):
        self.assertEqual(choose_display_font(("MS Gothic", "Meiryo", "Yu Gothic UI")), "Yu Gothic UI")
        self.assertEqual(choose_display_font(("MS Gothic", "Meiryo")), "Meiryo")
        self.assertEqual(choose_display_font(("Arial", "MS Gothic")), "MS Gothic")

    def test_ui_font_uses_display_font_family(self):
        self.assertEqual(choose_ui_font_family("나눔고딕"), "나눔고딕")

    def test_glass_theme_uses_dark_surfaces_and_glow_accents(self):
        self.assertEqual(GLASS_THEME["background"], "#070A0F")
        self.assertEqual(GLASS_THEME["surface"], "#111824")
        self.assertEqual(COLOR_TAGS["question"], GLASS_THEME["glow_warm"])
        self.assertEqual(COLOR_TAGS["menu"], GLASS_THEME["glow_cool"])
        self.assertEqual(COLOR_TAGS["kana"], GLASS_THEME["glow_cool"])

    def test_entry_stays_visible_with_large_font_size(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)
            root.update()
            app.text_font.configure(size=50)

            root.update_idletasks()

            self.assertTrue(app.entry.master.winfo_ismapped())
            self.assertTrue(app.entry.winfo_ismapped())
        finally:
            root.destroy()

    def test_submit_returns_focus_to_entry(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)
            calls = []
            app.handler = lambda _value: None
            app.focus_entry = lambda: calls.append("focused")
            app.entry_var.set("shi")

            app.submit_input()

            self.assertEqual(calls, ["focused"])
        finally:
            root.destroy()

    def test_semantic_color_tags_are_configured(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)

            self.assertEqual(app.output.tag_cget("question", "foreground"), GLASS_THEME["glow_warm"])
            self.assertEqual(app.output.tag_cget("input", "foreground"), GLASS_THEME["glow_input"])
            self.assertEqual(app.output.tag_cget("result", "foreground"), "#D9C2FF")
        finally:
            root.destroy()

    def test_menu_numbers_use_menu_color_tag(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)
            root.update()

            self.assertIn("menu", app.output.tag_names("3.0"))
        finally:
            root.destroy()

    def test_main_menu_buttons_are_shown(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)

            labels = [child.cget("text") for child in app.option_frame.winfo_children()]

            self.assertIn("1. 히라가나 보고 로마자 입력", labels)
            self.assertIn("0. 종료", labels)
        finally:
            root.destroy()

    def test_menu_button_uses_existing_input_handler(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)
            calls = []
            app.handler = lambda value: calls.append(value)

            app.option_frame.winfo_children()[0].invoke()

            self.assertEqual(calls, ["1"])
        finally:
            root.destroy()

    def test_free_input_quiz_clears_option_buttons(self):
        root = self.make_root()
        try:
            app = KanaTrainerApp(root)

            app.start_romaji_quiz("히라가나 연습", (("あ", "a"),))

            self.assertEqual(app.option_frame.winfo_children(), ())
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
