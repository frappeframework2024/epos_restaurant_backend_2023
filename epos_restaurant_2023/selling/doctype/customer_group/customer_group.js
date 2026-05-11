// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Group", {
	onload(frm) {
         frappe.realtime.on("update_allow_earn_point", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: data.color
            });
        });
	},
});
