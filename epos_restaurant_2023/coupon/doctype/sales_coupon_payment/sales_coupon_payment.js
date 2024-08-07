// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Coupon Payment", {
	refresh(frm) {

	},
    onload(frm){
        // on_member_type_changed(frm)
    },
    payment_type:function(frm){
        on_payment_type_changed(frm,true)
    },
    input_amount:function(frm){
        on_input_amount_changed(frm,true)
    }

});

function on_payment_type_changed(frm,changed){
    update_payment_amount(frm,changed)
}

function on_input_amount_changed(frm,changed){
    update_payment_amount(frm,changed)
}


function update_payment_amount(frm,changed){
    frm.set_df_property('payment_amount', 'read_only',0);
    frm.doc.payment_amount = frm.doc.input_amount / (frm.doc.exchange_rate || 1);
    frm.set_df_property('payment_amount', 'read_only',1);
    frm.refresh_field("payment_amount");
}
