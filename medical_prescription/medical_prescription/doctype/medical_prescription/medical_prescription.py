from frappe.model.document import Document

from medical_prescription.services.prescription import on_update, validate


class MedicalPrescription(Document):
    def validate(self):
        validate(self)

    def on_update(self):
        on_update(self)
