// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Sale Summary With Product Options"] = {
	onload: function(report) {
		if(frappe.query_report.get_filter_value('parent_row_group')!=="Vendor"){
			frappe.query_report.toggle_filter_display('vendor', true);
		}
		if(frappe.query_report.get_filter_value('row_group')!=="Vendor"){
			frappe.query_report.toggle_filter_display('vendor', true);
		}
		if(frappe.query_report.get_filter_value('filter_based_on')=="This Month"){
			frappe.query_report.toggle_filter_display('from_fiscal_year', true);
			frappe.query_report.toggle_filter_display('start_date', true  );
			frappe.query_report.toggle_filter_display('end_date', true );
		}
		report.page.add_inner_button("Preview Report", function () {
			frappe.call({
				method: 'epos_restaurant_2023.api.api.update_prepare_report_render',
				args: {"report_name":"Sale Summary Report" },
				type: 'POST',
				freeze: true,
				callback: function(resp) {
					frappe.query_report.refresh();
				},
				error: function(err) {
					console.error('Error:', err);
				}
			});			
		});
		
	},
	"filters": [
		{
			fieldname: "business_branch",
			label: "Business Branch",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Business Branch', txt);
			},
			"on_change": function (query_report) {},
			 
		},
		{
			"fieldname":"filter_based_on",
			"label": __("Filter Based On"),
			"fieldtype": "Select",
			"options": ["Fiscal Year","This Month", "Date Range"],
			"default": ["This Month"],
			"reqd": 1,
			on_change: function() { 
				let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
				
				//update select date filter 
				if(filter_based_on=="Fiscal Year"){
					let from_fiscal_year = frappe.query_report.get_filter_value('from_fiscal_year');
					frappe.query_report.set_filter_value("start_date", start_of_year(from_fiscal_year)); 					
					frappe.query_report.set_filter_value("end_date", end_of_year(from_fiscal_year));
					
				}else if( filter_based_on =="This Month"){
					let date = new Date()
					frappe.query_report.set_filter_value("start_date", start_of_month(date)); 					
					frappe.query_report.set_filter_value("end_date", end_of_month(date));
				}else{
					let date = new Date()
					frappe.query_report.set_filter_value("start_date", date); 					
					frappe.query_report.set_filter_value("end_date", date);
				}
				//end update select date filter

				if(filter_based_on!="This Month"){ 
					frappe.query_report.toggle_filter_display('from_fiscal_year', filter_based_on === 'Date Range');
					frappe.query_report.toggle_filter_display('start_date', filter_based_on === 'Fiscal Year'  );
					frappe.query_report.toggle_filter_display('end_date', filter_based_on === 'Fiscal Year' );

				
				}else{
					frappe.query_report.toggle_filter_display('from_fiscal_year', true);
					frappe.query_report.toggle_filter_display('start_date', true  );
					frappe.query_report.toggle_filter_display('end_date', true );

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
			"fieldname":"from_fiscal_year",
			"label": __("Start Year"),
			"fieldtype": "Int",
			"default": (new Date()).getFullYear(),
			"hide_in_filter":1,
			"on_change": function (query_report) {
				let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
				if(filter_based_on=="Fiscal Year"){
					let from_fiscal_year = frappe.query_report.get_filter_value('from_fiscal_year');
					frappe.query_report.set_filter_value("start_date", start_of_year(from_fiscal_year)); 					
					frappe.query_report.set_filter_value("end_date", end_of_year(from_fiscal_year));
				}
			},
		},
		{
			"fieldname": "outlet",
			"label": __("Outlet"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Outlet', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "product_group",
			"label": __("Product Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				
				return frappe.db.get_link_options('Product Category', txt,{"is_group":1});
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "product_category",
			"label": __("Product Category"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				group = frappe.query_report.get_filter_value("product_group");
				if(group==""){
					return frappe.db.get_link_options('Product Category', txt,filters={
						is_group:0
					});
				}
				else {
					return frappe.db.get_link_options('Product Category', txt,filters={
						is_group:0,
						"parent_product_category":["in",group]
					});
				}
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "customer_group",
			"label": __("Customer Group"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				
				return frappe.db.get_link_options('Customer Group', txt);
			},
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options":"Customer",
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "parent_row_group",
			"label": __("Parent Group By"),
			"fieldtype": "Select",
			"options": "\nCategory\nProduct Group\nRevenue Group\nBusiness Branch\nOutlet\nCustomer\nCustomer Group\nStock Location\nDate\n\Month\nYear\nSale Invoice\nVendor",
			on_change: function() { 
				filter = frappe.query_report.get_filter_value('parent_row_group')
				frappe.query_report.toggle_filter_display('vendor',filter !== 'Vendor');
				if(filter !== "vendor"){
					frappe.query_report.set_filter_value("vendor", []);
				}
			},
			
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Product Code\nProduct And Price\nCategory\nProduct Group\nRevenue Group\nBusiness Branch\nOutlet\nCustomer\nCustomer Group\nStock Location\nDate\n\Month\nYear\nSale Invoice\nSeller\nVendor",
			"default":"Category",
			on_change: function() { 
				filter = frappe.query_report.get_filter_value('row_group')
				frappe.query_report.toggle_filter_display('vendor',filter !== 'Vendor');
				if(filter !== "Vendor"){
					frappe.query_report.set_filter_value("vendor", []);
				}
			},
		},
		{
			"fieldname": "column_group",
			"label": __("Column Group By"),
			"fieldtype": "Select",
			"options": "None\nDaily\nWeekly\nMonthly\nQuarterly\nHalf Yearly\nYearly",
			"default":"None",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "hide_columns",
			"label": __("Hide Columns"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return [
					{"value":"Quantity","description":"Quantity"},
					{"value":"Sub Total","description":"Sub Total"},
					{"value":"Discount","description":"Discount"},
					{"value":"Tax","description":"Tax"},
					{"value":"Cost","description":"Cost"},
					{"value":"Profit","description":"Pofit"},
					{"value":"Gross Profit","description":"Gross Pofit"},
					{"value":"Revenue","description":"Revenue"},
				]
			},
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
            fieldname: "vendor",
            label: __("Vendor"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options('Vendor', txt);
            },
			"on_change": function (query_report) {},
        },
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline\npie",
			"default":"bar",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "include_foc",
			"label": __("Include FOC"),
			"fieldtype": "Check",
			hide_in_filter:1,
			"on_change": function (query_report) {},
		},
		{
			"fieldname": "show_summary",
			"label": __("Show Summary"),
			"fieldtype": "Check",
			default:true,
			hide_in_filter:1,
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

function start_of_month(date)
{
    return new Date(date.getFullYear(), date.getMonth(), 1);
}
function end_of_month(date)
{
	let lastDate = new Date(date.getFullYear(), date.getMonth() + 1, 0); 
    return new Date(date.getFullYear(), date.getMonth(), lastDate.getDate() ) ;
}

function start_of_year(year)
{
    return new Date(year, 0, 1); // January 1st
}
function end_of_year(year)
{
    return new Date(year, 11, 31);// December 31st
}

function update_filter_options(filter_name, options) {
    let filter = frappe.query_report.get_filter(filter_name);
    if (filter) {
        let updatedOptions = options;
        filter.df.options = updatedOptions.join("\n");
        filter.refresh();
    } else {
        console.error(`Filter ${filter_name} not found`);
    }
}

function update_row_group_options(default_sale_type) {
    let options = [
        "Product Code","Product And Price","Category", "Product Group", "Revenue Group", "Business Branch", 
        "Outlet", "POS Profile", "Customer", 
        "Customer Group", "Stock Location", "Date", "Month", "Year", 
        "Sale Invoice","Vendor"
    ];
    update_filter_options('row_group', options);
}

function update_parent_row_group_options(default_sale_type) {
    let options = [
        "", "Category", "Product Group", 
        "Revenue Group", "Business Branch", "Outlet", 
        "POS Profile", "Customer", "Customer Group", 
        "Stock Location", "Date", "Month", "Year", "Sale Invoice", 
        "Seller","Vendor"
    ];
    update_filter_options('parent_row_group', options);
}
