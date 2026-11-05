import importlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class PatientViewTests(unittest.TestCase):
    def load(self):
        fake = Mock()
        fake.session.user = "clinical-user"
        fake.whitelist = lambda **kwargs: lambda fn: fn
        fake.PermissionError = PermissionError
        fake.throw.side_effect = lambda message, exc=ValueError: (_ for _ in ()).throw(exc(message))
        fake.get_meta.return_value.has_field.return_value = True
        with patch.dict(sys.modules, {"frappe": fake}):
            sys.modules.pop("medical_prescription.patient_view", None)
            module = importlib.import_module("medical_prescription.patient_view")
        return module, fake

    def test_admission_history_checks_patient_and_preserves_row_permissions(self):
        module, fake = self.load()
        fake.get_list.return_value = [{"name": str(i)} for i in range(21)]
        result = module.admissions("test-patient", 20)
        fake.get_doc.return_value.check_permission.assert_called_once_with("read")
        self.assertEqual(len(result["rows"]), 20)
        self.assertTrue(result["has_more"])
        args = fake.get_list.call_args.kwargs
        self.assertEqual(args["filters"], {"patient": "test-patient"})
        self.assertEqual(args["limit_start"], 20)
        self.assertNotIn("ignore_permissions", args)
        fake.get_all.assert_not_called()

    def test_guest_and_inpatient_denial(self):
        module, fake = self.load()
        fake.session.user = "Guest"
        with self.assertRaises(PermissionError):
            module.admissions("test-patient")
        fake.session.user = "clinical-user"
        fake.has_permission.return_value = False
        with self.assertRaises(PermissionError):
            module.admissions("test-patient")
        fake.get_list.assert_not_called()

    def test_actions_keep_validation_gates_and_readonly_restriction(self):
        module, fake = self.load()
        fake.get_roles.return_value = ["System Manager", "Read Only"]
        fake.conf.get.return_value = []
        fake.get_list.return_value = [{"name": "test-admission"}]
        result = module.actions("test-patient")
        self.assertFalse(result["can_create"])
        self.assertFalse(result["can_discharge"])
        self.assertFalse(result["prescribing_enabled"])
        self.assertFalse(result["discharge_enabled"])
        self.assertEqual(fake.get_list.call_args.kwargs["filters"]["patient"], "test-patient")

    def test_layout_only_sets_presentation_properties(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "medical_prescription/configuration/patient_layout.json"
        )
        layout = json.loads(path.read_text())
        self.assertEqual(len(layout["field_order"]), len(set(layout["field_order"])))
        self.assertTrue(
            {p["property"] for p in layout["properties"]}
            <= {"hidden", "label", "in_list_view", "in_standard_filter"}
        )
        self.assertIn("custom_admissions_history", layout["field_order"])
        self.assertIn("custom_medical_prescription_history", layout["field_order"])

    def test_profile_uses_linked_admission_and_rejects_wrong_patient(self):
        module, fake = self.load()
        patient = Mock(name="patient-doc")
        patient.name = "P1"
        patient.inpatient_record = "IP1"
        patient.get.return_value = "IP1"
        patient.meta.has_field.return_value = True
        admission = Mock()
        admission.patient = "P1"
        admission.name = "IP1"
        admission.docstatus = 0
        admission.meta.has_field.return_value = True
        source = {
            "custom_floor": "First",
            "custom_service_unit": "Unit 1",
            "custom_medical_file": "004422",
            "custom_case_number": "214",
            "medical_department": "Ward",
        }
        admission.get.side_effect = source.get
        fake.get_doc.side_effect = lambda dt, name: patient if dt == "Patient" else admission
        result = module.inpatient_profile("P1")
        admission.check_permission.assert_called_once_with("read")
        self.assertEqual(result["values"]["custom_latest_case_number"], "214")
        self.assertEqual(result["values"]["custom_medical_file"], "004422")
        admission.patient = "P2"
        with self.assertRaises(ValueError):
            module.inpatient_profile("P1")


    def test_administrator_can_use_actions_with_readonly_roles(self):
        module, fake = self.load()
        fake.session.user = "Administrator"
        fake.get_roles.return_value = ["Read Only", "Medical Prescription Viewer"]
        fake.conf.get.return_value = []
        fake.get_list.return_value = [{"name": "IP1"}]
        result = module.actions("P1")
        self.assertTrue(result["can_create"])
        self.assertTrue(result["can_discharge"])
        self.assertFalse(result["prescribing_enabled"])
