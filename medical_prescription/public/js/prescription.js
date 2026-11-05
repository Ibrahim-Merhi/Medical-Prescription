/* Native form controls. All clinical mutations use server-authorized endpoints. */
frappe.ui.form.on("Medical Prescription", {
    refresh(frm) {
        render_prescription_overview(frm);
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


function render_prescription_overview(frm) {
    const page = $(frm.wrapper).closest(".page-container");
    page.addClass("medical-prescription-wide");
    if (!document.getElementById("medical-prescription-wide-style")) {
        $("<style id='medical-prescription-wide-style'>").text(`
            .medical-prescription-wide .container {max-width:100%;width:100%}
            .medical-prescription-wide .form-layout,
            .medical-prescription-wide .form-page,
            .medical-prescription-wide .form-section,
            .medical-prescription-wide .section-body,
            .medical-prescription-wide .form-dashboard-section,
            .medical-prescription-wide .form-dashboard {max-width:none!important;width:100%!important;margin-left:0!important;margin-right:0!important}
            .medical-prescription-wide .form-section {padding-left:24px;padding-right:24px}
            .medical-prescription-wide .rx-patient-box {border:1px solid #20a464!important;border-radius:5px!important;padding:7px 16px!important;font-weight:700!important;text-transform:uppercase;background:var(--card-bg)!important;color:var(--text-color)!important}

            .medical-prescription-wide .layout-main-section-wrapper {margin:0}
            .medical-prescription-wide .layout-side-section {display:none}
            .medical-prescription-wide .layout-main-section {width:100%;flex:1;max-width:100%}
            .medical-prescription-wide [data-fieldname="prescription_section"] .section-body {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px}
            .medical-prescription-wide [data-fieldname="prescription_section"] .form-column {width:100%;max-width:100%;padding:0}
            .medical-prescription-wide .rx-preparation {border:1px solid var(--border-color);border-radius:10px;overflow-x:auto;margin:16px 0}
            .medical-prescription-wide .rx-preparation h5 {padding:14px;margin:0;background:var(--subtle-fg)}
            .medical-prescription-wide .rx-preparation table {width:100%;min-width:800px;margin:0}
            .medical-prescription-wide .rx-preparation th,.medical-prescription-wide .rx-preparation td {padding:9px;border:1px solid var(--border-color);font-size:12px}
            @media(max-width:1100px) {.medical-prescription-wide [data-fieldname="prescription_section"] .section-body {grid-template-columns:repeat(2,minmax(0,1fr))}}
            @media(max-width:600px) {.medical-prescription-wide [data-fieldname="prescription_section"] .section-body {grid-template-columns:1fr}}
        `).appendTo(document.head);
    }
    // The export starts with an empty column; four populated columns follow it.
    const header = $(frm.wrapper).find('[data-fieldname="prescription_section"]');
    header.find(".form-column").each(function() {
        if (!$(this).find(".frappe-control[data-fieldname]").length) $(this).hide();
    });
    if (!frm.is_new()) {
        frm.set_intro(__(frm.doc.is_latest_version ? "This is the latest prescription" : "This is a previous prescription version"), frm.doc.is_latest_version ? "green" : "orange");
        frm.add_custom_button((frm.doc.patient_name || frm.doc.patient || __("Patient")).toLocaleUpperCase(), () => frappe.set_route("Form", "Patient", frm.doc.patient)).addClass("rx-patient-box");
        frm.add_custom_button(__("Print Prescription"), () => frm.print_doc());
    }
    const wrapper = frm.fields_dict.custom_schedule_matrix?.$wrapper;
    if (!wrapper) return;
    wrapper.empty();
    const box = $("<div class='rx-preparation'></div>").appendTo(wrapper);
    $("<h5></h5>").text(__("Pharmacy Medication Preparation")).appendTo(box);
    const table = $("<table><thead><tr></tr></thead><tbody></tbody></table>").appendTo(box);
    for (const label of ["Medication", "Dose", "Route", "Freq", "PRN", "Hold", "Time"]) $("<th></th>").text(__(label)).appendTo(table.find("thead tr"));
    for (const row of frm.doc.items || []) {
        const dose = [row.dose_number, row.dose_uom].filter(v => v !== null && v !== undefined && v !== "").join(" ") || row.dosage_custom || row.dosage || "—";
        const tr = $("<tr></tr>").appendTo(table.find("tbody"));
        for (const value of [row.drug_name || row.medication || row.drug, dose, row.route, row.frequency || row.frequencyy, row.prn || "—", row.hold ? __("Yes") : "—", row.custom_time]) $("<td></td>").text(value || "—").appendTo(tr);
    }
    if (!(frm.doc.items || []).length) $("<tr><td colspan='7'></td></tr>").find("td").text(__("No medications on this prescription.")).end().appendTo(table.find("tbody"));
}
frappe.ui.form.on("Medical Prescription Item", {
    items_remove(frm) {render_prescription_overview(frm);},
    drug_name(frm) {render_prescription_overview(frm);},
    dose_number(frm) {render_prescription_overview(frm);},
    dose_uom(frm) {render_prescription_overview(frm);},
    route(frm) {render_prescription_overview(frm);},
    frequency(frm) {render_prescription_overview(frm);},
    prn(frm) {render_prescription_overview(frm);},
    hold(frm) {render_prescription_overview(frm);},
    custom_time(frm) {render_prescription_overview(frm);}
});
