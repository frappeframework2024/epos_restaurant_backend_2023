// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Sale Combo Product Breakdown"] = {
	"filters": [
		{
			"fieldname": "start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"on_change": function (query_report) { }
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"on_change": function (query_report) { }
		},
	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
	},
	"formatter": function(value, row, column, data, default_formatter) {
		const origninal_value = value  || 0
		value = default_formatter(value, row, column, data);
		
		
		 
		value = value.toString().replace("style='text-align: right'","style='text-align: " + column.align + "'");	
	 
 
		if (
			(column.fieldtype || "") == "INT" || 
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency" ) 
		) 
		{
			if(origninal_value==0){
				return "-"
			}
		} 


		
		if ((data && data.is_group==1) || (data && data.is_total_row==1)) {
			
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");

			value = $value.wrap("<p></p>").parent().html();
		} 
	 
 
		return value;
	},
};