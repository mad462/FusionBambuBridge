# Architecture

## Goal

Keep Fusion-facing code thin and keep most future logic testable in plain Python.

## File Responsibilities

- `FusionBambuBridge.py`
  Fusion entrypoint. Only starts and stops command registration.
- `lib/config.py`
  Shared command ids, panel ids, and project constants.
- `lib/commands/batch_to_bambu.py`
  Fusion UI registration and button execution flow.
- `lib/services/export_service.py`
  Collects selected geometry and performs `3MF` export.
- `lib/services/bambu_launcher.py`
  Resolves the slicer executable and launches it.
- `lib/services/settings_service.py`
  Central place for config loading. Right now it uses environment defaults.

## Why This Split

This structure keeps the Autodesk-specific event model out of the service layer. That matters because:

- command registration changes for Fusion API reasons,
- export logic changes for geometry reasons,
- launcher logic changes for Windows installation reasons.

Those three change at different speeds, so they should not live in one file.

## Planned Multi-Selection Design

Multi-selection export is implemented with a temporary staging component:

1. Normalize the current selection into bodies, occurrences, or components.
2. Create a temporary component dedicated to export staging.
3. Copy selected geometry into that temporary component.
4. Export the temporary component as one `3MF`.
5. Delete the temporary component immediately after export.

The remaining work is mostly around UI polish and a few Fusion-specific edge cases in selection handling.
