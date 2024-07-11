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
    }
    
});
