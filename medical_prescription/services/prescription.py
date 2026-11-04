import frappe
from medical_prescription.domain import DOSAGE, build_grid, yes
from medical_prescription.permissions import DOCTORS, MANAGERS, READ_ONLY, require_roles
from medical_prescription.services.common import lock_admission, require_validation

SIGNED_FIELDS = ("step_1_done", "step_1_locked", "step_1_by", "step_1_on", "step_2_done",
                 "step_2_by", "step_2_on", "given", "given_by", "given_on", "completed", "locked",
                 "second_signature_done", "second_signature_by", "second_signature_on")
CONTROLLED = ("status", "locked", "discharge_initiated", "discharge_finalized", "medications_sent",
              "discharge_initiated_by", "discharge_initiated_on", "discharge_finalized_by",
              "discharge_finalized_on", "medications_sent_by", "medications_sent_on")


def validate(doc):
    require_roles(DOCTORS | MANAGERS)
    if set(frappe.get_roles()) & READ_ONLY:
        frappe.throw("Read-only users cannot modify prescriptions", frappe.PermissionError)
    require_validation("prescribing")
    lock_admission(doc.inpatient_record)
    ip = frappe.get_doc("Inpatient Record", doc.inpatient_record)
    ip.check_permission("read")
    frappe.get_doc("Patient", doc.patient).check_permission("read")
    if ip.patient != doc.patient or ip.docstatus == 2:
        frappe.throw("Patient and Inpatient Record do not match")
    if ip.status == "Discharged":
        frappe.throw("The admission is discharged")
    doc.floor = ip.custom_floor
    before = doc.get_doc_before_save()
    if before:
        if before.patient != doc.patient or before.inpatient_record != doc.inpatient_record:
            frappe.throw("Patient and admission cannot be changed after creation")
        if before.status in ("Locked", "Discharged") or before.locked or not before.is_latest_version:
            frappe.throw("This prescription is read-only")
        if (frappe.utils.now_datetime() - frappe.utils.get_datetime(before.creation)).total_seconds() > 3600:
            require_roles({"System Manager", "Emergency Medication Override"})
        if any(doc.get(k) != before.get(k) for k in CONTROLLED):
            frappe.throw("Use the dedicated workflow action to change clinical status")
        protect_history(before, doc)
    else:
        if doc.status not in (None, "", "Draft", "Active") or any(doc.get(k) for k in CONTROLLED[1:]):
            frappe.throw("A new prescription cannot contain signed or locked workflow state")
        if doc.administration_schedule:
            frappe.throw("Administration history cannot be supplied on a new prescription")
        doc.status = "Active"
        doc.is_latest_version = 1
    keys = set()
    for item in doc.items:
        if not item.get("medication") and not item.get("drug_name"):
            frappe.throw(f"Row {item.idx}: Medication is mandatory")
        if not item.item_unique_key:
            item.item_unique_key = frappe.generate_hash(length=20)
        if item.item_unique_key in keys:
            frappe.throw("Duplicate medication order key")
        keys.add(item.item_unique_key)
        if item.is_phone_order:
            require_validation("phone_orders")
        if not item.is_phone_order or item.phone_order_approved:
            for field in ("dose_number", "dose_uom", "frequency", "route"):
                if not item.get(field):
                    frappe.throw(f"Row {item.idx}: {field.replace('_', ' ').title()} is mandatory")
        item.dosage = item.dosage or DOSAGE.get(item.frequency, "1-0-0")
        item.medication = item.medication or item.drug_name
        item.drug_name = item.drug_name or item.medication
        if not frappe.db.exists("Medication", item.medication):
            frappe.throw("Medication must reference an existing Medication record")
        required = frappe.db.get_value("Medication", item.medication, "custom_need_double_signature")
        item.double_signature_required = int(yes(required))
    old = [r.as_dict() for r in doc.administration_schedule]
    try:
        grid = build_grid([r.as_dict() for r in doc.items], old, doc.prescription_date)
    except ValueError as exc:
        frappe.throw(str(exc))
    doc.set("administration_schedule", grid)


def protect_history(before, doc):
    old_rows = {r.name:r for r in before.administration_schedule}
    new_rows = {r.name:r for r in doc.administration_schedule}
    if old_rows.keys() != new_rows.keys():
        frappe.throw("Administration rows cannot be added or removed through document save")
    for name, old in old_rows.items():
        fields = [f.fieldname for f in old.meta.fields]
        if any(new_rows[name].get(k) != old.get(k) for k in fields):
            frappe.throw("Administration rows can only be changed through the nursing API")
        if any(new_rows[name].get(k) != old.get(k) for k in SIGNED_FIELDS):
            frappe.throw("Administration signatures must be recorded using the nursing API")
        if yes(old.completed) and new_rows[name].as_dict() != old.as_dict():
            # Compare persisted business columns only; idx may change in client serialization.
            fields = [f.fieldname for f in old.meta.fields]
            if any(new_rows[name].get(k) != old.get(k) for k in fields):
                frappe.throw("Completed administration history is immutable")


def on_update(doc):
    lock_admission(doc.inpatient_record)
    rows = frappe.get_all("Medical Prescription", filters={"inpatient_record":doc.inpatient_record,
        "patient":doc.patient,"docstatus":["!=",2]}, fields=["name","prescription_date","creation"],
        order_by="prescription_date asc, creation asc, name asc")
    admission = frappe.db.get_value("Inpatient Record", doc.inpatient_record,
        ["admission_ordered_for","admitted_datetime","creation"], as_dict=True)
    start = admission.admission_ordered_for or admission.admitted_datetime or admission.creation
    for i, row in enumerate(rows, 1):
        values = {"version_no":i,"total_prescriptions_for_patient":len(rows),
            "display_sequence_text":f"Prescription {i} out of {len(rows)}",
            "is_latest_version":int(i==len(rows)),"first_prescription_date":rows[0].prescription_date,
            "stay_duration_days":frappe.utils.date_diff(row.prescription_date,start)+1}
        frappe.db.set_value("Medical Prescription",row.name,values,update_modified=False)
        if row.name == doc.name:
            doc.update(values)

