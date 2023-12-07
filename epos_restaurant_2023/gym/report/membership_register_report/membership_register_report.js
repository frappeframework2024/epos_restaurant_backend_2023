// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["Membership Register Report"] = {
	"filters": [
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
			"fieldname": "customer",
			"label": __("Member"),
			"fieldtype": "Link",
			"options":"Customer",
			
		},
		{
			"fieldname": "sort_by",
			"label": __("Sort By"),
			"fieldtype": "Select",
			"options": "Member\nDate",
			"default":"Date"
		},
		{
			"fieldname": "sort_type",
			"label": __("Sort Type"),
			"fieldtype": "Select",
			"options": "ASC\nDESC",
			"default":"ASC"		
		}
	]
};
