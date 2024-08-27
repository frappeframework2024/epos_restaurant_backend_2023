// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sale Summary Report"] = {
	onload: function(report) {
		getPosProfileAndUpdateOptions();

        // Add event listener for the POS Profile filter
        frappe.query_report.get_filter('pos_profile').on_change = function() {
            getPosProfileAndUpdateOptions();
        };
		if(frappe.query_report.get_filter_value('filter_based_on')=="This Month"){
			frappe.query_report.toggle_filter_display('from_fiscal_year', true);
			frappe.query_report.toggle_filter_display('start_date', true  );
			frappe.query_report.toggle_filter_display('end_date', true );
		}
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
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
			"on_change": function (query_report) {},
		},
		{
            fieldname: "pos_profile",
            label: __("POS Profile"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options('POS Profile', txt);
            },
            on_change: getPosProfileAndUpdateOptions, // Attach the change handler
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
			"options": "\nCategory\nProduct Group\nRevenue Group\nBusiness Branch\nOutlet\nTable Group\nTable\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nDate\n\Month\nYear\nSale Invoice\nWorking Day\nCashier Shift\nSale Type",
			hide_in_filter:1,
			"on_change": function (query_report) {},
			
		},
		{
			"fieldname": "row_group",
			"label": __("Row Group By"),
			"fieldtype": "Select",
			"options": "Product\nProduct And Price\nCategory\nProduct Group\nRevenue Group\nBusiness Branch\nOutlet\nTable Group\nTable\nPOS Profile\nCustomer\nCustomer Group\nStock Location\nDate\n\Month\nYear\nSale Invoice\nWorking Day\nCashier Shift\nSale Type\nSeller",
			"default":"Category",
			hide_in_filter:1,
			"on_change": function (query_report) {},
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
					{"value":"Profit","description":"Pofit"}
				]
			},
			hide_in_filter:1,
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
function update_filter_options(filter_name, options, hideOptions) {
    let filter = frappe.query_report.get_filter(filter_name);

    if (filter) {
        // Filter out options based on hideOptions array
        let updatedOptions = options.filter(option => !hideOptions.includes(option));
        filter.df.options = updatedOptions.join("\n");
        filter.refresh();
    } else {
        console.error(`Filter ${filter_name} not found`);
    }
}

function update_row_group_options(default_sale_type) {
    let options = [
        "Product","Product And Price","Category", "Product Group", "Revenue Group", "Business Branch", 
        "Outlet", "Table Group", "Table", "POS Profile", "Customer", 
        "Customer Group", "Stock Location", "Date", "Month", "Year", 
        "Sale Invoice", "Working Day", "Cashier Shift", "Sale Type"
    ];

    let hideOptions = [];
    if (default_sale_type === 'Retail Sale') {
        hideOptions = ["Table", "Table Group", "Sale Type"];
    }

    let selectedPosProfiles = frappe.query_report.get_filter_value('pos_profile');
    if (!selectedPosProfiles || selectedPosProfiles.length === 0) {
        hideOptions = hideOptions.concat(["Table", "Table Group", "Sale Type"]);
    }

    update_filter_options('row_group', options, hideOptions);
}

function update_parent_row_group_options(default_sale_type) {
    let options = [
        "", "Category", "Product Group", 
        "Revenue Group", "Business Branch", "Outlet", "Table Group", 
        "Table", "POS Profile", "Customer", "Customer Group", 
        "Stock Location", "Date", "Month", "Year", "Sale Invoice", 
        "Working Day", "Cashier Shift", "Sale Type", "Seller"
    ];

    let hideOptions = [];
    if (default_sale_type === 'Retail Sale') {
        hideOptions = ["Table", "Table Group", "Sale Type"];
    }

    let selectedPosProfiles = frappe.query_report.get_filter_value('pos_profile');
    if (!selectedPosProfiles || selectedPosProfiles.length === 0) {
        hideOptions = hideOptions.concat(["Table", "Table Group", "Sale Type"]);
    }

    update_filter_options('parent_row_group', options, hideOptions);
}

function getPosProfileAndUpdateOptions() {
    let selectedPosProfiles = frappe.query_report.get_filter_value('pos_profile');
    
    if (selectedPosProfiles && selectedPosProfiles.length > 0) {
        // Assuming you need to work with the first selected POS Profile for simplicity
        let posProfile = selectedPosProfiles[0];
        
        // Fetch default_sale_type from the POS Profile
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "POS Profile",
                name: posProfile
            },
            callback: function(response) {
                if (response.message) {
                    let default_sale_type = response.message.default_sale_type || [];
                    update_row_group_options(default_sale_type);
                    update_parent_row_group_options(default_sale_type);
                } else {
                    console.error(`POS Profile ${posProfile} not found`);
                }
            }
        });
    } else {
        // Handle the case where no POS Profile is selected
        update_row_group_options(''); // or any default value
        update_parent_row_group_options(''); // or any default value
    }
}
