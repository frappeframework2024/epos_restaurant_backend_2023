// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Request", {
	refresh(frm) {
 
	},

	workflow_state(frm){
// /
	}
});


frappe.ui.form.on('Purchase Request Products', {
	
	quantity(frm, cdt, cdn) {
		const doc = locals[cdt][cdn];
		update_purchase_request_product_summary(frm, doc)
	},
	price(frm, cdt, cdn) {
		const doc = locals[cdt][cdn];
		update_purchase_request_product_summary(frm, doc)
	},
})


function update_purchase_request_product_summary(frm, doc) {
	doc.amount = (doc.price||0) * (doc.quantity<=0 ? 1 : doc.quantity);	
	frm.refresh_field('purchase_request_products');
    update_purchase_request_summary(frm);
	// updateSumTotal(frm);
}

function update_purchase_request_summary(frm){
    const products = frm.doc.purchase_request_products;
	if (products == undefined) {
		return false;
	}

    frm.set_value('total_quantity', products.reduce((n, d) => n + d.quantity, 0));
	frm.set_value('total_amount', products.reduce((n, d) => n + d.amount, 0)); 

    frm.refresh_field('total_quantity');
    frm.refresh_field('total_amount');
}