"""Read-only Patient history and action availability; mutations use existing services."""

import frappe

from medical_prescription.permissions import DOCTORS, MANAGERS, READ_ONLY


def patient_access(patient):
    if frappe.session.user == "Guest":
        frappe.throw("Sign in to view patient history", frappe.PermissionError)
    doc = frappe.get_doc("Patient", patient)
    doc.check_permission("read")
    return doc


@frappe.whitelist(methods=["GET"])
def admissions(patient, start=0):
    patient_access(patient)
    if not frappe.has_permission("Inpatient Record", "read"):
        frappe.throw("Inpatient Record read access is required", frappe.PermissionError)
    start = max(0, int(start))
    meta = frappe.get_meta("Inpatient Record")
    candidates = [
        "custom_case_number",
        "admission_ordered_for",
        "discharge_ordered_date",
        "status",
        "medical_department",
    ]
    fields = ["name", "creation"] + [f for f in candidates if meta.has_field(f)]
    rows = frappe.get_list(
        "Inpatient Record",
        filters={"patient": patient},
        fields=fields,
        order_by="creation desc, name desc",
        limit_start=start,
        limit_page_length=21,
    )
    return {"rows": rows[:20], "has_more": len(rows) > 20}


@frappe.whitelist(methods=["GET"])
def actions(patient):
    doc = patient_access(patient)
    roles = set(frappe.get_roles())
    manager = frappe.session.user == "Administrator"
    readonly = bool(roles & READ_ONLY)
    allowed = frappe.conf.get("medical_prescription_validated_workflows") or []
    admission = None
    if doc.get("inpatient_record") and frappe.has_permission("Inpatient Record", "read"):
        rows = frappe.get_list(
            "Inpatient Record",
            filters={
                "name": doc.inpatient_record,
                "patient": patient,
                "docstatus": ["!=", 2],
                "status": ["in", ["Admission Scheduled", "Admitted", "Discharge Scheduled"]],
            },
            fields=["name"],
            limit_page_length=1,
        )
        admission = rows[0]["name"] if rows else None
    return {
        "inpatient_record": admission,
        "can_create": not readonly
        and bool(manager or roles & (DOCTORS | MANAGERS))
        and bool(frappe.has_permission("Medical Prescription", "create")),
        "can_discharge": not readonly
        and bool(manager or roles & {"System Manager", "Pharmacist", "Discharge Patient"}),
        "prescribing_enabled": "prescribing" in allowed,
        "discharge_enabled": "discharge" in allowed,
    }


PROFILE_FIELDS = {
    "custom_floor": "custom_floor",
    "custom_service_unit": "custom_service_unit",
    "custom_medical_file": "custom_medical_file",
    "custom_latest_case_number": "custom_case_number",
    "custom_department": "medical_department",
}


@frappe.whitelist(methods=["GET"])
def inpatient_profile(patient):
    doc = patient_access(patient)
    if not doc.get("inpatient_record"):
        return {"values": {}, "message": "No Inpatient Record is linked to this Patient."}
    ip = frappe.get_doc("Inpatient Record", doc.inpatient_record)
    ip.check_permission("read")
    if ip.patient != doc.name or ip.docstatus == 2:
        frappe.throw("The linked admission is cancelled or belongs to another patient")
    values = {
        target: ip.get(source)
        for target, source in PROFILE_FIELDS.items()
        if doc.meta.has_field(target) and ip.meta.has_field(source)
    }
    return {"values": values, "inpatient_record": ip.name}
