import sys
from pathlib import Path
import unittest

APP_DIR = Path(__file__).resolve().parents[2] / "app"
sys.path.insert(0, str(APP_DIR))

from app import validate_title, validate_status


class TaskValidationTests(unittest.TestCase):
    def test_title_is_trimmed(self):
        self.assertEqual(validate_title("  Docker 作業  "), "Docker 作業")

    def test_empty_title_is_rejected(self):
        self.assertIsNone(validate_title("   "))
        self.assertIsNone(validate_title(None))

    def test_valid_status_values(self):
        self.assertEqual(validate_status("pending"), "pending")
        self.assertEqual(validate_status("done"), "done")

    def test_invalid_status_is_rejected(self):
        self.assertIsNone(validate_status("finished"))
        self.assertIsNone(validate_status(None))


if __name__ == "__main__":
    unittest.main()
