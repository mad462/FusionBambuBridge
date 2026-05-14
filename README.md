# FusionBambuBridge

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

Fusion add-ins on Windows live under:

```text
%APPDATA%\Autodesk\Autodesk Fusion\API\AddIns
```

Two options:

- Copy the `FusionBambuBridge` folder into your Fusion add-ins directory.
- Use [`scripts/copy-to-fusion.ps1`](./scripts/copy-to-fusion.ps1) to refresh the installed copy during development.

After the files are in place:

1. Open `Utilities -> Add-Ins -> Scripts and Add-Ins` in Fusion.
2. Switch to the `Add-Ins` tab.
3. Add the folder if needed, then run `FusionBambuBridge`.
4. Use the `Bambu Bridge` button from the Design workspace toolbar.

## Development Notes

- `3MF` is the default target because it is the smoothest path for multi-object slicing workflows.
- Bambu Studio discovery is isolated in one module so you can replace it later with registry lookup, a settings UI, or custom install paths.
- Multi-selection export uses a temporary Fusion component as a staging target and deletes it after export.

## Next Recommended Milestones

1. Add a small Fusion command dialog for path overrides and export mode.
2. Add user-editable settings storage for Bambu Studio path and temp export path.
3. Add more Fusion-side integration checks around unusual selection cases.
4. Polish the command UX to feel even closer to Fusion's native print workflow.

## References

- [docs/architecture.md](./docs/architecture.md)
- [docs/usage.md](./docs/usage.md)
- [docs/contributing.md](./docs/contributing.md)
- [docs/references.md](./docs/references.md)
