// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Check In Sale Coupon", {
	refresh(frm){
        if (frm.doc.__islocal) {
            // frm.dashboard.add_indicator(__("Remaining Visit: {0}", [0]), "green");                 
        }  
    },
    coupon_number:function(frm){  
        //    
    }
});
