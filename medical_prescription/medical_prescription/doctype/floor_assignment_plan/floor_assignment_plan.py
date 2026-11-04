from frappe.model.document import Document

from medical_prescription.services.floor import validate_plan


class FloorAssignmentPlan(Document):
    def validate(self):
        validate_plan(self)
