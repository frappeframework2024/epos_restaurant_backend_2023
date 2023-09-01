// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", {
	refresh(frm) {
        frappe.realtime.on('test_socket', (data) => {
            console.log(data)
            alert(145)
        })
	},
});
