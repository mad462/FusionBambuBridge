"""Fusion 360 add-in entrypoint for FusionBambuBridge."""

import traceback
import sys
import importlib
from pathlib import Path


_handlers = []
_debug_log = r"C:\FUCKfusion\FusionBambuBridge\debug.log"
_addin_dir = Path(__file__).resolve().parent

if str(_addin_dir) not in sys.path:
    sys.path.insert(0, str(_addin_dir))


def _log(message):
    with open(_debug_log, "a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def _clear_local_modules():
    removable = [
        name for name in list(sys.modules)
        if name == "lib" or name.startswith("lib.")
    ]
    for name in removable:
        sys.modules.pop(name, None)
    _log(f"cleared modules: {removable}")


_log("module import start")

try:
    _log(f"addin dir: {_addin_dir}")
    _log(f"sys.path[0]: {sys.path[0] if sys.path else '<empty>'}")
    _log("module import ready")
except Exception:
    pass


def run(context):
    del context
    _log("run() entered")
    try:
        _clear_local_modules()
        from lib.commands import batch_to_bambu

        _log("batch_to_bambu imported")
        importlib.invalidate_caches()
        batch_to_bambu.start(_handlers)
        _log("run() completed")
    except Exception:
        _log("run() failed")
        _log(traceback.format_exc())
        raise


def stop(context):
    del context
    _log("stop() entered")
    try:
        from lib.commands import batch_to_bambu

        _log("batch_to_bambu imported for stop")
        batch_to_bambu.stop()
        _log("stop() completed")
    except Exception:
        _log("stop() failed")
        _log(traceback.format_exc())
        raise
