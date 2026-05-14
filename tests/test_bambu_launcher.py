import unittest
from pathlib import Path

from lib.services import bambu_launcher


class BambuLauncherTests(unittest.TestCase):
    def test_build_launch_args_contains_model_path(self):
        model = Path(r"C:\temp\demo.3mf")
        self.assertEqual(bambu_launcher.build_launch_args(model), [str(model)])
