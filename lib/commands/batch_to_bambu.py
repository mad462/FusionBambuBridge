"""Custom Fusion command that exports geometry and opens Bambu Studio."""

from __future__ import annotations

import traceback

from lib import command_ui_state, config
from lib.services import bambu_launcher, export_service, settings_service

try:
    import adsk.core
    import adsk.fusion
except ImportError:  # pragma: no cover - allows local editing outside Fusion
    adsk = None


_local_handlers = []
_debug_log = r"C:\FUCKfusion\FusionBambuBridge\debug.log"


def _log(message):
    with open(_debug_log, "a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def start(shared_handlers):
    """Register the toolbar button and hook command events."""
    if adsk is None:
        _log("start() skipped because adsk is unavailable")
        return

    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        _log("start() begin")
        cmd_def = ui.commandDefinitions.itemById(config.COMMAND_ID)
        if not cmd_def:
            _log("creating command definition")
            cmd_def = ui.commandDefinitions.addButtonDefinition(
                config.COMMAND_ID,
                config.COMMAND_NAME,
                config.COMMAND_DESCRIPTION,
                config.COMMAND_RESOURCE_FOLDER,
            )
        else:
            _log("reusing existing command definition")
            try:
                cmd_def.resourceFolder = config.COMMAND_RESOURCE_FOLDER
            except Exception:
                _log("failed to refresh command resource folder")

        on_created = _CommandCreatedHandler()
        cmd_def.commandCreated.add(on_created)
        shared_handlers.append(on_created)
        _log("commandCreated handler registered")

        panel = _find_toolbar_panel(ui)
        if not panel:
            _log("no preferred toolbar panel found")
            return

        _log(f"toolbar panel selected: {panel.id}")
        control = panel.controls.itemById(config.COMMAND_ID)
        if not control:
            _log("creating toolbar control")
            control = panel.controls.addCommand(cmd_def)
            control.isPromoted = True
            control.isPromotedByDefault = True
        else:
            _log("toolbar control already exists")
        _log("start() success")
    except Exception as exc:  # pragma: no cover - depends on Fusion runtime
        _log("start() failed")
        _log(traceback.format_exc())
        ui.messageBox(
            f"FusionBambuBridge \u52a0\u8f7d\u5931\u8d25:\n{exc}\n\n{traceback.format_exc()}"
        )


def stop():
    """Remove the toolbar button and command definition."""
    if adsk is None:
        _log("stop() skipped because adsk is unavailable")
        return

    app = adsk.core.Application.get()
    ui = app.userInterface

    _log("stop() begin")
    panel = _find_toolbar_panel(ui)
    if panel:
        control = panel.controls.itemById(config.COMMAND_ID)
        if control:
            control.deleteMe()
            _log("toolbar control deleted")

    cmd_def = ui.commandDefinitions.itemById(config.COMMAND_ID)
    if cmd_def:
        cmd_def.deleteMe()
        _log("command definition deleted")
    _log("stop() success")


def _find_toolbar_panel(ui):
    available_ids = [ui.allToolbarPanels.item(index).id for index in range(ui.allToolbarPanels.count)]
    _log(f"available panels: {available_ids}")
    panel_id = command_ui_state.choose_toolbar_panel_id(
        available_panel_ids=available_ids,
        preferred_panel_ids=config.PREFERRED_PANEL_IDS,
    )
    if not panel_id:
        return None
    return ui.allToolbarPanels.itemById(panel_id)


def _get_command_inputs_from_event(event_args):
    sender = event_args.firingEvent.sender
    return sender.commandInputs if sender else None


def _build_selection_summary(inputs) -> None:
    if not inputs:
        return

    selection_input = adsk.core.SelectionCommandInput.cast(inputs.itemById(config.SELECTION_INPUT_ID))
    summary_input = adsk.core.TextBoxCommandInput.cast(inputs.itemById(config.SELECTION_SUMMARY_INPUT_ID))

    if not selection_input or not summary_input:
        return

    try:
        normalized_count = len(
            export_service.collect_supported_entities_from_selections(selection_input)
        )
    except Exception:
        normalized_count = selection_input.selectionCount

    summary_input.formattedText = command_ui_state.build_command_summary_html(
        selection_count=normalized_count,
    )


def _entity_debug_value(entity, attribute_name, fallback=""):
    value = getattr(entity, attribute_name, fallback)
    return "" if value is None else str(value)


def _describe_entity(entity) -> str:
    if not entity:
        return "<none>"

    parts = [
        f"type={_entity_debug_value(entity, 'objectType')}",
        f"token={_entity_debug_value(entity, 'entityToken', '-')} or tempId={_entity_debug_value(entity, 'tempId', '-')}",
    ]

    name = _entity_debug_value(entity, "name")
    if name:
        parts.append(f"name={name}")

    full_path = _entity_debug_value(entity, "fullPathName")
    if full_path:
        parts.append(f"fullPath={full_path}")

    assembly_context = getattr(entity, "assemblyContext", None)
    if assembly_context:
        parts.append(
            "assemblyContext=("
            f"{_entity_debug_value(assembly_context, 'objectType')},"
            f"{_entity_debug_value(assembly_context, 'entityToken', '-')},"
            f"{_entity_debug_value(assembly_context, 'fullPathName')}"
            ")"
        )

    parent_component = getattr(entity, "parentComponent", None)
    if parent_component:
        parts.append(
            "parentComponent=("
            f"{_entity_debug_value(parent_component, 'objectType')},"
            f"{_entity_debug_value(parent_component, 'entityToken', '-')},"
            f"{_entity_debug_value(parent_component, 'name')}"
            ")"
        )

    component = getattr(entity, "component", None)
    if component:
        parts.append(
            "component=("
            f"{_entity_debug_value(component, 'objectType')},"
            f"{_entity_debug_value(component, 'entityToken', '-')},"
            f"{_entity_debug_value(component, 'name')}"
            ")"
        )

    return "; ".join(parts)


def _log_selection_snapshot(label, selections) -> None:
    try:
        if hasattr(selections, "selectionCount") and hasattr(selections, "selection"):
            raw_entities = [selections.selection(index).entity for index in range(selections.selectionCount)]
        elif hasattr(selections, "count") and hasattr(selections, "item"):
            raw_entities = [selections.item(index).entity for index in range(selections.count)]
        else:
            raw_entities = [getattr(selection, "entity", selection) for selection in selections]
    except Exception:
        _log(f"{label}: failed to inspect raw selections")
        _log(traceback.format_exc())
        return

    _log(f"{label}: raw count={len(raw_entities)}")
    for index, entity in enumerate(raw_entities):
        _log(f"{label}: raw[{index}] {_describe_entity(entity)}")

    try:
        normalized_entities = export_service.collect_supported_entities_from_selections(selections)
    except Exception:
        _log(f"{label}: failed to normalize selections")
        _log(traceback.format_exc())
        return

    _log(f"{label}: normalized count={len(normalized_entities)}")
    for index, entity in enumerate(normalized_entities):
        _log(f"{label}: normalized[{index}] {_describe_entity(entity)}")

if adsk is not None:

    class _CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
        """Create Fusion-native command inputs and event hooks."""

        def notify(self, args):
            app = adsk.core.Application.get()
            ui = app.userInterface
            try:
                event_args = adsk.core.CommandCreatedEventArgs.cast(args)
                command = event_args.command
                inputs = command.commandInputs

                command.okButtonText = "\u53d1\u9001\u5230 Bambu"
                command.setDialogInitialSize(360, 210)

                selection_input = inputs.addSelectionInput(
                    config.SELECTION_INPUT_ID,
                    "\u5bf9\u8c61",
                    "\u9009\u62e9\u4e00\u4e2a body\u3001component \u6216 occurrence\u3002",
                )
                selection_input.addSelectionFilter("Bodies")
                selection_input.addSelectionFilter("Occurrences")
                selection_input.addSelectionFilter("RootComponents")
                selection_input.setSelectionLimits(1, 0)

                selection_summary = inputs.addTextBoxCommandInput(
                    config.SELECTION_SUMMARY_INPUT_ID,
                    "\u5f53\u524d\u9009\u62e9",
                    command_ui_state.build_command_summary_html(0),
                    2,
                    True,
                )
                selection_summary.isFullWidth = True

                _build_selection_summary(inputs)

                on_input_changed = _CommandInputChangedHandler()
                on_validate = _CommandValidateInputsHandler()
                on_execute = _CommandExecuteHandler()

                command.inputChanged.add(on_input_changed)
                command.validateInputs.add(on_validate)
                command.execute.add(on_execute)

                _local_handlers.extend([on_input_changed, on_validate, on_execute])
            except Exception as exc:
                _log("commandCreated notify failed")
                _log(traceback.format_exc())
                ui.messageBox(
                    f"FusionBambuBridge \u521b\u5efa\u547d\u4ee4\u5931\u8d25:\n{exc}\n\n{traceback.format_exc()}"
                )

    class _CommandInputChangedHandler(adsk.core.InputChangedEventHandler):
        """Refresh summary text when the selection changes."""

        def notify(self, args):
            try:
                event_args = adsk.core.InputChangedEventArgs.cast(args)
                inputs = event_args.inputs or _get_command_inputs_from_event(event_args)
                changed_input = event_args.input
                if changed_input and getattr(changed_input, "id", "") == config.SELECTION_INPUT_ID:
                    selection_input = adsk.core.SelectionCommandInput.cast(changed_input)
                    _log_selection_snapshot("inputChanged.selection", selection_input)
                _build_selection_summary(inputs)
            except Exception:
                _log("inputChanged notify failed")
                _log(traceback.format_exc())


    class _CommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
        """Require at least one selection before enabling OK."""

        def notify(self, args):
            try:
                event_args = adsk.core.ValidateInputsEventArgs.cast(args)
                inputs = _get_command_inputs_from_event(event_args)
                selection_input = adsk.core.SelectionCommandInput.cast(
                    inputs.itemById(config.SELECTION_INPUT_ID) if inputs else None
                )
                normalized_count = 0
                if selection_input:
                    normalized_count = len(
                        export_service.collect_supported_entities_from_selections(selection_input)
                    )
                event_args.areInputsValid = normalized_count > 0
            except Exception:
                _log("validateInputs notify failed")
                _log(traceback.format_exc())
                event_args = adsk.core.ValidateInputsEventArgs.cast(args)
                event_args.areInputsValid = False


    class _CommandExecuteHandler(adsk.core.CommandEventHandler):
        """Perform the export flow when the user confirms the command dialog."""

        def notify(self, args):
            event_args = adsk.core.CommandEventArgs.cast(args)
            app = adsk.core.Application.get()
            ui = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            if not design:
                ui.messageBox("FusionBambuBridge \u9700\u8981\u5728 Design \u5de5\u4f5c\u533a\u4e2d\u8fd0\u884c\u3002")
                return

            try:
                settings = settings_service.load_settings()
                inputs = event_args.command.commandInputs
                selection_input = adsk.core.SelectionCommandInput.cast(
                    inputs.itemById(config.SELECTION_INPUT_ID)
                )
                _log_selection_snapshot("execute.selection", selection_input)
                selection = export_service.collect_supported_entities_from_selections(selection_input)
                _log(f"execute selection count: {len(selection)}")
                if not selection:
                    raise ValueError(
                        "\u8bf7\u81f3\u5c11\u9009\u62e9\u4e00\u4e2a body\u3001component \u6216 occurrence\u3002"
                    )

                _log("calling export_selection_to_3mf")
                export_path = export_service.export_selection_to_3mf(
                    design=design,
                    selection=selection,
                    temp_dir=settings.temp_dir,
                )
                _log(f"export complete: {export_path}")
                bambu_path = _resolve_bambu_with_prompt(ui, settings.bambu_studio_path)
                _log(f"resolved bambu path: {bambu_path}")
                bambu_launcher.launch_bambu(bambu_path, export_path)
            except Exception as exc:  # pragma: no cover - depends on Fusion runtime
                _log("execute failed")
                _log(traceback.format_exc())
                details = traceback.format_exc()
                ui.messageBox(f"FusionBambuBridge \u8fd0\u884c\u5931\u8d25:\n{exc}\n\n{details}")
else:

    class _CommandCreatedHandler:  # pragma: no cover - local editing fallback
        pass


    class _CommandInputChangedHandler:  # pragma: no cover - local editing fallback
        pass


    class _CommandValidateInputsHandler:  # pragma: no cover - local editing fallback
        pass


    class _CommandExecuteHandler:  # pragma: no cover - local editing fallback
        pass


def _resolve_bambu_with_prompt(ui, configured_path):
    try:
        return bambu_launcher.resolve_executable(configured_path)
    except FileNotFoundError:
        _log("bambu executable not found via auto-detect; prompting user")

    if adsk is None:
        raise FileNotFoundError("Could not locate Bambu Studio.")

    file_dialog = ui.createFileDialog()
    file_dialog.title = "\u9009\u62e9 Bambu Studio \u53ef\u6267\u884c\u6587\u4ef6"
    file_dialog.filter = "Executable (*.exe)|*.exe"
    file_dialog.initialFilename = "bambu-studio.exe"

    if file_dialog.showOpen() != adsk.core.DialogResults.DialogOK:
        raise FileNotFoundError(
            "Could not locate Bambu Studio automatically, and no executable was selected."
        )

    selected_path = file_dialog.filename
    if not selected_path:
        raise FileNotFoundError("No Bambu Studio executable was selected.")

    return bambu_launcher.resolve_executable(settings_service.path_from_string(selected_path))
