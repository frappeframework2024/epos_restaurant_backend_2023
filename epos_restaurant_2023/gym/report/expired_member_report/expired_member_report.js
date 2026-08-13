// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Expired Member Report"] = {
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		if(frappe.query_report.get_filter_value('filter_based_on') != "Custom"){
			frappe.query_report.toggle_filter_display('start_date', true  );
			frappe.query_report.toggle_filter_display('end_date', true );
		}
		const custom_css = `
            <style>
                .datatable .dt-row .dt-cell:first-child .dt-cell__content{
					min-width: 100px !important;
					width: 100px !important;
					align-content: center !important;
				}
            </style>`;
        $(custom_css).appendTo("head");
	},
	"filters": [
		{
			"fieldname":"filter_based_on",
			"label": __("Based On"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": ["Today", "7 Days", "15 Days","30 Days","3 Months","6 Months","9 Months","12 Months","Custom"],
			"default": "Today",
			"on_change": function (query_report) {
				let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
				if(filter_based_on === "Custom"){
					frappe.query_report.toggle_filter_display('start_date', false  );
					frappe.query_report.toggle_filter_display('end_date', false );
				}
				else{
					frappe.query_report.toggle_filter_display('start_date', true  );
					frappe.query_report.toggle_filter_display('end_date', true );
				}
			},
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
	]
};
