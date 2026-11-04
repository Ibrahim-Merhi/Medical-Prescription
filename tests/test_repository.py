import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "medical_prescription"


class RepositoryTests(unittest.TestCase):
    def test_all_python_parses(self):
        for path in ROOT.rglob("*.py"):
            ast.parse(path.read_text(), filename=str(path))

    def test_child_table_targets_and_field_identity(self):
        schemas = [
            json.loads(p.read_text())
            for p in (PKG / "medical_prescription/doctype").glob("*/*.json")
        ]
        names = {s["name"]: s for s in schemas}
        self.assertEqual(len(names), 12)
        for schema in schemas:
            fields = schema["fields"]
            self.assertEqual(len(fields), len({f["fieldname"] for f in fields}))
            for field in fields:
                self.assertIn("fieldtype", field)
                if field["fieldtype"] == "Table":
                    self.assertIn(field["options"], names)
                    self.assertEqual(names[field["options"]]["istable"], 1)

    def test_print_templates_and_credentials(self):
        prints = json.loads((PKG / "configuration/print_formats.json").read_text())
        self.assertEqual(len(prints), 2)
        for template in prints:
            self.assertIn("organization_name", template["html"])
            self.assertNotIn("nini_hospital", template["html"])
        nurse = json.loads(
            (PKG / "medical_prescription/doctype/nurse_pin/nurse_pin.json").read_text()
        )
        self.assertEqual(nurse["permissions"], [])
        self.assertIn("pin_hash", {f["fieldname"] for f in nurse["fields"]})

    def test_no_manually_committed_or_guest_mutations(self):
        for path in PKG.rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    self.assertNotEqual(ast.unparse(node.func), "frappe.db.commit")
                    for keyword in node.keywords:
                        if keyword.arg == "allow_guest":
                            self.assertNotEqual(ast.literal_eval(keyword.value), True)
