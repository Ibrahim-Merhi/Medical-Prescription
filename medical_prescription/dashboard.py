"""Permission-filtered current census. No global cache or permission-bypassing SQL."""

from collections import Counter, defaultdict

import frappe

CURRENT = {"Admitted", "Discharge Scheduled"}
BATCH_SIZE = 2000


def _rows(doctype, fields, filters=None):
    if not frappe.has_permission(doctype, "read"):
        frappe.throw(f"Read access to {doctype} is required", frappe.PermissionError)
    result = []
    while True:
        batch = frappe.get_list(
            doctype,
            fields=fields,
            filters=filters or {},
            order_by="name asc",
            limit_start=len(result),
            limit_page_length=BATCH_SIZE,
        )
        result.extend(batch)
        if len(batch) < BATCH_SIZE:
            return result


def summarize(patients, admissions, prescriptions):
    """Count distinct patients, never infer a floor from prescription history."""
    visible = {p["name"] for p in patients}
    admissions = [a for a in admissions if a.get("patient") in visible]
    current = [a for a in admissions if a.get("status") in CURRENT]
    floors = defaultdict(lambda: {"patients": set(), "admissions": 0, "discharges": set()})
    for row in current:
        floor = row.get("custom_floor") or "Unassigned"
        floors[floor]["patients"].add(row["patient"])
        floors[floor]["admissions"] += 1
        if row["status"] == "Discharge Scheduled":
            floors[floor]["discharges"].add(row["patient"])
    floor_rows = [
        {
            "floor": floor,
            "patients": len(values["patients"]),
            "admissions": values["admissions"],
            "discharges": len(values["discharges"]),
        }
        for floor, values in sorted(floors.items())
    ]
    statuses = Counter(
        p.get("status") or "Unspecified" for p in prescriptions if p.get("patient") in visible
    )
    return {
        "patients": len(visible),
        "inpatients": len({a["patient"] for a in current}),
        "scheduled_admissions": len(
            {a["patient"] for a in admissions if a.get("status") == "Admission Scheduled"}
        ),
        "scheduled_discharges": len(
            {a["patient"] for a in current if a["status"] == "Discharge Scheduled"}
        ),
        "unassigned": len({a["patient"] for a in current if not a.get("custom_floor")}),
        "duplicate_admissions": len(current) - len({a["patient"] for a in current}),
        "floors": floor_rows,
        "prescription_statuses": dict(sorted(statuses.items())),
        "census": current,
    }


def census(include_prescriptions=False):
    if frappe.session.user == "Guest":
        frappe.throw("Sign in to view the census", frappe.PermissionError)
    patients = _rows("Patient", ["name"])
    admissions = _rows(
        "Inpatient Record",
        ["name", "patient", "status", "custom_floor"],
        {"docstatus": ["!=", 2], "status": ["in", sorted(CURRENT | {"Admission Scheduled"})]},
    )
    prescriptions = []
    prescription_access = include_prescriptions and frappe.has_permission(
        "Medical Prescription", "read"
    )
    if prescription_access:
        prescriptions = _rows(
            "Medical Prescription", ["name", "patient", "status"], {"docstatus": ["!=", 2]}
        )
    result = summarize(patients, admissions, prescriptions)
    result["prescription_access"] = bool(prescription_access)
    return result


@frappe.whitelist(methods=["GET"])
def overview():
    result = census(include_prescriptions=True)
    result.pop("census")
    result["as_of"] = str(frappe.utils.now_datetime())
    return result


def floor_report(filters=None):
    rows = census()["floors"]
    floor = (filters or {}).get("floor")
    if floor:
        rows = [r for r in rows if r["floor"] == floor]
    return rows


def inpatient_report(filters=None):
    filters = filters or {}
    rows = census()["census"]
    return [
        r
        for r in rows
        if (not filters.get("floor") or (r.get("custom_floor") or "Unassigned") == filters["floor"])
        and (not filters.get("status") or r["status"] == filters["status"])
    ]
