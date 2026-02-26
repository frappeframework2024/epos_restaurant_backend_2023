frappe.listview_settings['Sale'] = {
    add_fields: ['balance', 'total_amount','total_paid','is_foc','customer_name','grand_total'],
    hide_name_column: true, // hide the last column which shows the `name`
    // set this to true to apply indicator function on draft documents too
    has_indicator_for_draft: false,

    get_indicator(doc) {
        if(doc.is_foc==1){
            return [__("FOC"), "blue"];
        }else {
            if(doc.balance==0){ 
                return [__("Paid"), "green"];
            }else if(doc.total_paid + (doc.total_cash_coupon_claim||0)>0 && doc.balance>0){
                return [__("Partially Paid"), "orange"];
            }else if(doc.total_paid + (doc.total_cash_coupon_claim||0)==0){
                return [__("Unpaid"), "red"];
            }
        }
    },
    refresh: function(listview) {
        // pls use client script to add this button
        // or other metod that can show and hide this button 

        
        // listview.page.add_inner_button("Sync Sales", function() {
        //     frappe.call('epos_restaurant_2023.api.utils.sync_sale_to_server').then(r => {
        //         frappe.show_alert(r.message)
        //     })
        // });
    },
}





if (frappe.is_mobile()){


    frappe.views.ListView = class ListView extends frappe.views.ListView {

        get_mobile_row(left = "", doc) { 
            if (this.doctype === "Sale") {
                return frappe.render_template("mobile_list_view_row_template",{left:left,doc:doc,modified:comment_when(doc.modified,true)})           
            }
        }
        get_list_row_html(doc) {
        
            return this.get_mobile_row(
                this.get_left_html(doc),
                doc
            );
        }

    }
 
    setTimeout(() =>{
        const filter_section = document.querySelector('.standard-filter-section')
        if (filter_section) {
            // filter_section.style.transform = 'translateY(86%) !important'
            filter_section.insertAdjacentHTML('beforeend', 
                `<div class="open_filter_btn">
                    <svg width="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M20.058 9.72255C21.0065 9.18858 21.4808 8.9216 21.7404 8.49142C22 8.06124 22 7.54232 22 6.50448V5.81466C22 4.48782 22 3.8244 21.5607 3.4122C21.1213 3 20.4142 3 19 3H5C3.58579 3 2.87868 3 2.43934 3.4122C2 3.8244 2 4.48782 2 5.81466V6.50448C2 7.54232 2 8.06124 2.2596 8.49142C2.5192 8.9216 2.99347 9.18858 3.94202 9.72255L6.85504 11.3624C7.49146 11.7206 7.80967 11.8998 8.03751 12.0976C8.51199 12.5095 8.80408 12.9935 8.93644 13.5872C9 13.8722 9 14.2058 9 14.8729L9 17.5424C9 18.452 9 18.9067 9.25192 19.2613C9.50385 19.6158 9.95128 19.7907 10.8462 20.1406C12.7248 20.875 13.6641 21.2422 14.3321 20.8244C15 20.4066 15 19.4519 15 17.5424V14.8729C15 14.2058 15 13.8722 15.0636 13.5872C15.1959 12.9935 15.488 12.5095 15.9625 12.0976" stroke="#000000" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
                </div>
                <div class="close_filter_btn">
                    <svg width="40px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M19 15L12 9L10.25 10.5M5 15L7.33333 13" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>
                </div>`
            );

            const show_filter = document.querySelector('.open_filter_btn')
            const close_filter = document.querySelector('.close_filter_btn')
            close_filter.style.display = 'none'
            show_filter.addEventListener('click', () => {
                filter_section.classList.add('show')
                show_filter.style.display = 'none'
                close_filter.style.display = 'block'
                document.querySelector("body").insertAdjacentHTML('beforeend', `<div class="mobile_filter_back_drop_aa"></div>`);

                document.querySelector('.mobile_filter_back_drop_aa').addEventListener('click', (e) => {
                    filter_section.classList.remove('show')
                    show_filter.style.display = 'block'
                    close_filter.style.display = 'none'
                    e.target.remove()
                })
            })

            close_filter.addEventListener('click', () => {
                filter_section.classList.remove('show')
                show_filter.style.display = 'block'
                close_filter.style.display = 'none'

                const drop_filter = document.querySelector('.mobile_filter_back_drop_aa')

                setTimeout(() => {
                    if (drop_filter) {
                        drop_filter.remove()
                    }
                },100)

                document.querySelector('.mobile_filter_back_drop_aa').addEventListener('click', (e) => {
                    filter_section.classList.remove('show')
                    show_filter.style.display = 'block'
                    close_filter.style.display = 'none'
                    e.target.remove()
                })
            }) 

            
        }else {
            filter_section.style.transform = 'translateY(100%)'
        }
        
    },3000)


    document.querySelector('style').textContent +=
        `@media (min-width: 768px) { 
            .list-row-container .details-row { display: none; }
        }
        .list-row-container .details-row {
            color: #666;
            padding: 0 0 0 40px !important;
        }
        @media (max-width: 767.98px) {
            .standard-filter-section {
                position: fixed;
                bottom: 0;
                background: #fff;
                left: 0;
                z-index: 10000; 
                padding: 50px 10px 20px 10px;
                transition: transform 0.3s ease-in-out;
                transform: translateY(87%);
                border: 1px solid #ededed;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                overflow:hidden
            }
            .standard-filter-section.show {
                transform: translateY(0);
                transition: transform 0.3s ease-in-out;
            }
            .open_filter_btn, .close_filter_btn {
                position: absolute;
                top: 0;
                width: 100%;
                text-align: center;
                left:0
            }
            .open_filter_btn {
                background:#fafafa;
                padding: 5px;
            }
            .close_filter_btn {
                background:#fafafa;
            }
            .open_filter_btn svg, .close_filter_btn svg {
                transition: transform 0.5s ease-in-out;
            }    
            .close_filter_btn svg {
                transition: transform 0.5s ease-in-out;
                transform: rotate(180deg);
            }
            .mobile_filter_back_drop_aa {
                transition: transform 0.5s ease-in-out;
                background: #00000061;
                height: 100%;
                width: 100%;
                top: 0;
                position: fixed;
                z-index: 9999;
            }
            .mobile_filter_back_drop_aa {
                transition: transform 0.5s ease-in-out;
            }
            .list-paging-area {
                margin-bottom: 35px;
            }
            .layout-main-section-wrapper {
                padding:1px
            }

        }
        `
}

