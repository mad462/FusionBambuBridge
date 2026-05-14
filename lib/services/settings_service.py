"""Settings access for the local development scaffold."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BridgeSettings:
    """Runtime settings used by the add-in."""

    bambu_studio_path: Path | None
    temp_dir: Path
    keep_exports: bool = True


def load_settings() -> BridgeSettings:
    """Load settings from environment defaults for the scaffold version."""
    configured_path = os.environ.get("BAMBU_STUDIO_PATH")
    bambu_path = Path(configured_path) if configured_path else None
    temp_dir = Path(tempfile.gettempdir()) / "FusionBambuBridge"
    return BridgeSettings(
        bambu_studio_path=bambu_path,
        temp_dir=temp_dir,
    )
