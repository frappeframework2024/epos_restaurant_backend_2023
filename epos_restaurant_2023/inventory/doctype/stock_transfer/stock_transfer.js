// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Stock Transfer", {
	setup(frm) {
		for (const key in frm.fields_dict) {
			if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
				frm.fields_dict[key].$wrapper.addClass('custom_control');
			}
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
						stock_location:frm.doc.from_stock_location
					},
					callback: function(r){
						if(r.message!=undefined){
							if(r.message.status ==0){ 
								let row_exist = check_row_exist(frm,barcode);
								if(row_exist!=undefined && frm.doc.append_quantity == 1){
									update_product_quantity(frm,row_exist);
								}else {
									add_product_to_po_product(frm,r.message);
								}
								frm.refresh_field("stock_transfer_products");
							}else {
								frappe.show_alert({message:r.message.message, indicator:"orange"});
							}
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
    from_stock_location(frm, cdt, cdn){
        frm.set_query("to_stock_location", function() {
            return {
                filters: {
                    name: ['!=', frm.doc.from_stock_location]
                }
            }
        })
		if(frm.doc.stock_transfer_products.length > 0){
            $.each(frm.doc.stock_transfer_products, function(i, d) {
                if(d.product_code){
					get_currenct_cost(frm,d)
				}
            });
        }
		update_stock_from(frm)
    },
    to_stock_location(frm){
        frm.set_query("from_stock_location", function() {
            return {
                filters: {
                    name: ['!=', frm.doc.from_stock_location]
                }
            }
        })
    }
});
frappe.ui.form.on('Stock Transfer Products', {
	product_code(frm,cdt, cdn) {
		let doc=   locals[cdt][cdn];
		product_code(frm,cdt,cdn);
		get_currenct_cost(frm,doc)
	},
    quantity(frm,cdt, cdn) {
		update_stock_transfer_products_amount(frm,cdt,cdn);
	},
	unit(frm,cdt, cdn) {
		let doc = locals[cdt][cdn];
		get_currenct_cost(frm,doc)
	},
    business_branch(frm,cdt, cdn){
        let doc = locals[cdt][cdn];
      
        frm.set_query("stock_location", function() {
            return {
                filters: [
                    ["Stock Location","business_branch", "=", doc.business_branch]
                ]
            }
        });
        
        frm.refresh_field('stock_location');
    }
})

function update_stock_transfer_products_amount(frm,cdt, cdn)  {
    let doc=locals[cdt][cdn];
	if(doc.quantity <= 0) doc.quantity = 1;
	doc.amount=doc.quantity * doc.cost;
	frm.refresh_field('stock_transfer_products');
	updateSumTotal(frm);
}

function updateSumTotal(frm) {
    
    let sum_total = 0;
	let total_qty = 0;
  
    $.each(frm.doc.stock_transfer_products, function(i, d) {
        sum_total += flt(d.amount);
		total_qty +=flt(d.quantity);
		 
    });
	
    frm.set_value('total_quantity', total_qty);
	frm.refresh_field("total_quantity");

	frm.set_value('total_amount', sum_total);
	frm.refresh_field("total_amount");
}

function check_row_exist(frm, barcode){
	
	var row = frm.fields_dict["stock_transfer_products"].grid.grid_rows.filter(function(d)
			{ return (d.doc.product_code==undefined?"":d.doc.product_code).toLowerCase() ===barcode.toLowerCase() })[0];
	return row;
}
function update_product_quantity(frm, row){
	if(row!=undefined){
		row.doc.quantity = row.doc.quantity + 1;
		row.doc.amount = row.doc.quantity * row.doc.cost;
		frm.refresh_field('sale_products');
		updateSumTotal(frm);
	}
}

function get_currenct_cost(frm,doc){
	if (frm.doc.from_stock_location == undefined){
		frappe.throw("Please Select Stock Location First")
		return
	}
	frappe.call({
		method: "epos_restaurant_2023.api.product.get_currenct_cost",
		args: {
			product_code:doc.product_code,
			stock_location:frm.doc.from_stock_location,
			unit:doc.unit
		},
		callback: function(r){
			if(doc!=undefined){
				doc.cost = r.message.cost;
				doc.base_cost = r.message.cost;
				doc.amount = doc.cost * doc.quantity;
			}
			frm.refresh_field('stock_transfer_products');
		}
	});
	
}

function add_product_to_po_product(frm,p){
	
	let all_rows = frm.fields_dict["stock_transfer_products"].grid.grid_rows.filter(function(d) { return  d.doc.product_code==undefined});
	let row =undefined;
	
	if (all_rows.length>0){
		if ( all_rows[0].doc.product_code == undefined){ 
			row = all_rows[0];
		}
	}
	let doc = undefined;

	if(row==undefined){
		 doc = frm.add_child("stock_transfer_products");
	}else {
		doc = row.doc;
	}
	if(doc!=undefined){ 
		doc.product_code = p.product_code;
		doc.product_name = p.product_name_en;
		doc.cost = p.cost;
		doc.quantity = 1;
		doc.amount = doc.quantity * doc.cost;
		doc.unit = p.unit;
		doc.product_name = p.product_name_en;
        doc.is_inventory_product = p.is_inventory_product;
        doc.has_expired_date = p.has_expired_date;
		if (p.expired_date){
			doc.expired_date = p.expired_date
		}
		
		product_by_scan(frm,doc)
	} 
}

async function update_stock_from(frm){
	let rows = frm.fields_dict["stock_transfer_products"].grid.grid_rows;
	 $.each(rows, async function(i, d)  {
		
		if(d.doc.product_code!=undefined)
		{
			get_stock_location_product_infor(frm,d.doc).then((v)=>{
				d.doc.cost = v.cost;
				d.doc.base_cost = v.cost;
				if (v.expired_date){
					d.doc.expired_date = v.expired_date
				}
				d.doc.amount = d.doc.cost * d.doc.quantity;
				frm.refresh_field('stock_transfer_products');
				updateSumTotal(frm);
			});
		}
	});
	

}

function product_code(frm,cdt,cdn){
	let doc = locals[cdt][cdn]
	get_stock_location_product_infor(frm,doc).then((v)=>{
		doc.cost = v.cost;
		doc.base_cost = v.cost;
		if (v.expired_date){
			doc.expired_date = v.expired_date
		}
		frm.refresh_field('stock_transfer_products');
		update_stock_transfer_products_amount(frm,cdt,cdn)
	});
}
function product_by_scan(frm,doc){
	get_stock_location_product_infor(frm,doc).then((v)=>{
		doc.cost = v.cost;
		doc.base_cost = v.cost;
		if (v.expired_date){
			doc.expired_date = v.expired_date
		}
		doc.amount=doc.quantity * doc.cost;
		frm.refresh_field('stock_transfer_products');
		updateSumTotal(frm);
	});
}

let get_stock_location_product_infor = function (frm,doc) {
	return new Promise(function(resolve, reject) {
		frappe.call({
			method: "epos_restaurant_2023.inventory.doctype.product.product.get_stock_location_product_info",
			args: {
				stock_location:frm.doc.from_stock_location,
				product_code: doc.product_code
			},
			callback: function(r){
				resolve(r.message)
			},
			error: function(r) {
				reject("error")
			},
		});
	});
}