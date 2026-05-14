import unittest
from types import SimpleNamespace
from pathlib import Path

from lib.services import export_service


class ExportServiceLogicTests(unittest.TestCase):
    def test_collect_supported_entities_from_selection_input_shape(self):
        original_adsk = export_service.adsk
        fake_body_type = "fake-body"
        body = SimpleNamespace(objectType=fake_body_type, entityToken="body-1")
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: fake_body_type),
                Component=SimpleNamespace(classType=lambda: "fake-component"),
                Occurrence=SimpleNamespace(classType=lambda: "fake-occurrence"),
            )
        )

        class FakeSelectionInput:
            selectionCount = 1

            def selection(self, index):
                self.last_index = index
                return SimpleNamespace(entity=body)

        try:
            result = export_service.collect_supported_entities_from_selections(FakeSelectionInput())
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(result), 1)

    def test_collect_supported_entities_deduplicates_repeated_tokens(self):
        original_adsk = export_service.adsk
        fake_body_type = "fake-body"
        repeated_body = SimpleNamespace(objectType=fake_body_type, entityToken="body-1")
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: fake_body_type),
                Component=SimpleNamespace(classType=lambda: "fake-component"),
                Occurrence=SimpleNamespace(classType=lambda: "fake-occurrence"),
            )
        )

        class FakeSelectionInput:
            selectionCount = 2

            def selection(self, index):
                return SimpleNamespace(entity=repeated_body)

        try:
            result = export_service.collect_supported_entities_from_selections(FakeSelectionInput())
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(result), 1)

    def test_collect_supported_entities_prefers_object_identity_without_entity_token(self):
        original_adsk = export_service.adsk
        fake_body_type = "fake-body"
        repeated_body = SimpleNamespace(objectType=fake_body_type)
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: fake_body_type),
                Component=SimpleNamespace(classType=lambda: "fake-component"),
                Occurrence=SimpleNamespace(classType=lambda: "fake-occurrence"),
            )
        )

        class FakeSelectionInput:
            selectionCount = 2

            def selection(self, index):
                return SimpleNamespace(entity=repeated_body)

        try:
            result = export_service.collect_supported_entities_from_selections(FakeSelectionInput())
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(result), 1)

    def test_collect_supported_entities_collapses_bodies_from_same_occurrence(self):
        original_adsk = export_service.adsk
        body_type = "fake-body"
        occurrence_type = "fake-occurrence"
        shared_occurrence = SimpleNamespace(objectType=occurrence_type, entityToken="occ-1")
        body_a = SimpleNamespace(objectType=body_type, assemblyContext=shared_occurrence)
        body_b = SimpleNamespace(objectType=body_type, assemblyContext=shared_occurrence)
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: body_type),
                Component=SimpleNamespace(classType=lambda: "fake-component"),
                Occurrence=SimpleNamespace(classType=lambda: occurrence_type),
            )
        )

        class FakeSelectionInput:
            selectionCount = 2

            def selection(self, index):
                return SimpleNamespace(entity=[body_a, body_b][index])

        try:
            result = export_service.collect_supported_entities_from_selections(FakeSelectionInput())
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], shared_occurrence)

    def test_collect_supported_entities_collapses_bodies_from_same_non_root_component(self):
        original_adsk = export_service.adsk
        body_type = "fake-body"
        component_type = "fake-component"
        occurrence_type = "fake-occurrence"
        shared_occurrence = SimpleNamespace(objectType=occurrence_type, entityToken="occ-1")

        class FakeOccurrenceList:
            count = 1

            def item(self, index):
                return shared_occurrence

        shared_component = SimpleNamespace(
            objectType=component_type,
            entityToken="comp-1",
            parentDesign=SimpleNamespace(
                rootComponent=SimpleNamespace(
                    allOccurrencesByComponent=lambda component: FakeOccurrenceList()
                )
            ),
        )
        body_a = SimpleNamespace(objectType=body_type, parentComponent=shared_component)
        body_b = SimpleNamespace(objectType=body_type, parentComponent=shared_component)
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: body_type),
                Component=SimpleNamespace(classType=lambda: component_type),
                Occurrence=SimpleNamespace(classType=lambda: occurrence_type),
            )
        )

        class FakeSelectionInput:
            selectionCount = 2

            def selection(self, index):
                return SimpleNamespace(entity=[body_a, body_b][index])

        try:
            result = export_service.collect_supported_entities_from_selections(FakeSelectionInput())
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], shared_occurrence)

    def test_collect_supported_entities_collapses_single_instance_component_to_occurrence(self):
        original_adsk = export_service.adsk
        component_type = "fake-component"
        occurrence_type = "fake-occurrence"
        shared_occurrence = SimpleNamespace(objectType=occurrence_type, entityToken="occ-1")

        class FakeOccurrenceList:
            count = 1

            def item(self, index):
                return shared_occurrence

        shared_component = SimpleNamespace(
            objectType=component_type,
            entityToken="comp-1",
            parentDesign=SimpleNamespace(
                rootComponent=SimpleNamespace(
                    allOccurrencesByComponent=lambda component: FakeOccurrenceList()
                )
            ),
        )
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: "fake-body"),
                Component=SimpleNamespace(classType=lambda: component_type),
                Occurrence=SimpleNamespace(classType=lambda: occurrence_type),
            )
        )

        class FakeSelectionInput:
            selectionCount = 2

            def selection(self, index):
                return SimpleNamespace(entity=[shared_component, shared_occurrence][index])

        try:
            result = export_service.collect_supported_entities_from_selections(FakeSelectionInput())
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(result), 1)
        self.assertIs(result[0], shared_occurrence)

    def test_build_export_plan_expands_component_to_all_occurrences(self):
        original_adsk = export_service.adsk
        body_type = "fake-body"
        component_type = "fake-component"
        occurrence_type = "fake-occurrence"
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: body_type),
                Component=SimpleNamespace(classType=lambda: component_type),
                Occurrence=SimpleNamespace(classType=lambda: occurrence_type),
            )
        )

        target_component = SimpleNamespace(objectType=component_type, name="Widget")
        occ_a = SimpleNamespace(objectType=occurrence_type, name="Widget:1")
        occ_b = SimpleNamespace(objectType=occurrence_type, name="Widget:2")

        class FakeOccurrenceList:
            count = 2

            def item(self, index):
                return [occ_a, occ_b][index]

        root_component = SimpleNamespace(
            objectType=component_type,
            name="Root",
            allOccurrencesByComponent=lambda component: FakeOccurrenceList(),
        )

        try:
            plan = export_service.build_export_plan([target_component], root_component)
        finally:
            export_service.adsk = original_adsk

        self.assertEqual([item["kind"] for item in plan], ["occurrence", "occurrence"])
        self.assertEqual([item["occurrence"].name for item in plan], ["Widget:1", "Widget:2"])

    def test_build_export_plan_keeps_root_component_direct(self):
        original_adsk = export_service.adsk
        component_type = "fake-component"
        export_service.adsk = SimpleNamespace(
            fusion=SimpleNamespace(
                BRepBody=SimpleNamespace(classType=lambda: "fake-body"),
                Component=SimpleNamespace(classType=lambda: component_type),
                Occurrence=SimpleNamespace(classType=lambda: "fake-occurrence"),
            )
        )

        root_component = SimpleNamespace(
            objectType=component_type,
            name="Root",
            allOccurrencesByComponent=lambda component: None,
        )

        try:
            plan = export_service.build_export_plan([root_component], root_component)
        finally:
            export_service.adsk = original_adsk

        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["kind"], "component")
        self.assertIs(plan[0]["component"], root_component)

    def test_export_selection_to_3mf_unpacks_staging_target_before_export(self):
        original_prepare = export_service._prepare_export_target
        staging_component = object()

        class FakeOccurrence:
            def __init__(self):
                self.deleted = False

            def deleteMe(self):
                self.deleted = True

        staging_occurrence = FakeOccurrence()

        class FakeExportManager:
            def __init__(self):
                self.calls = []

            def createC3MFExportOptions(self, target, filename):
                self.calls.append((target, filename))
                if isinstance(target, tuple):
                    raise AssertionError("tuple target should be unpacked before export")
                return "options"

            def execute(self, options):
                self.executed = options
                return True

        design = SimpleNamespace(
            exportManager=FakeExportManager(),
            rootComponent=SimpleNamespace(occurrences=SimpleNamespace(count=0)),
        )

        try:
            export_service._prepare_export_target = lambda design_arg, selection_arg: (
                staging_component,
                staging_occurrence,
            )
            result = export_service.export_selection_to_3mf(
                design=design,
                selection=["a", "b"],
                temp_dir=Path(r"C:\Temp\FusionBambuBridge"),
            )
        finally:
            export_service._prepare_export_target = original_prepare

        self.assertTrue(result.name.endswith(".3mf"))
        self.assertEqual(design.exportManager.calls[0][0], staging_component)
        self.assertTrue(staging_occurrence.deleted)

    def test_cleanup_stale_staging_occurrences_removes_named_occurrences(self):
        class FakeOccurrence:
            def __init__(self, occurrence_name, component_name):
                self.name = occurrence_name
                self.component = SimpleNamespace(name=component_name)
                self.deleted = False

            def deleteMe(self):
                self.deleted = True

        stale_by_occurrence = FakeOccurrence(export_service.STAGING_COMPONENT_NAME, "Other")
        stale_by_component = FakeOccurrence("Other", export_service.STAGING_COMPONENT_NAME)
        regular = FakeOccurrence("Widget:1", "Widget")

        class FakeOccurrences:
            count = 3

            def item(self, index):
                return [stale_by_occurrence, stale_by_component, regular][index]

        root_component = SimpleNamespace(occurrences=FakeOccurrences())

        export_service._cleanup_stale_staging_occurrences(root_component)

        self.assertTrue(stale_by_occurrence.deleted)
        self.assertTrue(stale_by_component.deleted)
        self.assertFalse(regular.deleted)
