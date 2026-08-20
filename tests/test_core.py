import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core import config as config_module
from app.core.config import Config
from app.core.utils import format_duration, format_filesize


class UtilityTests(unittest.TestCase):
    def test_format_duration(self):
        self.assertEqual(format_duration(65), "1:05")
        self.assertEqual(format_duration(3661), "1:01:01")

    def test_format_filesize(self):
        self.assertEqual(format_filesize(0), "0 B")
        self.assertEqual(format_filesize(1024), "1.0 KB")


class ConfigTests(unittest.TestCase):
    def test_config_loads_and_saves_to_configured_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({"last_mode": "MP3"}), encoding="utf-8")
            with patch.object(config_module, "CONFIG_FILE", path):
                Config._instance = None
                config = Config()
                self.assertEqual(config.get("last_mode"), "MP3")
                config.set("theme", "Light")
                saved = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(saved["theme"], "Light")
        Config._instance = None


if __name__ == "__main__":
    unittest.main()
