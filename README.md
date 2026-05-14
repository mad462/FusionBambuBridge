# FusionBambuBridge

[English](./README.md) | [简体中文](./README.zh-CN.md)

FusionBambuBridge is a Windows-focused Fusion 360 add-in scaffold for one specific workflow:

1. Select one or more bodies or components in Fusion.
2. Run the `Bambu Bridge` command from the Fusion toolbar.
3. Export a temporary `3MF`.
4. Open the result in Bambu Studio automatically.

The add-in is designed to feel close to Fusion's native print flow while still targeting Bambu Studio directly.

## Current Status

- Add-in manifest and entrypoint are in place.
- Toolbar command registration works in the Fusion Design workspace.
- Multi-selection export merges selected geometry into one temporary `3MF`.
- The exported file opens in Bambu Studio automatically.
- Export staging is cleaned up automatically after each run.

## Project Layout

```text
FusionBambuBridge/
  FusionBambuBridge.manifest
  FusionBambuBridge.py
  lib/
    config.py
    commands/
    services/
  docs/
  scripts/
  tests/
```

## Install In Fusion

Recommended installation flow:

1. In Fusion, open the `Scripts and Add-Ins` window with `Shift+S`.
2. Switch to the `Add-Ins` tab.
3. Click the `+` button.
4. Choose `Script or Add-In from Device`.
5. Select the `FusionBambuBridge` folder on your machine.
6. Run `FusionBambuBridge`.
7. Use the `Bambu Bridge` button from the Design workspace toolbar.

For development, you can still use [`scripts/copy-to-fusion.ps1`](./scripts/copy-to-fusion.ps1) if you prefer a manual sync workflow.

## Development Notes

- `3MF` is the default target because it is the smoothest path for multi-object slicing workflows.
- Bambu Studio discovery is isolated in one module so you can replace it later with registry lookup, a settings UI, or custom install paths.
- Multi-selection export uses a temporary Fusion component as a staging target and deletes it after export.

## References

- [docs/architecture.md](./docs/architecture.md)
- [docs/usage.md](./docs/usage.md)
- [docs/contributing.md](./docs/contributing.md)
- [docs/references.md](./docs/references.md)
