from medical_prescription.dashboard import inpatient_report


def execute(filters=None):
    columns = [
        {
            "fieldname": "name",
            "label": "Admission",
            "fieldtype": "Link",
            "options": "Inpatient Record",
            "width": 220,
        },
        {
            "fieldname": "patient",
            "label": "Patient",
            "fieldtype": "Link",
            "options": "Patient",
            "width": 200,
        },
        {"fieldname": "custom_floor", "label": "Floor", "fieldtype": "Data", "width": 180},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 180},
    ]
    return (
        columns,
        inpatient_report(filters),
        "Current Admitted and Discharge Scheduled records only. Blank floors are Unassigned. Multiple rows for one patient require review.",
    )
