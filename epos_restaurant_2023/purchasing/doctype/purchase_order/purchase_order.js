// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Order", {
	onload(frm) {
		frappe.call({
			method: "epos_restaurant_2023.purchasing.doctype.purchase_order.purchase_order.get_exchange_rate",
			callback: function (r) {
				if (r.message != undefined) {
					if (frm.doc.__islocal == undefined) {
						frm.doc.exchange_rate = frm.doc.exchange_rate || r.message;
					} else {
						frm.doc.exchange_rate = r.message
					}

				} else {
					frm.doc.exchange_rate = 1
				}
				frm.doc.purchase_order_products.forEach((r => {
					r.exchange_rate = frm.doc.exchange_rate;
					r.cost_second_currency = r.exchange_rate * r.cost;
				}))

				frm.refresh_field('exchange_rate');
			},
			error: function (r) {
				alert("load data fail");
			},
		});

	},
	setup(frm) {
		for (const key in frm.fields_dict) {
			if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
				frm.fields_dict[key].$wrapper.addClass('custom_control');
			}

		}

	},
	refresh(frm) {
		updateSummary(frm);
		AddDiscountButton(frm);
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
    },
	discount_type(frm) {
		update_po_discount_to_po_product(frm);
	},
	discount(frm) {
		if (frm.doc.discount_type == "Percent" && frm.doc.discount > 100) {

			frappe.throw(__("Discount percent cannot greater than 100%"));
		}
		update_po_discount_to_po_product(frm);
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
					frm.doc.discount_type = d.discount_type;
					if (d.discount_type == "Percent") {
						frm.doc.discount = d.discount_percent;
					} else {
						frm.doc.discount = d.discount_amount;
					}
					frm.refresh_field("discount_type");
					frm.refresh_field("discount");
					updateSumTotal(frm);
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
		get_currenct_cost(frm,doc)
		update_po_product_amount(frm, doc);
	},
	unit(frm,cdt,cdn){
		let doc = locals[cdt][cdn];
		get_currenct_cost(frm,doc)
		update_po_product_amount(frm, doc);
	},
	quantity(frm, cdt, cdn) {
		update_purchase_order_products_amount(frm, cdt, cdn);
	},
	cost(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		doc.cost_second_currency = doc.cost * doc.exchange_rate;
		update_purchase_order_products_amount(frm, cdt, cdn);
	},
	cost_second_currency(frm, cdt, cdn) {

		let doc = locals[cdt][cdn];
		doc.cost = doc.cost_second_currency / (doc.exchange_rate || 1);
		update_purchase_order_products_amount(frm, cdt, cdn);
		// frm.refresh_field('purchase_order_products');
	},
	business_branch(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];

		frm.set_query("stock_location", function () {
			return {
				filters: [
					["Stock Location", "business_branch", "=", doc.business_branch]
				]
			}
		});

		frm.refresh_field('stock_location');
	},
	discount_type(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		update_po_product_amount(frm, row);
	},
	discount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (frm.doc.discount_type == "Percent" && frm.doc.discount > 100) {
			frappe.throw(__("Discount percent cannot greater than 100%"));
		}
		update_po_product_amount(frm, row);
		frm.refresh_field('sale_products')
	}
})

function update_purchase_order_products_amount(frm, cdt, cdn) {
	let doc = locals[cdt][cdn];
	if (doc.quantity <= 0) doc.quantity = 1;
	update_po_product_amount(frm, doc)
}

function updateSumTotal(frm) {
	const products = frm.doc.purchase_order_products;
	if (products == undefined) {
		return false;
	}

	frm.set_value('sub_total', products.reduce((n, d) => n + d.sub_total, 0));
	frm.set_value('total_quantity', products.reduce((n, d) => n + d.quantity, 0));
	frm.set_value('po_discountable_amount', products.reduce((n, d) => n + (d.discount_amount > 0 ? 0 : d.sub_total), 0));

	let discount = 0;
	if (frm.doc.discount_type == "Percent") {
		discount = frm.doc.po_discountable_amount * frm.doc.discount / 100;
	} else {
		discount = frm.doc.discount;
	}

	frm.set_value('product_discount', products.reduce((n, d) => n + d.discount_amount, 0));
	frm.set_value('po_discount', discount);
	frm.set_value('total_discount', discount + frm.doc.product_discount);
	frm.set_value('grand_total', frm.doc.sub_total - frm.doc.total_discount);
	frm.set_value('balance', frm.doc.grand_total - frm.doc.total_paid);

	frm.refresh_field("sub_total");
	frm.refresh_field("total_quantity");
	frm.refresh_field("product_discount");
	frm.refresh_field("total_discount");
	frm.refresh_field("grand_total");
	frm.refresh_field("po_discount");
	frm.refresh_field("po_discountable_amount");
	frm.refresh_field("balance");

	updateSummary(frm);
}

function check_row_exist(frm, barcode) {

	var row = frm.fields_dict["purchase_order_products"].grid.grid_rows.filter(function (d) { return (d.doc.product_code == undefined ? "" : d.doc.product_code).toLowerCase() === barcode.toLowerCase() })[0];
	return row;
}
function update_product_quantity(frm, row) {
	if (row != undefined) {
		row.doc.quantity = row.doc.quantity + 1;
		update_po_product_amount(frm, row.doc)
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
		doc.cost = p.cost;
		doc.quantity = 1;
		doc.sub_total = doc.quantity * doc.cost;
		doc.unit = p.unit;
		doc.product_name = p.product_name_en;
		product_by_scan(frm,doc)
		update_po_product_amount(frm, doc)
	}
}

function product_by_scan(frm,doc){
	get_product_cost(frm,doc).then((v)=>{
		doc.cost = v;
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
				resolve(r.message.cost)
			},
			error: function(r) {
				reject("error")
			},
		});
	});
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
				doc.amount = doc.cost * doc.quantity;
			}
			frm.refresh_field('purchase_order_products');
		}
	});
	
}

function update_po_product_amount(frm, doc) {
	doc.exchange_rate = frm.doc.exchange_rate;
	doc.sub_total = doc.cost * doc.quantity;


	if (doc.discount) {
		if (doc.discount_type == "Percent") {
			doc.discount_amount = (doc.sub_total * doc.discount / 100);
			doc.po_discount_percent = doc.discount;

		} else {
			doc.discount_amount = doc.discount;
		}
	} else {
		doc.discount_amount = 0;
		//check if sale have discount then add discount to sale
	}
	if (doc.po_discount_percent) {
		doc.po_discount_amount = (doc.sub_total * doc.po_discount_percent / 100);

	}
	doc.total_discount = doc.discount_amount + doc.po_discount_amount;

	doc.amount = (doc.sub_total - doc.discount_amount);

	frm.refresh_field('purchase_order_products');
	updateSumTotal(frm);

}

function update_po_discount_to_po_product(frm) {
	let products = frm.doc.purchase_order_products
	if (products == undefined) {
		return false;
	}
	let po_discount = frm.doc.discount


	if (po_discount > 0) {
		if (frm.doc.discount_type == "Amount") {
			let discountable_amount = products.reduce((n, d) => n + (d.discount_amount > 0 ? 0 : d.sub_total), 0)
			po_discount = (po_discount / discountable_amount) * 100
		}
	}
	$.each(products, function (i, d) {
		// check if sale has discount
		if (po_discount > 0 && d.discount == 0) {

			d.po_discount_percent = po_discount
			d.po_discount_amount = (po_discount / 100) * d.sub_total
		}
		else {
			d.po_discount_percent = 0
			d.po_discount_amount = 0
		}
		d.total_discount = d.po_discount_amount + d.discount_amount;
	});

	updateSumTotal(frm);
}