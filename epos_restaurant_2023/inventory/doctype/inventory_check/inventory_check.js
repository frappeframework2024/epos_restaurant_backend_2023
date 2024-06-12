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
frappe.ui.form.on("Inventory Check Items", {
        product_code(frm,cdt, cdn){
                
                    let doc = locals[cdt][cdn];

            get_product_quantity_information(frm,doc)
        },
        actual_quantity(frm,cdt, cdn){
                let doc = locals[cdt][cdn];
                doc.difference = (doc.actual_quantity || 0 )- (doc.current_on_hand || 0)    
                frm.refresh_field('items');
        }

        
    });

function get_product_quantity_information(frm,doc){
	 
       if(!doc.product_code){
                return 
       }

	frappe.call({
		method: "epos_restaurant_2023.inventory.doctype.inventory_check.inventory_check.get_product_quantity_information",
		args: {
			product_code:doc.product_code,
			date:frm.doc.posting_date,
			stock_location:frm.doc.stock_location,
		},
		callback: function(r){
                        
			if(doc!=undefined){
                                
                                doc.opening_quantity = r.message.opening_quantity || 0
                                doc.sale = r.message.sale || 0
                                doc.purchase = r.message.purchase || 0
                                doc.other_transaction = r.message.other_transaction || 0
                                doc.current_on_hand = r.message.current_on_hand || 0
                                doc.has_expired_date = r.message.has_expired_date || 0
                                doc.expired_date = r.message.expired_date || ''
                                doc.actual_quantity = doc.current_on_hand  
				doc.difference = 0
	
			}
			frm.refresh_field('items');
		}
	});
	
}