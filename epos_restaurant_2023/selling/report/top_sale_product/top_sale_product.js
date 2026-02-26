// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
/* eslint-disable */
 
frappe.query_reports["Top Sale Product"] = {
	
	"filters": [
		{
			fieldname: "business_branch",
			label: __("Business Branch"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Business Branch', txt);
			},
			"reqd": 1,
			"on_change": function (query_report) {},
			 
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "outlet",
			"label": __("Outlet"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Outlet', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"top",
			"label": __("Top"),
			"fieldtype": "Int",
			"default":50,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"default":"Sale Amount",
			"options":"Sale Amount\nQuantity Sold",
			"on_change": function (query_report) {},
		},
		
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
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},
	
};

 