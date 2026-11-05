from medical_prescription.dashboard import floor_report


def execute(filters=None):
    columns = [
        {"fieldname": "floor", "label": "Floor", "fieldtype": "Data", "width": 220},
        {"fieldname": "patients", "label": "Current Patients", "fieldtype": "Int", "width": 150},
        {
            "fieldname": "admissions",
            "label": "Active Admission Records",
            "fieldtype": "Int",
            "width": 190,
        },
        {
            "fieldname": "discharges",
            "label": "Scheduled Discharges",
            "fieldtype": "Int",
            "width": 180,
        },
    ]
    rows = floor_report(filters)
    chart = {
        "data": {
            "labels": [r["floor"] for r in rows],
            "datasets": [{"name": "Patients", "values": [r["patients"] for r in rows]}],
        },
        "type": "bar",
    }
    return (
        columns,
        rows,
        "Current census, restricted to visible Patient and Inpatient Record rows. Counts are distinct per floor, not bed capacity.",
        chart,
    )
