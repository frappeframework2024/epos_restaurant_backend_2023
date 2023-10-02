
 

// $(document).ready(function(){
//     // console.log(document.querySelector("#page-Workspaces"))
// let default_sidebar = document.querySelector('.layout-side-section');
// default_sidebar.remove()

// let my_menu = document.createElement("div")
// my_menu.classList.add("sidebar_menu")


// frappe.db.get_list('App Sidebar Menu', {
//     fields: ['name','parent_app_sidebar_menu', 'title','url','icon'],
//     limit:10000,
//     order_by:"sort_order"
    
// }).then(result => {
//     console.log(result)
    
//     let main_menu = document.createElement("ul")
//     main_menu.classList.add("main_menu")
//     result.filter(r=>r.parent_app_sidebar_menu=='root_menu').forEach(m=>{
//         let li = document.createElement("li")
//         li.textContent = m.title
        
//         //get child menu
//         if(result.filter(r=>r.parent_app_sidebar_menu==m.name).length>0){
//             let sub_menu = document.createElement("ul")
//             sub_menu.classList.add("sub_menu")
//             result.filter(r=>r.parent_app_sidebar_menu==m.name).forEach(s=>{
//                    let sub_li = document.createElement("li")
//                     sub_li.textContent = s.title
//                     sub_menu.appendChild(sub_li)
                    
//             })
//             li.appendChild(sub_menu)
            
//         }
        
    
//         main_menu.appendChild(li)
        
                
//     })
//     my_menu.appendChild(main_menu)    
//     console.log(main_menu)
//     document.querySelector("body").prepend(my_menu)
    

    
// })




// })

window.addEventListener('load', function () {
 
    if (frappe.session.user != 'Administrator'){
        const getParent = document.querySelector('#page-Workspaces')
        if(getParent){ 
            const childElement = getParent.querySelector('.flex.col.page-actions.justify-content-end')
            childElement.style.display = 'none'
        }
    }

    const navBar = document.querySelector('body')
    navBar.classList.add('full-width');


    frappe.router.on('change', () => {
        if (frappe.session.user != 'Administrator'){
            const getParent = document.querySelector('#page-Workspaces')
            if(getParent){ 
                const childElement = getParent.querySelector('.flex.col.page-actions.justify-content-end')
                childElement.style.display = 'none'
            }
        }

        this.setTimeout(function(){
       
            let kanban = document.querySelector('[data-view="Kanban"]')
            let gantt = document.querySelector('[data-view="Gantt"]')
            if (kanban){
                kanban.remove()
            }
            if (gantt){
                gantt.remove()
            }
        },2000)
    })
})
 
 
