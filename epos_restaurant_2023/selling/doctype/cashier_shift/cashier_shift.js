// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cashier Shift", {
    refresh(frm){
        frm.doc.cash_float.forEach(row => {
            row.payment_amount = row.input_system_close_amount - row.input_amount
        });
    },
	onload(frm) {
        if(!frm.is_new()){
            get_cash_float(frm)
        }
        frm.set_query("working_day", function () {
			return {
				filters: [
					["Working Day", "is_closed", "=", 0]
				]
			}
		});
	},
    pos_profile(frm){
         get_allow_cash_float_payment_type(frm)
    }
    
});
frappe.ui.form.on("Cashier Shift Cash Float", {
    input_close_amount(frm,cdt,cdn){
        update_diff_amount(frm,cdt,cdn)
    },
    input_amount(frm,cdt,cdn){
        update_system_close_amount(frm,cdt,cdn)
        update_diff_amount(frm,cdt,cdn)
    },
})

function update_system_close_amount(frm,cdt,cdn){
    let doc = locals[cdt][cdn];
    let system_close_amount = doc.input_amount + (doc.payment_amount || 0)
    frappe.model.set_value(cdt, cdn, "input_system_close_amount", system_close_amount);
}

function update_diff_amount(frm,cdt,cdn){
   let doc = locals[cdt][cdn];
   let diff_amount = doc.input_close_amount - doc.input_system_close_amount
   frappe.model.set_value(cdt, cdn, "input_different_amount", diff_amount);
}

function get_cash_float(frm){
    frappe.call({
        method: 'epos_restaurant_2023.api.api.get_close_shift_summary',
        args: {
            cashier_shift: frm.doc.name,
            show_system_closed_amount: 1
        },
        callback: (r) => {
            if((frm.doc.cash_float || []).length == 0){
                r.message.forEach(a => {
                    let row = frm.add_child("cash_float");
                    row.payment_method = a.payment_method;
                    row.input_amount = a.input_amount;
                    row.input_system_close_amount = a.input_system_close_amount;
                    row.input_close_amount = a.input_close_amount
                    row.input_different_amount = a.input_close_amount - a.input_system_close_amount
                    row.opening_amount = a.opening_amount
                    row.system_close_amount = a.system_close_amount
                    row.different_amount = a.different_amount
                    row.payment_amount = row.input_system_close_amount - row.input_amount
                });
                 frm.refresh_field("cash_float");
            }
            else{
                frm.doc.cash_float.forEach(row=> {
                    let a = r.message.find(r => r.payment_method === row.payment_method); 
                    row.input_amount = a.input_amount;
                    row.input_system_close_amount = a.input_system_close_amount;
                    row.input_close_amount = a.input_close_amount
                    row.input_different_amount = a.input_close_amount - a.input_system_close_amount
                    row.opening_amount = a.opening_amount
                    row.system_close_amount = a.system_close_amount
                    row.different_amount = a.different_amount
                    row.payment_amount = row.input_system_close_amount - row.input_amount
                });
                 frm.refresh_field("cash_float");
            }
        }
    })
}

function get_allow_cash_float_payment_type(frm){
    if(frm.doc.pos_profile){
            frappe.call({
            method: 'epos_restaurant_2023.api.api.get_allow_cash_float_payment_type',
            args: {
                pos_profile: frm.doc.pos_profile
            },
            callback: (r) => {
                frm.set_query("payment_method","cash_float", function() {
                return {
                    filters: [
                        ["name", "in", r.message]
                    ]
                }
            });
        }
    })
    }
}