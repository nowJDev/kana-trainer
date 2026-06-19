# 패키징 리소스 경로 계산을 검증한다.
import sys
import tempfile
import unittest
from pathlib import Path

from kana_trainer.resources import resource_path


class ResourcePathTests(unittest.TestCase):
    def test_resource_path_uses_project_root_during_normal_execution(self):
        self.assertEqual(resource_path("일본어.md"), Path(__file__).resolve().parents[1] / "일본어.md")

    def test_resource_path_uses_pyinstaller_temp_root_when_available(self):
        original = getattr(sys, "_MEIPASS", None)
        had_attribute = hasattr(sys, "_MEIPASS")
        with tempfile.TemporaryDirectory() as temp_dir:
            sys._MEIPASS = temp_dir
            try:
                self.assertEqual(resource_path("일본어.md"), Path(temp_dir) / "일본어.md")
            finally:
                if had_attribute:
                    sys._MEIPASS = original
                else:
                    del sys._MEIPASS


if __name__ == "__main__":
    unittest.main()
