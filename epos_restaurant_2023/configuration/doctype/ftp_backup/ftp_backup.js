// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("FTP Backup", {
    onload(frm){
        frappe.realtime.on("repair_database", (data) => {
            console.log("triggered")
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
               frappe.msgprint("Backup Added To Queue")
            }
        })
	},
    repair_database(frm) {
        frappe.call({
            method: 'epos_restaurant_2023.api.ftp_backup.execute_repair_table', 
            callback: function(r) { 
               frappe.msgprint(r.message)
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
