
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
    

    var side_bar = document.querySelector(".layout-side-section")
    if (side_bar){
        //find if sidebar is desk side bar
        var desk_sidebar = side_bar.querySelector(".desk-sidebar-item")
        if (desk_sidebar){
            side_bar.remove()
        }
        
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





 