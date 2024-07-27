// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Code", {
	refresh(frm) {
        frm.set_query("default_expense_account", function() {
            return {
                filters: [
                    ["is_group","=","0"],
                    ["root_type","=","Expenses"]
                ]
            }
        });
	},
});
