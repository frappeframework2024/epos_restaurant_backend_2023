// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Profit and Loss Statement"] = {
	onload: function(report) {
		let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
		if(filter_based_on=="Date Range"){ 
			frappe.query_report.toggle_filter_display('start_date', false  );
			frappe.query_report.toggle_filter_display('end_date', false );
			
		
		}else{
			
			frappe.query_report.toggle_filter_display('start_date', true  );
			frappe.query_report.toggle_filter_display('end_date', true );

		}
		if(filter_based_on=="Fiscal Year"){ 
			frappe.query_report.toggle_filter_display('start_year', false  );
			frappe.query_report.toggle_filter_display('end_year', false );
			
		
		}else{
			
			frappe.query_report.toggle_filter_display('start_year', true  );
			frappe.query_report.toggle_filter_display('end_year', true );

		}
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"reqd": 1,
			"on_change": function (query_report) {

			},
		},
		{
			"fieldname":"filter_based_on",
			"label": __("Filter Based On"),
			"fieldtype": "Select",
			"options": ["Fiscal Year", "Date Range"],
			"default": ["Fiscal Year"],
			"reqd": 1,
			on_change: function() {
				let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
				if(filter_based_on=="Date Range"){ 
					frappe.query_report.toggle_filter_display('start_date', false  );
					frappe.query_report.toggle_filter_display('end_date', false );
					
				
				}else{
					
					frappe.query_report.toggle_filter_display('start_date', true  );
					frappe.query_report.toggle_filter_display('end_date', true );

				}
				if(filter_based_on=="Fiscal Year"){ 
					frappe.query_report.toggle_filter_display('start_year', false  );
					frappe.query_report.toggle_filter_display('end_year', false );
					
				
				}else{
					
					frappe.query_report.toggle_filter_display('start_year', true  );
					frappe.query_report.toggle_filter_display('end_year', true );

				}
			},
			
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname":"start_year",
			"label": __("Start Year"),
			"fieldtype": "Int",
			"on_change": function (query_report) {},
			"default": (new Date()).getFullYear(),
			hide_in_filter:1,
		},
		{
			"fieldname":"end_year",
			"label": __("End Year"),
			"fieldtype": "Int",
			"on_change": function (query_report) {},
			"default": (new Date()).getFullYear(),
			hide_in_filter:1,
		},
		// {
		// 	"fieldname":"periodicity",
		// 	"label":_("Periodicity"),
		// 	"fieldtype":"Select",
		// 	"options": "Monthly\nQuarterly\nHalf-Yearly\nYearly",
		// 	"default":"Yearly",
		// 	"on_change": function (query_report) {},
		// },
		{
			"fieldname": "column_group",
			"fieldtype":"Select",
			"label": __("Column Group"),
			"on_change": function (query_report){ },
			"hide_in_filter": 1,
			"options": "Monthly\nQuarterly\nHalf-Yearly\nYearly",
			"default":"Yearly",
		},
		
	],
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
				return "<div style='text-align:" + (column.align || "left") + ";'>-</div>"
			}
		}



		if ((data && data.is_group == 1) || (data && data.is_total_row == 1) || (data && data.indent == 0)) {

			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");


			value = $value.wrap("<p></p>").parent().html();
		}


		return value;
	},
};
function setLinkField() {
	const property = frappe.query_report.get_filter_value("property")
	if (property) {
		const room_type_filter = frappe.query_report.get_filter('room_types');
		room_type_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};
		const business_source_filter = frappe.query_report.get_filter('business_source');
		business_source_filter.df.get_query = function () {
			return {
				filters: {
					"property": property
				}
			};
		};

	}

	frappe.call({
		method: "edoor.api.utils.get_report_config",

		args: {
			property: property,
			report: "Arrival Guest Report"
		},
		callback: function (r) {
			const show_columns = frappe.query_report.get_filter('show_columns');
			show_columns.df.options = r.message.report_fields.map(x => {
				return {
					value: x.fieldname,
					description: x.label
				}
			})

			const show_in_summary = frappe.query_report.get_filter('show_in_summary');
			show_in_summary.df.options = r.message.report_fields.filter(y=>y.show_in_summary==1).map(x => {
				return {
					value: x.fieldname,
					description: x.label
				}
			})
			// const show_in_group_by = frappe.query_report.get_filter('show_in_group_by');
			// show_in_group_by.df.options = r.message.report_fields.filter(y=>y.show_in_group_by==1).map(x => {
			// 	return {
			// 		value: x.fieldname,
			// 		description: x.label
			// 	}
			// })
		},
		error: function (r) {
			frappe.throw(_("Please update report configuration"))
		},
	});


}
