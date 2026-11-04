import frappe

from medical_prescription.domain import duplication_outcome, yes
from medical_prescription.permissions import DOCTORS, MANAGERS, require_roles
from medical_prescription.services.common import lock_admission, require_validation

HEADERS = (
    "patient_name",
    "patient_encounter",
    "practitioner",
    "practitioner_name",
    "practitioner_full_name",
    "medical_department",
    "floor",
    "service_unit",
    "bed_nb",
    "chief_complaint",
    "medical_diagnosis",
    "weight",
    "height",
    "allergies",
    "pregnancy",
    "breastfeeding",
    "renal_insufficiency",
    "dfg_estimated_mdrd",
    "source_patient_encounter",
)


def duplicate(source_name, new_prescription_date):
    require_roles(DOCTORS | MANAGERS)
    require_validation("duplication")
    if not source_name or not new_prescription_date:
        frappe.throw("Source prescription and new date are required")
    source = frappe.get_doc("Medical Prescription", source_name)
    source.check_permission("read")
    source.check_permission("write")
    if not frappe.has_permission("Medical Prescription", "create"):
        frappe.throw("Cannot create prescriptions", frappe.PermissionError)
    lock_admission(source.inpatient_record)
    source.reload()
    if source.discharge_initiated or source.discharge_finalized or source.status == "Discharged":
        frappe.throw("Cannot duplicate after discharge has started")
    day = frappe.utils.getdate(new_prescription_date)
    if day <= frappe.utils.getdate(source.prescription_date):
        frappe.throw("New date must be after the source prescription date")
    prior = frappe.db.get_value(
        "Medical Prescription",
        {"previous_prescription": source.name, "prescription_date": day, "docstatus": ["!=", 2]},
        "name",
    )
    if prior:
        # Do not disclose a previous result without its read permission.
        frappe.get_doc("Medical Prescription", prior).check_permission("read")
        return prior
    target = frappe.new_doc("Medical Prescription")
    for field in HEADERS:
        target.set(field, source.get(field))
    target.update(
        {
            "patient": source.patient,
            "inpatient_record": source.inpatient_record,
            "prescription_date": day,
            "prescription_time": frappe.utils.nowtime(),
            "status": "Active",
            "root_prescription": source.root_prescription or source.name,
            "previous_prescription": source.name,
            "version_source_type": "Daily Duplicate",
        }
    )
    for row in source.past_drugs:
        target.append("past_drugs", child_data(row))
    stats = {}
    for row in source.administration_schedule:
        if yes(row.disabled):
            continue
        counter = stats.setdefault(row.item_unique_key, [0, 0])
        counter[0] += 1
        counter[1] += int(yes(row.step_2_done) or yes(row.completed))
    for item in source.items:
        count, done = stats.get(item.item_unique_key, (0, 0))
        status, remaining = duplication_outcome(item.as_dict(), count > 0 and count == done)
        if status == "Pending Phone Order":
            continue
        if status:
            data = {
                f.fieldname: item.get(f.fieldname)
                for f in frappe.get_meta("Past Drug Item").fields
                if item.meta.has_field(f.fieldname)
            }
            data.update(
                status=status,
                remaining_period="0 Day",
                move_reason=status,
                moved_by=frappe.session.user,
                moved_on=frappe.utils.now_datetime(),
            )
            target.append("past_drugs", data)
        else:
            data = child_data(item)
            data.update(
                remaining_period=f"{remaining} Day" + ("s" if remaining != 1 else ""),
                day_counter=(item.day_counter or 0) + int(count > 0 and count == done),
            )
            target.append("items", data)
    target.insert()
    return target.name


def child_data(row):
    return {
        f.fieldname: row.get(f.fieldname)
        for f in row.meta.fields
        if f.fieldtype not in ("Section Break", "Column Break", "Tab Break", "HTML", "Button")
    }
