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
            frappe.call({
                method: 'epos_restaurant_2023.selling.doctype.customer.customer.get_unpaid_bills', 
                args: {
                    name: frm.doc.customer,
                    is_payment:1,
                    bulk_sale_payment:frm.doc.name
                },
                callback: function(response) { 
                    if (response.message) {
                        window.parent.postMessage({"data":frm.doc,"action":"AfterPayment"},"*")
                    }
                }
            })
          
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
    stock_location(frm) {
		if (frm.doc.customer) {
            // get default default fee amount
            frm.set_value('sale_list', []);
            if (frm.doc.payment_type){
                frappe.db.get_value("Payment Type",frm.doc.payment_type,["default_fee_amount"]).then((fee_response)=>{
                    frappe.call({
                        method: "epos_restaurant_2023.selling.doctype.bulk_sale_payment.bulk_sale_payment.get_sale_by_customer",
                        args: {
                            customer:frm.doc.customer,
                            stock_location:frm.doc.stock_location
                        },
                        callback: function(r){
                            r.message.forEach((r => {
                                doc = frm.add_child("sale_list");
                                doc.sale = r.sale;
                                doc.sale_amount = r.balance;
                                doc.fee_amount = r.balance * (fee_response.message.default_fee_amount > 0 ? (fee_response.message.default_fee_amount/100):1);
                                doc.amount = r.balance + (r.balance * (fee_response.message.default_fee_amount > 0 ? (fee_response.message.default_fee_amount/100):1));
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
                });
            }else{
              
                    frappe.call({
                        method: "epos_restaurant_2023.selling.doctype.bulk_sale_payment.bulk_sale_payment.get_sale_by_customer",
                        args: {
                            customer:frm.doc.customer
                        },
                        callback: function(r){
                            r.message.forEach((r => {
                                doc = frm.add_child("sale_list");
                                doc.sale = r.sale;
                                doc.sale_amount = r.balance;
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
		}
        else{
            frappe.throw("Please Select Customer First")
        }
	},
    payment_type(frm){ 
        if(frm.doc.sale_list){
            frappe.db.get_value("Payment Type",frm.doc.payment_type,["default_fee_amount"]).then((fee_response)=>{
                $.each(frm.doc.sale_list, function(i, d) {
                    backup_sale = JSON.parse(JSON.stringify(d))
                    if (fee_response.message.default_fee_amount > 0){
                        d.input_amount = doc.sale_amount;
                        d.fee_amount = d.sale_amount * (fee_response.message.default_fee_amount > 0 ? (fee_response.message.default_fee_amount/100):1);
                        d.amount = d.sale_amount + (d.sale_amount * (fee_response.message.default_fee_amount > 0 ? (fee_response.message.default_fee_amount/100):1));
                        console.log(d.fee_amount)
                    }else{
                        d.fee_amount = 0;
                        d.amount = d.sale_amount
                        d.input_amount = d.sale_amount
                    }
                    
                    d.payment_type = frm.doc.payment_type;
                    d.currency = frm.doc.currency;
                    d.exchange_rate = (frm.doc.exchange_rate || 0);
                    d.input_amount = d.sale_amount * (d.exchange_rate || 0);
                    d.payment_amount = d.input_amount == 0 ? 0 : d.input_amount /  (d.exchange_rate || 0);
                    d.balance = d.amount - d.payment_amount - d.fee_amount
                });
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
