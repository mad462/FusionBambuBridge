import unittest
from pathlib import Path

from lib import command_ui_state


class CommandUiStateTests(unittest.TestCase):
    def test_choose_toolbar_panel_prefers_first_matching_candidate(self):
        selected = command_ui_state.choose_toolbar_panel_id(
            available_panel_ids=["InspectPanel", "SolidCreatePanel", "SolidScriptsAddinsPanel"],
            preferred_panel_ids=["SolidScriptsAddinsPanel", "SolidCreatePanel"],
        )
        self.assertEqual(selected, "SolidScriptsAddinsPanel")

    def test_choose_toolbar_panel_falls_back_to_none_when_missing(self):
        selected = command_ui_state.choose_toolbar_panel_id(
            available_panel_ids=["InspectPanel", "RenderPanel"],
            preferred_panel_ids=["SolidScriptsAddinsPanel", "SolidCreatePanel"],
        )
        self.assertIsNone(selected)

    def test_build_selection_label_for_empty_selection(self):
        self.assertEqual(command_ui_state.build_selection_label(0), "未选择对象")

    def test_build_selection_label_for_single_selection(self):
        self.assertEqual(command_ui_state.build_selection_label(1), "1 个对象已选定")

    def test_build_selection_label_for_multiple_selections(self):
        self.assertEqual(command_ui_state.build_selection_label(3), "3 个对象已选定")

    def test_build_runtime_details_mentions_temp_dir(self):
        details = command_ui_state.build_runtime_details_html(
            bambu_path=Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe"),
            temp_dir=Path(r"C:\Temp\FusionBambuBridge"),
        )
        self.assertIn("Bambu Studio", details)
        self.assertIn(r"C:\Temp\FusionBambuBridge", details)

    def test_build_command_summary_html_includes_selection_and_format(self):
        summary = command_ui_state.build_command_summary_html(
            selection_count=1,
            format_name="3MF",
        )
        self.assertIn("1 个对象已选定", summary)
        self.assertIn("3MF", summary)
