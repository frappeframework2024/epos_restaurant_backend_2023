
 
frappe.query_reports["Account AR Aging Report"] = {
	"filters": [
		{
			fieldname: "business_branch",
			label: "Business Branch",
			fieldtype: "Link",
			options:"Business Branch",
			default:frappe.defaults.get_user_default("business_branch") ,
			"reqd": 1,
			"on_change": function (query_report) {

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
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options":"Customer",
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

 