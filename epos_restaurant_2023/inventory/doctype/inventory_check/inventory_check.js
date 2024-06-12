// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Inventory Check", {
	refresh(frm) {
                if(frm.is_new()){
                        frm.set_value('posting_date',frappe.datetime.nowdate())
                }
	},
        select_product(frm){
		if(frm.doc.items.length > 0){
            $.each(frm.doc.items, function(i, d) {
                if(d.product_code){
                        get_product_quantity_information(frm,d);
				}
            });
        }
    },
        
});

function get_product_quantity_information(frm,doc){
	if (frm.doc.stock_location == undefined){
		frappe.throw("Please Select Stock Location First")
		return
	}
	frappe.call({
		method: "epos_restaurant_2023.inventory.doctype.inventory_check.inventory_check.get_product_quantity_information",
		args: {
			product_code:doc.items.product_code,
			date:frappe.datetime.nowdate(),
			stock_location:frm.doc.stock_location,
		},
		callback: function(r){
			if(doc!=undefined){
				doc.difference = r.message.actual_quantity || 0 - r.message.current_on_hand || 0;
	
			}
			frm.refresh_field('items');
		}
	});
	
}