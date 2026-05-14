"""Windows launcher helpers for opening Bambu Studio."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


COMMON_PATHS = (
    Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe"),
    Path(r"C:\Program Files\Bambu Studio\BambuStudio.exe"),
    Path(r"C:\Program Files\Bambu Studio\orcaslicer.exe"),
    Path(r"C:\Program Files\Bambu Studio\OrcaSlicer.exe"),
)


def build_launch_args(model_path: Path) -> list[str]:
    """Build the arguments that Bambu Studio should receive."""
    return [str(model_path)]


def resolve_executable(configured_path: Path | None = None) -> Path:
    """Find the Bambu Studio executable, preferring explicit configuration."""
    candidates = []
    env_path = os.environ.get("BAMBU_STUDIO_PATH")

    if configured_path:
        candidates.append(configured_path)
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(COMMON_PATHS)

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    searched = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(
        "Could not locate Bambu Studio. Set BAMBU_STUDIO_PATH or update the candidate list.\n"
        f"Searched:\n{searched}"
    )


def launch_bambu(executable: Path, model_path: Path) -> list[str]:
    """Start Bambu Studio with the exported file and return the command line."""
    command = [str(executable), *build_launch_args(model_path)]
    subprocess.Popen(command)  # noqa: S603,S607 - local desktop app launch by design
    return command
