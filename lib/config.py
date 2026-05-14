"""Project-wide constants for FusionBambuBridge."""

from pathlib import Path


ADDIN_NAME = "FusionBambuBridge"
COMMAND_ID = "com_chizhi_fusionbambubridge_batch_to_bambu"
COMMAND_NAME = "Bambu Bridge"
COMMAND_DESCRIPTION = "Export selected geometry to 3MF and open it in Bambu Studio."
COMMAND_RESOURCE_FOLDER = "Resources/BambuBridge"

WORKSPACE_ID = "FusionSolidEnvironment"
PREFERRED_PANEL_IDS = [
    "MakePanel",
    "SolidScriptsAddinsPanel",
    "SolidCreatePanel",
    "ToolsTab",
]

SELECTION_INPUT_ID = "exportSelection"
PREP_TYPE_INPUT_ID = "prepType"
APP_INPUT_ID = "targetApp"
FORMAT_INPUT_ID = "exportFormat"
SELECTION_SUMMARY_INPUT_ID = "selectionSummary"
RUNTIME_DETAILS_INPUT_ID = "runtimeDetails"

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = PACKAGE_ROOT / "docs"
