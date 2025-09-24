// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Accounts Trail Balance Report"] = {
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		var fiscal_year = report.get_values().fiscal_year;
		frappe.query_report.set_filter_value({
			from_date: fiscal_year+"-01-01",
			to_date: fiscal_year+"-12-31",
		});
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
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Int",
			"on_change": function (query_report) {},
			"default": (new Date()).getFullYear(),
			reqd: 1,
			on_change: function (query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.query_report.set_filter_value({
						from_date: fiscal_year+"-01-01",
						to_date: fiscal_year+"-12-31",
					});
			},
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			"on_change": function (query_report) {

			},
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			"on_change": function (query_report) {

			},
		},
		{
			fieldname: "show_zero_values",
			label: __("Show zero values"),
			fieldtype: "Check",
			"on_change": function (query_report) {

			},
		},
		{
			fieldname: "show_net_values",
			label: __("Show net values in opening and closing columns"),
			fieldtype: "Check",
			default: 1,
			"on_change": function (query_report) {

			},
		},
		{
			fieldname: "show_group_accounts",
			label: __("Show Group Accounts"),
			fieldtype: "Check",
			default: 1,
			"on_change": function (query_report) {

			},
		},
	],
	tree: true,
	name_field: "account",
	parent_field: "parent_chart_of_account",
	export_hidden_cols: true,
	initial_depth: 3,
};

