// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt
 
 
frappe.query_reports["AR Aging Summary"] = {
	"filters": [
		{
			fieldname: "property",
			label: "Property",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"reqd": 1,
			"on_change": function (query_report) {
				const property = frappe.query_report.get_filter_value("property")
				const business_source_filter =frappe.query_report.get_filter('business_source');
				business_source_filter.df.get_query = function() {
					return {
						filters: {
							"property": property
						}
					};
				};

			 
				//set fitler city ledger
				const city_ledger =frappe.query_report.get_filter('city_ledger');
				city_ledger.df.get_query = function() {
					return {
						filters: {
							"property": property
						}
					};
				};
				  
			 

 

				 
			},
		},
		{
			"fieldname":"date",
			"label": __("Date"),
			"fieldtype": "Date",
			default: new Date(),
			"reqd": 1,
			"on_change": function (query_report) {},
		},
		 
  
		{
			"fieldname": "city_ledger",
			"label": __("City Ledger"),
			"fieldtype": "Link",
			"options":"City Ledger",
			"on_change": function (query_report) {},
		},
		 
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			"default":1,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_chart",
			"label": __("Show Chart"),
			"fieldtype": "Check",
			"default":1,
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},

	],
	onload: function(report) {
		report.page.add_inner_button ("Preview Report", function () {
			frappe.query_report.refresh();
		});
		 
	},
	"formatter": function(value, row, column, data, default_formatter) {
		const origninal_value = value  || 0
		value = default_formatter(value, row, column, data);
		
		
		 
		value = value.toString().replace("style='text-align: right'","style='text-align: " + column.align + "'");	
	 
 
		if (
			(column.fieldtype || "") == "Int" || 
			((column.fieldtype || "") == "Percent") ||
			((column.fieldtype || "") == "Currency" ) 
		) 
		{
			if(origninal_value==0){
				return "-"
			}
		} 


		
		if ((data && data.is_group==1) || (data && data.is_total_row==1)) {
			
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		} 
	 
 
		return value;
	},
	
};

 