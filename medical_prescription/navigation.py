"""Frappe v16 launcher registration; does not change clinical permissions."""

import frappe

LABEL = "Healthcare"
APP = "medical_prescription"
ROUTE = "/app/medical-prescription"
LOGO = "/assets/medical_prescription/images/healthcare.svg"


def has_launcher_permission():
    return frappe.session.user != "Guest" and frappe.has_permission("Medical Prescription", "read")


def ensure_launcher():
    if frappe.db.exists("Desktop Icon", LABEL):
        icon = frappe.get_doc("Desktop Icon", LABEL)
        if icon.app != APP:
            frappe.throw("The Healthcare desktop label is already used by another app or custom icon")
    else:
        icon = frappe.new_doc("Desktop Icon")
    icon.update(
        {
            "label": LABEL,
            "app": APP,
            "icon_type": "App",
            "link_type": "External",
            "link": ROUTE,
            "logo_url": LOGO,
            "standard": 1,
            "hidden": 0,
        }
    )
    icon.save(ignore_permissions=True)
    frappe.cache.delete_key("desktop_icons")
    frappe.cache.delete_key("bootinfo")
