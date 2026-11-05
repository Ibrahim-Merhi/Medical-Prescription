frappe.pages["medical-overview"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({parent: wrapper, title: __("Medical Dashboard"), single_column: true});
    const root = $("<div class='medical-overview'></div>").appendTo(page.body);
    root.append(`<style>
      .medical-overview {padding:24px;max-width:1400px;margin:auto}
      .medical-overview .metrics {display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin:20px 0}
      .medical-overview .metric,.medical-overview .chart {border:1px solid var(--border-color);border-radius:12px;padding:20px;background:var(--card-bg)}
      .medical-overview .metric strong {display:block;font-size:32px;margin-top:8px}
      .medical-overview .charts {display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
      .medical-overview .actions {display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
      .medical-overview table {width:100%;margin-top:18px}
      .medical-overview th,.medical-overview td {padding:10px;border-bottom:1px solid var(--border-color);text-align:left}
    </style>`);
    $("<p class='text-muted'></p>").text(__("Current census for records you can access. Current inpatients = Admitted + Discharge Scheduled. Floor comes from the Inpatient Record; this is not bed occupancy capacity.")).appendTo(root);
    const actions = $("<div class='actions'></div>").appendTo(root);
    for (const [label, route] of [
        ["Floor Census Report", ["query-report", "Medical Floor Census"]],
        ["Inpatient Census Report", ["query-report", "Medical Inpatient Census"]],
        ["Patients", ["List", "Patient"]],
        ["Prescriptions", ["List", "Medical Prescription"]]
    ]) $("<button class='btn btn-default btn-sm'></button>").text(__(label)).on("click", () => frappe.set_route(...route)).appendTo(actions);
    const content = $("<div aria-live='polite'></div>").appendTo(root);
    let loading = false;
    async function refresh() {
        if (loading) return;
        loading = true;
        content.empty().text(__("Loading census…"));
        try {
            const response = await frappe.call({method: "medical_prescription.dashboard.overview", type: "GET"});
            const data = response.message;
            if (!frappe.Chart) {
                try { await frappe.require("frappe-charts.bundle.js"); }
                catch (error) { console.warn("Medical dashboard chart assets unavailable", error); }
            }
            content.empty();
            $("<p class='text-muted'></p>").text(__("Updated") + ": " + data.as_of).appendTo(content);
            const cards = $("<div class='metrics'></div>").appendTo(content);
            for (const [label, key] of [["Visible patients", "patients"], ["Current inpatients", "inpatients"], ["Scheduled admissions", "scheduled_admissions"], ["Scheduled discharges", "scheduled_discharges"], ["Inpatients without floor", "unassigned"]]) {
                const card = $("<div class='metric'></div>").appendTo(cards);
                $("<span></span>").text(__(label)).appendTo(card);
                $("<strong></strong>").text(data[key]).appendTo(card);
            }
            if (data.duplicate_admissions) $("<p class='text-warning'></p>").text(__("Multiple active admissions exist for some patients. Floor totals may exceed the distinct inpatient total; review the census report.")).appendTo(content);
            const charts = $("<div class='charts'></div>").appendTo(content);
            function chart(title, labels, values, type) {
                const box = $("<div class='chart'></div>").appendTo(charts);
                $("<h4></h4>").text(__(title)).appendTo(box);
                if (!labels.length) { $("<p></p>").text(__("No matching records")).appendTo(box); return; }
                const target = $("<div></div>").appendTo(box)[0];
                if (!frappe.Chart) { $(target).text(__("Chart unavailable. Counts are shown in the table below.")); return; }
                new frappe.Chart(target, {data: {labels, datasets: [{name: __("Count"), values}]}, type, height: 280, colors: ["#168b91", "#527ac7", "#e5a541", "#bd6879"], truncateLegends: true});
            }
            chart("Current inpatients by floor", data.floors.map(r => r.floor), data.floors.map(r => r.patients), "bar");
            if (data.prescription_access) chart("Prescription records by status (all versions)", Object.keys(data.prescription_statuses), Object.values(data.prescription_statuses), "donut");
            const table = $("<table class='table'><thead><tr><th>Floor</th><th>Patients</th><th>Active admission records</th><th>Scheduled discharges</th></tr></thead><tbody></tbody></table>").appendTo(content);
            for (const row of data.floors) {
                const tr = $("<tr></tr>").appendTo(table.find("tbody"));
                const link = $("<button class='btn btn-link btn-sm'></button>").text(row.floor).on("click", () => frappe.set_route("query-report", "Medical Inpatient Census", {floor: row.floor}));
                $("<td></td>").append(link).appendTo(tr);
                for (const key of ["patients", "admissions", "discharges"]) $("<td></td>").text(row[key]).appendTo(tr);
            }
        } catch (error) {
            content.empty().append($("<p class='text-danger'></p>").text(__("Unable to load the dashboard. Check Patient and Inpatient Record read permissions, or review the server error. Use Refresh to retry.")));
        } finally { loading = false; }
    }
    page.set_primary_action(__("Refresh"), refresh, "refresh");
    wrapper.medical_refresh = refresh;
};
frappe.pages["medical-overview"].on_page_show = function(wrapper) { wrapper.medical_refresh(); };
