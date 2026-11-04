"""One-way PIN hashes; verification is performed inside the clinical transaction."""

import hashlib
import hmac
import secrets
import time

import frappe

from medical_prescription.permissions import NURSES, READ_ONLY, require_roles


def hash_pin(pin, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", str(pin).encode(), salt.encode(), 600000).hex()
    return f"pbkdf2_sha256$600000${salt}${digest}"


def matches(pin, encoded):
    try:
        algo, rounds, salt, digest = encoded.split("$")
        if algo != "pbkdf2_sha256" or int(rounds) != 600000:
            return False
        actual = hash_pin(pin, salt).split("$")[-1]
        return hmac.compare_digest(actual, digest)
    except (ValueError, AttributeError):
        return False


def throttle():
    # Redis INCR is atomic; no process-local throttling. Expiry does not reveal PINs.
    key = f"{frappe.local.site}:medical_prescription:pin_attempt:{frappe.session.user}:{int(time.time() // 300)}"
    cache = frappe.cache()
    count = cache.incr(key)
    if count == 1:
        cache.expire(key, 300)
    if count > 5:
        frappe.throw("Too many verification attempts. Retry after five minutes.")


def resolve_nurse(login):
    if not isinstance(login, str) or not login.strip():
        frappe.throw("Signature verification failed", frappe.PermissionError)
    login = login.strip()
    name = (
        login
        if frappe.db.exists("User", login)
        else frappe.db.get_value("User", {"username": login}, "name")
    )
    if (
        not name
        or not frappe.db.get_value("User", name, "enabled")
        or not set(frappe.get_roles(name)) & NURSES
    ):
        frappe.throw("Signature verification failed", frappe.PermissionError)
    if set(frappe.get_roles(name)) & READ_ONLY:
        frappe.throw("Read-only users cannot sign administration records", frappe.PermissionError)
    return name


def verify_second_nurse(login, pin):
    require_roles(NURSES)
    throttle()
    nurse = resolve_nurse(login)
    if nurse == frappe.session.user:
        frappe.throw("Second signature requires a different nurse")
    record = frappe.db.get_value(
        "Nurse PIN", {"nurse_user": nurse, "enabled": 1}, ["name", "pin_hash"], as_dict=True
    )
    # Legacy encrypted PINs must be explicitly reset; never decrypt them into responses.
    if not record or not matches(pin, record.pin_hash):
        frappe.throw("Signature verification failed", frappe.PermissionError)
    return nurse


def set_pin(pin):
    require_roles(NURSES)
    if not isinstance(pin, str) or not pin.isdigit() or not 6 <= len(pin) <= 12:
        frappe.throw("Use a PIN containing 6 to 12 digits")
    frappe.db.sql("select name from `tabUser` where name=%s for update", (frappe.session.user,))
    name = frappe.db.get_value("Nurse PIN", {"nurse_user": frappe.session.user}, "name")
    doc = frappe.get_doc("Nurse PIN", name) if name else frappe.new_doc("Nurse PIN")
    doc.nurse_user = frappe.session.user
    doc.pin_hash = hash_pin(pin)
    doc.enabled = 1
    # Narrow escalation: self-owned credential inaccessible through generic document APIs.
    doc.save(ignore_permissions=True)
    return {"success": True}
