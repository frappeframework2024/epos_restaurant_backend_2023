// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Journal Entry", {
	onload(frm) {
        if(frm.is_new()){
            frm.set_value('posting_date', frappe.datetime.get_today());
        }
	},
    business_branch(frm){
        frm.set_query("account","account_entries", function() {
            return {
                filters: [
                    ["business_branch", "=", frm.doc.business_branch]
                ]
            }
        });
        $.each(frm.doc.account_entries, function(idx, data) {
            data.account = ''
        });
        
        frm.refresh();
    }
});
