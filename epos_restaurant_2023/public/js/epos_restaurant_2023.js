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
        if (frappe.session.user == 'Administrator'){
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

        setFullScreenButton()
        
    })

    setFullScreenButton()
    
    
})

function setFullScreenButton () {
    if ((frappe.get_route()) == 'Workspaces,Member Check In'){
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
 
 
