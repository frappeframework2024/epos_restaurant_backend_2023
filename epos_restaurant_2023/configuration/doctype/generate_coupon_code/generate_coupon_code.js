// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Generate Coupon Code", {
	refresh(frm) {

	},

    generate: function (frm) {
        
		if (!frm.doc.start_number) {
			frappe.throw(__("Start number can not be blank"));
			return;
		}
		if (!frm.doc.end_number) {
			frappe.throw(__("End number can not be blank"));
			return;
		}

        if (frm.doc.end_number < frm.doc.start_number) {
			frappe.throw(__("End number must be greater than start number"));
			return;
		}

        if (!frm.doc.encrypt_key) {
			frappe.throw(__("Encrypt key can not be blank"));
			return;
		}
        if (!frm.doc.encrypt_iv) {
			frappe.throw(__("Encrypt iv can not be blank"));
			return;
		}

        
        frappe.call({
			method: 'epos_restaurant_2023.configuration.doctype.generate_coupon_code.generate_coupon_code.generate_button',
			args:{
                "param": { 
                    "start_number": frm.doc.start_number, 
                    "end_number": frm.doc.end_number, 
                    "prefix_url":frm.doc.prefix_url  ,
                    "key":frm.doc.encrypt_key,
                    "iv":frm.doc.encrypt_iv
                }
            },
            freeze: true,
			callback: (r) => {
                frm.clear_table("coupon_codes");
                frm.refresh_field("coupon_codes");
                for(var i of r.message){
                    console.log(i)
                    frm.add_child("coupon_codes", {
                        coupon_number: i.coupon_number,
                        coupon_number_encrypt: i.coupon_encrypt,
                        coupon_number_url: i.coupon_url 
                    });
                }
                
                frm.refresh_field("coupon_codes");  
			}
		});

    }
});
