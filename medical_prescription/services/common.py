import frappe


def lock_admission(name):
    if not name:
        frappe.throw("An Inpatient Record is required")
    # Parent admission lock serializes create/duplicate/version operations, including empty chains.
    rows = frappe.db.sql("select name from `tabInpatient Record` where name=%s for update", (name,))
    if not rows:
        frappe.throw("Inpatient Record does not exist")


def require_validation(workflow):
    """Keep unresolved clinical behavior out of live use; flags are deployment attestations."""
    validated = frappe.conf.get("medical_prescription_validated_workflows") or []
    if workflow not in validated:
        frappe.throw(
            f"{workflow} is isolated pending staging integration and clinical validation. "
            "See docs/validation_gates.md."
        )


def stamp():
    return frappe.session.user, frappe.utils.now_datetime()
