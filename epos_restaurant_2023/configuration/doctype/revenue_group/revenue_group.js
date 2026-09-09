// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Revenue Group", {
	refresh(frm) {
        let expenses = ["default_discount_account","default_expense_account"]
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
        let income = ["default_income_account"]
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
        let liabilities = ["default_coupon_expense_account"]
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
	},
});
