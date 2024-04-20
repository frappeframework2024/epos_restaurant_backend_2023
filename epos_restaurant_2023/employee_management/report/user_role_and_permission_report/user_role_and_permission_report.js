// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["User Role And Permission Report"] = {
	onload: function(report) { 		
		report.page.add_inner_button("Preview Report", function () {
			report.refresh();
		});
	},

	"filters": [
		{
			fieldname: "user",
			label: "Default All Users",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Employee', txt);
			},
			"on_change": function (query_report) {},			 
		},
	],
	"formatter": function(value, row, column, data, default_formatter) {
		
		value = default_formatter(value, row, column, data);
		console.log(column)
		if ((data && data.indent == 0) || (data && data.is_total_row == 1)) {

			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");


			value = $value.wrap("<p></p>").parent().html();
		}
		if ((column.fieldtype || "") == "Data") {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("text-align", "right");


			value = $value.wrap("<p></p>").parent().html();
		}
		
		return value;
	},
};
