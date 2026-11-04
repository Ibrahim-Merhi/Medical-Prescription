import frappe


def validate_plan(doc):
    if frappe.db.exists("Floor Assignment Plan", {"name":["!=",doc.name],
        "assignment_date":doc.assignment_date,"shift":doc.shift,"status":["!=","Cancelled"]}):
        frappe.throw("A plan already exists for this date and shift")
    seen = set()
    for row in doc.assignment_details:
        if row.employee:
            if row.employee in seen:
                frappe.throw("The same nurse appears more than once")
            seen.add(row.employee)
            row.user_id = frappe.db.get_value("Employee", row.employee, "user_id")
            if not row.user_id:
                frappe.throw("Assigned employees must have a linked User")
        if row.user_id and not set(frappe.get_roles(row.user_id)) & {"Nurse","Nursing User"}:
            frappe.throw("Floor assignments require a Nurse or Nursing User")

