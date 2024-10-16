// Copyright (c) 2022, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", { 
    onload(frm) {
        if (window.self !== window.top) { 
            setTimeout(() => {
                const tabParents = document.querySelector('#form-tabs')
                if (tabParents) {
                    const tabChild = tabParents.querySelectorAll('.nav-link')
                    const tabChildActive = tabParents.querySelector('.nav-link.active')
                    if (tabChildActive) {
                        tabChildActive.classList.add('active-tab')
                    }
                    if (tabChild.length > 0) {} {
                        tabChild.forEach(el => { 
                            el.addEventListener('click', () => {
                                tabChild.forEach(t => t.classList.remove('active-tab'));
                                el.classList.add('active-tab');
                            })
                        })
                    }
                }
            }, 100)
        }
    },

    refresh(frm){
        frm.set_query("district", function() {
            return {
                filters: [["province","=",frm.doc.province]]
            }
        });
        frm.set_query("commune", function() {
            return {
                filters: [["district","=",frm.doc.district]]
            }
        });
        frm.set_query("village", function() {
            return {
                filters: [["commune","=",frm.doc.commune]]
            }
        });
        frm.set_query("pos_print_format", function() {
            return {
                filters: [["doc_type","=",frm.doc.doctype]]
            }
        });
        if (!frm.doc.__islocal ) {
            if(frm.doc.balance > 0) {
                let balance =  format_currency(frm.doc.balance)
                frm.dashboard.add_indicator(__("Total Balance: {0}", [ balance]), "red");
            }

            if((frm.doc.total_sale_coupon_payment_balance||0) > 0 ){ 
                let sale_coupon_balance =  format_currency(frm.doc.total_sale_coupon_payment_balance)
                frm.dashboard.add_indicator(__("Sale Coupon Balance: {0}", [ sale_coupon_balance]), "yellow");
            }   

            if((frm.doc.total_crypto_amount||0) > 0 ){ 
                let total_crypto_amount =  format_currency(frm.doc.total_crypto_amount)
                frm.dashboard.add_indicator(__("Total Crypto Amount: {0}", [ total_crypto_amount]), "yellow");
            }   

            if((frm.doc.total_crypto_claim||0) > 0 ){ 
                let total_crypto_claim =  format_currency(frm.doc.total_crypto_claim)
                frm.dashboard.add_indicator(__("Total Crypto Claim: {0}", [ total_crypto_claim]), "orange");
            }   

            if((frm.doc.total_crypto_balance||0) > 0 ){ 
                let total_crypto_balance =  format_currency(frm.doc.total_crypto_balance)
                frm.dashboard.add_indicator(__("Total Crypto Balance: {0}", [ total_crypto_balance]), "green");
            }   
            if((frm.doc.total_crypto_balance_expired||0) > 0 ){ 
                let total_crypto_balance_expired =  format_currency(frm.doc.total_crypto_balance_expired)
                frm.dashboard.add_indicator(__("Total Crypto Balance Expired: {0}", [ total_crypto_balance_expired]), "red");
            }   

           
            if(frm.doc.total_point_earn > 0){
                frm.dashboard.add_indicator(__("Total Point Earn: {0} Point(s)", [Number(frm.doc.total_point_earn).toFixed(2)]), "green");
            }
        }
        try{
            getCustomerInfo(frm)
            getPOSMiscSaleInfo(frm)
            getGuestFolio(frm)
            getGuestNoteDetail(frm)
            getCustomerDocument(frm)
        }
        catch(err){

        }   


        frm.fields_dict['qb_customer_name'].get_query = function() {           
            return {
                query: 'epos_restaurant_2023.api.quickbook_intergration.qb_customer.get_customer_autocomplete',
                filters:{
                    "name": frm.doc.qb_customer_name
                }
            };
        }; 

    },

    onload(frm){
        frm.fields_dict['qb_customer_name'].get_query = function() {           
            return {
                query: 'epos_restaurant_2023.api.quickbook_intergration.qb_customer.get_customer_autocomplete',
            };
        }; 
    },
    qb_customer_name(frm,cdt, cdn){ 
        if((frm.doc.qb_customer_name||"" )!="" ){
            frappe.call({
                method:"epos_restaurant_2023.api.quickbook_intergration.qb_customer.get_customer_autocomplete",
                freeze: true,
                args:{
                    "name":frm.doc.qb_customer_name
                },
                callback:function(resp){
                    frm.doc.qb_customer_id = resp.message.Id  ;
                    frm.refresh_field("qb_customer_id");
                },
                error:function(err){
                    frm.doc.qb_customer_id = undefined;
                    frm.refresh_field("qb_customer_id");
                    console.log({"Bug" : err})
                }
            }) ;
        }else{
            row.qb_customer_id = undefined;
            frm.refresh_field("qb_customer_id");
        }
	},
  
});


function getCustomerInfo (frm) {
    $(frm.fields_dict["stay_history_detail"].wrapper).html("Loading customer stay history...");
    frm.refresh_field("stay_history_detail"); 

    frappe.call({
        method: "epos_restaurant_2023.selling.doctype.customer.customer.get_guest_stay_history",
        args: {
            customer_name: frm.doc.name,
        },
        callback: (result => { 
            result.message.forEach((r) => {
                r.rooms_data = JSON.parse(r.rooms_data) 
            })
    
            
            let html = frappe.render_template("customer_stay_history", {data:result.message,isInIframe:(window.self !== window.top)});
            $(frm.fields_dict["stay_history_detail"].wrapper).html(html);
            frm.refresh_field("stay_history_detail"); 
    
            pagination(frm, field_dict = 'stay_history_detail', wrapper = '#guest_stay_history', content = '.stay_history', items_per_page = 50)
            
        }),
        error: (error => {
            frappe.throw(error);
        })
    }); 
}

 
function getPOSMiscSaleInfo(frm) { 
    $(frm.fields_dict["pos_misc_sale"].wrapper).html("Loading customer POS Misc Sale...");
    frm.refresh_field("pos_misc_sale");

    frappe.call({
        method: "epos_restaurant_2023.selling.doctype.customer.customer.get_pos_misc_sale",
        args: {
            customer_name: frm.doc.name,
        },
        callback: (result => {
            let html = frappe.render_template("customer_pos_misc_sale", {data:result.message,dataLength:result.message.length}); 
            $(frm.fields_dict["pos_misc_sale"].wrapper).html(html);
            frm.refresh_field("pos_misc_sale");

            pagination(frm, field_dict = 'pos_misc_sale', wrapper = '#accordion', content = '.sale-card')
            
        }),
        error: (error => {
            frappe.throw(error);
        })
    });
}


function getGuestFolio (frm) {
    $(frm.fields_dict["guest_folio"].wrapper).html("Loading customer folio...");
    frm.refresh_field("guest_folio");

    frappe.call({
        method: "epos_restaurant_2023.selling.doctype.customer.customer.get_guest_folio_list",
        args: {
            customer_name: frm.doc.name,
        },
        callback: (result => {
            let html = frappe.render_template("guest_folio_list", {data:result.message,dataLength:result.message.length}); 
            $(frm.fields_dict["guest_folio"].wrapper).html(html);
            frm.refresh_field("guest_folio");

            pagination(frm, field_dict = 'guest_folio', wrapper = '#guest_folio_list', content = '.folio_list_data')
        }),
        error: (error => {
            frappe.throw(error);
        })
    })
}


function getGuestNoteDetail (frm) {
    $(frm.fields_dict["guest_note_detail"].wrapper).html("Loading customer folio...");
    frm.refresh_field("guest_note_detail");

    frappe.call({
        method: "epos_restaurant_2023.selling.doctype.customer.customer.get_guest_note_detail",
        args: {
            customer_name: frm.doc.name,
        },
        callback: (result => { 
            result.message.forEach((r)=> { 
                let date = new Date(r.modified);
                r.modified = prettyDate(date)
            })
 
            let html = frappe.render_template("guest_note_detail", {data:result.message}); 
            $(frm.fields_dict["guest_note_detail"].wrapper).html(html);
            frm.refresh_field("guest_note_detail");
        }),
        error: (error => {
            frappe.throw(error);
        })
    })
}

function getCustomerDocument (frm) {
    $(frm.fields_dict["customer_document"].wrapper).html("Loading customer document...");
    frm.refresh_field("customer_document");

    frappe.call({
        method: "epos_restaurant_2023.selling.doctype.customer.customer.get_customer_document",
        args: {
            customer_name: frm.doc.name,
        },
        callback: (result => {  

            result.message.forEach((r)=> { 
                let date = new Date(r.modified);
                r.modified = prettyDate(date)
            })


            let html = frappe.render_template("customer_document", {data:result.message}); 
            $(frm.fields_dict["customer_document"].wrapper).html(html);
            frm.refresh_field("customer_document");
        }),
        error: (error => {
            frappe.throw(error);
        })
    })

}


// pagination
function pagination (frm, field_dict, wrapper, content, items_per_page) {
    const pageContent = $(frm.fields_dict[field_dict].wrapper)[0].querySelector(wrapper)
    const itemsPerPage = items_per_page ? items_per_page : 20;
    let currentPage = 0;

    const items = Array.from(pageContent.querySelectorAll(content))

    function showPage(page) {
        const startIndex = page * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        items.forEach((item, index) => {
            item.classList.toggle('hidden', index < startIndex || index >= endIndex);
        }); 
        setTimeout(()=>{
            updateActiveButtonStates();
        }, 100)
    }

    function createPageButtons() {
        const totalPages = Math.ceil(items.length / itemsPerPage);
        const paginationContainer = document.createElement('div');
        const paginationWrapper = pageContent.querySelector('#pagination')

        const paginationDiv = paginationWrapper.appendChild(paginationContainer);
        paginationContainer.classList.add('pagination');

        for (let i = 0; i < totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i + 1;
            pageButton.addEventListener('click', () => {
                currentPage = i;
                showPage(currentPage);
                setTimeout(()=>{
                    updateActiveButtonStates();
                }, 100)
            })
            paginationDiv.appendChild(pageButton);
        } 
        
    }

    function updateActiveButtonStates() {
        const pageButtons = pageContent.querySelectorAll('.pagination button');
        pageButtons.forEach((button, index) => {
            if (index === currentPage) {
            button.classList.add('active');
            } else {
            button.classList.remove('active');
            }
        });
    } 


    showPage(currentPage)
    createPageButtons()
}

function prettyDate(date) {
    var diff = Math.floor((new Date() - date) / 1000);
    var dayDiff = Math.floor(diff / 86400);

    if (isNaN(dayDiff) || dayDiff < 0) {
        return '';
    }

    if (dayDiff === 0) {
        if (diff < 60) return 'Just now';
        if (diff < 120) return '1 minute ago';
        if (diff < 3600) return Math.floor(diff / 60) + ' minutes ago';
        if (diff < 7200) return '1 hour ago';
        if (diff < 86400) return Math.floor(diff / 3600) + ' hours ago';
    }

    if (dayDiff === 1) return 'Yesterday';
    if (dayDiff < 7) return dayDiff + ' days ago';
    if (dayDiff < 31) return Math.ceil(dayDiff / 7) + ' weeks ago';
    if (dayDiff < 365) return Math.ceil(dayDiff / 30) + ' months ago';
    return Math.ceil(dayDiff / 365) + ' years ago';
}