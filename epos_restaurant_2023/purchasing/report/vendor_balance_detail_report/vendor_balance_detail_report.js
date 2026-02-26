// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Vendor Balance Detail Report"] = {
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
			"on_change": function (query_report) {}
			 
		},
		{
			fieldname: "vendor",
			label: __("Vendor"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Vendor', txt);
			},
			"on_change": function (query_report) {}
		},
		{
			fieldname: "stock_location",
			label: __("Stock Location"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Stock Location', txt);
			},
			"on_change": function (query_report) {}
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"reqd": 1,
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) {}
		},
		
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) {}
		},

	
	],
	"formatter": function(value, row, column, data, default_formatter) {
	
		value = default_formatter(value, row, column, data);

		if (data && data.indent==0) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		}
		if(data && data.is_separate){
			value=""
		}
	 
		if(data && (data.operation_balance || 0 ) <0 && column.fieldname=="operation_balance"){
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("color", "red");
			

			value = $value.wrap("<p></p>").parent().html();
		}
		
		return value;
	},

	
	
};