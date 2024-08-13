// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Entry", {
	mode_of_payment(frm) {
        get_mode_of_payment_detail(frm)
	},
    payment_type(frm){
        get_mode_of_payment_detail(frm)
    },
    party_type(frm){
        get_mode_of_payment_detail(frm)
    },
    party(frm){
        frappe.call({
            method: 'epos_restaurant_2023.account.doctype.payment_entry.payment_entry.get_party_detail',
            args: {
                party_type: frm.doc.party_type,
                party: frm.doc.party,
                posting_date: frm.doc.posting_date
            },
            callback: (r) => {
                frm.set_value("party_name",r.message.name)
                frm.set_value("party_balance",r.message.balance)
            }
        })
    }
});

function get_mode_of_payment_detail(frm){
    frappe.call({
        method: 'epos_restaurant_2023.account.doctype.payment_entry.payment_entry.get_mode_of_payment_detail',
        args: {
            branch: frm.doc.business_branch,
            mode_of_payment: frm.doc.mode_of_payment,
            party_type: frm.doc.party_type
        },
        callback: (r) => {
            frm.set_value("account_paid_from","")
            frm.set_value("from_account_balance",0)
            frm.set_value("account_paid_to","")
            frm.set_value("to_account_balance",0)
            
            if(frm.doc.payment_type == "Pay"){
                frm.set_value("account_paid_from",r.message.mode_of_payment_account)
                frm.set_value("from_account_balance",r.message.mode_of_payment_balance)
                frm.set_value("account_paid_to",r.message.party_account)
                frm.set_value("to_account_balance",r.message.party_balance)
            }
            else{
                frm.set_value("account_paid_to",r.message.mode_of_payment_account)
                frm.set_value("to_account_balance",r.message.mode_of_payment_balance)
                frm.set_value("account_paid_from",r.message.party_account)
                frm.set_value("from_account_balance",r.message.party_balance)
            }
        }
    })
}