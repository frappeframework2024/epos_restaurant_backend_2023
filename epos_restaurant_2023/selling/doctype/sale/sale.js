// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sale", {
	onload(frm) { 
		
		frm.set_query("tip_account_code", function () {
			return {
				filters: [
					["Account Code", "is_group", "=", 0]
				]
			}
		});
		 
	},
	 

	refresh(frm) { 
		 

		frm.set_query("commission_01_account","sale_products", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
		frm.set_query("commission_02_account","sale_products", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
		frm.set_query("commission_03_account","sale_products", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
		frm.set_query("commission_04_account","sale_products", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
		frm.set_query("commission_05_account","sale_products", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
		frappe.call({
            method: "get_sale_payment_naming_series",
            doc: frm.doc,
            callback: function (r) {
                frm.set_df_property('sale_payment_naming_series', 'options', r.message);
                frm.refresh_field('sale_payment_naming_series');
            },
        });
		
		if (!frm.doc.__islocal && frm.doc.docstatus == 1) {
			frm.dashboard.add_indicator(__("Total Quantity: {0}", [frm.doc.total_quantity]), "blue");
			frm.dashboard.add_indicator(__("Grand Total: {0}", [format_currency(frm.doc.grand_total)]), "blue");
			frm.dashboard.add_indicator(__("Paid: {0}", [format_currency(frm.doc.total_paid)]), "green");
			if (frm.doc.changed_amount > 0) frm.dashboard.add_indicator(__("Changed: {0}", [format_currency(frm.doc.changed_amount)]), "green");
			frm.dashboard.add_indicator(__("Balance: {0}", [format_currency(frm.doc.balance)]), "blue");

			if (frm.doc.commission_amount > 0) {
				frm.dashboard.add_indicator(__("Commission: {0}", [format_currency(frm.doc.commission_amount)]), "green");
			}

			var iframe = document.createElement('iframe');
			iframe.height = "1024";
			iframe.width = "100%";
			iframe.style = "border:none"
			iframe.src = '/printview?doctype=Sale&name=' + frm.doc.name + '&format=' + frappe.get_meta("Sale").fields.find(r => r.fieldname == 'inventory_transaction').default + '&no_letterhead=1&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui';

			document.getElementById('inventory_transaction').appendChild(iframe);



		}

		updateSummary(frm)

		if (frm.doc.docstatus == 0){
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
		if (frm.doc.docstatus == 1 && frm.doc.is_genrate_tax_invoice == 0){
			frappe.db.get_value("POS Config", frm.doc.pos_config,"edit_closed_receipt_required_note",(r) => {
				if (r.edit_closed_receipt_required_note === 1){
					frm.add_custom_button(__('Edit Bill'), function () {
						frappe.prompt([
							{ 'fieldname': 'note', 'fieldtype': 'Data', 'label': 'Note',"reqd": 1,},
						],
							function (d) {
								frappe.call({
									method: "epos_restaurant_2023.api.api.edit_sale_order",
					
									args: {
										name: frm.doc.name,
										note:d.note,
										
									}, callback: function (r) { 
										frm.reload_doc()
										frappe.show_alert({
											message:__('You can change document now.'),
											indicator:'green'
										}, 5);
									}
								})
							},
							'Edit Bill',
							"Edit Bill"
						)
						
					}, __("Actions"));
				}else{
					
					frm.add_custom_button(__('Edit Bill'), function () {
						frappe.call({
							method: "epos_restaurant_2023.api.api.edit_sale_order",
			
							args: {
								name: frm.doc.name
							}, callback: function (r) { 
								frm.reload_doc()
								frappe.show_alert({
									message:__('You can change document now.'),
									indicator:'green'
								}, 5);
	
							}
						})
						
					}, __("Actions"));
				}
				
			});
		}
		 
		
	},
	setup(frm) {
		set_query(frm, "working_day", [["Working Day", "is_closed", "=", 0]]);
		set_query_cashier_shift(frm);
		set_query(frm, "product_code", { allow_sale: 1 });
		set_query(frm, "stock_location", [["Stock Location", "business_branch", "=", frm.doc.business_branch]]);
		set_query(frm, "outlet", [["Outlet", "business_branch", "=", frm.doc.business_branch]]);

		for (const key in frm.fields_dict) {
			if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
				frm.fields_dict[key].$wrapper.addClass('custom_control');
			}

		}
		
	},
	business_branch(frm) {
		set_query(frm, "stock_location", [["Stock Location", "business_branch", "=", frm.doc.business_branch]]);
		set_query(frm, "outlet", [["Outlet", "business_branch", "=", frm.doc.business_branch]]);
		if (frm.doc.business_branch) {
			update_product_price(frm);
		}
	},
	price_rule(frm) {
		if (frm.doc.price_rule) {
			update_product_price(frm);
		}
	},
	working_day(frm) {
		if (frm.doc.working_day == "") {
			frm.doc.posting_date = undefined;
			frm.set_df_property("posting_date", "read_only", 0);
			frm.refresh_field("posting_date");
		} else {
			frappe.db.get_doc('Working Day', frm.doc.working_day)
				.then(doc => {
					frm.doc.posting_date = doc.posting_date;
					frm.set_df_property("posting_date", "read_only", 1);
					frm.refresh_field("posting_date");
				});
		}
		set_query_cashier_shift(frm);
	},
	cashier_shift(frm) {
		frm.set_df_property("shift_name", "read_only", 1);
		if (frm.doc.cashier_shift == "") {
			frm.doc.shift_name = undefined;
			frm.refresh_field("shift_name");
		} else {
			frappe.db.get_doc('Cashier Shift', frm.doc.cashier_shift)
				.then(doc => {
					frm.doc.shift_name = doc.shift_name;
					frm.refresh_field("shift_name");
				});
		}
	},
	scan_barcode(frm) {
		if (frm.doc.scan_barcode != undefined) {
			let barcode = frm.doc.scan_barcode;
			frappe.call({
				method: "epos_restaurant_2023.inventory.doctype.product.product.get_product",
				args: {
					barcode: frm.doc.scan_barcode,
					business_branch: frm.doc.business_branch,
					price_rule: frm.doc.price_rule,
					allow_sale: 1,


				},
				callback: function (r) {

					if (r.message != undefined) {
						if (r.message.status == 0) {
							let row_exist = check_row_exist(frm, barcode, r.message.unit);

							if (row_exist != undefined && frm.doc.append_quantity == 1) {
								row_exist.doc.quantity = row_exist.doc.quantity + 1;
								update_sale_product_amount(frm, row_exist.doc);

							} else {
								add_product_to_sale_product(frm, r.message);
							}
							frm.refresh_field("sale_products");


						} else {
							frappe.show_alert({ message: r.message.message, indicator: "orange" });

						}

					}
					else {
						frappe.throw(_("Load data fail."))
					}
				},
				error: function (r) {
					frappe.throw(_("Load data fail."))
				},
			});


		}
		frm.doc.scan_barcode = "";
		frm.refresh_field('scan_barcode');


	},
	discount_type(frm) {
		update_sale_discount_to_sale_product(self);
		frm.refresh_field('sale_products');
		updateSumTotal(frm);
	},
	discount(frm) {
		if (frm.doc.discount_type == "Percent" && frm.doc.discount > 100) {

			frappe.throw(__("Discount percent cannot greater than 100%"));
		}
		update_sale_discount_to_sale_product(frm);
		frm.refresh_field('sale_products')
		updateSumTotal(frm);

	},
	tax_rule(frm) {
		if (frm.doc.tax_rule) {
			frappe.model.with_doc('Tax Rule', frm.doc.tax_rule, function () {
				let tax_rule = frappe.model.get_doc('Tax Rule', frm.doc.tax_rule);
				$.each(frm.doc.sale_products, function (i, d) {
					if (d.product_tax_rule == undefined) {
						set_product_tax(d, tax_rule);
						update_sale_product_amount(frm, d);
					}
				});

				frm.refresh_field('sale_products');

				updateSumTotal(frm);
			});
		} else {

			$.each(frm.doc.sale_products, function (i, d) {
				if (d.product_tax_rule == undefined) {
					set_product_tax(d, null);
					update_sale_product_amount(frm, d);
				}
			});

			frm.refresh_field('sale_products');

			updateSumTotal(frm);
		}

	},
	customer(frm) {
		frappe.model.with_doc('Customer', frm.doc.customer, function () {
			let customer = frappe.model.get_doc('Customer', frm.doc.customer);

			frm.set_value('discount_type', "Percent");
			frm.set_value('discount', customer.default_discount);
			update_sale_discount_to_sale_product(frm);
			updateSumTotal(frm);

		});
	},
	sale_commission_percent(frm) {
		if(frm.doc.sale_commission_based_on == "First Cost Profit"){
			frm.set_value('sale_commission_amount',frm.doc.sale_profit*(frm.doc.sale_commission_percent/100))
		}
		else if(frm.doc.sale_commission_based_on == "Second Cost Profit"){
			frm.set_value('sale_commission_amount',frm.doc.second_sale_profit*(frm.doc.sale_commission_percent/100))
		}
		else{
			frm.set_value('sale_commission_amount',frm.doc.grand_total*(frm.doc.sale_commission_percent/100))
		}
		frm.refresh_field('sale_commission_amount')
	},
	sale_commission_amount(frm) {
		if(frm.doc.sale_commission_based_on == "First Cost Profit"){
			frm.set_value('sale_commission_percent',frm.doc.sale_commission_amount*100/(frm.doc.sale_profit > 0 ? frm.doc.sale_profit : 1))
		}
		else if(frm.doc.sale_commission_based_on == "Second Cost Profit"){
			frm.set_value('sale_commission_percent',frm.doc.sale_commission_amount*100/(frm.doc.second_sale_profit > 0 ? frm.doc.second_sale_profit : 1))
		}
		else{
			frm.set_value('sale_commission_percent',frm.doc.sale_commission_amount*100/(frm.doc.grand_total > 0 ? frm.doc.grand_total : 1))
		}
		frm.set_value('sale_commission_balance',frm.doc.sale_commission_amount)
		frm.refresh_field('sale_commission_percent')
		frm.refresh_field('sale_commission_balance')
	},
	sale_commission_based_on(frm){
		if(frm.doc.sale_commission_based_on == "First Cost Profit"){
			frm.set_value('sale_commission_amount',frm.doc.sale_profit*(frm.doc.sale_commission_percent/100))
		}
		else if(frm.doc.sale_commission_based_on == "Second Cost Profit"){
			frm.set_value('sale_commission_amount',frm.doc.second_sale_profit*(frm.doc.sale_commission_percent/100))
		}
		else{
			frm.set_value('sale_commission_amount',frm.doc.grand_total*(frm.doc.sale_commission_percent/100))
		}
		frm.set_value('sale_commission_balance',frm.doc.sale_commission_amount)
		frm.refresh_field('sale_commission_amount')
		frm.refresh_field('sale_commission_balance')
	}
});

 
frappe.ui.form.on('Sale Cash Coupon Claim', {
	cash_coupon_items_remove: function (frm){
		updateSumTotal(frm);
	},
	claim_amount(frm,cdt, cdn){
		updateSumTotal(frm);
	}
})


frappe.ui.form.on('Sale Product', {
	form_render:function(frm, cdt,cdn){
		let doc = locals[cdt][cdn];
		const element = document.querySelector('[data-name="' + doc.name + '"]');	
		 
	},

	sale_products_remove: function (frm) {
		updateSumTotal(frm);
	},
	product_code(frm, cdt, cdn) {
		let doc = locals[cdt][cdn];
		product_code(frm, doc);
	},
	price(frm, cdt, cdn) {

		const row = locals[cdt][cdn];
		if (row.allow_change_price == 0 && row.price != row.base_price) {
			frappe.msgprint(__("This is not allow to change price"));
			row.price = row.base_price;
		}
		update_sale_product_amount(frm, row);

	},
	quantity(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		update_sale_product_amount(frm, row);
	},

	unit(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.product_code) {

			get_product_price(frm, row).then((v) => {
				row.price = v;
				update_sale_product_amount(frm, row)
			});
		}
	},
	discount_type(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		update_sale_product_amount(frm, row);
	},
	discount(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		update_sale_product_amount(frm, row);

	},
	product_code(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
	}
})


frappe.ui.form.on('Sale Trade In', {
	
	trade_in_remove: function (frm) {
		const products = frm.doc.trade_in_products; 
		frm.set_value('total_trade_in_amount',products==undefined?0: products.reduce((n, d) => n + d.amount, 0));
		frm.refresh_field("total_trade_in_amount")
		updateSumTotal(frm);
	},
	
	price(frm, cdt, cdn) {

		const row = locals[cdt][cdn];
		
		update_trade_in_amount(frm, row);

	},
	quantity(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		update_trade_in_amount(frm, row);
	},
 
})

function update_trade_in_amount(frm,doc){
	
	doc.amount = doc.price * doc.quantity
	frm.refresh_field('trade_in_products');
	const products = frm.doc.trade_in_products; 
	frm.set_value('total_trade_in_amount',products==undefined?0: products.reduce((n, d) => n + d.amount, 0));
	frm.refresh_field("total_trade_in_amount")
	

	updateSumTotal(frm);
	
}


frappe.ui.form.on("Sale", "refresh", function(frm) {
	frm.set_df_property("sale_commission_to", "read_only", (frm.doc.sale_commission_to ?? "") == "" && (frm.doc.docstatus == 1 || frm.doc.docstatus == 0) ? 0 : 1);
	frm.set_df_property("sale_commission_percent", "read_only", frm.doc.sale_commission_paid_amount > 0 ? 1 : 0);
	frm.set_df_property("sale_commission_amount", "read_only", frm.doc.sale_commission_paid_amount > 0 ? 1 : 0);
	frm.set_df_property("sale_commission_based_on", "read_only", frm.doc.sale_commission_paid_amount > 0 ? 1 : 0);
}),


frappe.ui.form.on('POS Sale Payment', {
	payment_type(frm, cdt, cdn){
		var d = frappe.model.get_doc(cdt, cdn);
		payment = 0
		frm.doc.payment.forEach(a => {
			if(a.name != d.name){
				payment += a.amount
			}
		});
		frappe.model.set_value(cdt, cdn, "input_amount", ((frm.doc.grand_total - payment) * d.exchange_rate));
	},

	input_amount(frm) {
		update_payment_amount(frm);
	}
	,
	payment_remove: function (frm) {
		update_payment_amount(frm);
	}
})


function updateSummary(frm) {
	if((frm.doc.sale_products??[]).length > 0){ 
		const html = frappe.render_template("sale_summary", frm.doc)		
		$(frm.fields_dict['html_summary'].wrapper).html(html);
		
	}else{
		$(frm.fields_dict['html_summary'].wrapper).empty();
	}
	frm.refresh_field('html_summary');
}

function update_payment_amount(frm) {
	$.each(frm.doc.payment, function (i, d) {
		d.amount = d.input_amount / d.exchange_rate;
	});


	frm.refresh_field('payment');
	let payments = frm.doc.payment;
	frm.set_value('total_paid',0);

	if (payments != undefined) {
		frm.set_value('total_paid', payments.reduce((n, d) => n + d.amount, 0));
	}
	// frm.refresh_field('total_paid');
	// frm.set_value('balance', frm.doc.grand_total - frm.doc.total_paid - (frm.doc.total_cash_coupon_claim||0) );
	// frm.refresh_field('balance');
	updateSumTotal(frm);
}

function add_product_to_sale_product(frm, p) {
	let all_rows = frm.fields_dict["sale_products"].grid.grid_rows.filter(function (d) { return d.doc.product_code == undefined });

	let row = undefined;
	if (all_rows.length > 0) {
		if (all_rows[0].doc.product_code == undefined) {
			row = all_rows[0];
		}
	}
	let doc = undefined;
	if (row == undefined) {
		doc = frm.add_child("sale_products");
	} else {
		doc = row.doc;
	}
	if (doc != undefined) {
		doc.product_code = p.product_code;
		doc.product_name = p.product_name_en;
		doc.base_price = p.price,

		doc.price = p.price;
		doc.quantity = 1;
		doc.product_name_kh = p.product_name_kh;
		doc.unit = p.unit;
		doc.allow_change_price = p.allow_change_price;
		doc.allow_free = p.allow_free;
		doc.allow_discount = p.allow_discount;
		doc.product_tax_rule = p.tax_rule;
		doc.tax_rule = p.tax_rule;
		if (p.tax_rule_doc) {
			set_product_tax(doc, p.tax_rule_doc);
		}
		update_sale_product_amount(frm, doc);
	}

}

function check_row_exist(frm, barcode, unit) {

	var row = frm.fields_dict["sale_products"].grid.grid_rows.filter(function (d) {
		return (
			(d.doc.product_code == undefined ? "" : d.doc.product_code).toLowerCase() === barcode.toLowerCase() &&
			d.doc.unit === unit)
	})[0];
	return row;
}

function set_query(frm, field_name, filters) {

	frm.set_query(field_name, function () {
		return {
			filters: filters
		}
	});

}
function set_query_cashier_shift(frm) {
	if (frm.doc.working_day != undefined) {
		set_query(frm, "cashier_shift", [["Cashier Shift", "is_closed", "=", 0], ["Cashier Shift", "working_day", "=", frm.doc.working_day]]);
	} else {
		set_query(frm, "cashier_shift", [["Cashier Shift", "is_closed", "=", 0]]);
	}
}

async function update_product_price(frm) {

	let rows = frm.fields_dict["sale_products"].grid.grid_rows;
	const promises = [];
	$.each(rows, async function (i, d) {


		if (d.doc.product_code != undefined) {
			const promise = frappe.call({
				method: "epos_restaurant_2023.inventory.doctype.product.product.get_product_price",

				args: {
					barcode: d.doc.product_code,
					business_branch: frm.doc.business_branch,
					price_rule: frm.doc.price_rule,
					unit: d.doc.unit,
					portion: d.portion
				},
				callback: function (r) {
					d.doc.price = r.message.price;
					d.doc.base_price = r.message.price;

					d.doc.sub_total = d.doc.price * d.doc.quantity;
					d.doc.amount = d.doc.sub_total - d.doc.discount_amount;
				},
				error: function (r) {
					frappe.throw(_("Load data fail."))
				},
			});
			promises.push(promise);
		}
	});

	Promise.all(promises).then(() => {
		updateSumTotal(frm);
		frm.refresh();

	})

}


function updateSumTotal(frm) { 
	const products = frm.doc.sale_products; 
 
	frm.set_value('sub_total',products==undefined?0: products.reduce((n, d) => n + d.sub_total, 0));
	frm.set_value('total_quantity',products==undefined?0: products.reduce((n, d) => n + d.quantity, 0));
	frm.set_value('product_discount',products==undefined?0: products.reduce((n, d) => n + d.discount_amount || 0, 0));
	frm.set_value('sale_discountable_amount',products==undefined?0: products.reduce((n, d) => n + (d.allow_discount == 0 || d.discount_amount > 0 ? 0 : d.sub_total), 0));

	let discount = 0;
	if (frm.doc.discount_type == "Percent") {
		discount = frm.doc.sale_discountable_amount * frm.doc.discount / 100;
	} else {
		discount = frm.doc.discount;
	}
	//UPDATE TAX FROM SALE PRODUCT
	frm.set_value('taxable_amount_1',products==undefined?0: products.reduce((n, d) => n + d.taxable_amount_1, 0));
	frm.set_value('taxable_amount_2',products==undefined?0: products.reduce((n, d) => n + d.taxable_amount_2, 0));
	frm.set_value('taxable_amount_3',products==undefined?0: products.reduce((n, d) => n + d.taxable_amount_3, 0));
	frm.set_value('tax_1_amount',products==undefined?0: products.reduce((n, d) => n + d.tax_1_amount, 0));
	frm.set_value('tax_2_amount',products==undefined?0: products.reduce((n, d) => n + d.tax_2_amount, 0));
	frm.set_value('tax_3_amount',products==undefined?0: products.reduce((n, d) => n + d.tax_3_amount, 0));
	frm.set_value('total_tax',products==undefined?0: products.reduce((n, d) => n + d.total_tax, 0));


	frm.set_value('sale_discount', discount);
	frm.set_value('total_discount', discount + frm.doc.product_discount);
	frm.set_value('grand_total', (frm.doc.sub_total - frm.doc.total_discount) + frm.doc.total_tax);

	frm.set_value('total_paid',0)
	if (frm.doc.payment != undefined) {
		frm.set_value('total_paid', frm.doc.payment.reduce((n, d) => n + d.amount, 0));
	}
	
	frm.set_value('total_cash_coupon_claim',0)
	if (frm.doc.cash_coupon_items != undefined) {
		frm.set_value('total_cash_coupon_claim', frm.doc.cash_coupon_items.reduce((n, d) => n + d.claim_amount, 0));
	}

	
	frm.set_value('balance', frm.doc.grand_total - frm.doc.total_paid - (frm.doc.total_cash_coupon_claim || 0) - (frm.doc.total_trade_in_amount || 0) );
	if (frm.doc.balance < 0){
		frm.set_value('balance',0)
		frm.set_value('changed_amount', (frm.doc.total_paid + (frm.doc.total_cash_coupon_claim||0)) - frm.doc.grand_total)
	}


	frm.refresh_field('grand_total');
	frm.refresh_field('html_summary');

	updateSummary(frm)


}

function calculate_sale_product_tax(doc) {
	if (doc.tax_rule) {

		if (doc.calculate_tax_1_after_discount == true) {
			doc.taxable_amount_1 = doc.sub_total - doc.total_discount
		} else {
			doc.taxable_amount_1 = doc.sub_total;
		}

		doc.tax_1_amount = doc.taxable_amount_1 * doc.tax_1_rate / 100;

		//tax 2
		if (doc.calculate_tax_2_after_discount == true) {
			doc.taxable_amount_2 = doc.sub_total - doc.total_discount;
		} else {
			doc.taxable_amount_2 = doc.sub_total;
		}
		if (doc.calculate_tax_2_after_adding_tax_1 == true) {
			doc.taxable_amount_2 = doc.taxable_amount_2 + doc.tax_1_amount;
		}
		doc.tax_2_amount = doc.taxable_amount_2 * doc.tax_2_rate / 100;

		//tax 3
		if (doc.calculate_tax_3_after_discount == true) {
			doc.taxable_amount_3 = doc.sub_total - doc.total_discount;
		} else {
			doc.taxable_amount_3 = doc.sub_total;
		}
		if (doc.calculate_tax_3_after_adding_tax_1 == true) {
			doc.taxable_amount_3 = doc.taxable_amount_3 + doc.tax_1_amount;
		}
		if (doc.calculate_tax_3_after_adding_tax_2 == true) {
			doc.taxable_amount_3 = doc.taxable_amount_3 + doc.tax_2_amount;
		}
		doc.tax_3_amount = doc.taxable_amount_3 * doc.tax_3_rate / 100;

		//total tax
		doc.total_tax = doc.tax_1_amount + doc.tax_2_amount + doc.tax_3_amount;
	} else {
		doc.taxable_amount_1 = 0;
		doc.tax_1_amount = 0;
		doc.taxable_amount_2 = 0;
		doc.tax_2_amount = 0;
		doc.taxable_amount_3 = 0;
		doc.tax_3_amount = 0;
		doc.total_tax = 0;
	}


	//end tax calculateion
}


function product_code(frm, doc) {
	if (doc.product_tax_rule) {
		frappe.model.with_doc('Tax Rule', doc.product_tax_rule, function () {
			let tax_rule = frappe.model.get_doc('Tax Rule', doc.product_tax_rule);

			set_product_tax(doc, tax_rule)

			get_product_price(frm, doc).then((v) => {
				doc.price = v;
				update_sale_product_amount(frm, doc)

			});
		});
	}

}

function set_product_tax(doc, tax_rule) {
	if (tax_rule) {
		doc.tax_rule = tax_rule.name;
		doc.tax_1_rate = tax_rule.tax_1_rate;
		doc.calculate_tax_1_after_discount = tax_rule.calculate_tax_1_after_discount;

		doc.tax_2_rate = tax_rule.tax_2_rate;
		doc.calculate_tax_2_after_discount = tax_rule.calculate_tax_2_after_discount;
		doc.calculate_tax_2_after_adding_tax_1 = tax_rule.calculate_tax_2_after_adding_tax_1;

		doc.tax_3_rate = tax_rule.tax_3_rate;
		doc.calculate_tax_3_after_discount = tax_rule.calculate_tax_3_after_discount;
		doc.calculate_tax_3_after_adding_tax_1 = tax_rule.calculate_tax_3_after_adding_tax_1;
		doc.calculate_tax_3_after_adding_tax_2 = tax_rule.calculate_tax_3_after_adding_tax_2;
	} else {
		doc.tax_rule = "";
		doc.tax_1_rate = 0;
		doc.calculate_tax_1_after_discount = 0;

		doc.tax_2_rate = 0;
		doc.calculate_tax_2_after_discount = 0;
		doc.calculate_tax_2_after_adding_tax_1 = 0;

		doc.tax_3_rate = 0;
		doc.calculate_tax_3_after_discount = 0;
		doc.calculate_tax_3_after_adding_tax_1 = 0;
		doc.calculate_tax_3_after_adding_tax_2 = 0;
	}
}

function update_product_variants(frm, doc) {
	frm.set_query("product_variants", "Product Variants", function (doc, cdt, cdn) {
		let d = locals[cdt][cdn];
		return {
			filters: { "docstatus": 0 }
		}
	})
}

function update_sale_product_amount(frm, doc) {

	doc.sub_total = doc.price * doc.quantity;

	if (doc.discount) {
		if (doc.discount_type == "Percent") {
			doc.discount_amount = (doc.sub_total * doc.discount / 100);
		} else {
			doc.discount_amount = doc.discount;
		}
		doc.sale_discount_percent = 0;
		doc.sale_discount_amount = 0;
	} else {
		doc.discount_amount = 0;
		//check if sale have discount then add discount to sale

	}
	if (doc.sale_discount_percent) {
		doc.sale_discount_amount = (doc.sub_total * doc.sale_discount_percent / 100);

	}
	doc.total_discount = doc.discount_amount + doc.sale_discount_amount;

	calculate_sale_product_tax(doc);

	doc.amount = (doc.sub_total - doc.discount_amount) + doc.total_tax;

	frm.refresh_field('sale_products');
	updateSumTotal(frm);

}
function update_sale_discount_to_sale_product(frm) {
	let products = frm.doc.sale_products
	if (products == undefined) {
		return false;
	}
	let sale_discount = frm.doc.discount


	if (sale_discount > 0) {
		if (frm.doc.discount_type == "Amount") {
			let discountable_amount = products.reduce((n, d) => n + (d.allow_discount == 0 || d.discount_amount > 0 ? 0 : d.sub_total), 0)
			sale_discount = (sale_discount / discountable_amount) * 100
		}
	}
	$.each(products, function (i, d) {
		// check if sale has discount
		if (sale_discount > 0 && d.allow_discount && d.discount == 0) {

			d.sale_discount_percent = sale_discount
			d.sale_discount_amount = (sale_discount / 100) * d.sub_total
		}
		else {
			d.sale_discount_percent = 0
			d.sale_discount_amount = 0
		}
		d.total_discount = d.sale_discount_amount + d.discount_amount;

		calculate_sale_product_tax(d);
	});
}

let get_product_price = function (frm, doc) {

	return new Promise(function (resolve, reject) {

		frappe.call({
			method: "epos_restaurant_2023.inventory.doctype.product.product.get_product_price",
			args: {
				barcode: doc.product_code,
				business_branch: frm.doc.business_branch,
				price_rule: frm.doc.price_rule,
				unit: doc.unit,
				portion: doc.portion
			},
			callback: function (r) {

				resolve(r.message.price)
			},
			error: function (r) {
				reject("error")
			},
		});
	});
}



window.addEventListener('message', function (event) {
	if (event.origin !== window.location.origin) {
		return;
	}
	//frappe.set_route('app/product/' + event.data);
});
