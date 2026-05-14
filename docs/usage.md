# Usage

## What The Scaffold Does Today

The command registers in Fusion and attempts this flow:

1. Read the current selection.
2. Validate that the selected entities are bodies, components, or occurrences.
3. Normalize and deduplicate the selection.
4. Build a temporary export target when multiple objects are selected.
5. Export a temporary `3MF` with a fixed format.
6. Launch Bambu Studio with that file path.

## What It Does Not Do Yet

- Extend the built-in Fusion `3D Print` dialog directly.

## Quick Start

1. In Fusion, press `Shift+S` to open `Scripts and Add-Ins`.
2. Switch to the `Add-Ins` tab.
3. Click `+` and choose `Script or Add-In from Device`.
4. Select the `FusionBambuBridge` folder.
5. Run the add-in.
6. In the Design workspace, look for `Bambu Bridge` in the toolbar.
7. Select one or more supported objects and click the command.

## Temporary Files

The current scaffold writes to:

```text
%TEMP%\FusionBambuBridge
```

Keeping that path simple makes debugging easier. Export staging inside Fusion is cleaned up automatically after export.
