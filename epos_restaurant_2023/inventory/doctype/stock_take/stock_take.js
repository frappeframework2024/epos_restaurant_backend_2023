// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
frappe.ui.form.on("Stock Take",{
    setup(frm){
        frm.set_query("product_code","stock_take_products", function() {
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
								frm.refresh_field("stock_take_products");
							}else {
								frappe.show_alert({message:r.message.message, indicator:"orange"});
							}
						}
						else {
							alert("Fail")
						}
					},
					error: function(r) {
						alert("load data fail");
					},
				});
		}
		frm.doc.scan_barcode = "";
		frm.refresh_field('scan_barcode');
	},
    stock_location(frm){
		if(frm.doc.stock_take_products.length > 0){
            $.each(frm.doc.stock_take_products, function(i, d) {
                if(d.product_code){
					get_currenct_cost(frm,d);
					update_totals(frm);
				}
            });
        }
    },
});

frappe.ui.form.on("Stock Take Products", {
    product_code(frm,cdt, cdn){
		let doc = locals[cdt][cdn];
        product_code(frm,cdt,cdn);
		get_currenct_cost(frm,doc)
    },
    quantity(frm,cdt, cdn){
        update_stock_take_product_amount(frm,cdt, cdn)
    },
    cost(frm,cdt, cdn){
        update_stock_take_product_amount(frm,cdt, cdn)
    },
	unit(frm,cdt,cdn){
		let doc = locals[cdt][cdn];
		get_currenct_cost(frm,doc)
	}
});

function update_stock_take_product_amount(frm,cdt, cdn)  {
    let doc = locals[cdt][cdn];
	if(doc.quantity <= 0) doc.quantity = 1;
	frappe.model.set_value(cdt, cdn, "amount", ((doc.quantity * doc.cost) || 0));
	frappe.model.set_value(cdt, cdn, "total_secondary_cost", ((doc.quantity * doc.secondary_cost) || 0));
	update_totals(frm);
}

function get_currenct_cost(frm,doc){
	if (frm.doc.stock_location == undefined){
		frappe.throw("Please Select Stock Location First")
		return
	}

	frappe.call({
		method: "epos_restaurant_2023.api.product.get_currenct_cost",
		args: {
			product_code:doc.product_code,
			stock_location:frm.doc.stock_location,
			unit:doc.unit
		},
		callback: function(r){
			if(doc!=undefined){
				doc.cost = r.message.cost;
				doc.base_cost = r.message.cost;
				doc.amount = doc.quantity * doc.cost;
			}
			frm.refresh_field('stock_take_products');
			update_totals(frm)
		}
	});
}

function update_totals(frm) {
    let sum_total = 0;
	let total_qty = 0;
    $.each(frm.doc.stock_take_products, function(i, d) {
        sum_total += flt(d.amount);
		total_qty +=flt(d.quantity);
    });
    frm.set_value('total_amount', sum_total);
    frm.set_value('total_quantity', total_qty);
	frm.refresh_field("total_amount");
	frm.refresh_field("total_quantity");
}

function check_row_exist(frm, barcode){
	var row = frm.fields_dict["stock_take_products"].grid.grid_rows.filter(function(d)
			{ return (d.doc.product_code==undefined?"":d.doc.product_code).toLowerCase() ===barcode.toLowerCase() })[0];
	return row;
}
function update_product_quantity(frm, row){
	if(row!=undefined){
		row.doc.quantity = row.doc.quantity + 1;
		row.doc.amount = row.doc.quantity * row.doc.cost;
		frm.refresh_field('stock_take_products');
		update_totals(frm);
	}
}

function add_product_child(frm,p){
	let all_rows = frm.fields_dict["stock_take_products"].grid.grid_rows.filter(function(d) { return  d.doc.product_code==undefined});
	let row =undefined;
	if (all_rows.length>0){
		if ( all_rows[0].doc.product_code == undefined){ 
			row = all_rows[0];
		}
	}
	let doc = undefined;

	if(row==undefined){
		 doc = frm.add_child("stock_take_products");
	}else {
		doc = row.doc;
	}
	if(doc!=undefined){ 
		doc.product_code = p.product_code;
		doc.product_name = p.product_name_en;
		doc.quantity = 1;
		doc.unit = p.unit;
		get_cost(frm,doc)
	} 
}

function get_cost(frm,doc){
	get_product_cost(frm,doc).then((v)=>{
		doc.cost = v;
		doc.base_cost = v;
		doc.amount = doc.quantity * doc.cost;
		frm.refresh_field('stock_take_products');
		update_totals(frm);
	});
}
let get_product_cost = function (frm,doc) {
	return new Promise(function(resolve, reject) {
		frappe.call({
			method: "epos_restaurant_2023.api.product.get_currenct_cost",
			args: {
				product_code:doc.product_code,
				stock_location:frm.doc.stock_location,
				unit:doc.unit
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

function product_code(frm,cdt,cdn){
	let doc = locals[cdt][cdn]
	get_product_cost(frm,doc).then((v)=>{
		doc.cost = v;
		doc.base_cost = v;
		frm.refresh_field('stock_take_products');
		update_stock_take_product_amount(frm,cdt,cdn)
	});
}