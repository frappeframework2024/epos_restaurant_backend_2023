// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Single Product Adjustment", {
	product_code(frm) {
       get_product_info(frm);
	},
    stock_location(frm) {
        get_product_info(frm);
    },
    unit(frm) {
        get_product_info(frm);
    },
    new_quantity(frm) {
        update_totals(frm);
    },
    new_cost(frm) {
        update_totals(frm);
    },
});

function get_product_info(frm) {
    frappe.call({
        method: "epos_restaurant_2023.api.product.get_currenct_cost",
        args: {
            product_code: frm.doc.product_code,
            stock_location: frm.doc.stock_location,
            unit: frm.doc.unit,
        },
        callback: function (r) {
            if (r.message != undefined) {
                frm.set_value("current_quantity", r.message.quantity);
                frm.set_value("current_cost", r.message.cost);
                frm.set_value("total_current_cost", r.message.quantity * r.message.cost);
                update_totals(frm)
            }
        },
    });
}

function update_totals(frm) {
    frm.set_value("total_new_cost", frm.doc.new_quantity * frm.doc.new_cost);
    frm.set_value("difference_quantity", frm.doc.new_quantity - frm.doc.current_quantity);
    frm.set_value("difference_amount", frm.doc.total_new_cost - frm.doc.total_current_cost);
}