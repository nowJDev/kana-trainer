# 터미널 출력 보조 함수가 입력 줄을 안정적으로 분리하는지 검증한다.
import unittest

from kana_trainer.terminal import input_prompt, should_clear_screen


class TerminalRenderingTests(unittest.TestCase):
    def test_input_prompt_keeps_answer_on_its_own_line(self):
        self.assertEqual(input_prompt("し 의 읽는 법은?"), "し 의 읽는 법은?\n> ")

    def test_clear_screen_is_only_used_for_interactive_output(self):
        self.assertTrue(should_clear_screen(is_interactive=True, no_clear=False))
        self.assertFalse(should_clear_screen(is_interactive=False, no_clear=False))
        self.assertFalse(should_clear_screen(is_interactive=True, no_clear=True))


if __name__ == "__main__":
    unittest.main()
