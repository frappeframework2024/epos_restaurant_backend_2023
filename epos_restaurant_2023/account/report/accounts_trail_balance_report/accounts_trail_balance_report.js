// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Accounts Trail Balance Report"] = {
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		 
	},
	filters: [
		  
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) {

			},
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default:frappe.datetime.get_today(),
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

