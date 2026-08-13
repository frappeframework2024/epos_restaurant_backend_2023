// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Training Schedule Report"] = {
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		const custom_css = `
            <style>
                .datatable .dt-row .dt-cell:first-child .dt-cell__content{
					min-width: 100px !important;
					width: 100px !important;
					align-content: center !important;
				}
            </style>`;
        $(custom_css).appendTo("head");
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
