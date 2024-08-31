// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Adjustment", {
	refresh(frm) {
		frm.set_query("product_code","products", function() {
            return {
                filters: [
                    ["Product","is_inventory_product", "=", 1]
                ]
            }
        });
		frm.page.remove_action_item(__('Duplicate'));
        
        // Add custom Duplicate button
        frm.page.add_menu_item(__('Duplicate'), function() {
            frappe.confirm(
                'Are you sure you want to duplicate this document?',
                function() {
                    frm.duplicate_doc();
                }
            );
            frappe.msgprint(__('Duplicate action clicked'));
        }, true);
	},
	setup(frm) {
		for (const key in frm.fields_dict) {
			if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
				frm.fields_dict[key].$wrapper.addClass('custom_control');
			}
		}
	},
    stock_location(frm){ 
        if(frm.doc.products.length > 0){
            $.each(frm.doc.products, function(i, d) {
				get_product(frm,d)
            });
        }
    },
    scan_barcode(frm){
		if(frm.doc.scan_barcode!=undefined){
				let barcode = frm.doc.scan_barcode;
				frappe.call({
					method: "epos_restaurant_2023.inventory.doctype.product.product.get_product",
					args: {
						barcode:frm.doc.scan_barcode,
						business_branch:frm.doc.business_branch,
					},
					callback: function(r){
						if(r.message!=undefined){
							if(r.message.status ==0){ 
								let row_exist = check_row_exist(frm,barcode);
								if(row_exist!=undefined && frm.doc.append_quantity == 1){
									if(row_exist!=undefined){
										row_exist.doc.quantity = row_exist.doc.quantity + 1;
										row_exist.doc.total_amount = row_exist.doc.quantity * row_exist.doc.cost;
										frm.refresh_field('products');
									}
								}else {
									add_product_child(frm,r.message);
								}
								update_totals(frm);
							}
						}
					}
				});
		}
		frm.doc.scan_barcode = "";
		frm.refresh_field('scan_barcode');
	},
});
frappe.ui.form.on('Stock Adjustment Product', {
	product_code(frm,cdt, cdn) {
        let doc = locals[cdt][cdn];
        get_product(frm, doc)
	},
    quantity(frm,cdt, cdn){
        update_product_amount(frm,cdt, cdn);
    },
    cost(frm,cdt, cdn){
        update_product_amount(frm,cdt, cdn);
    }
})

function get_product(frm, doc){
    frappe.call({
        method: "epos_restaurant_2023.api.product.get_currenct_cost",
        args: {
            product_code:doc.product_code,
			stock_location:frm.doc.stock_location,
			unit:doc.unit
        },
        callback: function(r){
            if(r.message!=undefined){
                doc.current_quantity = r.message.quantity;
				doc.current_cost = r.message.cost;
				doc.total_current_cost=doc.current_quantity * doc.current_cost;  
				doc.difference_account = frm.doc.difference_account
				doc.cost = r.message.cost;
				doc.quantity = doc.current_quantity;
				doc.total_amount = doc.quantity * doc.cost;      
                doc.difference_quantity = doc.quantity - doc.current_quantity;
                doc.difference_amount = (doc.cost * doc.quantity) - (doc.current_cost * doc.current_quantity); 
                update_totals(frm)
            }
        }
    });	
}

function update_product_amount(frm,cdt, cdn)  {
    let doc = locals[cdt][cdn];
	frappe.model.set_value(cdt,cdn, "total_amount", (doc.quantity * doc.cost));
	frappe.model.set_value(cdt,cdn, "difference_quantity", (doc.quantity - doc.current_quantity));
	frappe.model.set_value(cdt,cdn, "difference_amount", ((doc.cost * doc.quantity) - (doc.current_cost * doc.current_quantity)));
    update_totals(frm);
}

function update_totals(frm) {
    let sum_total = 0;
	let total_qty = 0;
    let current_sum_total = 0;
	let current_total_qty = 0;
  
    $.each(frm.doc.products, function(i, d) {
        sum_total += flt(d.total_amount);
		total_qty +=flt(d.quantity);
        current_sum_total += flt(d.total_current_cost);
		current_total_qty +=flt(d.current_quantity);
    });
    let difference_quantity = total_qty - current_total_qty; 
    let difference_cost = sum_total - current_sum_total; 
    frm.set_value('total_current_cost', current_sum_total);
    frm.set_value('total_current_quantity', current_total_qty);
    frm.set_value('total_cost', sum_total);
    frm.set_value('total_quantity', total_qty);
    frm.set_value('difference_quantity', difference_quantity);
    frm.set_value('difference_cost', difference_cost);  
    frm.set_value('difference_amount', difference_cost);  
	frm.refresh_field("products")
}
function check_row_exist(frm, barcode){
	var row = frm.fields_dict["products"].grid.grid_rows.filter(function(d)
			{ return (d.doc.product_code==undefined?"":d.doc.product_code).toLowerCase() ===barcode.toLowerCase() })[0];
	return row;
}

function add_product_child(frm,p){
	let all_rows = frm.fields_dict["products"].grid.grid_rows.filter(function(d) { return  d.doc.product_code==undefined});
	let row =undefined;
	if (all_rows.length>0){
		if ( all_rows[0].doc.product_code == undefined){ 
			row = all_rows[0];
		}
	}
	let doc = undefined;
	if(row==undefined){
		 doc = frm.add_child("products");
	}else {
		doc = row.doc;
	}
	if(doc!=undefined){
        doc.product_code = p.product_code;
		doc.product_name = p.product_name_en;
		doc.unit = p.unit;
		get_product(frm,doc)
	} 
}