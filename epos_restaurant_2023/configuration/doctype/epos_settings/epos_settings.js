// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("ePOS Settings", {
	refresh(frm) {

	},
    refresh_token:function(frm){
        //
    },
    refresh_token_button:function(frm){
        
        frappe.call({
            method: 'epos_restaurant_2023.api.quickbook_intergration.config.refresh_token',
            type: 'GET',  
            args: {
                "refresh_token":frm.doc.refresh_token
            },
            callback: function(response) {
                if(response){
                    frappe.msgprint({
                        title: __('Refresh Token'),
                        indicator: 'green',
                        message: __('Access token updated')
                    });
                    frm.reload_doc();
                }
            },
            error: function(err) {
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __(err)
                });
            }
        });
    }
});
