 

frappe.ui.form.on("Purchase Order Payment", {
    setup(frm) {
        frm.set_query("purchase_order", function() {
            return {
                filters: [
                    ["Purchase Order","docstatus", "=", 1]
                ]
            }
        });
    },
    input_amount(frm){
        frm.set_value('payment_amount', frm.doc.input_amount/frm.doc.exchange_rate);
    },
    payment_type(frm){
         
        frm.set_value('account_paid_from', "");
    },
});