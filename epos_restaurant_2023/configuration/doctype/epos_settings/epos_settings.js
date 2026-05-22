// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("ePOS Settings", {
    setup(frm){
        frappe.realtime.on("generate_sales_general_ledger", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
		});
    },
    generate_sale_general_ledger(frm){
        frappe.call({
            method: "generate_sale_general_ledger",
            doc: frm.doc,
            callback: function (r) {

            },
        });
    }
});
