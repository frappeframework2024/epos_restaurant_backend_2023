// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Produce", {
	product(frm) {
        frm.call({
            method: 'get_product_children',
            doc:frm.doc,
            callback:function(r){
                if(r.message){
                    frm.set_value('product_items',r.message);
                }
            },
            async: true,
        });
	},
});
