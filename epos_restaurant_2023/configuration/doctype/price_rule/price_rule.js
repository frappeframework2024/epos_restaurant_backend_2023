// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Price Rule", {
	before_save: function(frm) {
        if (frm.__already_validated == 1) {
            frm.__already_validated = 0;
            return;
        }
        frappe.validated = false;
        frappe.call({
            method: 'epos_restaurant_2023.configuration.doctype.price_rule.price_rule.verify_is_default', 
            args: { name: frm.doc.name,is_default: frm.doc.is_default },
            callback: function(a) {
                console.log(a);
            if (a.message != "") {
                frappe.confirm(
                    a.message,
                    function() {
                        frm.__already_validated = true;
                        frappe.validated = true;
                        frm.save();
                        frm.refresh();
                    },
                    function() {
                        frappe.validated = false;
                    }
                );
            }
            else {
                frm.__already_validated = true;
                frappe.validated = true;
                frm.save();
                frm.refresh();
            }
        }
        });
    }
});
