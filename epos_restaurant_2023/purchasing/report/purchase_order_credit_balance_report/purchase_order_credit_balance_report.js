// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Order Credit Balance Report"] = {
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},
	"filters": [
		{
			fieldname: "business_branch",
			label: __("Business Branch"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Business Branch', txt);
			},
			"on_change": function (query_report) {},
			 
		},
		{
			fieldname: "stock_location",
			label: __("Stock Location"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Stock Location', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"on_change": function (query_report) {},	
		},
		{
			"fieldname": "vendor_group",
			"label": __("Vendor Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				
				return frappe.db.get_link_options('Vendor Group', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "vendor",
			"label": __("Vendor"),
			"fieldtype": "Link",
			"options":"Vendor",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_po_transaction",
			"label": __("Show PO Transaction"),
			"fieldtype": "Check",
			"default":0,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			"default":1,
			"on_change": function (query_report) {},
		},
		 

	],
	"formatter": function(value, row, column, data, default_formatter) {
	
		value = default_formatter(value, row, column, data);
		 
		if (data && data.indent==0 && frappe.query_report.get_filter_value('show_po_transaction')==1) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		}
		
		return value;
	},
};
