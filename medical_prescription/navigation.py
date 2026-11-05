"""Frappe v16 launcher registration; does not change clinical permissions."""

import frappe

LABEL = "Healthcare"
APP = "medical_prescription"
ROUTE = "/app/medical-prescription"
LOGO = "/assets/medical_prescription/images/healthcare.svg"


def has_launcher_permission():
    return frappe.session.user != "Guest" and frappe.has_permission("Medical Prescription", "read")


def ensure_launcher():
    label = LABEL
    if (
        frappe.db.exists("Desktop Icon", label)
        and frappe.db.get_value("Desktop Icon", label, "app") != APP
    ):
        label = "Medical Prescription"
    if frappe.db.exists("Desktop Icon", label):
        icon = frappe.get_doc("Desktop Icon", label)
        if icon.app != APP:
            frappe.throw("The Medical Prescription desktop label is already used by another app or custom icon")
    else:
        icon = frappe.new_doc("Desktop Icon")
    icon.update(
        {
            "label": label,
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
