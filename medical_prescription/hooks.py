app_name = "medical_prescription"
app_title = "Medical Prescription"
app_publisher = "Medical Prescription contributors"
app_description = "Medical prescription management for Frappe Healthcare"
app_email = ""
app_license = "MIT"
required_apps = ["erpnext", "healthcare", "hrms"]

app_logo_url = "/assets/medical_prescription/images/healthcare.svg"
add_to_apps_screen = [
    {
        "name": app_name,
        "title": "Healthcare",
        "logo": app_logo_url,
        "route": "/app/medical-overview",
        "has_permission": "medical_prescription.navigation.has_launcher_permission",
    }
]

before_install = "medical_prescription.install.before_install"
after_install = "medical_prescription.install.after_install"
before_migrate = "medical_prescription.install.before_migrate"
after_migrate = "medical_prescription.install.after_install"

doctype_js = {
    "Medical Prescription": "public/js/prescription.js",
    "Patient": "public/js/patient.js",
    "User": "public/js/user.js",
}
permission_query_conditions = {
    "Medical Prescription": "medical_prescription.permissions.prescription_query",
    "Patient": "medical_prescription.permissions.patient_query",
}
has_permission = {
    "Medical Prescription": "medical_prescription.permissions.prescription_permission",
    "Patient": "medical_prescription.permissions.patient_permission",
}
doc_events = {
    "Patient": {"validate": "medical_prescription.integrations.patient_validate"},
    "Healthcare Practitioner": {
        "validate": "medical_prescription.integrations.practitioner_validate"
    },
}

doctype_list_js = {"Patient": "public/js/patient_list.js"}
