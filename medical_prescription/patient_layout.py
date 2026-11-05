"""Reference Patient presentation only; no changes to clinical data or permission fields."""

import json
from pathlib import Path

import frappe


def apply_layout():
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter

    layout = json.loads((Path(__file__).parent / "configuration/patient_layout.json").read_text())
    meta = frappe.get_meta("Patient")
    fields = {f.fieldname for f in meta.fields}
    order = [name for name in layout["field_order"] if name in fields]
    # Retain site-specific fields near their original preceding field.
    previous = None
    for field in meta.fields:
        if field.fieldname not in order:
            index = order.index(previous) + 1 if previous in order else 0
            order.insert(index, field.fieldname)
        previous = field.fieldname

    def set_property(doctype, field, prop, value, kind):
        current = frappe.get_meta(doctype)
        source = current.get_field(field) if field else current
        if source is not None and str(source.get(prop) or "") != str(value):
            make_property_setter(doctype, field, prop, value, kind, for_doctype=not bool(field))

    set_property("Patient", None, "field_order", json.dumps(order), "Data")
    set_property("Patient", None, "title_field", "patient_name", "Data")
    for prop in layout["properties"]:
        if prop["field"] in fields:
            set_property("Patient", prop["field"], prop["property"], prop["value"], prop["type"])
    for field in ("practitioner", "role_type", "specialty", "active"):
        set_property("Assigned Doctors", field, "in_list_view", 1, "Check")
    frappe.clear_cache(doctype="Patient")
    frappe.clear_cache(doctype="Assigned Doctors")
