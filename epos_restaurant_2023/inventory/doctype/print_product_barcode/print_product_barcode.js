// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Print Product Barcode", {
	refresh(frm) {
        frm.set_query("category", function() {
            return {
                filters: [
                    ["disabled","=",false]
                ]
            }
        });
	},
    category(frm){
        frappe.call({
			method: 'get_product_price',
			doc: frm.doc,
			callback: (r) => {
				if(r.message != null){
                   set_child_table(frm)
				}
                frm.refresh_field('items');
			}
		})
    }
});
function set_child_table(frm){
    frm.set_value('items', []);
    frm.refresh_field('items');
    frappe.call({
        method: 'get_product_price',
        doc: frm.doc,
        callback: (r) => {
            if(r.message){
                r.message.forEach(p => {
                    frm.add_child('items', {
                        product_code : p.product_code,
                        product_name_en : p.product_name_en,
                        product_name_kh : p.product_name_kh,
                        price_rule : p.price_rule,
                        photo : p.photo,
                        unit : p.unit,
                        price : p.price
                    });
                });
            }
        }
    }).then((result)=>{
        frm.refresh_field('items')
    })
}