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
		update_stock_from(frm)
    },
});

frappe.ui.form.on("Stock Take Products", {
    product_code(frm,cdt, cdn){
        product_code(frm,cdt,cdn);
        frm.refresh_field('stock_take_products');
    },
    quantity(frm,cdt, cdn){
        update_stock_take_product_amount(frm,cdt, cdn)
    },
    price(frm,cdt, cdn){
        update_stock_take_product_amount(frm,cdt, cdn)
    }
});

function update_stock_take_product_amount(frm,cdt, cdn)  {
    let doc = locals[cdt][cdn];
		if(doc.quantity <= 0) doc.quantity = 1;
		doc.amount=doc.quantity * doc.price;
	    frm.refresh_field('stock_take_products');
		updateSumTotal(frm);
}

function updateSumTotal(frm) {
    
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
		row.doc.amount = row.doc.quantity * row.doc.price;
		frm.refresh_field('stock_take_products');
		updateSumTotal(frm);
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
		doc.amount=doc.quantity * doc.price;
		frm.refresh_field('stock_take_products');
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
async function update_stock_from(frm){
	let rows = frm.fields_dict["stock_take_products"].grid.grid_rows;
	 $.each(rows, async function(i, d)  {
		
		if(d.doc.product_code!=undefined)
		{
			get_product_cost(frm,d.doc).then((v)=>{
				d.doc.price = v;
				d.doc.amount = d.doc.price * d.doc.quantity;
				frm.refresh_field('stock_take_products');
				updateSumTotal(frm);
			});
		}
	});
	

}
function product_code(frm,cdt,cdn){
	let doc = locals[cdt][cdn]
	get_product_cost(frm,doc).then((v)=>{
		doc.price = v;
		frm.refresh_field('stock_take_products');
		update_stock_take_product_amount(frm,cdt,cdn)
	});
}