// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Training Attendance Report"] = {
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
			"fieldname":"start_date",
			"label": __("Training (Start Date)"),
			"fieldtype": "Date",
			"default":frappe.datetime.get_today(),	
			"on_change": function (query_report) { },		 
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("Training (End Date)"),
			"fieldtype": "Date",
			"default":frappe.datetime.get_today(),
			"on_change": function (query_report) { },
			"reqd": 1
		},

		
		{
			"fieldname": "class_type",
			"label": __("Class Type"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				 // Fetch all the available training times
				 return frappe.db.get_list('GYM Class Types', {
					filters: {
						'name': ['like', '%' + txt + '%'] // Adjust this filter as necessary
					},
					fields: ['name', 'disabled'],
					order_by: 'name ASC'  // Sort based on 'sort_order' field
				}).then(function(results) {
					// Map the results to match the expected format
					return results.map(function(row) {
						let description = __("Actived");
						if(row.disabled == 1){
							description = __("Disabled");
						}
						return {
							value: row.name, // Or any field you want to display as the value
							description: description // Or another field for description if needed
						};
					});
				});
			},
			"on_change": function (query_report) { },
			
		},
		{
			"fieldname": "time_training",
			"label": __("Time Training"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				 // Fetch all the available training times
				 return frappe.db.get_list('GYM Training Time', {
					filters: {
						'name': ['like', '%' + txt + '%'] // Adjust this filter as necessary
					},
					fields: ['name', 'typical_time', 'sort_order'],
					order_by: 'sort_order ASC'  // Sort based on 'sort_order' field
				}).then(function(results) {
					// Map the results to match the expected format
					return results.map(function(row) {
						return {
							value: row.name, // Or any field you want to display as the value
							description: row.typical_time // Or another field for description if needed
						};
					});
				});
			},
			"on_change": function (query_report) { },
			
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
