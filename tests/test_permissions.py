"""Isolated policy tests. These are not Frappe authorization integration tests."""

import importlib
import sys
import types
import unittest
from unittest.mock import patch


class PolicyTests(unittest.TestCase):
    def policy(self, roles, user="synthetic-user"):
        fake = types.SimpleNamespace(
            session=types.SimpleNamespace(user=user),
            get_roles=lambda u=None: roles,
            db=types.SimpleNamespace(escape=lambda value: "'" + value.replace("'", "''") + "'"),
            utils=types.SimpleNamespace(today=lambda: "2026-11-04"),
        )
        return fake

    def query(self, roles, user="synthetic-user"):
        with patch.dict(sys.modules, {"frappe": self.policy(roles, user)}):
            sys.modules.pop("medical_prescription.permissions", None)
            mod = importlib.import_module("medical_prescription.permissions")
            return mod.prescription_query(user)

    def test_guest_and_unrecognized_roles_fail_closed(self):
        self.assertEqual(self.query([], "Guest"), "1=0")
        self.assertEqual(self.query(["Accounts User"]), "1=0")

    def test_nurse_floor_restriction_survives_resident_role(self):
        result = self.query(["Nurse", "Resident"])
        self.assertIn("fad.user_id=", result)
        self.assertIn("fap.assignment_date='2026-11-04'", result)
        self.assertIn("ip.docstatus != 2", result)

    def test_doctor_assignment_and_active_admission_required(self):
        result = self.query(["Physician"])
        self.assertIn("ad.active=1", result)
        self.assertIn("ip.primary_practitioner=hp.name", result)

    def test_manager_unrestricted_row_scope(self):
        self.assertEqual(self.query(["System Manager"]), "")

    def test_read_only_nurse_cannot_mutate(self):
        fake = self.policy(["Nurse", "Read Only"])
        fake.PermissionError = PermissionError

        def fail(message, exception):
            raise exception(message)

        fake.throw = fail
        with patch.dict(sys.modules, {"frappe": fake}):
            sys.modules.pop("medical_prescription.permissions", None)
            mod = importlib.import_module("medical_prescription.permissions")
            with self.assertRaises(PermissionError):
                mod.require_roles({"Nurse"})
