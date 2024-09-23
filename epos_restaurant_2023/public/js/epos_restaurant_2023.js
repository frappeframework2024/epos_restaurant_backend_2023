
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
            const listSidebar = sidebar.querySelector('.desk-sidebar.list-unstyled.sidebar-menu')
            // const formSidebar = sidebar.querySelector('.list-unstyled.sidebar-menu')
            if (listSidebar) {
                const listParent = listSidebar.parentNode
                const listTopParent = listParent.parentNode
                if (listTopParent) {
                    listTopParent.remove()
                }
            }
            // if (formSidebar) {
            //     const formParent = formSidebar.parentNode
            //     const topParent = formParent.parentNode
            //     if (topParent) {
            //         $(topParent).css('display', 'none')
            //     }
            // }
        }
        
        if (!frappe.is_mobile()){ 
            const layoutsidebar = document.querySelectorAll(".layout-side-section")
            
            layoutsidebar.forEach(s=>{
                s.style.display="none";
            })
        }
       
    })


    //eDoor menu mobile
    const observerQueryReportRender = new MutationObserver((mutationsList) => {
			for (const mutation of mutationsList) {
				if (mutation.type === 'childList') {
				// Check if the element with ID 'page-query-report' is in the DOM
				const element = document.getElementById('page-query-report');
				if (element) {
					apply_mobile_report_view()
					// Optionally, disconnect the observer if you only want to detect it once
					observerQueryReportRender.disconnect();
					break;
				}
				}
			}
		});
		observerQueryReportRender.observe(document.body, { childList: true, subtree: true });

		function apply_mobile_report_view(){
			if (!frappe.is_mobile()){
				return
			}
			const filter = document.querySelector(".page-form")

			if (filter) {
				filter.classList.add("mobile_filter")
				addViewReportButton(filter)

			}
			// append filter button
			// Create and append the wrapper div with buttons
			document.querySelector("#page-query-report").insertAdjacentHTML('beforeend', `
				<div class="mobile_report_filter_wrapper">
				<button class="filter_report btn btn-primary">
					<svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M20.058 9.72255C21.0065 9.18858 21.4808 8.9216 21.7404 8.49142C22 8.06124 22 7.54232 22 6.50448V5.81466C22 4.48782 22 3.8244 21.5607 3.4122C21.1213 3 20.4142 3 19 3H5C3.58579 3 2.87868 3 2.43934 3.4122C2 3.8244 2 4.48782 2 5.81466V6.50448C2 7.54232 2 8.06124 2.2596 8.49142C2.5192 8.9216 2.99347 9.18858 3.94202 9.72255L6.85504 11.3624C7.49146 11.7206 7.80967 11.8998 8.03751 12.0976C8.51199 12.5095 8.80408 12.9935 8.93644 13.5872C9 13.8722 9 14.2058 9 14.8729L9 17.5424C9 18.452 9 18.9067 9.25192 19.2613C9.50385 19.6158 9.95128 19.7907 10.8462 20.1406C12.7248 20.875 13.6641 21.2422 14.3321 20.8244C15 20.4066 15 19.4519 15 17.5424V14.8729C15 14.2058 15 13.8722 15.0636 13.5872C15.1959 12.9935 15.488 12.5095 15.9625 12.0976" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
					Filter Report
				</button>
				<button class="btn_refresh_report btn btn-primary">
					<svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M15.9775 8.71452L15.5355 8.2621C13.5829 6.26318 10.4171 6.26318 8.46447 8.2621C6.51184 10.261 6.51184 13.5019 8.46447 15.5008C10.4171 17.4997 13.5829 17.4997 15.5355 15.5008C16.671 14.3384 17.1462 12.7559 16.9611 11.242M15.9775 8.71452H13.3258M15.9775 8.71452V6" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> <path d="M7 3.33782C8.47087 2.48697 10.1786 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 10.1786 2.48697 8.47087 3.33782 7" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
					Refresh Report
				</button>
				</div>
			`);
			// Add click event listeners for both buttons
			document.querySelector('.filter_report').addEventListener('click', () => {
				let mainSection = document.querySelector('.main-section')
				mainSection.classList.add('filter-report')
				filter.style.opacity =1;
				filter.classList.add("show")
				addViewReportButton(filter)
				document.querySelector("body").insertAdjacentHTML('beforeend', `<div class="mobile_filter_back_drop"></div>`);

				document.querySelector('.mobile_filter_back_drop').addEventListener('click', (event) => {
					document.querySelector('.mobile_filter_back_drop').remove()
					filter.classList.remove("show")
				});

			});

			document.querySelector('.btn_refresh_report').addEventListener('click', () => {
				frappe.query_report.refresh();
                if (document.querySelector('.mobile_filter_back_drop')) {
				    document.querySelector('.mobile_filter_back_drop').remove()
                }
			}); 
		}

		function addViewReportButton(filter){
			
			if (!document.querySelector(".btn_view_report")){
				filter.insertAdjacentHTML('beforeend', `
							<div class="prev-close">
								<button class="btn_view_report btn btn-primary">
									<svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M9 4.45962C9.91153 4.16968 10.9104 4 12 4C16.1819 4 19.028 6.49956 20.7251 8.70433C21.575 9.80853 22 10.3606 22 12C22 13.6394 21.575 14.1915 20.7251 15.2957C19.028 17.5004 16.1819 20 12 20C7.81811 20 4.97196 17.5004 3.27489 15.2957C2.42496 14.1915 2 13.6394 2 12C2 10.3606 2.42496 9.80853 3.27489 8.70433C3.75612 8.07914 4.32973 7.43025 5 6.82137" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"></path> <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="#ffffff" stroke-width="1.5"></path> </g></svg>
									Preview Report
								</button>
								<button class="btn_close_filter btn btn-primary">
									<svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M14.5 9.50002L9.5 14.5M9.49998 9.5L14.5 14.5" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"></path> <path d="M7 3.33782C8.47087 2.48697 10.1786 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 10.1786 2.48697 8.47087 3.33782 7" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
									Close
								</button>
							</div>
						`);

				document.querySelector('.btn_view_report').addEventListener('click', () => {
					let mainSection = document.querySelector('.main-section')
					mainSection.classList.remove('filter-report')
					frappe.query_report.refresh();
					filter.classList.remove("show")
					document.querySelector('.mobile_filter_back_drop').remove()

				});
				document.querySelector('.btn_close_filter').addEventListener('click', () => {
					let mainSection = document.querySelector('.main-section')
					mainSection.classList.remove('filter-report')
					filter.classList.remove("show")
					document.querySelector('.mobile_filter_back_drop').remove()
				});
			}
		
		} 

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
        const listSidebar = sidebar.querySelector('.desk-sidebar.list-unstyled.sidebar-menu')
        // const formSidebar = sidebar.querySelector('.list-unstyled.sidebar-menu')
        if (listSidebar) {
            const listParent = listSidebar.parentNode
            const listTopParent = listParent.parentNode
            if (listTopParent) {
                listTopParent.remove()
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

    if(frappe.session.user !="Administrator"){ 
        // hide set chart, create card, and add chart to dashboard
        hideCreateCardButton();
        // Monitor any changes on the page and hide the button again if it reappears
        const observer = new MutationObserver(() => {
            hideCreateCardButton();
        });

        // Start observing the body for changes
        observer.observe(document.body, { childList: true, subtree: true });
    }
    function hideCreateCardButton() {
				
				
        // Select the "Create Card" button based on class or other attributes
        let el = document.querySelector('button[data-label="Create%20Card"]');
        if (el) {
            el.style.display = 'none';
        }
        
        let buttons = document.querySelectorAll('button.btn.btn-default.btn-sm.ellipsis');
        buttons.forEach(function(button) {
            if (button.innerText.trim() === "Set Chart" || button.innerText.trim() =="Add Chart to Dashboard" ) {
                button.style.display = 'none';
            }
        });

    }

    // get default letter and store in window object
    frappe.db.get_doc("Letter Head", "Default Letterhead").then(doc=>{
        window.default_letter_head = {header:doc.content, footer:doc.footer}
     })
     
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
 
