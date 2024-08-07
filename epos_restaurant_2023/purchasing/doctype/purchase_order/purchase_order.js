// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Order", {
	setup(frm) {
		for (const key in frm.fields_dict) {
			if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
				frm.fields_dict[key].$wrapper.addClass('custom_control');
			}

		}
	},
	refresh(frm) {
		AddDiscountButton(frm);
		updateSumTotal(frm);
	},
	scan_barcode(frm) {
		if (frm.doc.scan_barcode != undefined) {
			let barcode = frm.doc.scan_barcode;
			frappe.call({
				method: "epos_restaurant_2023.inventory.doctype.product.product.get_product",
				args: {
					barcode: frm.doc.scan_barcode,
					business_branch: frm.doc.business_branch,
				},
				callback: function (r) {
					if (r.message != undefined) {
						if (r.message.status == 0) {
							let row_exist = check_row_exist(frm, barcode);
							if (row_exist != undefined && frm.doc.append_quantity == 1) {
								update_product_quantity(frm, row_exist);
							} else {
								add_product_to_po_product(frm, r.message);
							}
							frm.refresh_field("purchase_order_products");
						} else {
							frappe.show_alert({ message: r.message.message, indicator: "orange" });
						}
					}
					else {
						alert("faile")
					}
				},
				error: function (r) {
					alert("load data fail");
				},
			});
		}
		frm.doc.scan_barcode = "";
		frm.refresh_field('scan_barcode');
	},
	stock_location(frm){ 
        if(frm.doc.purchase_order_products.length > 0){
            $.each(frm.doc.purchase_order_products, function(i, d) {
                if(d.product_code){
					get_currenct_cost(frm,d)
				}
            });
        }
    }
});

function AddDiscountButton(frm) {
	if (frm.doc.docstatus == 0) {
		frm.add_custom_button(__('Apply Discount'), function () {
			frappe.prompt([
				{ 'fieldname': 'discount_type', 'fieldtype': 'Select', 'label': 'Discount Type', 'default': "Percent", "options": "Percent\nAmount" },
				{ 'fieldname': 'discount_percent', 'fieldtype': 'Percent', 'label': 'Discount Percent', "depends_on": "eval:doc.discount_type=='Percent'", },
				{ 'fieldname': 'discount_amount', 'fieldtype': 'Currency', 'label': 'Discount Amount', "depends_on": "eval:doc.discount_type=='Amount'" },
				{ 'fieldname': 'discount_note', 'fieldtype': 'SmallText', 'label': 'Reason' }
			],
				function (d) {
					frm.doc.discount_type = d.discount_type
					frm.doc.purchase_order_products.forEach(r => {
						if(r.discount_amount == 0){
							if(d.discount_type == "Percent"){
								r.po_discount_percent = d.discount_percent
								r.po_discount_amount = (r.amount*(d.discount_percent/100))
							}
							else{
								r.po_discount_percent = ((d.discount_amount/frm.doc.discountable_amount)*100)
								r.po_discount_amount = r.po_discount_percent/100 * r.amount
							}
							r.total_discount = r.po_discount_amount + r.discount_amount
							frm.refresh_field('purchase_order_products');
							updateSumTotal(frm)
						}
					});
				},
				'Discount',
				"Apply Discount"
			)
		}, __("Actions"));
	}
}

function updateSummary(frm) {
	const html = frappe.render_template("purchase_order_summary", frm.doc)
	$(frm.fields_dict['html_summary'].wrapper).html(html);
	frm.refresh_field('html_summary');
}

frappe.ui.form.on('Purchase Order Products', {
	product_code(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		update_product_info(frm, doc);
		set_account(frm,cdt,cdn)
	},
	unit(frm,cdt,cdn){
		let doc = locals[cdt][cdn];
		update_product_info(frm, doc, 1);
	},
	quantity(frm, cdt, cdn) {
		const doc = locals[cdt][cdn];
		update_product_info(frm, doc)
	},
	cost(frm, cdt, cdn) {
		const doc = locals[cdt][cdn];
		update_product_info(frm, doc)
	},
	discount_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_product_info(frm, row);
	},
	discount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (frm.doc.discount_type == "Percent" && frm.doc.discount > 100) {
			frappe.throw(__("Discount percent cannot greater than 100%"));
		}
		update_product_info(frm, row);
	}
})

function updateSumTotal(frm) {
	const products = frm.doc.purchase_order_products;
	if (products == undefined) {
		return false;
	}
	frm.set_value('total_quantity', products.reduce((n, d) => n + d.quantity, 0));
	frm.set_value('sub_total', products.reduce((n, d) => n + d.sub_total, 0));
	frm.set_value('discountable_amount', products.reduce((n, d) => n + (d.discount_amount > 0 ? 0 : d.sub_total), 0));
	frm.set_value('product_discount', products.reduce((n, d) => n + d.discount_amount, 0));
	frm.set_value('discount_amount', products.reduce((n, d) => n + d.po_discount_amount, 0));
	frm.set_value('total_discount', frm.doc.discount_amount + frm.doc.product_discount);
	frm.set_value('grand_total', frm.doc.sub_total - frm.doc.total_discount);
	frm.set_value('balance', frm.doc.grand_total - frm.doc.total_paid);
	discount = frm.doc.discount_amount
	if(frm.doc.discount_type == "Percent"){
		discount = (frm.doc.discount_amount/frm.doc.discountable_amount*100)
	}
	frm.set_value('discount',discount)
	updateSummary(frm);
}

function check_row_exist(frm, barcode) {
	var row = frm.fields_dict["purchase_order_products"].grid.grid_rows.filter(function (d) { return (d.doc.product_code == undefined ? "" : d.doc.product_code).toLowerCase() === barcode.toLowerCase() })[0];
	return row;
}
function update_product_quantity(frm, row) {
	if (row != undefined) {
		row.doc.quantity = row.doc.quantity + 1;
		update_product_info(frm, row.doc)
	}
}
function add_product_to_po_product(frm, p) {
	let all_rows = frm.fields_dict["purchase_order_products"].grid.grid_rows.filter(function (d) { return d.doc.product_code == undefined });
	let row = undefined;

	if (all_rows.length > 0) {
		if (all_rows[0].doc.product_code == undefined) {
			row = all_rows[0];
		}
	}
	let doc = undefined;
	if (row == undefined) {
		doc = frm.add_child("purchase_order_products");
	} else {
		doc = row.doc;
	}
	if (doc != undefined) {
		doc.product_code = p.product_code;
		doc.product_name = p.product_name_en;
		doc.cost = p.last_purchase_cost;
		doc.quantity = 1;
		doc.sub_total = doc.quantity * doc.cost;
		doc.unit = p.unit;
		doc.product_name = p.product_name_en;
		product_by_scan(frm,doc)
		update_product_info(frm, doc)
	}
}

function product_by_scan(frm,doc){
	get_product_cost(frm,doc).then((v)=>{
		doc.cost = v.last_purchase_cost;
		doc.amount = doc.cost * doc.quantity;
		frm.refresh_field('purchase_order_products');
		updateSumTotal(frm);
	});
}
let get_product_cost = function (frm,doc) {
	return new Promise(function(resolve, reject) {
		frappe.call({
			method: "epos_restaurant_2023.inventory.doctype.product.product.get_product_cost_by_stock",
			args: {
				stock_location:frm.doc.stock_location,
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

function validate_filters(frm){
	if (frm.doc.stock_location == undefined){
		frappe.throw("Please Select Stock Location First")
		return
	}
}

function set_account(frm,cdt,cdn){
	validate_filters(frm)
	let doc = locals[cdt][cdn];
	frappe.call({
		method: "epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.get_accounts",
		args: {
			branch: frm.doc.business_branch,
			product: doc.product_code
		},
		callback: function(r){
			if(doc!=undefined){
				frappe.model.set_value(cdt, cdn, "expense_account", (r.message.expense_account || ""));
				frappe.model.set_value(cdt, cdn, "stock_account", (r.message.stock_account || ""));
			}
		}
	});
}

let get_currenct_cost = function(frm,doc){
	validate_filters(frm)
	return new Promise(function(resolve, reject) {
		frappe.call({
			method: "epos_restaurant_2023.api.product.get_currenct_cost",
			args: {
				product_code:doc.product_code,
				stock_location:frm.doc.stock_location,
				unit:doc.unit
			},
			callback: function(r){
				if(doc!=undefined){
					get_uom_conversion(frm,doc).then((factor)=>{
						conversion_factor = ((1/factor).toFixed(2) || 1)
						resolve((r.message.last_purchase_cost * conversion_factor) || 0)
					})
				}
			},
			error: function(r) {
				reject("error")
			}
		});
	})
}

let get_uom_conversion = function (frm,doc) {
	return new Promise(function(resolve, reject) {
    frappe.call({
        method: "epos_restaurant_2023.inventory.inventory.get_uom_conversion",
        args: {
            from_uom: doc.base_unit, 
            to_uom: doc.unit
        },
        callback: function(r){
			resolve(r.message)
		},
		error: function(r) {
			reject("error")
		},
    })
})}

function update_product_info(frm, doc, from_unit=0) {
	if(from_unit == 1){
		get_currenct_cost(frm,doc).then((cost)=>{
			doc.cost = cost
			doc.discount = 0
			update_product_infos(frm,doc)
		})
	}
	else{
		update_product_infos(frm,doc)
	}
}

function update_product_infos(frm,doc){
	doc.sub_total = doc.cost * (doc.quantity<=0 ? 1 : doc.quantity);
	if (doc.discount_type == "Percent") {
		doc.discount_amount = (doc.sub_total * doc.discount / 100);
	} 
	else {
		doc.discount_amount = doc.discount;
	}
	doc.po_discount_amount = doc.po_discount_percent / 100 * doc.sub_total
	doc.total_discount = doc.discount_amount + doc.po_discount_amount;
	doc.amount = (doc.sub_total - doc.total_discount);
	frm.refresh_field('purchase_order_products');
	updateSumTotal(frm);
}