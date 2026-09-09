// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Product Category", {
	refresh(frm) {
       let fields = ["default_expense_account","default_discount_account"]
        fields.forEach((fieldname) => {
            frm.set_query(fieldname, "default_accounts", function () {
                return {
                    filters: [
                        ["Chart Of Account", "is_group", "=", 0],
                        ["Chart Of Account", "root_type", "=", "Expenses"]
                    ]
                }
            });
        })
         frm.set_query("default_income_account", "default_accounts", function () {
            return {
                filters: [
                    ["Chart Of Account", "is_group", "=", 0],
                    ["Chart Of Account", "root_type", "=", "Income"]
                ]
            }
        });
        frm.set_query("default_inventory_account", "default_accounts", function () {
            return {
                filters: [
                    ["Chart Of Account", "is_group", "=", 0],
                    ["Chart Of Account", "root_type", "=", "Asset"]
                ]
            }
        });
	},
    setup(frm){
        frm.set_query('parent_product_category', () => {
            return {
                filters: {
                    is_group: 1
                }
            }
        });
    },
});
