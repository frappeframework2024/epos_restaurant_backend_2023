// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("ePOS Sync Setting", {
	refresh(frm) {
        frm.add_custom_button(__('Init Data From Server'), function(){
           frappe.call({
            method: "epos_restaurant_2023.api.sync_api.generate_init_data_sync_to_client",
            args: {
                business_branch: frm.doc.current_client_branch
               
            },
            callback: function (r) {
                frappe.show_alert({message:__("Data init success."), indicator:"green"});
            }
           })
        },__("Synchronization"));
        frm.add_custom_button(__('Manual Sync From Server'), function(){
            frappe.call({
             method: "epos_restaurant_2023.api.sync_api.get_all_data_for_sync_from_server",
             args: {
                 business_branch: frm.doc.current_client_branch
             },
             callback: function (r) {
                 frappe.show_alert({message:__("Sync Successed."), indicator:"green"});
             }
            })
         },__("Synchronization"));
	},
});
