// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Working Day", {
    onload: function(frm) {
       
    },
	refresh(frm) {
        
        frm.remove_custom_button('Print')
	},
    posting_date(frm){
        
    }
});
