(() => {
    async function history(frm, field, method, columns, start = 0, prescriptions = false) {
        const wrapper = frm.fields_dict[field]?.$wrapper;
        if (!wrapper) return;
        const patient = frm.doc.name;
        wrapper.empty().append($("<p class='text-muted'></p>").text(__("Loading…")));
        try {
            const response = await frappe.call({method, type: "GET", args: {patient, start, ...(prescriptions ? {page_length: 21} : {})}});
            if (frm.doc.name !== patient) return;
            const payload = response.message;
            const rows = prescriptions ? payload.slice(0, 20) : payload.rows;
            const more = prescriptions ? payload.length > 20 : payload.has_more;
            wrapper.empty();
            if (!rows.length) {
                $("<div class='alert alert-light border'></div>").text(__(prescriptions ? "No medical prescriptions found for this patient." : "No admissions found for this patient.")).appendTo(wrapper);
            } else {
                if (!prescriptions) $("<h5></h5>").text(__("Admissions History")).appendTo(wrapper);
                const scroll = $("<div style='overflow-x:auto'></div>").appendTo(wrapper);
                const table = $("<table class='table table-bordered'><thead><tr></tr></thead><tbody></tbody></table>").appendTo(scroll);
                for (const [label] of columns) $("<th></th>").text(__(label)).appendTo(table.find("thead tr"));
                $("<th></th>").text(__("Action")).appendTo(table.find("thead tr"));
                for (const row of rows) {
                    const tr = $("<tr></tr>").appendTo(table.find("tbody"));
                    for (const [, key] of columns) $("<td></td>").text(row[key] ?? "—").appendTo(tr);
                    $("<td></td>").append($("<button class='btn btn-default btn-xs'></button>").text(__("Open")).on("click", () => frappe.set_route("Form", prescriptions ? "Medical Prescription" : "Inpatient Record", row.name))).appendTo(tr);
                }
            }
            const nav = $("<div class='flex' style='gap:8px;margin:12px 0'></div>").appendTo(wrapper);
            if (start) $("<button class='btn btn-default btn-sm'></button>").text(__("Previous")).on("click", () => history(frm, field, method, columns, start - 20, prescriptions)).appendTo(nav);
            if (more) $("<button class='btn btn-default btn-sm'></button>").text(__("Next")).on("click", () => history(frm, field, method, columns, start + 20, prescriptions)).appendTo(nav);
        } catch (error) {
            wrapper.empty().append($("<p class='text-muted'></p>").text(__("History could not be loaded. Check your record permissions and retry.")));
            $("<button class='btn btn-default btn-sm'></button>").text(__("Retry")).on("click", () => history(frm, field, method, columns, start, prescriptions)).appendTo(wrapper);
        }
    }
    frappe.ui.form.on("Patient", {
        async refresh(frm) {
            if (frm.is_new()) return;
            history(frm, "custom_admissions_history", "medical_prescription.patient_view.admissions", [["Case Number", "custom_case_number"], ["Inpatient Record", "name"], ["Admission Date", "admission_ordered_for"], ["Discharge Date", "discharge_ordered_date"], ["Status", "status"], ["Department", "medical_department"]]);
            history(frm, "custom_medical_prescription_history", "medical_prescription.api.patient_prescriptions", [["Prescription", "name"], ["Date", "prescription_date"], ["Status", "status"], ["Version", "version_no"]], 0, true);
            const patient = frm.doc.name;
            const create = frm.add_custom_button(__("Create Prescription"), () => {}).addClass("btn-primary").prop("disabled", true);
            const discharge = frm.add_custom_button(__("Finalize Discharge"), () => {}).addClass("btn-danger").prop("disabled", true);
            const notice = $("<div class='medical-patient-action-status text-muted' style='padding:8px 0'></div>");
            frm.fields_dict.custom_admissions_history?.$wrapper.before(notice);
            $(frm.wrapper).find(".medical-patient-action-status").not(notice).remove();
            try {
                const profile = await frappe.call({method: "medical_prescription.patient_view.inpatient_profile", type: "GET", args: {patient}});
                if (frm.doc.name === patient && !frm.is_dirty()) {
                    const values = profile.message.values || {};
                    const changed = Object.fromEntries(Object.entries(values).filter(([key, value]) => (frm.doc[key] ?? "") !== (value ?? "")));
                    if (Object.keys(changed).length && frm.perm.some(p => p.write)) {
                        await frm.set_value(changed);
                        frappe.show_alert({message: __("Inpatient details fetched. Save the Patient to keep these values."), indicator: "blue"});
                    } else if (Object.keys(changed).length) {
                        for (const [key, value] of Object.entries(changed)) {
                            frm.doc[key] = value;
                            frm.refresh_field(key);
                        }
                    }
                }
            } catch (error) {
                notice.text(__("Inpatient details could not be fetched. Check access to the linked Inpatient Record."));
            }
            try {
                const {message: action} = await frappe.call({method: "medical_prescription.patient_view.actions", type: "GET", args: {patient}});
                if (frm.doc.name !== patient) return;
                create.remove();
                discharge.remove();
                const reasons = [];
                if (!action.can_create) reasons.push(__("Create Prescription: your role or create permission does not allow this action."));
                else if (!action.prescribing_enabled) reasons.push(__("Create Prescription: prescribing is pending staging validation."));
                if (!action.can_discharge) reasons.push(__("Finalize Discharge: your role does not allow this action."));
                else if (!action.discharge_enabled) reasons.push(__("Finalize Discharge: discharge is pending staging validation."));
                if (!action.inpatient_record) reasons.push(__("An accessible active Inpatient Record is required."));
                notice.text([notice.text(), ...reasons].filter(Boolean).join(" "));
                {
                    const button = frm.add_custom_button(__("Create Prescription"), () => {
                        if (frm.is_dirty()) { frappe.msgprint(__("Save the Patient before creating a prescription.")); return; }
                        frappe.new_doc("Medical Prescription", {patient, inpatient_record: action.inpatient_record, prescription_date: frappe.datetime.get_today()});
                    }).addClass("btn-primary");
                    button.prop("disabled", !action.can_create || !action.prescribing_enabled || !action.inpatient_record).attr("title", !action.prescribing_enabled ? __("Prescribing requires staging validation.") : !action.inpatient_record ? __("An accessible active admission is required.") : "");
                }
                {
                    const button = frm.add_custom_button(__("Finalize Discharge"), () => {
                        if (frm.is_dirty()) { frappe.msgprint(__("Save the Patient before finalizing discharge.")); return; }
                        frappe.prompt([{fieldname: "reason", label: __("Reason"), fieldtype: "Small Text", reqd: 1}], values => {
                            frappe.confirm(__("Finalize discharge for the current admission?"), async () => {
                                await frappe.call({method: "medical_prescription.api.finalize_discharge", type: "POST", args: {inpatient_record: action.inpatient_record, reason: values.reason}, freeze: true});
                                frm.reload_doc();
                            });
                        }, __("Finalize Discharge"), __("Continue"));
                    }).addClass("btn-danger");
                    button.prop("disabled", !action.can_discharge || !action.discharge_enabled || !action.inpatient_record).attr("title", action.discharge_enabled ? "" : __("Discharge requires staging validation."));
                }
            } catch (error) { notice.text(__("Patient actions could not load. Refresh and check the server error; the buttons remain disabled.")); }
        }
    });
})();
