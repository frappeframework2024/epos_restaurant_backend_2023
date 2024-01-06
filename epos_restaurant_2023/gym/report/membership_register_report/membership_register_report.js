// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Membership Register Report"] = {
	"filters": [
		{
			"fieldname":"start_date",
			"label": __("Register (Start Date)"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),	
			"on_change": function (query_report) { },		 
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("Register (End Date)"),
			"fieldtype": "Date",
			default:frappe.datetime.get_today(),
			"on_change": function (query_report) { },
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label": __("Member"),
			// "fieldtype": "Link",
			// "options":"Customer",
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Customer', txt,{"disabled": ['in',[1,0]]});
			},
			"on_change": function (query_report) { },
			
		},
		{
			"fieldname": "personal_trainer",
			"label": __("Trainer"),
			
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				frappe.call({
					"method": 'epos_restaurant_2023.api.gym.get_trainer_link_option',
					"args": {
						"name": txt
					},
					callback: function (r) {
						console.log(r)
					}
				});
				const data = frappe.db.get_link_options('Trainer', txt,{"disabled": ['in',[0]]})
				return data;
			},
			"on_change": function (query_report) { },
			
		},
		{
			"fieldname": "sort_by",
			"label": __("Sort By"),
			"fieldtype": "Select",
			"options": "Member Code\nMember\nRegister Date",
			"default":"Register Date",
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "sort_type",
			"label": __("Sort Type"),
			"fieldtype": "Select",
			"options": "ASC\nDESC",
			"default":"ASC"		,
			"on_change": function (query_report) { },
		},
		{
			"fieldname": "is_all_transaction",
			"label": __("All Transaction"),
			"fieldtype": "Check",
			"default":"0"		,
			"on_change": function (query_report) { 
				let is_all_transaction = query_report.get_filter_value('is_all_transaction');
				query_report.toggle_filter_display('end_date', is_all_transaction === 1 );
				query_report.toggle_filter_display('start_date', is_all_transaction === 1 );				
			}, 
		}
	],
	onload: function (report) {
		report.page.add_inner_button("Preview Report", function () {
			frappe.query_report.refresh();
		});

		let is_all_transaction = report.get_filter_value('is_all_transaction');
		report.toggle_filter_display('end_date', is_all_transaction === 1 );
		report.toggle_filter_display('start_date', is_all_transaction === 1 );
		report.refresh();
	},
};
