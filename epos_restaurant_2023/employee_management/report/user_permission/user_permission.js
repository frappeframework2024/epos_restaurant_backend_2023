// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.query_reports["User Permission"] = {
	"filters": [
		{
			fieldname: "allow_login_in_pos",
			label: "Allow In POS",
			fieldtype: "Check",
		},
	]
};
