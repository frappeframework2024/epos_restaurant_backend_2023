// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Timesheet", {
	setup: function (frm) {
        pfrm = frm;
        frm.fields_dict["time_sheets"].grid.get_field("task").get_query = function (frm, cdt, cdn) {
			return {
				filters: {
					project: pfrm.doc.project,
					status: ["!=", "Cancelled"],
				},
			};
		};
	},
});
