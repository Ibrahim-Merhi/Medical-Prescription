frappe.ui.form.on("User", {
    refresh(frm) {
        if (frm.doc.name !== frappe.session.user ||
            !["Nurse", "Nursing User"].some(role => frappe.user.has_role(role))) return;
        frm.add_custom_button(__("Set my nurse PIN"), () => {
            const dialog = new frappe.ui.Dialog({
                title: __("Set my nurse PIN"),
                fields: [{fieldname: "pin", label: __("PIN (6 to 12 digits)"), fieldtype: "Password", reqd: 1}],
                primary_action_label: __("Save"),
                async primary_action(values) {
                    await frappe.call({method: "medical_prescription.api.set_my_nurse_pin", args: values});
                    dialog.set_value("pin", "");
                    dialog.hide();
                    frappe.show_alert(__("PIN saved"));
                }
            });
            dialog.show();
        });
    }
});

