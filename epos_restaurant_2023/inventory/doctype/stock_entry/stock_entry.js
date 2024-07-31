// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
frappe.ui.form.on("Stock Entry",{
    setup(frm){
        frm.set_query("product_code","items", function() {
            return {
                filters: {
                    is_inventory_product: 1
                }
            }
        });
    },
    scan_barcode(frm){
		if(frm.doc.scan_barcode!=undefined){
				let barcode = frm.doc.scan_barcode;
				frappe.call({
					method: "epos_restaurant_2023.inventory.doctype.product.product.get_product",
					args: {
						barcode:frm.doc.scan_barcode,
						business_branch:frm.doc.business_branch,
						is_inventory_product:1
					},
					callback: function(r){
						if(r.message!=undefined){
							if(r.message.status ==0){ 
								let row_exist = check_row_exist(frm,barcode);
								if(row_exist!=undefined && frm.doc.append_quantity == 1){
									update_product_quantity(frm,row_exist);
								}else {
									add_product_child(frm,r.message);
								}
								frm.refresh_field("items");
							}else {
								frappe.show_alert({message:r.message.message, indicator:"orange"});
							}
						}
					}
				});
		}
		frm.doc.scan_barcode = "";
		frm.refresh_field('scan_barcode');
	},
    stock_location(frm){
		frm.doc.items.forEach(a => {
			set_expense_account(frm,'Stock Entry Products',a.name);
			set_cost(frm,'Stock Entry Products',a.name);
		});
		update_totals(frm);
    },
});

frappe.ui.form.on("Stock Entry Products", {
    product_code(frm,cdt, cdn){
		set_cost(frm,cdt,cdn)
		set_expense_account(frm,cdt,cdn)
    },
    quantity(frm,cdt, cdn){
        update_item_amount(frm,cdt, cdn)
    },
    price(frm,cdt, cdn){
        update_item_amount(frm,cdt, cdn)
    },
	unit(frm,cdt,cdn){
		set_cost(frm,cdt,cdn)
	}
});

function validate_stock_location(frm){
	if (frm.doc.stock_location == undefined){
		frappe.throw("Please Select Stock Location First")
		return
	}
}

function set_expense_account(frm,cdt,cdn){
	validate_stock_location(frm)
	let doc = locals[cdt][cdn];
	frm.call({
		method: 'epos_restaurant_2023.inventory.doctype.stock_entry.stock_entry.get_expense_account',
		args: {
			product_code: doc.product_code,
			branch:frm.doc.business_branch
		},
		callback: (r) => {
			if(r.message){
				frappe.model.set_value(cdt, cdn, "expense_account", (r.message || ""));
			}
		}
	})
}

function update_item_amount(frm,cdt, cdn)  {
    doc = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", (doc.quantity * doc.price));
	frappe.model.set_value(cdt, cdn, "total_secondary_cost", (doc.quantity * doc.secondary_cost));
	update_totals(frm);
}

function set_cost(frm,cdt,cdn){
	let doc = locals[cdt][cdn];
	frappe.call({
		method: "epos_restaurant_2023.api.product.get_currenct_cost",
		args: {
			product_code:doc.product_code,
			stock_location:frm.doc.stock_location,
			unit:doc.unit
		},
		callback: function(r){
			if(doc!=undefined){
				frappe.model.set_value(cdt, cdn, "price", (r.message.cost));
				frappe.model.set_value(cdt, cdn, "base_cost", (r.message.cost));
				frappe.model.set_value(cdt, cdn, "amount", (doc.quantity * doc.price));
			}
		}
	});
}

function update_totals(frm) {
    let sum_total = 0;
	let total_qty = 0;
	frm.doc.items.forEach(d => {
		sum_total += flt(d.amount);
		total_qty += flt(d.quantity);
	});
    frm.set_value('total_amount', sum_total);
    frm.set_value('total_quantity', total_qty);
}

function check_row_exist(frm, barcode){
	var row = frm.fields_dict["items"].grid.grid_rows.filter(function(d)
			{ return (d.doc.product_code == undefined ? "" : d.doc.product_code).toLowerCase() === barcode.toLowerCase() })[0];
	return row;
}
function update_product_quantity(frm, row){
	if(row!=undefined){
		frappe.model.set_value('Stock Entry Products', row.doc.name, "quantity", (row.doc.quantity + 1));
		frappe.model.set_value('Stock Entry Products', row.doc.name, "amount", (row.doc.quantity * row.doc.price));
		update_totals(frm);
	}
}

function add_product_child(frm,p){
	let all_rows = frm.fields_dict["items"].grid.grid_rows.filter(function(d) { return  d.doc.product_code==undefined});
	let row = undefined;
	if (all_rows.length>0)
	{
		if ( all_rows[0].doc.product_code == undefined)
		{ 
			row = all_rows[0];
		}
	}
	let doc = undefined;
	if(row==undefined){
		 doc = frm.add_child("items");
	}else {
		doc = row.doc;
	}
	if(doc!=undefined){ 
		doc.product_code = p.product_code;
		doc.product_name = p.product_name_en;
		doc.price = p.price;
		doc.quantity = 1;
		doc.amount = doc.quantity * doc.price;
		doc.unit = p.unit;
        doc.is_inventory_product = p.is_inventory_product;
		frappe.call({
			method: "epos_restaurant_2023.api.product.get_currenct_cost",
			args: {
				product_code:doc.product_code,
				stock_location:frm.doc.stock_location,
				unit:doc.unit
			},
			callback: function(r){
				doc.price = r.message.cost;
				doc.base_cost = r.message.cost;
				doc.amount = doc.quantity * doc.price;
			}
		}).then((v)=>{
			frm.refresh_field('items');
			set_expense_account(frm,'Stock Entry Products',doc.name);
			update_totals(frm);
		});
	} 
}