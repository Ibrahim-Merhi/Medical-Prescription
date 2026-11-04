/* Native form controls. All clinical mutations use server-authorized endpoints. */
frappe.ui.form.on("Medical Prescription", {
    refresh(frm) {
        if (frm.is_new()) return;
        frm.add_custom_button(__("Duplicate prescription"), () => {
            if (frm.is_dirty()) {
                frappe.msgprint(__("Save the prescription first."));
                return;
            }
            frappe.prompt([
                {fieldname: "date", label: __("New prescription date"), fieldtype: "Date", reqd: 1}
            ], async values => {
                const result = await frappe.call({
                    method: "medical_prescription.api.duplicate_medical_prescription",
                    args: {source_name: frm.doc.name, new_prescription_date: values.date},
                    freeze: true
                });
                if (result.message) frappe.set_route("Form", "Medical Prescription", result.message);
            }, __("Duplicate prescription"));
        });
        frm.add_custom_button(__("Record administration"), () => {
            if (frm.is_dirty()) {
                frappe.msgprint(__("Save the prescription first."));
                return;
            }
            const dialog = new frappe.ui.Dialog({
                title: __("Record administration"),
                fields: [
                    {fieldname: "schedule_row", label: __("Administration row ID"), fieldtype: "Select",
                        options: (frm.doc.administration_schedule || []).map(row => ({value: row.name,
                            label: `${row.drug_name || row.medication} — ${row.scheduled_time}`})), reqd: 1},
                    {fieldname: "action", label: __("Action"), fieldtype: "Select", options: ["step_1", "step_2"], reqd: 1},
                    {fieldname: "second_nurse", label: __("Second nurse login"), fieldtype: "Data"},
                    {fieldname: "pin", label: __("Second nurse PIN"), fieldtype: "Password"},
                    {fieldname: "reason", label: __("Delay or override reason"), fieldtype: "Small Text"}
                ],
                primary_action_label: __("Record"),
                async primary_action(values) {
                    await frappe.call({method: "medical_prescription.api.record_administration",
                        args: {prescription: frm.doc.name, ...values}, freeze: true});
                    dialog.set_value("pin", "");
                    dialog.hide();
                    await frm.reload_doc();
                }
            });
            dialog.show();
        });
    }
});

