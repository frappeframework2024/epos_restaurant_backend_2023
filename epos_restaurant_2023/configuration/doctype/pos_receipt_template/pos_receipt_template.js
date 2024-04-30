// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

// frappe.ui.form.on("", {
// 	refresh(frm) {

// 	},
// });

// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt
let dialog = null
frappe.ui.form.on("POS Receipt Template", {

    refresh(frm) {
         
        if (!frm.is_new()) {
            frm.add_custom_button(__('Preview'), function () {
    
                let dialog = new frappe.ui.Dialog({
                    title: 'Preview',
                    fields: [
                        {
                            label: 'Preview',
                            fieldname: 'preview',
                            fieldtype: 'HTML',
                            options: "hello"
                        },
    
    
                        // Add other fields as needed
                    ],
                    size: 'extra-large', // Choose from 'small', 'large', or 'extra-large'
    
                });
    
                dialog.show()
    
                setTimeout(function () {
                    frappe.call({ method: "epos_restaurant_2023.configuration.doctype.pos_receipt_template.pos_receipt_template.get_print_preview_data", args: { name: frm.doc.name } }).then(result => {
                        alert(222)
                        // const html = frappe.render_template("preview", { html: "<h1>Hello</h1",stype:"<style>h1 {background:red;}</style>"} )
                        const html = frappe.render_template("preview",{content: "<h1>Hello</h1>",style:"<style>h1 {background:red;}</style>"})
                        alert(html)
                        dialog.set_value("preview", html);
    
                    })
                }, 1000)
    
    
            });
    
        }


    },
     

});

 
   
 