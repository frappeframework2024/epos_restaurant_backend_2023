// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Commission Payment", {
	setup: function(frm) {
		frm.set_query("sale", function() {
			return {
				filters: [
					["Sale","docstatus", "=", "1"],
					["Sale","sale_commission_amount", ">", "0"],
					["Sale","sale_commission_balance", ">", "0"]
				]
			}
		});
	},
    refresh(frm) {

    },
    paid_amount(frm){
		frm.set_value('balance',frm.doc.commission_amount-frm.doc.paid_amount)
		frm.refresh_field('balance')
    }
});
