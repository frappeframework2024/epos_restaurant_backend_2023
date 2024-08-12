// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
    is_selling_agent(frm){
        frm.set_query("agent_stock_location", function() {
            return {
                filters: [["is_for_consignment","=",1]]
            }
        });
    },
});
