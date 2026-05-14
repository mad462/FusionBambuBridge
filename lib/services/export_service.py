"""Fusion export helpers for the Batch To Bambu command."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

try:
    import adsk.core
    import adsk.fusion
except ImportError:  # pragma: no cover - allows local editing outside Fusion
    adsk = None


STAGING_COMPONENT_NAME = "FusionBambuBridge Export"


def collect_export_targets(ui):
    """Return supported selections from the current Fusion UI state."""
    if adsk is None:
        raise RuntimeError("Fusion API modules are not available outside Fusion.")

    selection_set = ui.activeSelections
    targets = []
    for index in range(selection_set.count):
        entity = selection_set.item(index).entity
        if _is_supported_geometry(entity):
            targets.append(entity)

    if not targets:
        raise ValueError("Select at least one body, component, or occurrence before running the command.")

    return targets


def collect_supported_entities_from_selections(selections) -> list:
    """Return supported entities from a Fusion selection collection or list."""
    if adsk is None:
        raise RuntimeError("Fusion API modules are not available outside Fusion.")

    targets = []
    seen_keys = set()
    if hasattr(selections, "selectionCount") and hasattr(selections, "selection"):
        for index in range(selections.selectionCount):
            entity = _normalize_selection_entity(selections.selection(index).entity)
            if _is_supported_geometry(entity) and _mark_entity_once(entity, seen_keys):
                targets.append(entity)
        return targets

    if hasattr(selections, "count") and hasattr(selections, "item"):
        for index in range(selections.count):
            entity = _normalize_selection_entity(selections.item(index).entity)
            if _is_supported_geometry(entity) and _mark_entity_once(entity, seen_keys):
                targets.append(entity)
        return targets

    for selection in selections:
        entity = _normalize_selection_entity(getattr(selection, "entity", selection))
        if _is_supported_geometry(entity) and _mark_entity_once(entity, seen_keys):
            targets.append(entity)
    return targets


def export_selection_to_3mf(design, selection, temp_dir: Path) -> Path:
    """Export the current selection to a temporary 3MF file.
    """
    export_dir = Path(temp_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    filename = export_dir / _build_export_name()
    export_manager = design.exportManager
    _cleanup_stale_staging_occurrences(design.rootComponent)
    export_target = _prepare_export_target(design, selection)
    staging_occurrence = None
    if isinstance(export_target, tuple):
        export_target, staging_occurrence = export_target

    options = export_manager.createC3MFExportOptions(export_target, str(filename))
    if not options:
        raise RuntimeError("Fusion did not create 3MF export options.")

    try:
        success = export_manager.execute(options)
        if not success:
            raise RuntimeError("Fusion failed to export the temporary 3MF file.")
    finally:
        if staging_occurrence:
            staging_occurrence.deleteMe()

    return filename


def build_export_plan(selection, root_component) -> list:
    """Normalize the user selection into exportable component or occurrence steps."""
    plan = []
    for entity in selection:
        if _is_brep_body(entity):
            plan.append({"kind": "body", "body": entity})
        elif _is_occurrence(entity):
            plan.append({"kind": "occurrence", "occurrence": entity})
        elif _is_component(entity):
            if entity == root_component:
                plan.append({"kind": "component", "component": entity})
                continue

            occurrences = root_component.allOccurrencesByComponent(entity)
            if not occurrences or occurrences.count == 0:
                plan.append({"kind": "component", "component": entity})
                continue

            for index in range(occurrences.count):
                plan.append({"kind": "occurrence", "occurrence": occurrences.item(index)})
        else:
            raise TypeError(f"Unsupported export entity: {entity}")
    return plan


def _prepare_export_target(design, selection):
    if len(selection) == 1 and _is_direct_export_supported(selection[0]):
        return selection[0]

    root_component = design.rootComponent
    plan = build_export_plan(selection, root_component)
    if len(plan) == 1 and plan[0]["kind"] == "component":
        return plan[0]["component"]

    return _build_staging_component(root_component, plan)


def _build_staging_component(root_component, plan):
    transform = adsk.core.Matrix3D.create()
    staging_occurrence = root_component.occurrences.addNewComponent(transform)
    staging_component = staging_occurrence.component
    staging_component.name = STAGING_COMPONENT_NAME

    for item in plan:
        if item["kind"] == "occurrence":
            staging_component.occurrences.addExistingComponent(
                item["occurrence"].component,
                item["occurrence"].transform2,
            )
        elif item["kind"] == "component":
            staging_component.occurrences.addExistingComponent(
                item["component"],
                adsk.core.Matrix3D.create(),
            )
        elif item["kind"] == "body":
            item["body"].copyToComponent(staging_occurrence)
        else:
            raise TypeError(f"Unsupported staging plan item: {item['kind']}")

    return staging_component, staging_occurrence


def _cleanup_stale_staging_occurrences(root_component):
    occurrences = getattr(root_component, "occurrences", None)
    if not occurrences:
        return

    stale_occurrences = []
    count = getattr(occurrences, "count", 0)
    for index in range(count):
        occurrence = occurrences.item(index)
        component = getattr(occurrence, "component", None)
        occurrence_name = getattr(occurrence, "name", "")
        component_name = getattr(component, "name", "")
        if (
            component_name == STAGING_COMPONENT_NAME
            or occurrence_name == STAGING_COMPONENT_NAME
            or str(occurrence_name).startswith(f"{STAGING_COMPONENT_NAME}:")
        ):
            stale_occurrences.append(occurrence)

    for occurrence in stale_occurrences:
        occurrence.deleteMe()


def _build_export_name() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"fusionbambubridge-{timestamp}.3mf"


def _mark_entity_once(entity, seen_keys: set) -> bool:
    key = getattr(entity, "entityToken", None)
    if not key:
        key = getattr(entity, "tempId", None)
    if not key:
        key = str(id(entity))
    if key in seen_keys:
        return False
    seen_keys.add(key)
    return True


def _normalize_selection_entity(entity):
    if _is_brep_body(entity):
        assembly_context = getattr(entity, "assemblyContext", None)
        if assembly_context:
            return assembly_context
        parent_component = getattr(entity, "parentComponent", None)
        if parent_component:
            single_occurrence = _single_root_occurrence_for_component(parent_component)
            if single_occurrence:
                return single_occurrence
            parent_design = getattr(parent_component, "parentDesign", None)
            root_component = getattr(parent_design, "rootComponent", None)
            if root_component and parent_component != root_component:
                return parent_component
    if _is_component(entity):
        single_occurrence = _single_root_occurrence_for_component(entity)
        if single_occurrence:
            return single_occurrence
    return entity


def _single_root_occurrence_for_component(component):
    parent_design = getattr(component, "parentDesign", None)
    root_component = getattr(parent_design, "rootComponent", None)
    if not root_component or component == root_component:
        return None

    all_occurrences = getattr(root_component, "allOccurrencesByComponent", None)
    if not all_occurrences:
        return None

    try:
        occurrences = all_occurrences(component)
    except Exception:
        return None

    if not occurrences or getattr(occurrences, "count", 0) != 1:
        return None

    return occurrences.item(0)


def _is_direct_export_supported(entity) -> bool:
    return _is_brep_body(entity) or _is_component(entity) or _is_occurrence(entity)


def _is_brep_body(entity) -> bool:
    return entity.objectType == adsk.fusion.BRepBody.classType()


def _is_component(entity) -> bool:
    return entity.objectType == adsk.fusion.Component.classType()


def _is_occurrence(entity) -> bool:
    return entity.objectType == adsk.fusion.Occurrence.classType()


def _is_supported_geometry(entity) -> bool:
    return _is_direct_export_supported(entity)
