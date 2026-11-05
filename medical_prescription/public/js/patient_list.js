(() => {
    const previous = frappe.listview_settings.Patient || {};
    frappe.listview_settings.Patient = {
        ...previous,
        hide_name_column: true,
        add_fields: [...new Set([...(previous.add_fields || []), "patient_name", "custom_medical_file", "custom_service_unit", "custom_floor"])],
        onload(listview) {
            if (previous.onload) previous.onload(listview);
            // Keep native filtering, permissions and list actions; change presentation only.
            const wanted = ["patient_name", "custom_medical_file", "custom_service_unit", "custom_floor"];
            const original = listview.setup_columns.bind(listview);
            listview.setup_columns = async (...args) => {
                await original(...args);
                if (listview.list_filter?.active_layout_name && listview.list_filter.active_layout_name !== "default_layout") return;
                const columns = listview.columns.filter(c => c.type === "Tag" || wanted.includes(c.df?.fieldname));
                columns.sort((a, b) => (a.type === "Tag" ? 0.5 : wanted.indexOf(a.df?.fieldname)) - (b.type === "Tag" ? 0.5 : wanted.indexOf(b.df?.fieldname)));
                listview.columns = columns;
            };
            listview.setup_columns().then(() => listview.refresh());
        }
    };
})();
