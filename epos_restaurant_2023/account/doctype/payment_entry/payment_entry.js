// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Entry", {
    refresh(frm){
        if(frm.is_new()){
            set_filters(frm)
            get_mode_of_payment_detail(frm)
            get_party_detail(frm)
        }
    },
	mode_of_payment(frm) {
        get_mode_of_payment_detail(frm)
	},
    business_branch(frm) {
        get_mode_of_payment_detail(frm)
	},
    payment_type(frm){
        get_mode_of_payment_detail(frm)
    },
    party_type(frm){
        get_mode_of_payment_detail(frm)
    },
    party(frm){
        get_party_detail(frm)
        set_filters(frm)
    },
    posting_date(frm){
        get_party_detail(frm)
    },
    paid_amount(frm){
        update_allocated_amount(frm)
    }
});

frappe.ui.form.on("Payment Entry Reference", {
    reference_name(frm,cdt,cdn){
        get_reference_detail(frm,cdt,cdn)
    },
    input_amount(frm,cdt,cdn){
        let doc=  locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "balance", (doc.total_amount-(doc.paid_amount/frm.doc.exchange_rate)));
    }
})

function update_allocated_amount(frm){
    paid_amount = frm.doc.paid_amount/frm.doc.exchange_rate
    if((frm.doc.payment_entry_reference || []).length > 0){
        frm.doc.payment_entry_reference.forEach(r => {
            if(paid_amount<r.total_amount){
                r.input_amount = paid_amount * frm.doc.exchange_rate
                r.paid_amount = paid_amount
            }
            else{
                r.input_amount = r.total_amount * frm.doc.exchange_rate
                r.paid_amount = r.total_amount
            }
            r.balance = r.total_amount - r.paid_amount
            paid_amount = paid_amount - r.paid_amount
        });
        frm.set_value("unallocated_amount",paid_amount*frm.doc.exchange_rate)
        frm.refresh_field("payment_entry_reference")
    }
    else{
        frm.set_value("unallocated_amount",frm.doc.paid_amount - Math.abs(frm.doc.to_account_balance))
    }
}

function set_filters(frm){
    frm.set_query("reference_doctype","payment_entry_reference", function() {
        return {
            filters: [
                ["name", "in", "Sale,Purchase Order"]
            ]
        }
    });
    frm.set_query("reference_name","payment_entry_reference", function() {
        return {
            filters: [
                ["docstatus", "=", 1],
                ["balance",">",0]
            ]
        }
    });
    if(frm.doc.party_type == "Vendor"){
        frm.set_query("reference_name","payment_entry_reference", function() {
            return {
                filters: [
                    ["docstatus", "=", 1],
                    ["balance",">",0],
                    ["vendor","=",frm.doc.party]
                ]
            }
        });
    }
    else if(frm.doc.party_type == "Employee"){
        frm.set_query("party", function() {
            return {
                filters: [
                    ["is_selling_agent", "=", 1]
                ]
            }
        });
    }
    else{
        frm.set_query("reference_name","payment_entry_reference", function() {
            return {
                filters: [
                    ["docstatus", "=", 1],
                    ["balance",">",0],
                    ["customer","=",frm.doc.party]
                ]
            }
        });
    }
}

function get_reference_detail(frm,cdt,cdn){
    let doc=  locals[cdt][cdn];
    frappe.call({
        method: 'epos_restaurant_2023.account.doctype.payment_entry.payment_entry.get_reference_detail',
        args: {
            doctype: doc.reference_doctype,
            docname: doc.reference_name
        },
        callback: (r) => {
            frappe.model.set_value(cdt, cdn, "total_amount", (r.message));
            frappe.model.set_value(cdt, cdn, "input_amount", 0);
            frappe.model.set_value(cdt, cdn, "paid_amount", 0);
            frappe.model.set_value(cdt, cdn, "balance",  (r.message));
            frappe.model.set_value(cdt, cdn, "exchange_rate",  frm.doc.exchange_rate);
        }
    }).then((r)=>{
        if(frm.doc.paid_amount > 0){
            update_allocated_amount(frm)
        }
    })
}

function get_party_detail(frm){
    frappe.call({
        method: 'epos_restaurant_2023.account.doctype.payment_entry.payment_entry.get_party_detail',
        args: {
            party_type: (frm.doc.party_type || ""),
            party: (frm.doc.party || ""),
            posting_date: frm.doc.posting_date
        },
        callback: (r) => {
            frm.set_value("party_name",r.message.name)
            if(frm.doc.payment_type == "Pay"){
                frm.set_value("to_account_balance",r.message.balance)
                if(r.message.account != ""){
                    frm.set_value("account_paid_to",r.message.account)
                }
            }
            else{
                frm.set_value("from_account_balance",r.message.balance)
                if(r.message.account != ""){
                    frm.set_value("account_paid_from",r.message.account)
                }
            }
        }
    })
}

function get_mode_of_payment_detail(frm){
    frappe.call({
        method: 'epos_restaurant_2023.account.doctype.payment_entry.payment_entry.get_mode_of_payment_detail',
        args: {
            branch: (frm.doc.business_branch || ""),
            mode_of_payment: (frm.doc.mode_of_payment || ""),
            party_type: (frm.doc.party_type || ""),
            posting_date: frm.doc.posting_date,
            party: (frm.doc.party || "")
        },
        callback: (r) => {
            frm.set_value("account_paid_from","")
            frm.set_value("from_account_balance",0)
            frm.set_value("account_paid_to","")
            frm.set_value("to_account_balance",0)
            frm.set_value("paid_amount",0)
            
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