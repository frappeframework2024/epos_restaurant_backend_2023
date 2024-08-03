// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Produce", {
    refresh(frm){
        set_filters(frm)
    },
    source_location(frm){
        update_chidrent_cost(frm)
        update_children(frm)
    },
    product(frm){
        frappe.call({
			method: 'epos_restaurant_2023.inventory.doctype.produce.produce.get_default_bom',
			args: {
				product: frm.doc.product
			},
			callback: (r) => {
				if(r.message != "None"){
                   frm.doc.bom = r.message
                   set_child_table(frm)
				}
                else{
                    frm.doc.bom = ""
                }
                frm.refresh_field('bom');
			}
		})
    },
	bom(frm){
        set_child_table(frm)
    },
    quantity(frm){
        update_children(frm)
    }
});
frappe.ui.form.on("Produce Item", {
    quantity(frm,cdt,cdn){
        update_child(self,cdt,cdn)
    },
    unit(frm,cdt,cdn){
        update_child(self,cdt,cdn)
    },
    product(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        get_product_cost(frm,doc).then((v)=>{
            frappe.model.set_value(cdt, cdn, "cost", (v));
            update_child(self,cdt,cdn)
        });
    }
})

function update_child(self,cdt,cdn){
    let doc = locals[cdt][cdn];
    frappe.call({
        method: "epos_restaurant_2023.inventory.inventory.get_uom_conversion",
        args: {
            from_uom: doc.base_unit, 
            to_uom: doc.unit
        },
        callback: (r) => {
            if(r.message){
                uom_conversion = (1/(r.message || 0))
                console.log(uom_conversion)
                frappe.model.set_value("Produce Item", doc.name, "amount", (doc.quantity*doc.cost*uom_conversion.toFixed(2)));
            }
        }
    }).then((r)=>{
        update_totals(frm)
    })
}

function update_children(frm){
    frm.doc.produce_items.forEach(a => {
        frappe.call({
            method: "epos_restaurant_2023.inventory.inventory.get_uom_conversion",
            args: {
                from_uom: a.base_unit, 
                to_uom: a.unit
            },
            callback: (r) => {
                if(r.message){
                    uom_conversion = (1/(r.message || 0))
                    frappe.model.set_value("Produce Item", a.name, "quantity", (a.current_quantity * frm.doc.quantity));
                    frappe.model.set_value("Produce Item", a.name, "amount", (a.quantity*a.cost*uom_conversion.toFixed(2)));
                }
            }
        }).then((r)=>{
            update_totals(frm)
        })
    });
}

function update_chidrent_cost(frm){
    frm.doc.produce_items.forEach(a => {
        get_product_cost(frm,a).then((v)=>{
            frappe.model.set_value("Produce Item", a.name, "cost", (v));
            update_totals(frm)
        });
    })
}

let get_product_cost = function (frm,doc) {
    if(!frm.doc.source_location){
        frappe.msgprint("Please Select Source Location First!")
        return
    }
	return new Promise(function(resolve, reject) {
        frappe.call({
			method: "epos_restaurant_2023.inventory.doctype.product.product.get_product_cost_by_stock",
			args: {
				stock_location:frm.doc.source_location,
				product_code: doc.product
			},
			callback: function(r){
				resolve(r.message.cost)
			},
			error: function(r) {
				reject("error")
			},
		});
	});
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
    frm.set_query("product","produce_items", function() {
        return {
            filters: [
                ["Product","is_inventory_product", "=", 1]
            ]
        }
    });
}

function set_child_table(frm){
    frm.set_value('produce_items', []);
    frm.refresh_field('produce_items');
    frappe.call({
        method: 'get_bom_items',
        doc: frm.doc,
        callback: (r) => {
            if(r.message){
                r.message.forEach(p => {
                    frm.add_child('produce_items', {
                        product : p.product,
                        product_name : p.product_name,
                        unit : p.unit,
                        base_unit : p.base_unit,
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
        update_totals(frm)
    })
}

function update_totals(frm){
    total_qty = 0
    total_amount = 0

    frm.doc.produce_items.forEach(a => {
        total_qty += a.quantity
        total_amount += a.amount
    });
    frm.set_value("total_quantity",total_qty)
    frm.set_value("total_amount",total_amount)
}