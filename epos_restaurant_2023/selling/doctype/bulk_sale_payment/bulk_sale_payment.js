// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Sale Payment", {
    setup(frm){
        frm.set_query("sale","sale_list", function() {
            return {
                filters: {
                    balance: ['>', 0],
                    docstatus: ['=', 1]
                }
            }
        });
    },
    on_submit(frm){
        // Check Current call from Iframe
        if (window.self !== window.top) {
           window.parent.postMessage(frm.doc)
        }
    },
	refresh(frm) {
        
        frappe.call({
            method: "get_sale_payment_naming_series",
            doc: frm.doc,
            callback: function (r) {
                frm.set_df_property('sale_payment_naming_series', 'options', r.message);
                frm.refresh_field('sale_payment_naming_series');
            },
        });
        updatetotal(frm);
	},
    customer(frm) {
		if (frm.doc.customer) {
            frm.set_value('sale_list', []);
			frappe.call({
                method: "epos_restaurant_2023.selling.doctype.bulk_sale_payment.bulk_sale_payment.get_sale_by_customer",
                args: {
                    customer:frm.doc.customer
                },
                callback: function(r){
                    r.message.forEach((r => {
                        doc = frm.add_child("sale_list");
                        doc.sale = r.sale;
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
                    frm.refresh_field('sale_list');
                    updatetotal(frm);
                }
            });
		}
	},
    payment_type(frm){ 
        if(frm.doc.sale_list){
            $.each(frm.doc.sale_list, function(i, d) {
                d.payment_type = frm.doc.payment_type;
                d.currency = frm.doc.currency;
                d.exchange_rate = (frm.doc.exchange_rate || 0);
                d.input_amount = d.amount * (d.exchange_rate || 0);
                d.payment_amount = d.input_amount == 0 ? 0 : d.input_amount /  (d.exchange_rate || 0);
                d.balance = d.amount - d.payment_amount;
                frm.refresh_field('sale_list');
                updatetotal(frm);
            });
        }
    },
});

frappe.ui.form.on('Bulk Sale', {
    input_amount(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
        doc.payment_amount = doc.input_amount / doc.exchange_rate
        if(doc.payment_amount>doc.amount){
            doc.payment_amount = doc.amount
            doc.input_amount = doc.amount * doc.exchange_rate
        }
        doc.balance = doc.amount - doc.payment_amount
        frm.refresh_field('sale_list');
        updatetotal(frm);
	},
    sale(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        doc.payment_type = frm.doc.payment_type;
        doc.currency = frm.doc.currency;
        doc.exchange_rate = (frm.doc.exchange_rate || 0);
        doc.input_amount = doc.amount * (doc.exchange_rate || 0);
        doc.payment_amount = doc.input_amount == 0 ? 0 : doc.input_amount /  (doc.exchange_rate || 0);
        doc.balance = doc.amount - doc.payment_amount;
        frm.refresh_field('sale_list');
        updatetotal(frm);
    }
})

function updatetotal(frm){
    const sales = frm.doc.sale_list;
	if (sales == undefined) {
		return false;
	}
    frm.set_value('total_amount', sales.reduce((n, d) => n + d.amount, 0));
	frm.set_value('total_payment_amount', sales.reduce((n, d) => n + d.payment_amount, 0));
	frm.set_value('total_balance', sales.reduce((n, d) => n + d.balance, 0));
	frm.set_value('total_sale', sales.reduce((n, d) => n + 1, 0));
}
