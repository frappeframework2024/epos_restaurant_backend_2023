// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
    is_selling_agent(frm){
        frm.set_query("agent_stock_location", function() {
            return {
                filters: [["is_for_consignment","=",1]]
            }
        });
        frm.set_query("commission_account", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
    },
    refresh(frm){
        frappe.call({
			method: 'epos_restaurant_2023.employee_management.doctype.employee.employee.get_account_balance',
			args: {
				posting_date: new Date().toJSON().slice(0, 10),
                party_type: "Employee",
                party: frm.doc.name,
                account: frm.doc.commission_account
			},
			callback: (r) => {
                frm.doc.commission_amount = r.message.total_amount
                frm.doc.paid_amount = r.message.paid_amount
                frm.doc.balance = r.message.balance
                frm.refresh_field("commission_amount")
                frm.refresh_field("paid_amount")
                frm.refresh_field("balance")
			},
			error: (r) => {
				reject(r)
			}
		})
        frm.set_query("commission_account", function() {
            return {
                filters: [["is_group","=",0],["root_type","=","Liabilities"]]
            }
        });
    }
});
