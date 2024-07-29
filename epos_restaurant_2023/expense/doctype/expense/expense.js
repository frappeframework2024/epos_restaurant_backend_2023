// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense", {
	refresh(frm) {

	},
	setup(frm) {
		if (frm.is_new()){
			frappe.call("epos_restaurant_2023.expense.doctype.expense.get_expense_code_account").then(result=>{
				frm.doc.exchange_rate = result.message
				frm.refresh_field("exchange_rate");
			})
		}
	}
    
});


frappe.ui.form.on('Expense Item', {
	expense_code(frm,cdt,cdn){
		let doc = locals[cdt][cdn];
		frappe.call({
			method: 'epos_restaurant_2023.expense.doctype.expense.expense.get_expense_code_account',
			args: {
				expense_code: doc.expense_code,
				branch: frm.doc.business_branch
			},
			callback: (r) => {
			    frm.set_query("account","default_expense_account", function() {
					return {
						filters: [
							["business_branch", "in", r.message],
							["is_group", "=", 0]
						]
					}
				});
			},
			error: (r) => {
				reject(r)
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

function update_expense_item_amount(frm,cdt, cdn)  {
    let doc = locals[cdt][cdn];
		doc.amount=doc.quantity*doc.price;
	    frm.refresh_field('expense_items');
		updateSumTotal(frm);
}

function updateSumTotal(frm) {
    let sum_total = 0;
	let total_qty = 0;
 

    $.each(frm.doc.expense_items, function(i, d) {
        sum_total += flt(d.amount);
		total_qty +=flt(d.quantity);
		 
    });
	
 
    frm.set_value('total_amount', sum_total);
    frm.set_value('total_quantity', total_qty);
   
	frm.refresh_field("total_amount");
	frm.refresh_field("total_quantity");
}

