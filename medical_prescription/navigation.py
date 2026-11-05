"""Frappe v16 launcher registration; does not change clinical permissions."""

import frappe

LABEL = "Healthcare"
APP = "medical_prescription"
ROUTE = "/app/medical-overview"
LOGO = "/assets/medical_prescription/images/healthcare.svg"


def has_launcher_permission():
    return frappe.session.user != "Guest" and frappe.has_permission("Medical Prescription", "read")


def ensure_launcher():
    sidebar_name = "Medical Prescription"
    if frappe.db.exists("Workspace Sidebar", sidebar_name):
        sidebar = frappe.get_doc("Workspace Sidebar", sidebar_name)
        if sidebar.app != APP:
            frappe.throw("The Medical Prescription sidebar belongs to another app or customization")
    else:
        sidebar = frappe.get_doc(
            {
                "doctype": "Workspace Sidebar",
                "title": sidebar_name,
                "app": APP,
                "module": "Medical Prescription",
                "standard": 1,
                "items": [
                    {
                        "type": "Link",
                        "label": "Medical Prescription",
                        "link_type": "DocType",
                        "link_to": "Medical Prescription",
                    }
                ],
            }
        )
        sidebar.insert(ignore_permissions=True)
    sync_sidebar(sidebar)
    label = LABEL
    if (
        frappe.db.exists("Desktop Icon", label)
        and frappe.db.get_value("Desktop Icon", label, "app") != APP
    ):
        label = "Medical Prescription"
    if frappe.db.exists("Desktop Icon", label):
        icon = frappe.get_doc("Desktop Icon", label)
        if icon.app != APP:
            frappe.throw(
                "The Medical Prescription desktop label is already used by another app or custom icon"
            )
    else:
        icon = frappe.new_doc("Desktop Icon")
    icon.update(
        {
            "label": label,
            "app": APP,
            "icon_type": "App",
            "link_type": "Workspace Sidebar",
            "link_to": sidebar_name,
            "sidebar": sidebar_name,
            "link": "",
            "logo_url": LOGO,
            "standard": 1,
            "hidden": 0,
        }
    )
    icon.save(ignore_permissions=True)
    frappe.cache.delete_key("desktop_icons")
    frappe.cache.delete_key("bootinfo")


# Labels describe the existing records; there is no separate Doctor or Nurse DocType.
SECTIONS = [
    (
        "Patients and Admissions",
        [
            ("Patients", "Patient"),
            ("Inpatient Records", "Inpatient Record"),
            ("Patient Encounters", "Patient Encounter"),
            ("Patient Appointments", "Patient Appointment"),
            ("Vital Signs", "Vital Signs"),
        ],
    ),
    (
        "Prescriptions and Medicines",
        [
            ("Medical Prescriptions", "Medical Prescription"),
            ("Medications", "Medication"),
            ("Drug Items", "Item"),
            ("Dosages", "Prescription Dosage"),
            ("Dosage Forms", "Dosage Form"),
            ("Prescription Durations", "Prescription Duration"),
        ],
    ),
    (
        "Doctors and Nursing",
        [
            ("Doctors / Practitioners", "Healthcare Practitioner"),
            ("Nurses / Staff (Employees)", "Employee"),
            ("Nurse Floor Assignments", "Floor Assignment Plan"),
        ],
    ),
    (
        "Floors and Care Units",
        [
            ("Floors", "Floor"),
            ("Prescription Service Units", "Service Unit"),
            ("Healthcare Service Units", "Healthcare Service Unit"),
            ("Service Unit Types", "Healthcare Service Unit Type"),
            ("Medical Departments", "Medical Department"),
        ],
    ),
    (
        "Administration",
        [
            ("Prescription Settings", "Medical Prescription Settings"),
            ("Healthcare Settings", "Healthcare Settings"),
            ("Users", "User"),
        ],
    ),
]


def sidebar_items():
    items = [
        {
            "type": "Link",
            "label": "Medical Dashboard",
            "link_type": "Page",
            "link_to": "medical-overview",
        }
    ]
    sections = [
        (
            "Reports",
            [
                ("Floor Census", "Report", "Medical Floor Census"),
                ("Inpatient Census", "Report", "Medical Inpatient Census"),
            ],
        )
    ]
    for title, entries in SECTIONS:
        sections.append(
            (
                title,
                [
                    (label, "DocType", target)
                    for label, target in entries
                    if frappe.db.exists("DocType", target) and not frappe.get_meta(target).istable
                ],
            )
        )
    for title, entries in sections:
        if not entries:
            continue
        items.append({"type": "Section Break", "label": title, "collapsible": 1, "keep_closed": 0})
        items.extend(
            {"type": "Link", "label": label, "link_type": kind, "link_to": target, "child": 1}
            for label, kind, target in entries
        )
    return items


def sync_sidebar(sidebar):
    """Refresh app navigation while retaining unrelated local links and sections."""
    items = sidebar_items()
    targets = {(row.get("link_type"), row.get("link_to")) for row in items if row["type"] == "Link"}
    sections = {row["label"] for row in items if row["type"] == "Section Break"}
    extra = []
    for row in sidebar.items:
        if (row.link_type, row.link_to) in targets:
            continue
        if row.type == "Section Break" and row.label in sections:
            continue
        extra.append(
            {
                key: value
                for key, value in row.as_dict().items()
                if key
                not in {
                    "name",
                    "parent",
                    "parenttype",
                    "parentfield",
                    "idx",
                    "creation",
                    "modified",
                    "owner",
                    "modified_by",
                }
            }
        )
    if extra:
        items.append({"type": "Section Break", "label": "Additional Links", "collapsible": 1})
        # Avoid growing another Additional Links heading on every migration.
        extra = [
            row
            for row in extra
            if not (row.get("type") == "Section Break" and row.get("label") == "Additional Links")
        ]
        items.extend(extra)
    sidebar.set("items", items)
    sidebar.save(ignore_permissions=True)
