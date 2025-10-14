// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("FTP Backup", {
    setup(frm){
        frappe.realtime.on("repair_database", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'green'
            });
		});
       
         frappe.realtime.on("backup_database", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'green'
            });
		});
    },
	run_backup(frm) {
        frappe.call({
            method: 'epos_restaurant_2023.api.ftp_backup.execute_backup_command', 
            callback: function(r) { 
               
            }
        })
	},
    repair_database(frm) {
        frappe.call({
            method: 'epos_restaurant_2023.api.ftp_backup.execute_repair_table', 
            callback: function(r) { 
                
            }
        })
	},
    check_database(frm) {
        frappe.call({
            method: 'epos_restaurant_2023.api.ftp_backup.check_table', 
            callback: function(r) { 
                frm.set_value('message', r.message);
            }
        })
	},
});
