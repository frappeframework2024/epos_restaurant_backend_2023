// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.provide("epos_restaurant_2023.employee_time_sheet_summary");

epos_restaurant_2023.employee_time_sheet_summary = {
  "open_report": function(data) {
    // frappe.msgprint((data))
  }
}


frappe.query_reports["Employee Time Sheet Summary"] = {
	onload: function() {
		switch(frappe.query_report.get_filter_value('filter_based_on')){
			case 'This Month':
				frappe.query_report.toggle_filter_display('from_fiscal_year', true);
				frappe.query_report.toggle_filter_display('start_date', true  );
				frappe.query_report.toggle_filter_display('end_date', true );
				break;
			case 'Fiscal Year':
				frappe.query_report.toggle_filter_display('start_date', true  );
				frappe.query_report.toggle_filter_display('end_date', true );
				break
			default:
				frappe.query_report.toggle_filter_display('from_fiscal_year', true);
				break;
		} 
	},

	"filters": [
				// Business Branch
				{
					fieldname: "business_branch",
					label: "Business Branch",
					fieldtype: "MultiSelectList",
					get_data: function(txt) {
						return frappe.db.get_link_options('Business Branch', txt);
					}
					
				},
				// Date and Date Rang
				{
					"fieldname":"filter_based_on",
					"label": __("Filter Based On"),
					"fieldtype": "Select",
					"options": ["Fiscal Year","This Month", "Date Range"],
					"default": ["This Month"],
					"reqd": 1,
					on_change: function() {
						let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
						if(filter_based_on!="This Month"){ 
							frappe.query_report.toggle_filter_display('from_fiscal_year', filter_based_on === 'Date Range');
							frappe.query_report.toggle_filter_display('start_date', filter_based_on === 'Fiscal Year'  );
							frappe.query_report.toggle_filter_display('end_date', filter_based_on === 'Fiscal Year' );

						
						}else{
							frappe.query_report.toggle_filter_display('from_fiscal_year', true);
							frappe.query_report.toggle_filter_display('start_date', true  );
							frappe.query_report.toggle_filter_display('end_date', true );

						}

						frappe.query_report.refresh();

					}
				},
				{
					"fieldname":"start_date",
					"label": __("Start Date"),
					"fieldtype": "Date",
					default:frappe.datetime.get_today(),

					"reqd": 1
				},
				{
					"fieldname":"end_date",
					"label": __("End Date"),
					"fieldtype": "Date",
					default:frappe.datetime.get_today(),

					"reqd": 1
				},
				{
					"fieldname":"from_fiscal_year",
					"label": __("Start Year"),
					"fieldtype": "Int",
					
					"default": (new Date()).getFullYear()
				},
	],
	"formatter": function(value, row, column, data, default_formatter) {	
		value = default_formatter(value, row, column, data);
		var start_date = frappe.query_report.get_filter_value('start_date')
		var filter_based_on = frappe.query_report.get_filter_value('filter_based_on')
		var end_date = frappe.query_report.get_filter_value('end_date')
		var today = new Date();
		var year = today.getFullYear();
		var month = today.getMonth() + 1; // JavaScript months are zero-based
		var firstDayOfMonth = year + '-' + (month < 10 ? '0' : '') + month + '-01';
		
		if (column.fieldname=="employee_name") {
			if(filter_based_on == "This Month"){
				value = $(`<span><a onclick="epos_restaurant_2023.employee_time_sheet_summary.open_report('${value}')" href='/printview?doctype=Employee&name=${data.employee_code}&format=Employee%20Time%20Sheet&start_date=${firstDayOfMonth}&end_date=${end_date}&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&trigger_print=1'>${value}</a></span>`);
			}else{
				value = $(`<span><a onclick="epos_restaurant_2023.employee_time_sheet_summary.open_report('${value}')" href='/printview?doctype=Employee&name=${data.employee_code}&format=Employee%20Time%20Sheet&start_date=${start_date}&end_date=${end_date}&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&trigger_print=1'>${value}</a></span>`);
			}
			

			var $value = $(value).css("font-weight", "bold");
			// value = "<a target='_blank' href='http://192.168.10.19:1216/printview?doctype=Business%20Branch&name=ESTC%20HOTEL&format=Front%20Desk%20Arrival%20Guest%20Report&&settings=%7B%7D&show_toolbar=0&start_date=2024-02-29&end_date=2024-03-06&_lang=en&refresh=14.15485363871575'"+ "</a>";

			value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	},
};
