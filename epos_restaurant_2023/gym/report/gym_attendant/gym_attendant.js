// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt
frappe.query_reports["GYM Attendant"] = {
	"filters": [
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),	
			"on_change": function (query_report) { },		 
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) { },
			"reqd": 1
		},
		{
			"fieldname":"member",
			"label": __("Member"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Customer', txt);
			},
			"on_change": function (query_report) { },
			
		}
	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			report.refresh();
		});
		
	},
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


