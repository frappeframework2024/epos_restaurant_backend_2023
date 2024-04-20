// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Sale Summary Report V2"] = {
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},

	"filters": [
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

	],
	"formatter": function(value, row, column, data, default_formatter) {
		
		value = default_formatter(value, row, column, data);
		console.log(value)
		if ((data && data.indent == 0) || (data && data.is_total_row == 1)) {
			value = `<span style="font-weight: bold; display: block;">${value}</span>`;
		}
		if ((column.fieldtype || "") == "Data") {
			value = `<span style="text-align: right; display: block;">${value}</span>`;
		}
		if ((column.fieldname || "") == "total_qty") {
			value = `<span style="text-align: center; display: block;">${value}</span>`;
		}
		
		return value;
	},
	
};

