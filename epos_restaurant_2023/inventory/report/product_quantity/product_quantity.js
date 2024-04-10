// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt
 
 
frappe.query_reports["Product Quantity"] = {
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
			"fieldname": "stock_location",
			"label": __("Stock Location"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Stock Location', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "product_category",
			"label": __("Product Category"),
			"fieldtype": "Link",
			"options": "Product Category",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_product_option",
			"label": __("Show Product Option"),
			"fieldtype": "Select",
			"options": "All Products\nProduct Out of Stock\nProduct to Order\nProduct Expired\nProduct Expired Within Day",
			"default": "All Products",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "expired_day",
			"label": __("Expired Within"),
			"fieldtype": "Int",
			
			"default": 7,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "order_by",
			"label": __("Order By"),
			"fieldtype": "Select",
			"options": "Product Name\nProduct Code\nCategory\nQuantity\nExpired Date",
			"default": "Product Name",
			"on_change": function (query_report) {},
			hide_in_filter:1,
		},
		{
			"fieldname": "order_by_type",
			"label": __("Order By Type"),
			"fieldtype": "Select",
			"options": "ASC\nDesc",
			"default":"ASC",
			hide_in_filter:1,
			"on_change": function (query_report) {},
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
 
