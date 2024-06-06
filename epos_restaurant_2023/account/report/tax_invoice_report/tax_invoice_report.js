// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Tax Invoice Report"] = {
 
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options: "Business Branch",
			default: frappe.defaults.get_user_default("business_branch"),
			"on_change": function (query_report) {
				setLinkField()
			},
		},
		{
			"fieldname":"timespan",
			"label": __("Timespan"),
			"fieldtype": "Select",
			"options": ["Today","Yesterday","This Month","Next Month","Last Month","This Year","Last Year", "Date Range"],
			"default": ["This Month"],
			hide_in_filter: 1,
			on_change: function() {
				let filter_based_on = frappe.query_report.get_filter_value('timespan');
				if(filter_based_on=="Date Range"){ 
					frappe.query_report.toggle_filter_display('start_date', false  );
					frappe.query_report.toggle_filter_display('end_date', false );
					
				
				}else{
					
					frappe.query_report.toggle_filter_display('start_date', true  );
					frappe.query_report.toggle_filter_display('end_date', true );

				}

			},
			
		},
		{
			"fieldname": "start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth(), 1),
			"reqd": 1,
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default: new Date((new Date()).getFullYear(), (new Date()).getMonth() + 1, 0),
			"on_change": function (query_report) { },
			"reqd": 1
		},

		{
			"fieldname": "room_type",
			"label": __("Room Type"),
			"fieldtype": "Link",
			"options": "Room Type",
			"on_change": function (query_report) { },

		},
		{
			"fieldname": "reservation_type",
			"label": __("Reservation Type"),
			"fieldtype": "Select",
			"options": "\nFIT\nGIT",
			"on_change": function (query_report) { },

		},
		{
			"fieldname": "business_source",
			"label": __("Business Source"),
			"fieldtype": "Link",
			"options": "Business Source",
			"on_change": function (query_report) { },
		},
	
		{
			"fieldname": "guest_type",
			"label": __("Guest Type"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"on_change": function (query_report) { },
		},
		 
		{
			"fieldname": "row_group",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "Tax Invoice Type\nDocument Type",
			"default": "",
			"on_change": function (query_report) { },
			hide_in_filter: 1,
		},
		// {
		// 	"fieldname": "show_columns",
		// 	"label": __("Show Columns"),
		// 	"fieldtype": "MultiSelectList",
		// 	"on_change": function (query_report) { },
		// 	"hide_in_filter": 1,
		// },
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			"default": 1,
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "show_summary_field",
			"label": __("Show Summary Field"),
			"fieldtype": "MultiSelectList",
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default": "bar",
			hide_in_filter: 1,
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "show_chart_series",
			"label": __("Show Chart Series"),
			"fieldtype": "MultiSelectList",
			"on_change": function (query_report) { },
			"hide_in_filter": 1,
		},

	],
	onload: function (report) {
		let filter_based_on = frappe.query_report.get_filter_value('Timespan');
		
		if(filter_based_on=="Date Range"){ 
			frappe.query_report.toggle_filter_display('start_date', false  );
			frappe.query_report.toggle_filter_display('end_date', false );
			
		
		}else{
			frappe.query_report.toggle_filter_display('start_date', true  );
			frappe.query_report.toggle_filter_display('end_date', true );
		}

		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});

		setLinkField()


	},
	"formatter": function (value, row, column, data, default_formatter) {
		const origninal_value = value || 0
		value = default_formatter(value, row, column, data);



		value = value.toString().replace("style='text-align: right'", "style='text-align: " + column.align + "'");


		if (
			(column.fieldtype || "") == "Int" ||
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency")
		) {
			if (origninal_value == 0) {
				return "-"
			}
		}



		if ((data && data.is_group == 1) || (data && data.is_total_row == 1)) {

			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");


			value = $value.wrap("<p></p>").parent().html();
		}


		return value;
	},

};



function setLinkField() {
	const property = frappe.query_report.get_filter_value("property")
		const business_source_filter = frappe.query_report.get_filter('business_source');
		business_source_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		//room type
		const room_type_filter = frappe.query_report.get_filter('room_type');
		room_type_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

		//set option for show fields




		frappe.call({
			method: "edoor.api.utils.get_report_config",

			args: {
				property: property,
				report: "Tax Invoice Report"
			},
			callback: function (r) {
				const show_columns = frappe.query_report.get_filter('show_columns');
				show_columns.df.options = r.message.report_fields.map(x => {
					return {
						value: x.fieldname,
						description: x.label
					}
				})
				const show_chart_series = frappe.query_report.get_filter('show_chart_series');
				show_chart_series.df.options = r.message.report_fields.filter(y=>y.show_in_chart==1).map(x => {
					return {
						value: x.fieldname,
						description: x.label
					}
				})
				
				const show_summary_field = frappe.query_report.get_filter('show_summary_field');
				show_summary_field.df.options = r.message.report_fields.filter(y=>y.show_in_chart==1).map(x => {
					return {
						value: x.fieldname,
						description: x.label
					}
				})
				
			},
			error: function (r) {
				frappe.throw(_("Please update report configuration"))
			},
		});



}