// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Mobile Stock Adjustment"] = {
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
			on_change: function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			on_change: function (query_report) {},
		},
		{
			fieldname: "business_branch",
			label: __("Business Branch"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Business Branch', txt);
			},
			on_change: function (query_report) {},
			 
		},
		{
			"fieldname": "stock_location",
			"label": __("Stock Location"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				
				return frappe.db.get_link_options('Stock Location', txt);
			},
			on_change: function (query_report) {},
		}	
	],
	"formatter": function(value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		if (data && data.is_group==1) {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	},
};
