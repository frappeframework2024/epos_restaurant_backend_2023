// Copyright (c) 2025, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Request", {
	refresh(frm) {
		if(frm.doc.docstatus == 1 && frm.doc.workflow_state == "Convert as PO"){
			frm.add_custom_button(__('View Purchase Order'), function () {
				let po_name = frm.doc.purchase_order; // Assuming a field like 'purchase_order' stores the PO name
                if (po_name) {
                    frappe.set_route("Form", "Purchase Order", po_name);
                } else {
                    frappe.msgprint(__("No Purchase Order linked to this Purchase Request yet."));
                }
			});
		}

		function hexToRgba(hex, opacity) {
            let cleanHex = hex.replace('#', '');
            let r = parseInt(cleanHex.substr(0, 2), 16);
            let g = parseInt(cleanHex.substr(2, 2), 16);
            let b = parseInt(cleanHex.substr(4, 2), 16);
            return `rgba(${r}, ${g}, ${b}, ${opacity})`;
        }

		function update_indicator_color(state) {
			let color_map = {
                'Draft': '#6c757d',             
                'Request Approval': '#663399',  
                'Approved By Supervisor': '#4B0082', 
                'Approved By GM': '#7B68EE',     
                'Rejected': '#dc3545',           
                'Convert as PO': '#006400'      
            };

            let color = color_map[state] || '#808080'; 
            let indicator = frm.page.wrapper.find('.indicator-pill'); 
            if (indicator.length) {
				console.log(hexToRgba(color,0.5))
                indicator.css({ 
                    'color':color,
                });
				indicator[0].style.setProperty('background-color', hexToRgba(color,0.1), 'important');				
            } else {
                console.log('Indicator element not found');
            }
        }

		if (frm.doc.workflow_state) {
            update_indicator_color(frm.doc.workflow_state);
        }
	},

	// before_workflow_action: function(frm) { 		
	
    // },


	after_workflow_action: function(frm) { 
        if (frm.doc.workflow_state === 'Convert as PO') { // Adjust state name
            frm.reload_doc();
        }
    },	
	
	
	workflow_state: function(frm) {
		if (frm.doc.workflow_state) {
            update_indicator_color(frm.doc.workflow_state);
        }
    }
});


frappe.ui.form.on('Purchase Request Products', {
	
	quantity(frm, cdt, cdn) {
		const doc = locals[cdt][cdn];
		update_purchase_request_product_summary(frm, doc)
	},
	price(frm, cdt, cdn) {
		const doc = locals[cdt][cdn];
		update_purchase_request_product_summary(frm, doc)
	},
})


function update_purchase_request_product_summary(frm, doc) {
	doc.amount = (doc.price||0) * (doc.quantity<=0 ? 1 : doc.quantity);	
	frm.refresh_field('purchase_request_products');
    update_purchase_request_summary(frm);
	// updateSumTotal(frm);
}

function update_purchase_request_summary(frm){
    const products = frm.doc.purchase_request_products;
	if (products == undefined) {
		return false;
	}

    frm.set_value('total_quantity', products.reduce((n, d) => n + d.quantity, 0));
	frm.set_value('total_amount', products.reduce((n, d) => n + d.amount, 0)); 

    frm.refresh_field('total_quantity');
    frm.refresh_field('total_amount');
}