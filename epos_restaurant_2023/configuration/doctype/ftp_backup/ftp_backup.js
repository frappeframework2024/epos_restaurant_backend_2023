// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("FTP Backup", {
    refresh(frm){
         frm.set_query("log","clear_logs", function() {
           return {
                filters: [
                    ["name", "in", "Error Log,Scheduled Job Log,Access Log,Console Log,Activity Log,Webhook Request Log"]
                ]
            }
        });
    },
    setup(frm){
        frappe.realtime.on("repair_database", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
		});
       
        frappe.realtime.on("backup_database", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
            });
		});

        frappe.realtime.on("check_database", (data) => {
            frappe.show_alert({
                message: data.message,
                indicator: 'blue'
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
