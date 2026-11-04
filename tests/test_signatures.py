import importlib
import sys
import types
import unittest
from unittest.mock import patch


class SignatureTests(unittest.TestCase):
    def test_pin_hash_is_salted_and_checks_without_plaintext_storage(self):
        fake = types.SimpleNamespace()
        with patch.dict(sys.modules, {"frappe": fake}):
            sys.modules.pop("medical_prescription.services.signatures", None)
            mod = importlib.import_module("medical_prescription.services.signatures")
            first = mod.hash_pin("572903")
            second = mod.hash_pin("572903")
            self.assertNotEqual(first, second)
            self.assertNotIn("572903", first)
            self.assertTrue(mod.matches("572903", first))
            self.assertFalse(mod.matches("000000", first))
            self.assertFalse(mod.matches("572903", "malformed"))
