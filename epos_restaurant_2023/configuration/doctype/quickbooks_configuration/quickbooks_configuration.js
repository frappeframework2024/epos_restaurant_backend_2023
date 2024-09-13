// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("QuickBooks Configuration", {
	refresh(frm) { 

	},
    onload(frm){
        var currentUrl = window.location.href;
        var url = new URL(currentUrl);
        var params = new URLSearchParams(url.search);        
        if(params.size> 0){
            var code  = params.get('code')
            var state  = params.get('state')
            var realmId  = params.get('realmId')
            if(code != "" || code != undefined){
                // Remove specific query parameters
                params.delete('code'); 
                params.delete('state');
                params.delete('realmId'); 
                url.search = params.toString();
                window.history.replaceState({}, '', url.toString());
                frappe.call({
                    method:"epos_restaurant_2023.api.quickbook_intergration.config.exchange_authorization_code",  
                    type: 'POST',  
                    freeze: true,
                    args: {
                        params:{
                            "code":code,
                            "realm_id":realmId
                        }
                    },
                    callback:function(resp){
                        frappe.msgprint({
                            title: __('Qb Connected'),
                            indicator: 'green',
                            message: __("System was connected to QuickBooks Online")
                        });

                        frm.reload_doc();                      
                    },
                    error:function(err){
                        console.log({"Bug" : err})
                    }
                });
            }        
        }
        frm.fields_dict['qb_default_payment_type'].get_query = function(doc) {
            return {
                query: 'epos_restaurant_2023.api.quickbook_intergration.qb_payment_method.get_payment_type_autocomplete'
            }
        }
        frm.fields_dict['payment_method_mapping'].grid.get_field('qb_payment_type').get_query = function(doc, cdt, cdn) {           
            return {
                query: 'epos_restaurant_2023.api.quickbook_intergration.qb_payment_method.get_payment_type_autocomplete'
            };
        }; 
        
    },
    qb_default_payment_type(frm,cdt, cdn){ 
        if((frm.doc.qb_default_payment_type||"" )!="" ){
            frappe.call({
                method:"epos_restaurant_2023.api.quickbook_intergration.qb_payment_method.get_payment_type_by_name",
                freeze: true,
                args:{
                    "name":frm.doc.qb_default_payment_type
                },
                callback:function(resp){
                    frm.doc.qb_default_payment_type_id = resp.message.Id  ;
                    frm.refresh_field("qb_default_payment_type_id");
                },
                error:function(err){
                    frm.doc.qb_default_payment_type_id = undefined;
                    frm.refresh_field("qb_default_payment_type_id");
                    console.log({"Bug" : err})
                }
            }) ;
        }else{
            row.qb_payment_type_id = undefined;
            frm.refresh_field("payment_method_mapping");
        }
	},
    environment:function(frm){
        frm.doc.connected = 0;
        frm.doc.realm_id = undefined;
        frm.doc.qb_company_name = undefined;
        frm.doc.refresh_token = undefined;
        frm.doc.access_token = undefined;

        frm.refresh_field("connected");   
        frm.refresh_field("qb_company_name");   
        frm.refresh_field("realm_id");   
        frm.refresh_field("refresh_token");   
        frm.refresh_field("access_token");   
    },
    connect_to_quickbooks_button:function(frm){
        if (frm.doc.__unsaved == undefined){
            if( (frm.doc.client_id  || "") != "" && (frm.doc.client_secret||"")!="" && (frm.doc.redirect_url || "")!="" ){
                frappe.call({
                    method:"epos_restaurant_2023.api.quickbook_intergration.config.connect_quickbooks",  
                    freeze: true,
                    callback:function(resp){
                        if(resp){
                            window.location.href = resp.message
                        }
                    },
                    error:function(err){
                        //
                    }
                })
            }else{
                frappe.msgprint({
                    title: __('Warning'),
                    indicator: 'orange',
                    message: __("Field cannot be blank")
                });
            }
        }else{
            frappe.msgprint({
                title: __('Warning'),
                indicator: 'orange',
                message: __("Please save document first")
            });
        }
    },
    request_token_button:function(frm){
        if((frm.doc.refresh_token||"") !="" ){
            frappe.call({
                method: 'epos_restaurant_2023.api.quickbook_intergration.config.refresh_token',
                type: 'GET',  
                args: {
                    "refresh_token":frm.doc.refresh_token
                },
                freeze: true,
                callback: function(response) {
                    if(response){
                        frm.reload_doc();
                        if(response.message.status == 1){
                            frappe.msgprint({
                                title: __('Refresh Token'),
                                indicator: 'green',
                                message: __('Access token updated')
                            });
                        }else{
                            frappe.msgprint({
                                title: __('Warning'),
                                indicator: 'orange',
                                message: __(response.message.msg)
                            });
                        }
                        
                    }
                },
                error: function(err) {
                    frappe.msgprint({
                        title: __('Error'),
                        indicator: 'red',
                        message: __(err)
                    });
                }
            });
        }
    }
});

frappe.ui.form.on("QB Payment Method Mapping", {
    qb_payment_type(frm,cdt, cdn){ 
        const row = locals[cdt][cdn];
        if((row.qb_payment_type||"" )!="" ){
            frappe.call({
                method:"epos_restaurant_2023.api.quickbook_intergration.qb_payment_method.get_payment_type_by_name",
                freeze: true,
                args:{
                    "name":row.qb_payment_type
                },
                callback:function(resp){
                    row.qb_payment_type_id = resp.message.Id  ;
                    frm.refresh_field("payment_method_mapping");
                },
                error:function(err){
                    row.qb_payment_type_id = undefined;
                    frm.refresh_field("payment_method_mapping");
                    console.log({"Bug" : err})
                }
            }) ;
        }else{
            row.qb_payment_type_id = undefined;
            frm.refresh_field("payment_method_mapping");
        }
	},
})