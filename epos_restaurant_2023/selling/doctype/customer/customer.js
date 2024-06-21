// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", { 

    refresh(frm){
        if (!frm.doc.__islocal && frm.doc.total_point_earn > 1) {
            frm.dashboard.add_indicator(__("Total Point Earn: {0}", [frm.doc.total_point_earn]), "green");
        }
    }
    
});
