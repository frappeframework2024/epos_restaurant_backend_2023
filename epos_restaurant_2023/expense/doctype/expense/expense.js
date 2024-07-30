// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense", {
	refresh(frm){
		frm.set_query("expense_account","expense_items", function() {
            return {
                filters: [
                    ["Chart Of Account","business_branch", "=", frm.doc.business_branch],
                    ["Chart Of Account","is_group", "=", 0],
                    ["Chart Of Account","root_type", "=", "Expenses"]
                ]
            }
        });
	},
	business_branch(frm) {
		change_branch(frm)
	},
});
frappe.ui.form.on('Expense Payment', {
	payment_type(frm,cdt,cdn){
		let doc = locals[cdt][cdn];
		frappe.call({
			method: 'epos_restaurant_2023.expense.doctype.expense.expense.get_payment_type_account',
			args: {
				payment_type: doc.payment_type,
				branch: frm.doc.business_branch
			},
			callback: (r) => {
				if(r.message && r.message != "no_record"){
					frappe.model.set_value(cdt, cdn, "default_account", (r.message[0].account || ""));
				}
			},
			error: (r) => {
				reject(r)
			}
		})
	},
	input_amount(frm,cdt,cdn){
		let doc = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", (doc.input_amount / doc.exchange_rate));
		updateSumTotal(frm);
	}
})

frappe.ui.form.on('Expense Item', {
	expense_code(frm,cdt,cdn){
		if(!frm.doc.business_branch){
			frappe.throw("Please Select Business Branch First")
		}
		let doc = locals[cdt][cdn];
		frappe.call({
			method: 'epos_restaurant_2023.expense.doctype.expense.expense.get_expense_code_account',
			args: {
				expense_code: doc.expense_code,
				branch: frm.doc.business_branch
			},
			callback: (r) => {
				if(r.message && r.message != "no_record"){
					frappe.model.set_value(cdt, cdn, "expense_account", (r.message[0].default_expense_account || ""));
				}
			}
		})
	},
	quantity(frm,cdt, cdn) {
		update_expense_item_amount(frm,cdt,cdn);
	},
    price(frm,cdt, cdn) {
		let doc=  locals[cdt][cdn];
		doc.price_second_currency =  doc.price * (frm.doc.exchange_rate || 1)
		update_expense_item_amount(frm,cdt,cdn);
		
	},
    price_second_currency(frm,cdt, cdn) {
		let doc=  locals[cdt][cdn];
		doc.price =  doc.price_second_currency / (frm.doc.exchange_rate || 1)
		update_expense_item_amount(frm,cdt, cdn)
	},

})

function change_branch(frm){
	frm.doc.expense_items.forEach(a => {
		if((a.expense_code || "") != ""){
			frappe.call({
				method: 'epos_restaurant_2023.expense.doctype.expense.expense.get_expense_code_account',
				args: {
					expense_code: a.expense_code,
					branch: frm.doc.business_branch
				},
				callback: (r) => {
					a.expense_account = ""
					if(r.message && r.message != "no_record"){
						  a.expense_account = r.message[0].default_expense_account || ""
					}
				}
			}).then((result)=>{
				frm.refresh_field('expense_items');
			})
		}
	});
}

function update_expense_item_amount(frm,cdt, cdn)  {
    let doc = locals[cdt][cdn];
		doc.amount=doc.quantity*doc.price;
	    frm.refresh_field('expense_items');
		updateSumTotal(frm);
}

function updateSumTotal(frm) {
    let total_amount = 0;
	let total_qty = 0;
	let total_payment = 0;

    $.each(frm.doc.expense_items, function(i, d) {
        total_amount += flt(d.amount);
		total_qty +=flt(d.quantity);
		 
    });

	$.each(frm.doc.payments, function(i, d) {
        total_payment += flt(d.amount);
		 
    });
	
 
    frm.set_value('total_amount', total_amount);
    frm.set_value('total_quantity', total_qty);
    frm.set_value('total_paid', total_payment);
    frm.set_value('balance', total_amount - total_payment);
   
	frm.refresh_field("total_amount");
	frm.refresh_field("total_quantity");
	frm.refresh_field("total_paid");
	frm.refresh_field("balance");
}

