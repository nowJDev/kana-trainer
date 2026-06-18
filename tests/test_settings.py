# GUI 앱 설정 저장과 보정 동작을 검증한다.
import tempfile
import unittest
from pathlib import Path

from kana_trainer.settings import AppSettings, SettingsStore, clamp_font_size


class SettingsTests(unittest.TestCase):
    def test_missing_settings_file_uses_default_font_size(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SettingsStore(Path(temp_dir) / "settings.json")

            settings = store.load()

        self.assertEqual(settings.font_size, 24)

    def test_saved_font_size_can_be_loaded_again(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SettingsStore(Path(temp_dir) / "settings.json")

            store.save(AppSettings(font_size=36))
            settings = store.load()

        self.assertEqual(settings.font_size, 36)

    def test_font_size_is_clamped_to_gui_bounds(self):
        self.assertEqual(clamp_font_size(5), 12)
        self.assertEqual(clamp_font_size(50), 50)
        self.assertEqual(clamp_font_size(100), 72)


if __name__ == "__main__":
    unittest.main()
