import unittest
import os
from pathlib import Path

from lib.services import settings_service


class SettingsServiceTests(unittest.TestCase):
    def test_load_settings_uses_temp_directory_name(self):
        settings = settings_service.load_settings()
        self.assertEqual(settings.temp_dir.name, "FusionBambuBridge")
        self.assertIsInstance(settings.temp_dir, Path)

    def test_path_from_string_returns_none_for_empty_value(self):
        self.assertIsNone(settings_service.path_from_string(None))
        self.assertIsNone(settings_service.path_from_string(""))

    def test_load_settings_reads_bambu_path_from_env(self):
        original_value = os.environ.get("BAMBU_STUDIO_PATH")
        os.environ["BAMBU_STUDIO_PATH"] = r"C:\Program Files\Bambu Studio\bambu-studio.exe"
        try:
            settings = settings_service.load_settings()
        finally:
            if original_value is None:
                os.environ.pop("BAMBU_STUDIO_PATH", None)
            else:
                os.environ["BAMBU_STUDIO_PATH"] = original_value

        self.assertEqual(
            settings.bambu_studio_path,
            Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe"),
        )
