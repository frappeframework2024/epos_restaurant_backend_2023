// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("BOM", {
    refresh(frm){
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__('Update Cost'), function(){
                frappe.confirm('<b>This Will Update Product Cost For All Stock Location.</b></br> Are you sure you want to proceed?',
                    () => {
                        update_all_cost(frm)
                    }, () => {
                       
                    })
            });
        }
    },
	valuation_based_on(frm) {
        link = frm.doc.valuation_based_on == "Cost" ? 'epos_restaurant_2023.inventory.inventory.get_bom_product_cost':'epos_restaurant_2023.inventory.inventory.get_bom_product_price'
        frm.doc.items.forEach(a => {
            update_item(frm,"BOM Items",a.name)
        });
	},
});

frappe.ui.form.on("BOM Items", {
	product(frm,cdt,cdn) {
        update_item(frm,cdt,cdn)
	},
    cost(frm,cdt,cdn){
        update_item(frm,cdt,cdn)
    },
    quantity(frm,cdt,cdn){
        update_item(frm,cdt,cdn)
    },
    unit(frm,cdt,cdn){
        update_item(frm,cdt,cdn)
    }
});

function update_item(frm,cdt,cdn){
    let doc = locals[cdt][cdn];
    link = frm.doc.valuation_based_on == "Cost" ? 'epos_restaurant_2023.inventory.inventory.get_bom_product_cost':'epos_restaurant_2023.inventory.inventory.get_bom_product_price'
    frappe.call({
        method: link,
        args: {
            product_code: (doc.product || ""),
            unit: (doc.unit || "")
        },
        callback: (r) => {
            if(r.message){
                doc.cost = r.message
                doc.amount = doc.cost * doc.quantity
            }
        }
    }).then((r)=>{
        frm.refresh_field("items")
        update_totals(frm)
    })
}

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

function update_all_cost(frm) {
    frappe.call({
        method: "update_cost",
        doc:frm.doc,
        callback: (r) => {
            if(r.message){
                frappe.msgprint(r.message)
            }
        }
    })
}