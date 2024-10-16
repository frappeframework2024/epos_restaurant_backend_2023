// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Code", {
    onload(frm){
        if(frm.is_new()){
            frappe.call({
                method: 'epos_restaurant_2023.expense.doctype.expense_code.expense_code.get_branches',
                callback: (r) => {
                    if(r.message){
                        r.message.forEach(p => {
                            frm.add_child('default_expense_accounts', {
                                business_branch : p.name
                            });
                        });
                        frm.refresh_field('default_expense_accounts')
                    }
                },
                error: (r) => {
                    reject(r)
                }
            })
        }
    },
	refresh(frm) {
        frm.set_query("default_expense_account", function() {
            return {
                filters: [
                    ["is_group","=","0"],
                    ["root_type","=","Expenses"]
                ]
            }
        });
        frm.set_query("default_expense_account", "default_expense_accounts", function(doc, cdt, cdn) {
            var item = locals[cdt][cdn];
            return {
                filters: [
                    ["business_branch", "=", item.business_branch],
                    ["is_group", "=", 0],
                    ["account_type","=","Expense"]
                ]
            }
        })
	},
});