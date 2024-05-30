// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Purchase Order Payment", {
    setup(frm){
        frm.set_query("purchase_order","purchase_order_list", function() {
            return {
                filters: {
                    balance: ['>', 0],
                    docstatus: ['=', 1]
                }
            }
        });
    },
	refresh(frm) {
        updatetotal(frm);
	},
    vendor(frm) {
		if (frm.doc.vendor) {
            frm.set_value('purchase_order_list', []);
			frappe.call({
                method: "epos_restaurant_2023.purchasing.doctype.bulk_purchase_order_payment.bulk_purchase_order_payment.get_purchase_order_by_vendor",
                args: {
                    vendor:frm.doc.vendor
                },
                callback: function(r){
                    r.message.forEach((r => {
                        doc = frm.add_child("purchase_order_list");
                        doc.purchase_order = r.purchase_order;
                        doc.amount = r.balance;
                        doc.payment_type = frm.doc.payment_type;
                        doc.currency = frm.doc.currency;
                        doc.exchange_rate = (frm.doc.exchange_rate || 0);
                        doc.input_amount = doc.amount * (doc.exchange_rate || 0);
                        doc.payment_amount = doc.input_amount == 0 ? 0 : doc.input_amount /  (doc.exchange_rate || 0);
                        doc.balance = doc.amount - doc.payment_amount;
                        doc.posting_date = frm.doc.posting_date,
                        doc.stock_location = r.stock_location
                    }))
                    frm.refresh_field('purchase_order_list');
                    updatetotal(frm);
                }
            });
		}
	},
    payment_type(frm){ 
        if(frm.doc.purchase_order_list.length > 0){
            $.each(frm.doc.purchase_order_list, function(i, d) {
                d.payment_type = frm.doc.payment_type;
                d.currency = frm.doc.currency;
                d.exchange_rate = (frm.doc.exchange_rate || 0);
                d.input_amount = d.amount * (d.exchange_rate || 0);
                d.payment_amount = d.input_amount == 0 ? 0 : d.input_amount /  (d.exchange_rate || 0);
                d.balance = d.amount - d.payment_amount;
                frm.refresh_field('purchase_order_list');
                updatetotal(frm);
            });
        }
    },
});

frappe.ui.form.on('Bulk Purchase Order', {
    input_amount(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
        doc.payment_amount = doc.input_amount / doc.exchange_rate
        if(doc.payment_amount>doc.amount){
            doc.payment_amount = doc.amount
            doc.input_amount = doc.amount * doc.exchange_rate
        }
        doc.balance = doc.amount - doc.payment_amount
        frm.refresh_field('purchase_order_list');
        updatetotal(frm);
	},
    purchase_order(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        doc.payment_type = frm.doc.payment_type;
        doc.currency = frm.doc.currency;
        doc.exchange_rate = (frm.doc.exchange_rate || 0);
        doc.input_amount = doc.amount * (doc.exchange_rate || 0);
        doc.payment_amount = doc.input_amount == 0 ? 0 : doc.input_amount /  (doc.exchange_rate || 0);
        doc.balance = doc.amount - doc.payment_amount;
        frm.refresh_field('purchase_order_list');
        updatetotal(frm);
    }
})

function updatetotal(frm){
    const purchase_orders = frm.doc.purchase_order_list;
	if (purchase_orders == undefined) {
		return false;
	}
    frm.set_value('total_amount', purchase_orders.reduce((n, d) => n + d.amount, 0));
	frm.set_value('total_payment_amount', purchase_orders.reduce((n, d) => n + d.payment_amount, 0));
	frm.set_value('total_balance', purchase_orders.reduce((n, d) => n + d.balance, 0));
	frm.set_value('total_purchase_order', purchase_orders.reduce((n, d) => n + 1, 0));
}
