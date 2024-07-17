// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("FTP Backup", {
	run_backup(frm) {
        frappe.call({
            method: 'epos_restaurant_2023.api.ftp_backup.execute_backup_command', 
            callback: function(r) { 
               frappe.msgprint("Backup Added To Queue")
            }
        })
	},
});
