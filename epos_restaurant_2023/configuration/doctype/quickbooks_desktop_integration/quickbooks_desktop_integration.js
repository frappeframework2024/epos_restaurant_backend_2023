// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quickbooks Desktop Integration", {
	refresh(frm) { 
     // Make reference_type readonly in all child tables
        const child_tables = [
            "tbl_payment_types_mapping",
            "tbl_categories_mapping",
            "tbl_customers_mapping",
            "tbl_chart_of_account_mapping"
        ];      

        child_tables.forEach(table => {
            frm.fields_dict[table].grid.update_docfield_property('reference_type', 'read_only', 1);
        });


        //data chart of account filter
        frm.set_query('qb_data', 'tbl_chart_of_account_mapping', function(doc, cdt, cdn) {
            return {
                filters: {
                    data_type: "Chart Of Account"
                }
            };
        });

        //data payment type filter
        frm.set_query('qb_data', 'tbl_payment_types_mapping', function(doc, cdt, cdn) {
            return {
                filters: {
                    data_type: "Payment Type"
                }
            };
        });

        //data customer filter
        frm.set_query('qb_data', 'tbl_customers_mapping', function(doc, cdt, cdn) {
            return {
                filters: {
                    data_type: "Customer"
                }
            };
        });

        //data customer filter
        frm.set_query('qb_data', 'tbl_products_mapping', function(doc, cdt, cdn) {
            return {
                filters: {
                    data_type: "Product"
                }
            };
        });
        
	},
});


frappe.ui.form.on('Quickbooks Mapping', {
	form_render:function(frm, cdt,cdn){
		let doc = locals[cdt][cdn];		 
	},

    // Trigger when a new row is added to tbl_chart_of_account_mapping
    tbl_chart_of_account_mapping_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'reference_type', "Chart Of Account");
    },


    tbl_payment_types_mapping_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'reference_type', "Payment Type");
    },

    // Trigger when a new row is added to tbl_categories_mapping
    tbl_categories_mapping_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'reference_type', "Revenue Group");
    },

    // Trigger when a new row is added to tbl_customers_mapping
    tbl_customers_mapping_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'reference_type', "Customer"); 
    },

    // Trigger when a new row is added to tbl_customers_mapping
    tbl_products_mapping_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'reference_type', "Product"); 
    },
    

});
