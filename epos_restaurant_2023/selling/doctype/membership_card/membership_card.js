// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Membership Card", { 
    refresh(frm) {
       // frm.set_df_property('expired_date', 'read_only', frm.doc.__islocal ? 0 : 1)
	},

    membership_type:function(frm){        
        frm.doc.expired_date ="";
        frm.refresh_field("expired_date");
        if(frm.doc.membership_type !=""){
            frappe.db.get_value("Membership Type",frm.doc.membership_type,["duration","base_on_month"]).then((r)=>{
                const _date = new Date(frm.doc.issue_date);
                if(r.message.base_on_month == 1){  
                    const new_month = new Date(_date.setMonth(_date.getMonth() + r.message.duration)); 
                    frm.doc.expired_date =  new Date(new_month.setDate(new_month.getDate() -1)); 
    
                }else{
                    frm.doc.expired_date = new Date(_date.setDate(_date.getDate() + r.message.duration));   
                }           
                frm.refresh_field("expired_date");
                
            }) ;
        }       
      },
      issue_date:function(frm){        
        frm.doc.expired_date ="";
        frm.refresh_field("expired_date");
        if(frm.doc.membership_type !=""){
            frappe.db.get_value("Membership Type",frm.doc.membership_type,["duration","base_on_month"]).then((r)=>{
                const _date = new Date(frm.doc.issue_date);
                if(r.message.base_on_month == 1){  
                    const new_month = new Date(_date.setMonth(_date.getMonth() + r.message.duration)); 
                    frm.doc.expired_date =  new Date(new_month.setDate(new_month.getDate() -1)); 
    
                }else{
                    frm.doc.expired_date = new Date(_date.setDate(_date.getDate() + r.message.duration));   
                }           
                frm.refresh_field("expired_date");
                
            }) ;
        }     
      }
});
