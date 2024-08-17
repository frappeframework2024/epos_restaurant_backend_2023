// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Check In Sale Coupon", {
	refresh(frm){
        if (frm.doc.__islocal || frm.doc.docstatus == 0) {           
            frm.dashboard.add_indicator(__("Remaining Visit: {0}", [0]), "green","remaining-visit");  
            console.log(frm.dashboard.stats_area.wrapper.html())
            frm.dashboard.stats_area.wrapper.find('.col-sm-12.indicator-column').remove();            
            frm.dashboard.stats_area.wrapper.find('.section-head').remove();              
            frm.dashboard.stats_area.wrapper.find(".section-body.hide"). removeClass('hide')           
        }  
    },
    setup(frm){
        set_query(frm, "coupon_number",  [["Sale Coupon", "balance", ">", 0],["Sale Coupon", "docstatus", "=", 1]]);
    },
    coupon_number:function(frm){          
        frappe.db.get_doc("Sale Coupon",frm.doc.coupon_number).then((resp)=>{ 
            frm.dashboard.stats_area.wrapper.find('.col-sm-12.indicator-column').remove();
            frm.dashboard.add_indicator(__("Remaining Visit: {0}", [resp.balance]), "green");       
        });      
    }
});


function set_query(frm, field_name, filters) {
	frm.set_query(field_name, function () {
		return {
			filters: filters
		}
	});

}