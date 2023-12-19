// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Sale Payment", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Sale Payment", {
    onload(frm){
        if(frm.doc.__islocal){
            if((frm.doc.pos_reservation||"") !="" ){
                frm.doc.transaction_type = "Payment";
                frm.doc.sale =undefined;
                set_query(frm,"sale",[["Sale","docstatus", "=", 1], ["Sale","from_reservation", "=", frm.doc.pos_reservation], ["Sale","balance", ">=", 0.01]]);                
                set_df_propert(frm,"transaction_type","read_only",1);
                set_df_propert(frm,"sale_information_section","hidden",1);
            }else{

            }
        }

    },
    setup(frm) {
        set_query(frm,"sale",[["Sale","docstatus", "=", 1], ["Sale","balance", ">=", 0.01]]);
        set_query(frm,"pos_reservation",[["POS Reservation","reservation_status", "not in", "Void"]]);         
    },
    input_amount(frm){
        frm.set_value('payment_amount', frm.doc.input_amount/frm.doc.exchange_rate);
    }
});

function set_df_propert(frm,field_name,property,property_value){
    frm.set_df_property(field_name,property, property_value);	
    frm.refresh_field(field_name);
}


function set_query(frm,doc_field,filters){
    frm.set_query(doc_field, function() {
        return {
            filters: filters
        }
    });
      
}