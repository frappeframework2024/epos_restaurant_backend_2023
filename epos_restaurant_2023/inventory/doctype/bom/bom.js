// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("BOM", {
	valuation_based_on(frm) {
        link = frm.doc.valuation_based_on == "Cost" ? 'epos_restaurant_2023.inventory.inventory.get_product_cost':'epos_restaurant_2023.inventory.inventory.get_product_price'
        frm.doc.items.forEach(a => {
            frappe.call({
                method: link,
                args: {
                    stock_location: "None",
                    product_code: a.product
                },
                callback: (r) => {
                    if(r.message){
                        a.cost = r.message
                        a.amount = a.cost * a.quantity
                    }
                }
            }).then((result)=>{
                frm.refresh_field("items")
                update_totals(frm)
            })
        });
	},
});

frappe.ui.form.on("BOM Items", {
	product(frm,cdt,cdn) {
        let doc = locals[cdt][cdn];
		frappe.call({
			method: 'epos_restaurant_2023.inventory.inventory.get_product_cost',
			args: {
				stock_location: "None",
				product_code: doc.product
			},
			callback: (r) => {
				if(r.message){
					frappe.model.set_value(cdt, cdn, "cost", (r.message || 0));
				}
			}
		})
	},
    cost(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", (doc.cost * doc.quantity));
        update_totals(frm)
    },
    quantity(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", (doc.cost * doc.quantity));
        update_totals(frm)
    }
});

function update_totals(frm){
    let total_cost = 0;
	let total_qty = 0;

    frm.doc.items.forEach(d => {
        total_cost += flt(d.amount);
		total_qty += flt(d.quantity); 
    });

    frm.set_value('total_qty', total_qty);
    frm.set_value('total_cost', total_cost);
}