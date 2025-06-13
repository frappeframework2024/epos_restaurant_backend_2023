// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Expense Analytics"] = {
	onload: function(report) {
		frappe.query_report.set_filter_value("start_date", start_of_year()); 					
		frappe.query_report.set_filter_value("end_date", end_of_year());		
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
	},
	"filters": [
		{
			fieldname: "business_branch",
			label: "Business Branch",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Business Branch', txt);
			},
			"on_change": function (query_report) {},
			 
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Group By"),
			"fieldtype": "Select",
			"options": "\nBusiness Branch\nExpense By\nExpense Category\nExpense Code",
			"on_change": function (query_report) {},
			
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Business Branch\nExpense By\nExpense Category\nExpense Code",
			"default":"Expense Code",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group By"),
			"fieldtype": "Select",
			"options": "Daily\nWeekly\nMonthly\nQuarterly\nHalf Yearly\nYearly",
			"default":"None",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default":"bar",
			"on_change": function (query_report) {},
		},
	]
};
function start_of_year()
{
    return new Date(new Date().getFullYear(), 0, 1); // January 1st
}
function end_of_year()
{
    return new Date(new Date().getFullYear(), 11, 31);// December 31st
}
