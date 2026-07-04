// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Active Member Report"] = {
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
	},
 "filters": [
	{
			"fieldname": "member_types",
			"label": __("Member Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {	
				return frappe.db.get_link_options('Customer Group', txt,filters={
					disabled: ['=', 0]
				});
			},
			"on_change": function (query_report) {},
		},
	]
};
