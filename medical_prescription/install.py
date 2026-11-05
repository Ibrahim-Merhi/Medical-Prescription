"""Conflict-first installation. Existing custom DocType adoption requires reconciliation."""

import importlib
import json
from pathlib import Path

import frappe

BASE = Path(__file__).parent


def records(name):
    return json.loads((BASE / "configuration" / f"{name}.json").read_text())


def prerequisites():
    installed = set(frappe.get_installed_apps())
    missing = {"erpnext", "healthcare", "hrms"} - installed
    if missing:
        frappe.throw("Install prerequisite apps on this site first: " + ", ".join(sorted(missing)))
    for app in ("frappe", "erpnext", "healthcare", "hrms"):
        version = getattr(importlib.import_module(app), "__version__", "")
        if version.split(".")[0] != "16":
            frappe.throw(f"{app} v16 is required; detected {version or 'unknown'}")
    if not frappe.db.exists("DocType", "Employee"):
        frappe.throw("Floor Assignment Detail requires the HRMS Employee DocType")


def conflicts(check_ownership=True):
    problems = []
    for doctype, name in (
        ("Page", "medical-overview"),
        ("Report", "Medical Floor Census"),
        ("Report", "Medical Inpatient Census"),
    ):
        if (
            frappe.db.exists(doctype, name)
            and frappe.db.get_value(doctype, name, "module") != "Medical Prescription"
        ):
            problems.append(f"{doctype} {name}: belongs to another module")
    for name, schema in records("source_schema").items():
        if not frappe.db.exists("DocType", name):
            continue
        meta = frappe.get_meta(name)
        if check_ownership and (meta.custom or meta.module != "Medical Prescription"):
            problems.append(
                f"{name}: existing database-managed or foreign-owned DocType; staged adoption required"
            )
        for expected in schema["fields"]:
            actual = meta.get_field(expected["fieldname"])
            if (
                not actual
                or actual.fieldtype != expected["fieldtype"]
                or str(actual.options or "") != expected["options"]
            ):
                problems.append(
                    f"{name}.{expected['fieldname']}: schema differs from the supplied export"
                )
    for definition in records("custom_fields"):
        meta = frappe.get_meta(definition["dt"])
        field = meta.get_field(definition["fieldname"])
        if field and (
            field.fieldtype != definition["fieldtype"]
            or str(field.options or "") != str(definition.get("options") or "")
        ):
            problems.append(
                f"{definition['dt']}.{definition['fieldname']}: incompatible existing field"
            )
        setters = frappe.get_all(
            "Property Setter",
            filters={
                "doc_type": definition["dt"],
                "field_name": definition["fieldname"],
                "property": ["in", ["fieldtype", "options", "reqd", "read_only"]],
            },
            fields=["name"],
        )
        problems.extend(f"Property Setter {r.name}: manual review required" for r in setters)
    for definition in records("print_formats"):
        if frappe.db.exists("Print Format", definition["name"]):
            old = frappe.get_doc("Print Format", definition["name"])
            if old.html != definition["html"]:
                problems.append(f"Print Format {definition['name']}: local content differs")
    return problems


def preflight():
    prerequisites()
    return {"conflicts": conflicts(), "writes_performed": False}


def before_install():
    prerequisites()
    issues = conflicts()
    if issues:
        frappe.throw("Medical Prescription preflight failed:\n" + "\n".join(issues))


def before_migrate():
    before_install()


def after_install():
    # Validate the whole configuration before writing any configuration records.
    before_install()
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    for role in records("roles"):
        if not frappe.db.exists("Role", role["role_name"]):
            frappe.get_doc(role).insert(ignore_permissions=True)
    custom = {}
    for field in records("custom_fields"):
        # Compatible existing fields are retained verbatim, preserving client-specific presentation.
        if not frappe.get_meta(field["dt"]).has_field(field["fieldname"]):
            data = {k: v for k, v in field.items() if k not in ("name", "doctype", "dt")}
            custom.setdefault(field["dt"], []).append(data)
    if custom:
        create_custom_fields(custom, update=False)
    for definition in records("print_formats"):
        if not frappe.db.exists("Print Format", definition["name"]):
            frappe.get_doc(definition).insert(ignore_permissions=True)
    from medical_prescription.patient_layout import apply_layout

    apply_layout()
    from medical_prescription.navigation import ensure_launcher

    ensure_launcher()
