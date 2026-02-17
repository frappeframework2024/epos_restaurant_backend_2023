// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("POS Station", {
	refresh(frm) {

	},
    setup(frm) {
        set_query(frm, "pos_profile", [["POS Profile", "business_branch", "=", frm.doc.business_branch]]);
    },

    business_branch(frm){
        set_query(frm, "pos_profile", [["POS Profile", "business_branch", "=", frm.doc.business_branch]]);
        frm.doc.pos_profile = "";
        frm.refresh_field("pos_profile");
    },

    refresh_license: async (frm) =>{
       const license = await frappe.onRunDocMethodToast(frm,"on_refresh_license");
       frm.set_value("license", license, null, false); 
       frm.refresh_field("license");
    }
});



function set_query(frm, field_name, filters) {
	frm.set_query(field_name, function () {
		return {
			filters: filters
		}
	});

}
