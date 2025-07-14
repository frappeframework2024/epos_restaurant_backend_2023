// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Payment", {
	business_branch(frm) {
		change_branch(frm)
	},
	vendor(frm) {
		frappe.call({
			method: 'epos_restaurant_2023.selling.doctype.store_payment.store_payment.get_vendor_credit_balance',
			args: {
				pos_profile: frm.doc.pos_profile
			},
			callback: (r) => {
				frm.set_value("credit_amount", r.message.balance)
			}
		})
	},
	pos_profile(frm) {
		
	}
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
    },
    input_amount(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "payment_amount", (doc.input_amount / doc.exchange_rate));
    }
})

function change_branch(frm){
	frm.doc.payments.forEach(a => {
		if((a.payment_type || "") != ""){
			frappe.call({
				method: 'epos_restaurant_2023.selling.doctype.store_payment.store_payment.get_payment_type_account',
				args: {
					payment_type: a.payment_type,
					branch: frm.doc.business_branch
				},
				callback: (r) => {
					if(r.message && r.message != "no_record"){
						a.account_code = (r.message[0].account || "");
						a.exchange_rate = (r.message[0].exchange_rate || 1);
						a.payment_amount = a.input_amount / (a.exchange_rate || 1);
					}
					else{
						a.account_code = "";
						a.exchange_rate = 0;
						a.payment_amount = 0;
					}
				}
			}).then((result)=>{
				frm.refresh_field('payments');
			})
		}
	});
}