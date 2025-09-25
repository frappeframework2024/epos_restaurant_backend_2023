 
 
 
frappe.query_reports["Coupon Transaction Summary"] = {
	
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
			"fieldname": "pos_profile",
			"label": __("POS Profile"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('POS Profile', txt);
			},
			"on_change": function (query_report) {},
			"hidden":1
		},
		{
			"fieldname": "chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			"options": "None\nbar\nline",
			"default":"bar",
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

		if (data && data.is_total_row==1) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			

			value = $value.wrap("<p></p>").parent().html();
		}
		
		return value;
	},
	onload: function(report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});
		
	},
	
};

 