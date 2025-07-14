// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Payment", {
	refresh(frm) {

	},
});

frappe.ui.form.on('Store Payment Type', {
    payment_type(frm,cdt,cdn){
        if(frm.doc.business_branch == "" || frm.doc.business_branch == null){
			frappe.throw("Please Select Business Branch First")
			return
		}
		let doc = locals[cdt][cdn];
		frappe.call({
			method: 'epos_restaurant_2023.selling.doctype.store_payment.store_payment.get_payment_type_account',
			args: {
				payment_type: doc.payment_type,
				branch: frm.doc.business_branch
			},
			callback: (r) => {
				if(r.message && r.message != "no_record"){
					frappe.model.set_value(cdt, cdn, "account_code", (r.message[0].account || ""));
                    frappe.model.set_value(cdt, cdn, "exchange_rate", (r.message[0].exchange_rate || 1));
				}
			},
			error: (r) => {
				reject(r)
			}
		})
    }
})
