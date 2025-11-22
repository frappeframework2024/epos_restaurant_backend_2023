// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Printer", {
	setup(frm) {
    frappe.realtime.on("update_printer_to_products", (data) => {
                frappe.show_alert({
                    message: data.message,
                    indicator: 'blue'
                });
        });
	},
});
