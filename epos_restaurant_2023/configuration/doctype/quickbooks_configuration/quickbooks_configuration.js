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
