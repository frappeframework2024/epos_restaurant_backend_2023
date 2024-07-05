// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
frappe.ui.form.on("Stock Entry ",{
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
		if(frm.doc.items.length > 0){
            $.each(frm.doc.items, function(i, d) {
                if(d.product_code){
					get_currenct_cost(frm,d);
					updateSumTotal(frm);
				}
            });
        }
    },
});

frappe.ui.form.on("Stock Entry Products", {
    product_code(frm,cdt, cdn){
		let doc = locals[cdt][cdn];
        product_code(frm,cdt,cdn);
		get_currenct_cost(frm,doc)
    },
    quantity(frm,cdt, cdn){
        update_stock_take_product_amount(frm,cdt, cdn)
    },
    price(frm,cdt, cdn){
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
		doc.amount=doc.quantity * doc.price;
	    frm.refresh_field('items');
		updateSumTotal(frm);
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
				doc.price = r.message.cost;
				doc.base_cost = r.message.cost;
				doc.amount = doc.quantity * doc.price;
			}
			frm.refresh_field('items');
		}
	});
	
}

function updateSumTotal(frm) {
    
    let sum_total = 0;
	let total_qty = 0;
  
    $.each(frm.doc.items, function(i, d) {
        sum_total += flt(d.amount);
		total_qty +=flt(d.quantity);
		 
    });
	
    
    frm.set_value('total_amount', sum_total);
    frm.set_value('total_quantity', total_qty);
   
	frm.refresh_field("total_amount");
	frm.refresh_field("total_quantity");
}

function check_row_exist(frm, barcode){
	
	var row = frm.fields_dict["items"].grid.grid_rows.filter(function(d)
			{ return (d.doc.product_code==undefined?"":d.doc.product_code).toLowerCase() ===barcode.toLowerCase() })[0];
	return row;
}
function update_product_quantity(frm, row){
	if(row!=undefined){
		row.doc.quantity = row.doc.quantity + 1;
		row.doc.amount = row.doc.quantity * row.doc.price;
		frm.refresh_field('items');
		updateSumTotal(frm);
	}
}

function add_product_child(frm,p){
	let all_rows = frm.fields_dict["items"].grid.grid_rows.filter(function(d) { return  d.doc.product_code==undefined});
	let row =undefined;
	
	if (all_rows.length>0){
		if ( all_rows[0].doc.product_code == undefined){ 
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
		product_by_scan(frm,doc)
	} 
}

function product_by_scan(frm,doc){
	get_product_cost(frm,doc).then((v)=>{
		doc.price = v;
		doc.base_cost = v;
		doc.amount=doc.quantity * doc.price;
		frm.refresh_field('items');
		updateSumTotal(frm);
	});
}
let get_product_cost = function (frm,doc) {
	return new Promise(function(resolve, reject) {
		frappe.call({
			method: "epos_restaurant_2023.inventory.doctype.product.product.get_product_cost_by_stock",
			args: {
				//barcode:d.doc.product_code,
				stock_location:frm.doc.stock_location,
				product_code: doc.product_code
				// product: d.doc.unit,
				// unit: d.doc.unit
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
		doc.price = v;
		doc.base_cost = v;
		frm.refresh_field('items');
		update_stock_take_product_amount(frm,cdt,cdn)
	});
}