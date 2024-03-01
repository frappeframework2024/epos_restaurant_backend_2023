// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

// frappe.query_reports["Employee Time Sheet Detail"] = {
// 	"filters": [

// 	]
// };
// // Copyright (c) 2023, Tes Pheakdey and contributors
// // For license information, please see license.txt
// /* eslint-disable */
// frappe.provide("epos_restaurant_2023.employee_time_sheet_summary");

// epos_restaurant_2023.employee_time_sheet_summary = {
//   "open_report": function(data) {
//     // frappe.msgprint((data))
//   }
// }


frappe.query_reports["Employee Time Sheet Detail"] = {

	"filters": [
				// Business Branch
				{
					fieldname: "business_branch",
					label: "Business Branch",
					fieldtype: "Link",
					options:"Business Branch",
					default: frappe.defaults.get_user_default("business_branch"),
					"reqd": 1,

					
				},

				{
					"fieldname":"start_date",
					"label": __("Start Date"),
					"fieldtype": "Date",
					default:frappe.datetime.get_today(),

					"reqd": 1
				},
				{
					"fieldname":"end_date",
					"label": __("End Date"),
					"fieldtype": "Date",
					default:frappe.datetime.get_today(),

					"reqd": 1
				},
				{
					"fieldname":"sale_number",
					"label": __("Sale Number"),
					"fieldtype": "Link",
					"options":"Sale",
				},

	],
	"formatter": function(value, row, column, data, default_formatter) {	
		value = default_formatter(value, row, column, data);
		
		return value;
	},
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
	},
};
