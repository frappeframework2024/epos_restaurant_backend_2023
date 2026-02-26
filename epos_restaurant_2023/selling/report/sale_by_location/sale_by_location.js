// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Sale By Location"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Busuiness Branch"),
			"fieldtype": "Link",
			"options": "Business Branch",
			"reqd": 1,
			on_change: function (query_report) {},
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px",
			on_change: function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px",
			on_change: function (query_report) {},
		},
		{
			"fieldname":"province",
			"label": __("Province"),
			"fieldtype": "MultiSelectList",
			"options": "Province",
			get_data: function(txt) {
				return frappe.db.get_link_options('Province', txt, {});
			},
			on_change: function (query_report) {},
		},
		{
			"fieldname":"district",
			"label": __("District"),
			"fieldtype": "MultiSelectList",
			"options": "District",
			get_data: function(txt) {
				return frappe.db.get_link_options('District', txt, {});
			},
			on_change: function (query_report) {},
		},
		{
			"fieldname":"commune",
			"label": __("Commune"),
			"fieldtype": "MultiSelectList",
			"options": "Commune",
			get_data: function(txt) {
				return frappe.db.get_link_options('Commune', txt, {});
			},
			on_change: function (query_report) {},
		},
		{
			"fieldname":"village",
			"label": __("Village"),
			"fieldtype": "MultiSelectList",
			"options": "Village",
			get_data: function(txt) {
				return frappe.db.get_link_options('Village', txt, {});
			},
			on_change: function (query_report) {},
		},
	],
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},
};
