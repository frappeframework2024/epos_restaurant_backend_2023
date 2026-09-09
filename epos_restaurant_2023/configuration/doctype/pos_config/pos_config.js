// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("POS Config", {
	onload(frm) {
        frm.set_query("tip_account_code", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        frm.set_query("account_code","payment_type", function() {
            return {
                filters: [
                    ["Account Code","is_group", "=", 0]
                ]
            }
        });
       let expenses = ["default_discount_account","default_expense_account","default_coupon_payment_expense_account"]
        expenses.forEach((fieldname) => {
            frm.set_query(fieldname, "default_account", function () {
                return {
                    filters: [
                        ["Chart Of Account", "is_group", "=", 0],
                        ["Chart Of Account", "root_type", "=", "Expenses"]
                    ]
                }
            });
        });
        let income = ["default_income_account","default_unused_coupon_account"]
        income.forEach((fieldname) => {
            frm.set_query(fieldname, "default_account", function () {
                return {
                    filters: [
                        ["Chart Of Account", "is_group", "=", 0],
                        ["Chart Of Account", "root_type", "=", "Income"]
                    ]
                }
            });
        });
        let liabilities = ["default_unearned_revenue_account","default_credit_account"]
        liabilities.forEach((fieldname) => {
            frm.set_query(fieldname, "default_account", function () {
                return {
                    filters: [
                        ["Chart Of Account", "is_group", "=", 0],
                        ["Chart Of Account", "root_type", "=", "Liabilities"]
                    ]
                }
            });
        });
        frm.set_query("default_inventory_account", "default_account", function () {
            return {
                filters: [
                    ["Chart Of Account", "is_group", "=", 0],
                    ["Chart Of Account", "root_type", "=", "Asset"]
                ]
            }
        });
	},
});
