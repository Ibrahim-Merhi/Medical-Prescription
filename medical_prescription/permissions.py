"""One row restriction shared by list queries and direct-document access."""

import frappe

MANAGERS = {"System Manager", "Healthcare Manager", "Healthcare Administrator"}
DOCTORS = {"Physician", "Doctor", "Healthcare User", "Healthcare Practitioner"}
NURSES = {"Nurse", "Nursing User"}
READ_ALL_ACTIVE = {"Pharmacist", "Resident", "Medical Prescription Viewer"}
READ_ONLY = {"Medical Prescription Viewer", "Read Only"}


def prescription_query(user=None):
    user = user or frappe.session.user
    roles = set(frappe.get_roles(user))
    if user == "Administrator" or roles & MANAGERS:
        return ""
    if user == "Guest":
        return "1=0"
    user_sql = frappe.db.escape(user)
    today = frappe.db.escape(frappe.utils.today())
    active = """exists (select 1 from `tabInpatient Record` ip
      where ip.patient=`tabMedical Prescription`.patient and ip.docstatus != 2
      and ip.status in ('Admission Scheduled','Admitted','Discharge Scheduled'))"""
    # Both active legacy nursing queries constrain nurses, even if they have another role.
    if roles & NURSES:
        return (
            active
            + f""" and `tabMedical Prescription`.floor in (
          select fad.floor from `tabFloor Assignment Detail` fad
          join `tabFloor Assignment Plan` fap on fap.name=fad.parent
          where fad.parenttype='Floor Assignment Plan' and fad.user_id={user_sql}
          and fap.status='Active' and fap.assignment_date={today})"""
        )
    if roles & READ_ALL_ACTIVE:
        return active
    if roles & DOCTORS:
        return (
            active
            + f""" and exists (select 1 from `tabHealthcare Practitioner` hp
          where hp.user_id={user_sql} and (
          hp.name=(select p.custom_attending_practitioner from `tabPatient` p
            where p.name=`tabMedical Prescription`.patient)
          or exists (select 1 from `tabAssigned Doctors` ad
            where ad.parent=`tabMedical Prescription`.patient and ad.parenttype='Patient'
            and ad.practitioner=hp.name and ad.active=1)
          or exists (select 1 from `tabInpatient Record` ip
            where ip.patient=`tabMedical Prescription`.patient and ip.docstatus != 2
            and ip.status in ('Admission Scheduled','Admitted','Discharge Scheduled')
            and ip.primary_practitioner=hp.name)))"""
        )
    return "1=0"


def prescription_permission(doc, user=None, permission_type=None, **kwargs):
    user = user or frappe.session.user
    roles = set(frappe.get_roles(user))
    kind = permission_type or kwargs.get("ptype") or "read"
    if kind in ("write", "create", "delete", "submit", "cancel", "amend"):
        if roles & READ_ONLY:
            return False
        if user != "Administrator" and not roles & (DOCTORS | MANAGERS):
            return False
    condition = prescription_query(user)
    if condition == "1=0":
        return False
    if condition and not doc.is_new():
        rows = frappe.db.sql(
            f"""select name from `tabMedical Prescription`
          where name=%s and ({condition}) limit 1""",
            (doc.name,),
        )
        if not rows:
            return False
    # None leaves native role/User Permission checks in charge of the final grant.
    return None


def require_roles(roles):
    assigned = set(frappe.get_roles())
    if (
        assigned & READ_ONLY
        or frappe.session.user == "Guest"
        or (frappe.session.user != "Administrator" and not assigned & set(roles))
    ):
        frappe.throw("You are not authorized for this action", frappe.PermissionError)


def patient_query(user=None):
    return (
        prescription_query(user)
        .replace("`tabMedical Prescription`.patient", "`tabPatient`.name")
        .replace("`tabMedical Prescription`.floor", "`tabPatient`.custom_floor")
    )


def patient_permission(doc, user=None, permission_type=None, **kwargs):
    condition = patient_query(user)
    if (
        condition
        and not doc.is_new()
        and not frappe.db.sql(
            f"select name from `tabPatient` where name=%s and ({condition})", (doc.name,)
        )
    ):
        return False
    return None
