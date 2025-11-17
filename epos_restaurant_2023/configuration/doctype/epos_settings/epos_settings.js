// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("ePOS Settings", {
	get_site_id(frm) {
        frappe.call({
            method: "get_site_id",
            doc: frm.doc,
            callback: function (r) {
				frm.set_value("site_id",r.message)
                frm.refresh_field('site_id');
				frm.save()
            },
        });
	},
});
