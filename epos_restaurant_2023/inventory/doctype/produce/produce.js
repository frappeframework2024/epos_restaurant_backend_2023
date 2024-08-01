// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Produce", {
    refresh(frm){
        set_filters(frm)
    },
    product(frm){
        frappe.call({
			method: 'epos_restaurant_2023.inventory.inventory.get_default_bom',
			args: {
				product: frm.doc.product
			},
			callback: (r) => {
				if(r.message != "None"){
                   frm.doc.bom = r.message
				}
                else{
                    frm.doc.bom = ""
                }
			}
		}).then((result)=>{
            frm.refresh_field('bom');
            set_child_table(frm)
            
        })
    },
	bom(frm){
        set_child_table(frm)
    },
    quantity(frm){
        update_child_qty(frm)
    }
});
frappe.ui.form.on("Produce Item", {
    quantity(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", (doc.quantity*doc.cost));
    },
    product(frm,cdt,cdn){

    }
})

function update_child_qty(frm){
    frm.doc.produce_items.forEach(a => {
        a.quantity = a.current_quantity * frm.doc.quantity
        a.amount = a.quantity * a.cost
    });
    frm.refresh_field('produce_items');
}

function set_filters(frm){
    frm.set_query("bom", function() {
        return {
            filters: [
                ["product","=",frm.doc.product],
                ["is_active","=",true]
            ]
        }
    });
}
function set_child_table(frm){
    frm.set_value('produce_items', []);
    frm.refresh_field('produce_items');
    frappe.call({
        method: 'epos_restaurant_2023.inventory.inventory.get_bom_items',
        args: {
            bom_name: frm.doc.bom
        },
        callback: (r) => {
            if(r.message){
                r.message.forEach(p => {
                    frm.add_child('produce_items', {
                        product : p.product,
                        product_name : p.product_name,
                        unit : p.unit,
                        base_unit : p.unit,
                        quantity : p.quantity,
                        current_quantity : p.quantity,
                        cost : p.cost,
                        amount : p.amount
                    });
                });
            }
        }
    }).then((result)=>{
        frm.refresh_field('produce_items');
        set_filters(frm)
        update_child_qty(frm)
    })
}