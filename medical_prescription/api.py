"""Authenticated, POST-only mutation endpoints. No allow_guest or manual commits."""

import frappe

from medical_prescription.services import administration, duplication, signatures


@frappe.whitelist(methods=["POST"])
def duplicate_medical_prescription(source_name, new_prescription_date):
    return duplication.duplicate(source_name, new_prescription_date)


@frappe.whitelist(methods=["POST"])
def set_my_nurse_pin(pin):
    return signatures.set_pin(pin)


@frappe.whitelist(methods=["POST"])
def record_administration(
    prescription, schedule_row, action, second_nurse=None, pin=None, reason=None
):
    return administration.administer(prescription, schedule_row, action, second_nurse, pin, reason)


@frappe.whitelist(methods=["POST"])
def reactivate_discharge_admission(inpatient_record, reason):
    from medical_prescription.services.discharge import transition

    return transition(inpatient_record, reactivate=True, reason=reason)


@frappe.whitelist(methods=["POST"])
def finalize_discharge(inpatient_record, reason):
    from medical_prescription.services.discharge import transition

    return transition(inpatient_record, reason=reason)


@frappe.whitelist(methods=["GET"])
def patient_prescriptions(patient, start=0, page_length=20):
    frappe.get_doc("Patient", patient).check_permission("read")
    start = max(0, int(start))
    page_length = min(100, max(1, int(page_length)))
    # get_list applies both native permissions and prescription query restrictions.
    return frappe.get_list(
        "Medical Prescription",
        filters={"patient": patient},
        fields=["name", "prescription_date", "status", "version_no", "is_latest_version"],
        order_by="prescription_date desc, creation desc",
        start=start,
        page_length=page_length,
    )
