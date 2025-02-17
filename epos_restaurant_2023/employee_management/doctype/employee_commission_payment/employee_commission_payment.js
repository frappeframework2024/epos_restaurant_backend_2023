// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Commission Payment", {
	refresh(frm) {
		frm.set_query('sale', 'employee_commission_sale', function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return {
				filters: [
					["Sale","docstatus", "=", "1"],
					["Sale","sale_commission_balance", ">", "0"]
				]
			};
		});
	},
	setup: function(frm) {
		renderSummary(frm)
	},
	get_sales(frm){
		frm.call({
            method: 'get_sale_commission',
            doc:frm.doc,
            callback:function(r){
                if(r.message){
                    frm.set_value('employee_commission_sale',r.message);
					renderSummary(frm)
                }
				else{
					frm.set_value('employee_commission_sale',[]);
				}
            },
            async: true,
        }).then((result)=>{
			if(!result.message){
				frappe.msgprint("No Sales Found")
			}
		})
	},
}),
frappe.ui.form.on('Employee Commission Sale', {
	paid_amount(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		row.balance = row.commission_amount - row.paid_amount
		frm.refresh_field('employee_commission_sale')
		renderSummary(frm)
	  },
});

function renderSummary(frm){
	if(frm.doc.employee_commission_sale != undefined){
		let summary={}
		summary.total_commission = frm.doc.employee_commission_sale.reduce((a, b) => a + b.commission_amount, 0)
		summary.total_paid = frm.doc.employee_commission_sale.reduce((a, b) => a + b.paid_amount, 0)
		summary.total_balance = frm.doc.employee_commission_sale.reduce((a, b) => a + b.balance, 0)
		
		const html = frappe.render_template("total_commission", {doc:frm.doc,summary:summary})

		$(frm.fields_dict['total'].wrapper).html(html);
		frm.refresh_field('total');
	}
}
