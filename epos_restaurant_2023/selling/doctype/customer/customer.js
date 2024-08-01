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
        if (!frm.doc.__islocal && frm.doc.total_point_earn > 1) {
            frm.dashboard.add_indicator(__("Total Point Earn: {0}", [frm.doc.total_point_earn]), "green");
        }
        getCustomerInfo(frm)
        getPOSMiscSaleInfo(frm)
        getGuestFolio(frm)
        
    }
    
});


function getCustomerInfo (frm) {
    $(frm.fields_dict["stay_history_detail"].wrapper).html("Loading customer stay history...");
    frm.refresh_field("stay_history_detail"); 

    frappe.db.get_list("Reservation Stay", {
        fields:[
            'name',
            'reservation',
            'reference_number',
            'reservation_type',
            'group_code',
            'reservation_date',
            'arrival_date',
            'departure_date',
            'room_nights',
            'rooms',
            'guest',
            'guest_name',
            'business_source',
            'adr',
            'total_amount',
            'reservation_status',
            'rooms_data'
        ],
        filters:[['guest','=',frm.doc.name]]
    }).then(result=>{
        result.forEach((r) => {
            r.rooms_data = JSON.parse(r.rooms_data) 
        })

        let html = frappe.render_template("customer_stay_history", {data:result});
        $(frm.fields_dict["stay_history_detail"].wrapper).html(html);
        frm.refresh_field("stay_history_detail"); 
    })
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

// pagination
function pagination (frm, field_dict, wrapper, content) {
    const pageContent = $(frm.fields_dict[field_dict].wrapper)[0].querySelector(wrapper)
    const itemsPerPage = 20;
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


