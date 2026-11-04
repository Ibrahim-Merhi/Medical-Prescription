import frappe


def validate_plan(doc):
    # A stable existing row serializes even two inserts into an empty date/shift slot.
    # Low-frequency administrative writes; no database-specific advisory lock required.
    frappe.db.sql(
        "select name from `tabDocType` where name=%s for update", ("Floor Assignment Plan",)
    )
    if frappe.db.exists(
        "Floor Assignment Plan",
        {
            "name": ["!=", doc.name],
            "assignment_date": doc.assignment_date,
            "shift": doc.shift,
            "status": ["!=", "Cancelled"],
        },
    ):
        frappe.throw("A plan already exists for this date and shift")
    seen = set()
    users = set()
    for row in doc.assignment_details:
        if row.employee:
            if row.employee in seen:
                frappe.throw("The same nurse appears more than once")
            seen.add(row.employee)
            row.user_id = frappe.db.get_value("Employee", row.employee, "user_id")
            if not row.user_id:
                frappe.throw("Assigned employees must have a linked User")
        if row.user_id and not set(frappe.get_roles(row.user_id)) & {"Nurse", "Nursing User"}:
            frappe.throw("Floor assignments require a Nurse or Nursing User")
        if not row.floor or not row.user_id:
            frappe.throw("Every floor assignment requires a floor and linked nurse user")
        if row.user_id in users:
            frappe.throw("The same nurse user appears more than once")
        users.add(row.user_id)
