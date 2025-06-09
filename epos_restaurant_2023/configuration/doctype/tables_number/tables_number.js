// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tables Number", {
	refresh(frm) {
        if(!frm.doc.__islocal){
            frm.add_custom_button('Generate QR', () => {                
                let d = new frappe.ui.Dialog({
                    title: 'Select Information for QR Code',
                    fields: [
                        {
                            label: 'Business Branch',
                            fieldname: 'business_branch',
                            fieldtype: 'Link',
                            options: 'Business Branch',
                            reqd: 1,
                            
                        },
                        {
                            label: 'POS Profile',
                            fieldname: 'pos_profile',
                            fieldtype: 'Link',
                            options: 'POS Profile',
                            reqd: 1,
                            get_query: () => {
                                return {
                                    filters: {
                                        is_edoor_profile: 0
                                    }
                                };
                            }
                        },
                        {
                            label: 'eMenu',
                            fieldname: 'emenu',
                            fieldtype: 'Link',
                            options: 'eMenu', // Replace with your actual Doctype name
                            reqd: 1
                        }
                    ],
                    primary_action_label: 'Generate',
                    primary_action(values) {
                        d.hide();

                        frappe.call({
                        method: 'epos_restaurant_2023.api.api.generate_table_qr_menu',
                        args: {
                            param: {
                                business_branch: values.business_branch,
                                pos_profile: values.pos_profile,                                
                                emenu: values.emenu,
                                table_id: frm.doc.name
                            }  // or any data you want in QR
                        },
                        callback(r) {
                            if (r.message && r.message.file_url) {
                                frm.set_value('qr_menu_file', r.message.file_url);
                                frm.save()
                                    .then(() => {
                                        frappe.msgprint('QR code generated and saved.');
                                    });
                            } else {
                                frappe.msgprint('QR code generation failed.');
                            }
                        }
                    });
                    }
                });

                d.show();

            });
        }
	},
});
