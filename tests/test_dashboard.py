"""Census calculation and permission-boundary tests without a Frappe site."""

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch


class DashboardTests(unittest.TestCase):
    def load(self, user="clinical-user"):
        fake = Mock()
        fake.session.user = user
        fake.PermissionError = PermissionError
        fake.whitelist = lambda **kwargs: lambda fn: fn
        fake.has_permission.return_value = True
        fake.throw.side_effect = lambda message, exc=ValueError: (_ for _ in ()).throw(exc(message))
        with patch.dict(sys.modules, {"frappe": fake}):
            sys.modules.pop("medical_prescription.dashboard", None)
            module = importlib.import_module("medical_prescription.dashboard")
        return module, fake

    def test_distinct_patients_floor_and_hidden_patient_exclusion(self):
        module, _ = self.load()
        data = module.summarize(
            [{"name": "A"}, {"name": "B"}],
            [
                {"name": "I1", "patient": "A", "status": "Admitted", "custom_floor": "1"},
                {"name": "I2", "patient": "A", "status": "Admitted", "custom_floor": "1"},
                {
                    "name": "I3",
                    "patient": "B",
                    "status": "Discharge Scheduled",
                    "custom_floor": None,
                },
                {"name": "I4", "patient": "hidden", "status": "Admitted", "custom_floor": "secret"},
            ],
            [{"patient": "A", "status": "Active"}, {"patient": "hidden", "status": "Locked"}],
        )
        self.assertEqual(data["patients"], 2)
        self.assertEqual(data["inpatients"], 2)
        self.assertEqual(data["duplicate_admissions"], 1)
        self.assertEqual(data["unassigned"], 1)
        self.assertEqual(data["scheduled_discharges"], 1)
        self.assertEqual(data["floors"][0]["patients"], 1)
        self.assertEqual(data["floors"][0]["admissions"], 2)
        self.assertEqual(data["prescription_statuses"], {"Active": 1})
        self.assertEqual(len(data["census"]), 3)

    def test_scheduled_admission_is_not_current_inpatient(self):
        module, _ = self.load()
        result = module.summarize(
            [{"name": "A"}], [{"patient": "A", "status": "Admission Scheduled"}], []
        )
        self.assertEqual(result["inpatients"], 0)
        self.assertEqual(result["scheduled_admissions"], 1)
        self.assertEqual(result["floors"], [])

    def test_empty_census_is_zero(self):
        module, _ = self.load()
        result = module.summarize([], [], [])
        self.assertEqual(result["patients"], 0)
        self.assertEqual(result["inpatients"], 0)
        self.assertEqual(result["prescription_statuses"], {})

    def test_guest_and_read_denial_do_not_query(self):
        module, fake = self.load("Guest")
        with self.assertRaises(PermissionError):
            module.census()
        fake.get_list.assert_not_called()
        fake.session.user = "clinical-user"
        fake.has_permission.return_value = False
        with self.assertRaises(PermissionError):
            module.census()
        fake.get_list.assert_not_called()

    def test_pagination_uses_permission_filtered_queries_without_truncation(self):
        module, fake = self.load()
        module.BATCH_SIZE = 2
        fake.get_list.side_effect = [[{"name": "A"}, {"name": "B"}], [{"name": "C"}]]
        self.assertEqual(len(module._rows("Patient", ["name"])), 3)
        self.assertEqual([c.kwargs["limit_start"] for c in fake.get_list.call_args_list], [0, 2])
        for call in fake.get_list.call_args_list:
            self.assertNotIn("ignore_permissions", call.kwargs)
        fake.get_all.assert_not_called()
        fake.db.sql.assert_not_called()

    def test_unpermitted_prescriptions_omitted_and_cancelled_admissions_excluded(self):
        module, fake = self.load()
        fake.has_permission.side_effect = lambda dt, perm: dt != "Medical Prescription"
        fake.get_list.side_effect = [
            [{"name": "A"}],
            [{"name": "IP", "patient": "A", "status": "Admitted"}],
        ]
        result = module.overview()
        self.assertFalse(result["prescription_access"])
        self.assertNotIn("census", result)
        self.assertEqual(fake.get_list.call_args_list[1].kwargs["filters"]["docstatus"], ["!=", 2])
        self.assertEqual(fake.get_list.call_count, 2)

    def test_reports_filter_floor_and_status(self):
        module, _ = self.load()
        with patch.object(
            module,
            "census",
            return_value={
                "census": [
                    {"patient": "A", "status": "Admitted", "custom_floor": None},
                    {"patient": "B", "status": "Discharge Scheduled", "custom_floor": "2"},
                ]
            },
        ):
            self.assertEqual(module.inpatient_report({"floor": "Unassigned"})[0]["patient"], "A")
            self.assertEqual(module.inpatient_report({"floor": "2", "status": "Admitted"}), [])


class NavigationTests(unittest.TestCase):
    def test_repeated_upgrade_preserves_existing_items_and_adds_dashboard_once(self):
        class Row(types.SimpleNamespace):
            def __getattr__(self, name):
                return None

            def as_dict(self):
                return vars(self).copy()

        class Sidebar:
            app = "medical_prescription"

            def __init__(self):
                self.items = [
                    Row(type="Link", link_type="DocType", link_to="Medical Prescription"),
                    Row(type="Link", label="Local Help", link_type="URL", url="/help"),
                ]

            def set(self, field, rows):
                self.items = [Row(**row) for row in rows]

            def save(self, **kwargs):
                pass

        sidebar = Sidebar()
        fake = Mock()
        fake.db.exists.side_effect = lambda dt, name: name != "Dosage Form"
        fake.get_meta.return_value.istable = False
        fake.db.get_value.return_value = "medical_prescription"
        icon = Mock(app="medical_prescription")
        fake.get_doc.side_effect = lambda dt, name: sidebar if dt == "Workspace Sidebar" else icon
        with patch.dict(sys.modules, {"frappe": fake}):
            sys.modules.pop("medical_prescription.navigation", None)
            module = importlib.import_module("medical_prescription.navigation")
        module.ensure_launcher()
        initial = [r.as_dict() for r in sidebar.items]
        module.ensure_launcher()
        self.assertEqual(initial, [r.as_dict() for r in sidebar.items])
        self.assertEqual(sidebar.items[0].link_to, "medical-overview")
        self.assertEqual(sidebar.items[-1].label, "Local Help")
        targets = [r.link_to for r in sidebar.items if r.type == "Link"]
        for target in (
            "Patient",
            "Employee",
            "Healthcare Practitioner",
            "Floor Assignment Plan",
            "Inpatient Record",
            "Medical Prescription",
            "Medical Prescription Settings",
        ):
            self.assertEqual(targets.count(target), 1)
        self.assertNotIn("Dosage Form", targets)
        self.assertNotIn("Nurse PIN", targets)
        self.assertEqual(icon.update.call_args.args[0]["link_type"], "Workspace Sidebar")
