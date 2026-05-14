import unittest
from pathlib import Path

from lib.services import settings_service


class SettingsServiceTests(unittest.TestCase):
    def test_load_settings_uses_temp_directory_name(self):
        settings = settings_service.load_settings()
        self.assertEqual(settings.temp_dir.name, "FusionBambuBridge")
        self.assertIsInstance(settings.temp_dir, Path)
