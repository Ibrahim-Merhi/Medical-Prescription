import frappe
from medical_prescription.domain import frequency_interval, spacing_allowed, yes
from medical_prescription.permissions import NURSES, prescription_query, require_roles
from medical_prescription.services.common import lock_admission, require_validation
from medical_prescription.services.signatures import verify_second_nurse

BYPASS = {"System Manager","Nurse Supervisor","Nursing Manager","Emergency Medication Override"}


def administer(prescription, schedule_row, action, second_nurse=None, pin=None, reason=None):
    require_roles(NURSES)
    require_validation("administration")
    if action not in ("step_1", "step_2"):
        frappe.throw("Unknown administration action")
    doc=frappe.get_doc("Medical Prescription",prescription)
    doc.check_permission("read")
    lock_admission(doc.inpatient_record)
    doc.reload()
    doc.check_permission("read")
    if not doc.is_latest_version or doc.status in ("Locked","Discharged") or doc.locked or doc.discharge_finalized:
        frappe.throw("The prescription is locked")
    row=next((r for r in doc.administration_schedule if r.name==schedule_row),None)
    if not row:
        frappe.throw("Administration row does not belong to this prescription")
    item=next((i for i in doc.items if i.item_unique_key==row.item_unique_key),None)
    if not item or item.hold or item.stop_change or item.is_stopped or row.disabled:
        frappe.throw("This medication cannot be administered")
    if item.is_phone_order or item.prn:
        frappe.throw("Phone orders and PRN administration require separate clinical reconciliation")
    # Overnight source dates disagree with the 10:00 nursing day. Do not guess.
    if int(str(row.scheduled_time).split(':')[0]) < 10:
        require_validation("overnight_dates")
    now=frappe.utils.now_datetime()
    user=frappe.session.user
    values={}
    if action=="step_1":
        if row.step_1_done:
            return {"success":True,"already_recorded":True}
        after_lock = frappe.utils.getdate(doc.prescription_date)<now.date() or (
            frappe.utils.getdate(doc.prescription_date)==now.date() and now.hour>=10)
        if after_lock:
            require_roles(BYPASS)
            if not reason:
                frappe.throw("An emergency override reason is required")
        for other in doc.administration_schedule:
            if other.item_unique_key==row.item_unique_key and other.step_1_done and not spacing_allowed(
                other.scheduled_time,row.scheduled_time,frequency_interval(item.frequency)):
                frappe.throw("Selected time violates the medication frequency interval")
        values.update(step_1_done=1,step_1_locked=1,step_1_by=user,step_1_on=now)
    else:
        if row.completed:
            return {"success":True,"already_recorded":True}
        if not row.step_1_done or not row.step_1_locked:
            frappe.throw("Step 1 must be validated first")
        scheduled=frappe.utils.get_datetime(f"{row.scheduled_date} {row.scheduled_time}")
        if abs((now-scheduled).total_seconds())>3600 and not reason:
            frappe.throw("A delay reason is required outside the one-hour administration window")
        required=bool(frappe.db.get_value("Medication",item.medication,"custom_need_double_signature"))
        if required or row.double_signature_required:
            nurse=verify_second_nurse(second_nurse,pin)
            # The second signer must also have floor/patient access.
            condition=prescription_query(nurse)
            if condition and not frappe.db.sql(
                f"select name from `tabMedical Prescription` where name=%s and ({condition})",(doc.name,)):
                frappe.throw("Second nurse does not have access to this prescription",frappe.PermissionError)
            values.update(second_signature_done=1,second_signature_by=nurse,second_signature_on=now)
        values.update(step_2_done=1,step_2_by=user,step_2_on=now,given=1,given_by=user,
            given_on=now,completed=1,locked=1)
    if reason:
        values['reason_of_delay']=str(reason)[:2000]
    # Narrow write after parent read + nurse + floor + workflow checks; normal save rejects forged state.
    frappe.db.set_value("Medication Administration Schedule",row.name,values)
    frappe.db.set_value("Medical Prescription",doc.name,"modified",now)
    doc.add_comment("Info",f"{action} recorded for schedule row {row.name} by {user}.")
    return {"success":True}

