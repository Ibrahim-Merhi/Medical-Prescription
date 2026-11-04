"""Generic Jinja synthetic rendering; does not substitute for Frappe/PDF QA."""

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[1] / "medical_prescription"


class TemplateTests(unittest.TestCase):
    def render(self, name, count):
        formats = json.loads((ROOT / "configuration/print_formats.json").read_text())
        template = next(f["html"] for f in formats if f["name"] == name)
        meta = json.loads(
            (
                ROOT / "medical_prescription/doctype/medical_prescription/medical_prescription.json"
            ).read_text()
        )
        values = {f["fieldname"]: None for f in meta["fields"]}
        values.update(
            name="SYNTHETIC-RX",
            patient_name="<script>test</script>",
            inpatient_record="SYNTHETIC-IP",
            items=[
                SimpleNamespace(
                    drug_name=f"SyntheticDrug{i:03}",
                    medication=f"SyntheticDrug{i:03}",
                    dose_number="1",
                    dose_uom="mg",
                    route="PO",
                    frequency="OD",
                    comment="Synthetic only",
                )
                for i in range(count)
            ],
        )
        fake = SimpleNamespace(
            db=SimpleNamespace(get_single_value=lambda *a: "Synthetic Hospital"),
            get_list=lambda *a, **kw: [],
            get_fullname=lambda *a: "Synthetic Nurse",
            session=SimpleNamespace(user="synthetic@example.invalid"),
        )
        return (
            Environment(autoescape=True)
            .from_string(template)
            .render(doc=SimpleNamespace(**values), frappe=fake)
        )

    def test_empty_template_renders_and_escapes_patient_text(self):
        result = self.render("Empty Medical Prescription", 0)
        self.assertIn("Synthetic Hospital", result)
        self.assertNotIn("<script>test</script>", result)

    def test_all_orders_render_beyond_original_36_order_limit(self):
        result = self.render("Medical Prescription", 55)
        for i in range(55):
            self.assertIn(f"SyntheticDrug{i:03}", result)
        self.assertEqual(result.count('<div class="mp-page">'), 4)

    def test_empty_populated_format_retains_two_pages(self):
        self.assertEqual(self.render("Medical Prescription", 0).count('<div class="mp-page">'), 2)
