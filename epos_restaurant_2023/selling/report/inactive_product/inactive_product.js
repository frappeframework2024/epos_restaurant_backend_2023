// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Inactive Product"] = {
	"filters": [
		{
			"fieldname": "product_categories",
			"label": __("Product Catrgories"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Product Category', txt);
			},
			"on_change": function (query_report){
				
			}
		},
		{
			"fieldname": "ranges",
			"label": __("Range (Days)"),
			"fieldtype": "Select",
			"options":"30\n45\n60\n90\n120\nCustom",
			"default":"60",
			"on_change": function (query_report){
				if (frappe.query_report.get_filter_value('ranges') == "Custom"){
					frappe.query_report.toggle_filter_display('custom_ranges', false);
				}else{
					frappe.query_report.toggle_filter_display('custom_ranges', true);
				}
			}
		},
		{
			"fieldname": "custom_ranges",
			"label": __("Custom Range (Days)"),
			"fieldtype": "Int",
			"on_change": function (query_report){
				
			}
		},
	],
	onload: function (report) {  
		report.page.add_inner_button("Preview Report", function () {
			report.refresh();
		});		
	},
};
