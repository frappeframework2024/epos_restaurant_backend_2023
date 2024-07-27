// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Journal Entry", {
	onload(frm) {
        if(frm.is_new()){
            frm.set_value('posting_date', frappe.datetime.get_today());
        }
       
	},
    refresh(frm){
        frm.set_df_property("party_type","options","Reference Doctype")
        frm.fields_dict['account_entries'].grid.update_docfield_property(
            'party_type', 'options', 'Reference Doctype'
        );
    },
    business_branch(frm){
        frm.set_query("account","account_entries", function() {
            return {
                filters: [
                    ["business_branch", "=", frm.doc.business_branch],
                    ["is_group", "=", 0]
                ]
            }
        });
        $.each(frm.doc.account_entries, function(idx, data) {
            data.account = ''
        });
        
        frm.refresh();
    }
});
