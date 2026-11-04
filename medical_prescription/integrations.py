import frappe


def patient_validate(doc, method=None):
    treating = [r for r in doc.get("custom_practitioner") or [] if r.active and r.role_type=="Treating"]
    if len(treating) > 1:
        frappe.throw("Only one active Treating doctor is allowed")
    seen = set()
    for row in doc.get("custom_practitioner") or []:
        key = (row.practitioner,row.inpatient_record,row.role_type)
        if key in seen:
            frappe.throw("Duplicate doctor assignment")
        seen.add(key)


def practitioner_validate(doc, method=None):
    name = " ".join((doc.first_name or "").split()).upper()
    if name:
        doc.first_name = doc.practitioner_name = name
        if doc.meta.has_field("custom_display_name"):
            doc.custom_display_name = "DR. " + name

