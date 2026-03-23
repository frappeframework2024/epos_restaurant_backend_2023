// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cash Transaction", {
    refresh(frm) {
        set_transaction_type(frm)
    },
	setup(frm) {
       set_transaction_type(frm)
    },
    transaction_status(frm){
       set_transaction_type(frm)
    },
    input_amount(frm){ 
        update_amount(frm)
    },
    payment_type(frm){ 
        update_amount(frm)
    },
});

function update_amount(frm) {
    if(frm.doc.exchange_currency){
        let amount = frm.doc.input_amount / frm.doc.exchange_currency
        frm.set_value('amount', amount);
    }
    
}
function set_transaction_type(frm){
    let options;
    if (frm.doc.transaction_status === "Cash In") {
        options = ["Cash Float"];
        frm.set_value('transaction_type', 'Cash Float');
    } else {
        options = ["Expense"];
        frm.set_value('transaction_type', 'Expense');
    }
    frm.set_df_property('transaction_type', 'options', options.join("\n"));
}