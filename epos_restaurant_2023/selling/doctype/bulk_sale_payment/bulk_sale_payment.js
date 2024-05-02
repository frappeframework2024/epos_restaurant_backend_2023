// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Sale Payment", {
	refresh(frm) {

	},
    customer(frm) {
		if (frm.doc.customer) {
			frappe.call({
                method: "epos_restaurant_2023.selling.doctype.bulk_sale_payment.bulk_sale_payment.get_sale_by_customer",
                args: {
                    customer:frm.doc.customer,
                    payment_type:frm.doc.payment_type
                },
                callback: function(r){
                    r.message.forEach((r => {
                        doc = frm.add_child("sale_list");
                        doc.sale = r.sale;
                        doc.amount = r.amount;
                        doc.payment_type = r.payment_type;
                        doc.payment_amount = r.balance == r.amount ? r.amount : r.payment_amount;
                        doc.balance = r.balance == r.amount ? 0 : r.balance;
                    }))
                    frm.refresh_field('sale_list');
                    updatetotal(frm);
                }
            });
		}
	},
});

function updatetotal(frm){
    const sales = frm.doc.sale_list;
	if (sales == undefined) {
		return false;
	}
    frm.set_value('total_amount', sales.reduce((n, d) => n + d.amount, 0));
	frm.set_value('total_payment_amount', sales.reduce((n, d) => n + d.payment_amount, 0));
	frm.set_value('total_balance', sales.reduce((n, d) => n + d.balance, 0));
}
