frappe.ui.form.on("Patient", {
    refresh(frm) {
        if (frm.is_new()) return;
        frm.add_custom_button(__("Medical Prescriptions"), () => {
            frappe.set_route("List", "Medical Prescription", {patient: frm.doc.name});
        });
    }
});

