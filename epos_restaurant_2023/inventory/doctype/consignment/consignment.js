// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Consignment", {
    refresh(frm){
        if(frm.doc.docstatus == 1){
            frm.add_custom_button(__('Add Sale'), function(){
                frappe.call({
                        method: "epos_restaurant_2023.inventory.doctype.consignment.consignment.make_sale",
                        args: {
                            consignment: frm.doc.name
                        },
                        callback: function(r){
                            if(r.message!=undefined){
                                frappe.model.sync(r.message);
                                frappe.set_route("Form", "Sale", r.message.name);
                            }
                        },
                        async: true,
                    });	
            });
        }
        frm.set_query("from_stock_location", function() {
            return {
                filters: [["is_for_consignment","=",0]]
            }
        });
        frm.set_query("employee", function() {
            return {
                filters: [["is_selling_agent","=",1]]
            }
        });
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(("Return Consignment"),
              function () {
                frappe.call({
                    method: "epos_restaurant_2023.inventory.doctype.consignment.consignment.make_return_consignment",
                    args: {
                        consignment: frm.doc.name
                    },
                    callback: function(r){
                        if(r.message!=undefined){
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", "Stock Transfer", r.message.name);
                        }
                    }
                });	
              },
            );
          }
    },
    from_stock_location(frm){
        frm.doc.products.forEach(r => {
            get_product(frm,'Consignment Products',r.name)
        });
    },
    price_rule(frm){
        frm.doc.products.forEach(a => {
            get_product(frm, "Consignment Products", a.name)
        });
    }
});

frappe.ui.form.on('Consignment Products', {
	product(frm,cdt, cdn) {
        get_product(frm, cdt, cdn)
	},
    quantity(frm,cdt, cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt,cdn, "total_cost", (doc.cost * doc.quantity));
        frappe.model.set_value(cdt,cdn, "total_amount", (doc.price * doc.quantity));
        update_product_totals(frm)
    },
    price(frm,cdt, cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt,cdn, "total_cost", (doc.cost * doc.quantity));
        frappe.model.set_value(cdt,cdn, "total_amount", (doc.price * doc.quantity));
        update_product_totals(frm)
    },
    unit(frm,cdt, cdn){
        get_product(frm, cdt, cdn)
    }
})

frappe.ui.form.on('Consignment Payments', {
	payment_type(frm,cdt, cdn) {
        get_payment_type_account(frm, cdt, cdn)
	},
    input_amount(frm,cdt,cdn){
        let doc = locals[cdt][cdn];
        frappe.model.set_value(cdt,cdn, "amount", (doc.input_amount / doc.exchange_rate));
        update_payment_totals(frm)
    }
})

function get_payment_type_account(frm,cdt,cdn){
    let doc = locals[cdt][cdn];
    frappe.call({
        method: "epos_restaurant_2023.inventory.doctype.consignment.consignment.get_payment_type_account",
        args: {
            payment_type: doc.payment_type,
            branch: frm.doc.business_branch
        },
        callback: function(r){
            if(r.message!=undefined){
                frappe.model.set_value(cdt,cdn, "account", (r.message));
            }
        }
    });	
}

function get_product(frm,cdt,cdn){
    let doc = locals[cdt][cdn];
    frappe.call({
        method: "epos_restaurant_2023.api.product.get_currenct_cost",
        args: {
            product_code:doc.product,
			stock_location:frm.doc.from_stock_location,
			unit:doc.unit
        },
        callback: function(r){
            if(r.message!=undefined){
                frappe.model.set_value(cdt,cdn, "quantity_on_hand", (r.message.quantity));
                frappe.model.set_value(cdt,cdn, "cost", (r.message.cost));
                frappe.model.set_value(cdt,cdn, "price", (r.message.price));
                frappe.model.set_value(cdt,cdn, "total_cost", (doc.cost * doc.quantity));
                frappe.model.set_value(cdt,cdn, "total_amount", (doc.price * doc.quantity));
                update_product_totals(frm)
            }
        }
    });	
}

function update_product_totals(frm){
    total_qty = 0
    total_amount = 0
    total_cost = 0
    frm.doc.products.forEach(r => {
        total_qty += (r.quantity || 0)
        total_amount += (r.total_amount || 0)
        total_cost += (r.total_cost || 0)
    });
    frm.set_value("total_quantity",total_qty)
    frm.set_value("total_amount",total_amount)
    frm.set_value("total_cost",total_cost)
}

function update_payment_totals(frm){
    total_amount = 0
    frm.doc.payments.forEach(r => {
        total_amount += (r.amount || 0)
    });
    frm.set_value("total_payment",total_amount)
}