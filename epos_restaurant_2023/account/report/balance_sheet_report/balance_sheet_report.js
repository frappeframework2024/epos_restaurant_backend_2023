// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Balance Sheet Report"] = {
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			validate_date(report);
			setTimeout(() => {
				frappe.query_report.refresh();
			}, 100);
		});
		validate_date(report);
	},
	filters: [
		{
			fieldname: "business_branch",
			label: "Business Branch",
			fieldtype: "Link",
			options:"Business Branch",
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname":"filter_based_on",
			"label": __("Filter Based On"),
			"fieldtype": "Select",
			"options": ["Fiscal Year", "Date Range"],
			"default": ["Fiscal Year"],
			"reqd": 1,
			on_change: function() {
				let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
				frappe.query_report.toggle_filter_display('from_fiscal_year', filter_based_on === 'Date Range');
				frappe.query_report.toggle_filter_display('to_fiscal_year', filter_based_on === 'Date Range');
				frappe.query_report.toggle_filter_display('period_start_date', filter_based_on === 'Fiscal Year');
				frappe.query_report.toggle_filter_display('period_end_date', filter_based_on === 'Fiscal Year');

				frappe.query_report.refresh();
			},
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname":"period_start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Date Range'",
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname":"period_end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Date Range'",
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname":"from_fiscal_year",
			"label": __("Start Year"),
			"fieldtype": "Data",
			"default": get_current_fiscal_year(),
			"reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Fiscal Year'",
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname":"to_fiscal_year",
			"label": __("End Year"),
			"fieldtype": "Data",
			"default": get_current_fiscal_year(),
			"reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Fiscal Year'",
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname": "periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Half-Yearly", "label": __("Half-Yearly") },
				{ "value": "Yearly", "label": __("Yearly") }
			],
			"default": "Yearly",
			"reqd": 1,
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check",
			"default": 1,
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname": "show_zero_values",
			"label": __("Show Zero Values"),
			"fieldtype": "Check",
			"default": 0,
			"on_change": function (query_report) {

			},
		}
	],
	tree: true,
	name_field: "account",
	parent_field: "parent_chart_of_account",
	export_hidden_cols: true,
	initial_depth: 3
};

function get_current_fiscal_year() {
	var current_date = new Date();
	var current_year = current_date.getFullYear();
	return current_year;
}

function validate_date(report){
	if (report.get_values().filter_based_on == "Fiscal Year") {
		var from_fiscal_year = report.get_values().from_fiscal_year;
		var to_fiscal_year = report.get_values().to_fiscal_year;
		frappe.query_report.get_filter('period_start_date').set_value(from_fiscal_year + "-01-01");
		frappe.query_report.get_filter('period_end_date').set_value(to_fiscal_year + "-12-31");
	}
}

