frappe.listview_settings['*'] = {
    onload: function(listview) {
   
        listview.page.add_inner_button('Custom Button', () => {
            frappe.msgprint('This is a custom button for all list views.');
        });
    }
};

window.addEventListener('load', function () {

    removeButtomCustom()

    setFullScreenButton()

    removeGanttKanban()

    removeAddButton()
    const navBar = document.querySelector('body')
    navBar.classList.add('full-width');


    frappe.router.on('change', () => {
        removeButtomCustom()

        removeGanttKanban()

        setFullScreenButton()

        removeAddButton()

        const navBar = document.querySelector('body')
        navBar.classList.add('full-width');


        const sidebar = document.querySelector(".layout-side-section")
        if (sidebar){
            const listSidebar = sidebar.querySelector('.list-sidebar.overlay-sidebar')
            const formSidebar = sidebar.querySelector('.form-sidebar.overlay-sidebar')
            if (listSidebar) {
                const listParent = listSidebar.parentNode
                if (listParent) {
                    listParent.remove()
                }
            }
            if (formSidebar) {
                console.log('form Sidebar')
                const formParent = formSidebar.parentNode
                if (formParent) {
                    $(formParent).css('display', 'none')
                }
            }
        }
        
        if (!frappe.is_mobile()){ 
            const layoutsidebar = document.querySelectorAll(".layout-side-section")
            
            layoutsidebar.forEach(s=>{
                s.style.display="none";
            })
        }
       
    })

})

function setFullScreenButton () {
    if ((frappe.get_route()) == 'Workspaces,Check In'){
        if (!document.querySelector('#btn-full-screen')){
            let btn = this.document.createElement('button')
            btn.setAttribute('id', 'btn-full-screen')

            btn.innerText = 'Full Screen'
            btn.addEventListener('click', function(){
                const el = document.querySelector('[custom_block_name="Member Check In"]').querySelector(".widget-body").children[0].shadowRoot.querySelector("iframe")
                
                el.requestFullscreen()
                el.contentWindow.postMessage("Open Fullscreen", "*");

            })

            btn.style.padding = "4px 10px"
            btn.style.borderRadius = "6px"
            btn.style.height = "30px"
            btn.style.marginLeft = "8px"
            btn.style.background = "#fff" 
            btn.style.border = "1px solid #e3e3e3"
            btn.style.color = "#1F272E"
            btn.style.fontSize = "13px"
            
            
            this.document.querySelector('.page-actions').appendChild(btn)
        }
    }else {
        if(document.querySelector('#btn-full-screen')){
            document.querySelector('#btn-full-screen').remove()
        }
        
    }
}
 
function removeButtomCustom (){
    if (frappe.session.user != 'Administrator'){
        const getParent = document.querySelector('#page-Workspaces')
        if(getParent){ 
            const customActions = getParent.querySelector('.custom-actions')
            const standardActions = getParent.querySelector('.standard-actions')
            if (customActions){
                customActions.remove()
            }
            if (standardActions){ 
                standardActions.remove()
            }
        }
    }
}

function removeAddButton () {
    if (frappe.session.user != 'Administrator'){ 
        this.setTimeout(function(){
            const getParent = document.querySelector('.page-head')
            if (getParent) {
                btnAddRes = getParent.querySelector('[data-label="Add Reservation"]')
                btnNewRes = getParent.querySelector('[data-label="New%20Reservation%20Stay"]')
                btnNewResStay = getParent.querySelector('[data-label="Add Reservation Stay"]')
                if (btnAddRes) {
                    btnAddRes.remove()
                }
                if (btnNewRes) {
                    const parentEl = btnNewRes.parentElement
                    const grantParentEl = parentEl.parentElement
                    grantParentEl.remove()
                }
                if (btnNewResStay) {
                    btnNewResStay.remove()
                }
            }
        },1000)
    }
}

function removeGanttKanban () {
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
}


document.addEventListener('DOMContentLoaded', function () {
    var myTab = document.getElementById('myTab');
    if(myTab != null){
        var lastChild = myTab.lastElementChild;
    }
    if (lastChild != undefined){
        var lastChildLink = lastChild.querySelector('a');
        lastChildLink.click();
    } 
});


// check if my app is running in iframe then hide app bar and workspance menu nav bar
$(document).ready(function(){

    if (window.self !== window.top) {
        ClearUI()
    }

    // sidebar menu

    const sidebar = document.querySelector(".layout-side-section")

    if (sidebar){
        const listSidebar = sidebar.querySelector('.list-sidebar.overlay-sidebar')
        const formSidebar = sidebar.querySelector('.form-sidebar.overlay-sidebar')
        if (listSidebar) {
            const listParent = listSidebar.parentNode
            if (listParent) {
                listParent.remove()
            }
        }
        if (formSidebar) {
            const formParent = formSidebar.parentNode
            if (formParent) {
                $(formParent).css('display', 'none')
            }
        }
    }


    let isMobile = window.matchMedia('(max-width: 768px)').matches;

    let submenus= []
    var bodyElement = document.querySelector(".main-section");
    
    if (!document.querySelector("#main-menu")){
        RenderNavMenu()
    }
    
    function RenderNavMenu(){
        if (window.self === window.top) {
            let parser = new DOMParser()
            if (!isMobile){
                frappe.call("epos_restaurant_2023.api.app_menu.get_sidebar_menu_template").then(result=>{
                    let dom = parser.parseFromString(result.message, "text/html").querySelector("div.render-element")
                    submenus = dom.querySelectorAll(".submenu-content")
                    bodyElement.appendChild(dom)
                    bodyElement.style.transition = '0.4s'

                    //get active menu-name 
                    var selectedWorkspaceName =  document.body.getAttribute('data-route').split("/");
                    
                    if(selectedWorkspaceName.length>=2){

                        const selectedWorkspace = document.querySelector('.sidebar a[data-workspace=' + selectedWorkspaceName[1] + ']');

                        if (selectedWorkspace){
                            
                            selectedWorkspace.parentNode.classList.add("active")
                            
                            showMenu(selectedWorkspace.parentNode.getAttribute('data-submenu'),$(selectedWorkspace.parentNode).hasClass("submenu"))
                        }
                        
                    }
                })
            }else {
                frappe.call("epos_restaurant_2023.api.app_menu.get_sidebar_menu_template").then(result=>{ 
                    let dom = parser.parseFromString(result.message, "text/html").querySelector("div#mobile-side-menu")
                    bodyElement.appendChild(dom)

                    $(document).on("click", ".menu-btn", function (event){
                        $(this).toggleClass('open');
                        $('.sidebar-a').toggleClass('open');
                    }) 
                    
                    $(document).on('click', '.sidebar-a ul li:not(.submenu)', function (e) {
                        removeClOpen()
                    })
                    
                    $(document).on('click', '.sidebar-a ul li a:not(.sub_menu_link)', function (e) {
                        removeLiMobileActive('.sub_menu_mobile') 
                        removeAMenuActive('.sub_menu_mobile.active')
                        openLink(this)  
                        const parents = $(this).parent() 
                        activeParent(parents)
                        $(this).addClass('active')
                    });

                    $(document).on('click', '.sidebar-a ul li .arrow-drop-down', function (e) { 
                        removeLiMobileActive('.arrow-drop-down') 
                        removeAMenuActive('.sub_menu_mobile.active')
                        // e.stopPropagation();  
                        const subParents = $(this).parent() 
                        const parents = $(subParents).parent()
                        const child = $(parents).find('.sub_menu_p') 
                        const grandChild = $(child).find('a') 
                        $(grandChild).addClass('active');  
                        activeParent(subParents)
                    });

                    const allGrandSubMenu = document.body.querySelectorAll('.sub_menu_link')

                    allGrandSubMenu.forEach(a => {
                        a.addEventListener('click', function (){
                            const childEl = $(this)
                            const topParentEl = $(childEl).closest('.submenu')
                            $(topParentEl).addClass('active')
                            removeClOpen()
                        })
                    })


                    $(document).on('click', function (event) {
                        if (!$(event.target).closest('.menu-btn, .sidebar-a').length) {
                            removeClOpen()
                        }
                    });
                })
            }
        }
    }
    function removeClOpen () {
        $('.menu-btn').removeClass('open')
        $('.sidebar-a').removeClass('open');
    }

    function removeAMenuActive (aactive) {
        var allSubMenu = document.body.querySelectorAll(aactive)

        allSubMenu.forEach(sub => { 
            $(sub).removeClass('active')
        })

    }

    function activeParent (parents) {
        const grandParents = $(parents).parent() 
        const greatGrand = $(grandParents).parent() 
        $(greatGrand).addClass('active');
    }

    function removeLiMobileActive (liactive) {
        var allSubMenu = document.body.querySelectorAll(liactive)
        allSubMenu.forEach(sub => { 
            const subParent = $(sub).parent()
            const parents = $(subParent).parent()
            const grandParent = $(parents).parent()
            $(grandParent).removeClass('active')
        })
    }
        
    $(document).on("click",".sidebar a",function(event){
        openLink(this)
    })

    $(document).on("click","#hide_sub_menu",function(event){
        document.querySelector("#submenu-panel").style.left = "-250px"
        document.querySelector(".main-section").style.marginLeft="0px";

    })

    // ======
    $(document).on("click",".menu-section-header",function() {
        $(this).toggleClass('active');
    });


    // $(document).on("mouseover", ".sidebar .submenu",function() {
    $(document).on("click", ".sidebar li",function() {
        const has_submenu = $(this).hasClass("submenu")
        var submenuId = $(this).attr('data-submenu');
        if($(this).hasClass("active")){
            if (has_submenu) {
                document.querySelector("#submenu-panel").style.left=document.querySelector("#submenu-panel").style.left=="56px"?"-250px":"56px";
                document.querySelector(".main-section").style.marginLeft=document.querySelector("#submenu-panel").style.left=="56px"?"248px":"0px";
            }
        }else{
            showMenu(submenuId,has_submenu)
        }
        
        $(this).addClass("active")
        
    });

    $(document).on("click", ".sub_menu_link",function() {
        var selectedWorkspaceName =  document.body.getAttribute('data-route').split("/");

        var allSubMenu = document.body.querySelectorAll('.sub_menu_link')
        
        allSubMenu.forEach(sub => {

            const subParent = $(sub).parent()

            $(sub).removeClass('active')

            $(subParent).parent().removeClass('active')

        })
        
        if(selectedWorkspaceName.length>=2){ 

            const selectedSubWorkspace = $(this).attr('data-name')

            const seletedGrandSub = $(this).attr('data-link-to')

            if (selectedSubWorkspace || seletedGrandSub) {

                $(this).addClass('active')

                const subParent = $(this).parent()

                $(subParent).parent().addClass('active')
            
            } else {
                
                $(this).removeClass('active')

            }

        }  

        openLink(this); 
    });

        
    $(document).on("input", ".search-input",function(e) {
            
        const sub_menu = $('div.submenu-content[style*="display: block;"]')
        if (sub_menu){
            let elements = sub_menu.find('a');
            // Loop through the selected elements
            elements.each(function(index, element) {
                const parentEl = $(element).closest('.sub-hover')
                const parentGrEl = $(element).closest('.sub__menu')
                if(e.target.value.length>=3){ 
                    if ($(element).text().toLowerCase().includes( e.target.value.toLowerCase())) {
                        $(parentEl).attr('style', 'display: flex !important;');
                        $(parentGrEl).attr('style', 'display: flex !important;');
                    }else {
                        $(parentEl).attr('style', 'display: none !important;');
                        $(parentGrEl).attr('style', 'display: none !important;');
                    }
                }else {
                    $(parentEl).attr('style', 'display: flex !important;');
                    $(parentGrEl).attr('style', 'display: flex !important;');
                }
            });
            
            //show hide report group
            let report_groups = sub_menu[0].querySelectorAll('.card')
            report_groups.forEach(g=>{
                if(g.querySelectorAll('.sub__menu[style*="display: flex !important;"]').length>0){
                    g.style.display = "block"
                    g.querySelector(".collapse").classList.add("show")
                }else {
                    g.style.display = "none"
                }
            })
            

            
        }
        
    });

    function showMenu(submenu_id,has_submenu){
        //clear active menu 
        const activeMenu = document.querySelector("li.active")
        if(activeMenu){
            activeMenu.classList.remove("active")
        }

        submenus.forEach(sub=>{	
            if(has_submenu){ 
                document.querySelector("#submenu-panel").style.left="56px";
                sub.style.display =  (sub.id === submenu_id ? 'block' : 'none');
                document.querySelector(".main-section").style.marginLeft="248px";
            }else {
                document.querySelector("#submenu-panel").style.left="-250px";
                document.querySelector(".main-section").style.marginLeft="0px";
                
            }
            
        })
    }

    function openLink(el){
        const route =  $(el).data("custom-route")
        if(route){
            frappe.set_route(route)
        }else if($(el).data("workspace")) {
            const url ="/app/" +  frappe.router.slug($(el).data("workspace"))
            frappe.set_route(url)
        }else if($(el).data("type")=="DocType" ){
            let view = $(el).data("doc-view")
            if (!view){
                view = "List"
            }

            if($(el).data("doc-view")=="New"){
                frappe.new_doc($(el).data("link-to") );
            }else {
                frappe.set_route(view,$(el).data("link-to") );
            }
            
        }else if($(el).data("type")=="Dashboard"){
            frappe.set_route("dashboard-view",$(el).data("link-to") );
        
        }else if($(el).data("type")=="Report"){
                
            frappe.set_route("query-report",$(el).data("link-to") );
        }else if($(el).data("type")=="Page"){
                
            const url ="/app/" +  $(el).data("link-to")
            frappe.set_route(url)
        }else {
            const url ="/app/" +  frappe.router.slug($(el).data("name"))
            frappe.set_route(url)
        }
    }

    $('.report-wrapper').on('click', function(event) {
        var x = event.clientX;
        var y = event.clientY;
        
        var element = document.elementFromPoint(x, y);
        if(element.classList.contains("link")){
            ViewDocDetailModal(element.dataset.doctype,element.dataset.name)
        }

    });


 })

function removeHeaderSticky(){
    var page_head = document.querySelector(".page-head")
    if (page_head){
        page_head.classList.remove('page-head');
        page_head.style.position = 'unset!important';
        page_head.classList.add("custom-page-head")
    }
    var form_tab = document.querySelector(".form-tabs-list")
    if (form_tab){
        form_tab.classList.remove('form-tabs-list');
        form_tab.classList.add("custom-tab")
         
    }
}
function ClearUI(){
    //reset width to 100%
    var main_container = document.querySelector(".container")
    if (main_container){
        main_container.style.width = "100%"
    }
    
    var body = document.querySelector(".page-body")
     
    if (body){
        body.style.width = "100%"
    }

    var header = document.querySelector("header.navbar")
    if(header){
        header.remove()
    }
    

    let side_bar = document.querySelector(".layout-side-section")
    if (side_bar){
        //find if sidebar is desk side bar
        var desk_sidebar = side_bar.querySelector(".desk-sidebar-item")
        if (desk_sidebar){
            side_bar.remove()
        }
        
    } 
    side_bar = document.querySelector(".desk-sidebar")
    if (side_bar){
        
            side_bar.parentNode.parentNode.remove()
 
        
    } 

    
}

// check if app is running in iframe

if (window.self !== window.top) {
    //disable right click
    document.addEventListener('contextmenu', function(event) {
        event.preventDefault();
    });

    var bodyElement = document.body;

    // Create a callback function to be executed when mutations are observed
    var callback = function(mutationsList) {
        for (var mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-ajax-state') {
                // Check the new value of the data-ajax-state attribute
                var newState = bodyElement.getAttribute('data-ajax-state');
                if (newState === 'complete') {
                      
                        

                    preventLink()
                    removeHeaderSticky()
                    ClearUI()
                    
                    // set workspace main layout height = 100%
                    main_layout = document.querySelector("[data-page-route=Workspaces] .layout-main")
                    
                    if(main_layout){
                        main_layout.style.height = "100%"
                    }
                   
                    
                    
                }
            }
        }
    };

    // Create a MutationObserver instance with the callback
    var observer = new MutationObserver(callback);

    // Start observing the <body> element for attribute changes
    observer.observe(bodyElement, { attributes: true });


    function preventLink() {
         
        // Select all anchor tags within the iframe
        const links = document.querySelectorAll('a');
        
        // Add click event listener to each link
        links.forEach(link => {
            link.addEventListener('click', function(event) {
 
                if (event.ctrlKey || event.metaKey) {
                    event.preventDefault();
                     
                }
            });
        });
    } 


}

function ViewDocDetailModal(doctype,docname){
    const url = "/app/" +  frappe.router.slug(doctype) + "/" + docname
    const dialogGoogleSearch = new frappe.ui.Dialog({
        title: 'View ' + doctype + " - " + docname,
        fields: [
            {
                fieldname: 'result',
                fieldtype: 'HTML',
                options: "<iframe src='" + url + "' style='height:80vh;width:100%;border:none'/>"
            },
        ],
        

    });
    dialogGoogleSearch.$wrapper.find('.modal-dialog').css("max-width", "90%");

    dialogGoogleSearch.show()
}
 



 