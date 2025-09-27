// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Payment", {
	business_branch(frm) {
		// change_branch(frm)
		// auto load working day when branch changes
		if (frm.doc.business_branch) {
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Working Day",
					filters: {
						is_closed: 0,
						business_branch: frm.doc.business_branch
					},
					fields: ["name"],
					order_by: "creation desc",
					
				},
				callback: function(r) {
					if (r.message && r.message.length > 0) {
						let working_day = r.message[0].name;
						frm.set_value("working_day", working_day);

						// after setting working day → auto load cashier shift
						set_default_cashier_shift(frm, working_day);
					} else {
						frm.set_value("working_day", "");
						frm.set_value("cashier_shift", "");
					}
				}
			});
		} 
	},

	pos_profile(frm) {
		// alert(frm.doc.pos_profile)
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

	 
	calculate_total(frm) {
		let total = 0;
		(frm.doc.payments || []).forEach(row => {
			total += row.payment_amount || 0;
		});
		frm.set_value("total_payment_amount", total);
	},

	 
	refresh(frm) {
		frm.events.calculate_total(frm);

		// --- Working Day setup ---
		frm.set_query("working_day", function() {
			return {
				filters: {
					is_closed: 0,
					business_branch: frm.doc.business_branch
				}
			};
		});
		 
	}
});

frappe.ui.form.on('Store Payment Type', {
     
    input_amount(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "payment_amount", (doc.input_amount / doc.exchange_rate));

		 
		frm.events.calculate_total(frm);
    },
	
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
				frm.events.calculate_total(frm);  
			})
		}
	});
}

// helper function to set default cashier shift
function set_default_cashier_shift(frm, working_day) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Cashier Shift",
			filters: {
				is_closed: 0,
				working_day: working_day,
				business_branch: frm.doc.business_branch
			},
			fields: ["name"],
			order_by: "creation desc",
			limit: 1
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				frm.set_value("cashier_shift", r.message[0].name);
			} else {
				frm.set_value("cashier_shift", "");
			}
		}
	});
}