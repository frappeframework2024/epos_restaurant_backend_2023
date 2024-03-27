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
    paid_amount(frm){
		frm.set_value('balance',frm.doc.commission_amount-frm.doc.paid_amount)
		frm.refresh_field('balance')
    },
	get_sales(frm){
		frm.call({
            method: 'get_sale_commission',
            doc:frm.doc,
            callback:function(r){
                if(r.message){
                    frm.set_value('employee_commission_sale',r.message);
                }
            },
            async: true,
        });
	},
}),
frappe.ui.form.on('Employee Commission Sale', {
	paid_amount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		row.balance = row.commission_amount - row.paid_amount
		frm.refresh_field('employee_commission_sale')
	  },
});
