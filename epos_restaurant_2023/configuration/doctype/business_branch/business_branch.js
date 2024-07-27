// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Business Branch", {
	refresh(frm, ) {
        if(!frm.is_new()){
            frm.add_custom_button(__('Update Business Name Transaction'), function () {
                frm.call("update_to_transaction").then(r=>{
                    
                })
            },"Actions")
        }
        frm.set_query("default_temporary_opening_account", function() {
            return {
                filters: [
                    ["is_group","=","0"],
                    ["account_type","=","Temporary"]
                ]
            }
        });
	},
});
