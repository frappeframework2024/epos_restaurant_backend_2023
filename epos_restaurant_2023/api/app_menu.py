import frappe
from epos_restaurant_2023.api.api import get_workspace_sidebar_items
from functools import lru_cache

@frappe.whitelist()
def clear_cache():
    get_sidebar_menu_template_cached.cache_clear()
    
@frappe.whitelist()
def get_sidebar_menu_template():
    
    return get_sidebar_menu_template_cached(frappe.session.user, frappe.local.site)

@lru_cache(maxsize=128)
def get_sidebar_menu_template_cached(user,site= frappe.local.site):
    data = get_workspace_sidebar_items()
    menus = [d for d in data["pages"] if  not d["parent_page"] and d["is_hidden"]==0]
    # return [d["name"] for d in data["pages"]]
    
    
    shortcut_menus = frappe.db.sql("select parent,  type,link_to,label, doc_view from `tabWorkspace Shortcut` where parent in %(parent_menu)s and custom_show_in_app_menu = 1 order by idx",{"parent_menu":[d["name"] for d in  data["pages"]]}, as_dict=1)
    shortcut_menus =  get_list_with_permission(shortcut_menus) 
    workspace_links = frappe.db.sql("select name,idx, parent,link_to,link_type,label,link_count,type from `tabWorkspace Link` where parent in %(parents)s and custom_show_in_app_menu = 1   order by custom_sort_order, idx ",{"parents":[d["name"] for d in  data["pages"]]},as_dict=1)
    workspace_links =  get_list_with_permission(workspace_links)
    for d in menus:
        d["sub_menus"] = {"shortcut_menu":[],"workspace_links":[]}
        
        d["id"] = str(d["name"]).lower().replace(" ","_")
        
        # sub menu from sub workspace
        if len([x for x in data["pages"] if x['parent_page'] == d["name"] and x["is_hidden"]==0] ):
            d["sub_menus"]["shortcut_menu"] =  [x for x in data["pages"] if x['parent_page'] == d["name"] and x["is_hidden"]==0]
    
        # get sub from shourt cut
        sub_menu = [s for s in shortcut_menus if s["parent"]==d["name"]]
        if sub_menu:
            if "sub_menus" in d:
                d["sub_menus"]["shortcut_menu"] = d["sub_menus"]["shortcut_menu"]  + [{"name":x["label"],"link_to":x["link_to"],'type':x["type"],"doc_view":x["doc_view"] } for x in  sub_menu ]
                
        # workspace link
        if d["name"] in [x["parent"] for x  in workspace_links]:
            sub_workspace_links = [x for x in workspace_links if x["parent"]==d["name"] and x["type"]=="Card Break" and x["link_count"]>0]
            if sub_workspace_links:
                sub_workspace_links[0]["show"] = True
            

            for c in sub_workspace_links:
                c["links"] = [x for x in workspace_links if x["parent"]==d["name"] and x["idx"] in range(c["idx"] + 1, c["idx"] + c["link_count"] + 1)]
                
                d["sub_menus"]["workspace_links"].append( c)
        # end get workspace link
   
    for d in menus:
        if not d["sub_menus"]["shortcut_menu"] and not d["sub_menus"]["workspace_links"]:
            del d["sub_menus"]
 
    # return data
    template = """
    <div class="render-element">
        <div class="sidebar">
            <div class="sidebar-inner">
                <div>
                    <div class="logo-sidebar">
                        <a href="/app">
                            <img class="app-logo" src="{{app_logo}}" />
                        </a>
                    </div>
                    <div>
                        <ul class="menu">
                            {%for d in data%}
                                <li class="{{'' if not 'sub_menus' in d else 'submenu'}}" data-submenu="{{d.id}}">
                                    <a class="menus tooltips" data-workspace="{{d.name}}" data-custom-route="{{d.custom_route or ""}}">
                                        <span class="icon">
                                            {%if d.custom_menu_icon%}
                                                {{d.custom_menu_icon}}
                                            {%else%}
                                            <svg class="icon  icon-md" style="">
                                                <use class="" href="#icon-{{d.icon}}"></use>
                                            </svg>
                                            {%endif%}
                                        </span>
                                        <span class="tooltiptext">{{_(d.name)}}</span>
                                    </a>
                                </li>
                            {%endfor%}
                        </ul>
                    </div>
                </div>
                
                <div class="user-profile">
                    <div style="cursor:pointer" class="tooltips">
                        <svg onclick="return frappe.app.logout()" width="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M15 12L6 12M6 12L8 14M6 12L8 10" stroke="#ff0000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> <path d="M12 21.9827C10.4465 21.9359 9.51995 21.7626 8.87865 21.1213C8.11027 20.3529 8.01382 19.175 8.00171 17M16 21.9983C18.175 21.9862 19.3529 21.8897 20.1213 21.1213C21 20.2426 21 18.8284 21 16V14V10V8C21 5.17157 21 3.75736 20.1213 2.87868C19.2426 2 17.8284 2 15 2H14C11.1715 2 9.75733 2 8.87865 2.87868C8.11027 3.64706 8.01382 4.82497 8.00171 7" stroke="#ff0000" stroke-width="1.5" stroke-linecap="round"></path> <path d="M3 9.5V14.5C3 16.857 3 18.0355 3.73223 18.7678C4.46447 19.5 5.64298 19.5 8 19.5M3.73223 5.23223C4.46447 4.5 5.64298 4.5 8 4.5" stroke="#ff0000" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
                        <span class="tooltiptext">Log Out</span>
                    </div> 
                </div>
            </div>
        </div>

        <div class="submenu-panel" id="submenu-panel">
            <div class="d-flex justify-between align-center" style="gap:10px">
                <div>
                    <input type="text" class="search-input" placeholder="{{_("Search...")}}">
                </div>
                <div>
                    <div id="hide_sub_menu">
                        <svg width="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M15 19L9 12L10.5 10.25M15 5L13 7.33333" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>
                    </div>
                </div>
            </div>
            <br/>
            {%for d in data%}
                {%if 'sub_menus' in d%}
                <div class="submenu-content" id="{{d.id}}">
                    <div class="shortcut_menu">
                        {%for s in d.sub_menus.shortcut_menu%}
                            <div class="p-2 d-flex align-center sub-hover">
                                <div>
                                    <?xml version="1.0" encoding="utf-8"?>
                                    <!-- Generator: Adobe Illustrator 26.0.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
                                    <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                        width="18.8px" height="18.8px" viewBox="0 0 18.8 18.8" style="enable-background:new 0 0 18.8 18.8;" xml:space="preserve">
                                    <style type="text/css">
                                        .st0{fill:#EAECEE;}
                                        .st1{fill:#495057;}
                                    </style>
                                    <g>
                                        <path class="st0" d="M15.6,18.8H3.2c-1.7,0-3.2-1.4-3.2-3.2L0,3.2C0,1.4,1.4,0,3.2,0l12.4,0c1.7,0,3.2,1.4,3.2,3.2v12.4
                                            C18.8,17.4,17.4,18.8,15.6,18.8z"/>
                                        <circle class="st1" cx="9.4" cy="9.4" r="2.1"/>
                                    </g>
                                    </svg>
                                </div>
                                <div class="ml-2"><a class="sub_menu_link" data-name="{{s.name}}" data-doc-view="{{s.doc_view}}" data-link-to="{{s.link_to}}" data-type="{{s.type}}">{{_(s.name)}}</a></div>
                            </div>
                        {%endfor%}
                          <div class="accordion" id="accordionExample">
                            {% for g in d.sub_menus.workspace_links%}
                            <div class="card">
                                <div class="card-header" id="head_{{g.name}}">
                                <h2 class="mb-0">
                                    <button class="btn btn-link btn-block text-left p-0" type="button" data-toggle="collapse" data-target="#collapse{{g.name}}" aria-expanded="true" aria-controls="collapse{{g.name}}">
                                        <div class="d-flex align-center">
                                            <div><svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M18 10L13 10" stroke="#000000" stroke-width="1.5" stroke-linecap="round"></path> <path d="M10 3H16.5C16.9644 3 17.1966 3 17.3916 3.02567C18.7378 3.2029 19.7971 4.26222 19.9743 5.60842C20 5.80337 20 6.03558 20 6.5" stroke="#000000" stroke-width="1.5"></path> <path d="M22 11.7979C22 9.16554 22 7.84935 21.2305 6.99383C21.1598 6.91514 21.0849 6.84024 21.0062 6.76946C20.1506 6 18.8345 6 16.2021 6H15.8284C14.6747 6 14.0979 6 13.5604 5.84678C13.2651 5.7626 12.9804 5.64471 12.7121 5.49543C12.2237 5.22367 11.8158 4.81578 11 4L10.4497 3.44975C10.1763 3.17633 10.0396 3.03961 9.89594 2.92051C9.27652 2.40704 8.51665 2.09229 7.71557 2.01738C7.52976 2 7.33642 2 6.94975 2C6.06722 2 5.62595 2 5.25839 2.06935C3.64031 2.37464 2.37464 3.64031 2.06935 5.25839C2 5.62595 2 6.06722 2 6.94975M21.9913 16C21.9554 18.4796 21.7715 19.8853 20.8284 20.8284C19.6569 22 17.7712 22 14 22H10C6.22876 22 4.34315 22 3.17157 20.8284C2 19.6569 2 17.7712 2 14V11" stroke="#000000" stroke-width="1.5" stroke-linecap="round"></path> </g></svg></div>
                                            <div class="ml-2 dir-menu">{{_(g.label)}}</div>
                                        </div>
                                    </button>
                                </h2>
                                </div>

                                <div id="collapse{{g.name}}" class="collapse {{'show' if g.show else ''}}" aria-labelledby="head_{{g.name}}" data-parent="#accordionExample">
                                <div class="card-body">
                                    {%for l in g.links%}
                                        <div class="sub__menu d-flex align-center">
                                            <div style="margin-left:20px">
                                                <div>
                                                    <?xml version="1.0" encoding="utf-8"?>
                                                        <!-- Generator: Adobe Illustrator 26.0.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
                                                        <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                                            width="18.8px" height="18.8px" viewBox="0 0 18.8 18.8" style="enable-background:new 0 0 18.8 18.8;" xml:space="preserve">
                                                        <style type="text/css">
                                                            .st0{fill:#EAECEE;}
                                                            .st1{fill:#495057;}
                                                        </style>
                                                        <g>
                                                            <path class="st0" d="M15.6,18.8H3.2c-1.7,0-3.2-1.4-3.2-3.2L0,3.2C0,1.4,1.4,0,3.2,0l12.4,0c1.7,0,3.2,1.4,3.2,3.2v12.4
                                                                C18.8,17.4,17.4,18.8,15.6,18.8z"/>
                                                            <circle class="st1" cx="9.4" cy="9.4" r="2.1"/>
                                                        </g>
                                                        </svg>
                                                </div>
                                            </div>
                                            <div class="ml-2"><a class="sub_menu_link"  data-link-to="{{l.link_to}}" data-type="{{l.link_type}}">{{_(l.label)}}</a></div>
                                        </div>
                                    {%endfor%}
                                </div>
                                </div>
                            </div>
                           {%endfor%}
                        </div>
                    </div>
                </div>
                {%endif%}
            {%endfor%}
        </div>
    </div>


    <div id="mobile-side-menu">
        <div class="menu-btn">
            <div class="bar1"></div>
            <div class="bar2"></div>
            <div class="bar3"></div>
        </div>
        <div class="sidebar-a"> 
            <div class="inner-sidebar">
                <div class="p-2 mb-2" style="background:#204887">
                    <div class="us-pro-inner mb-1" id="popover-button">
                        <img style="height:inherit;object-fit:cover;" src="{{user.profile}}" />
                    </div>
                    <h3 class="text-white mb-0">{{user.name}}</h3>
                    <p class="text-white">{{user.email}}</p>
                </div>
                <ul>
                    {%for d in data%}
                        <li class="{{'' if not 'sub_menus' in d else 'submenu'}} limenu" data-submenu="{{d.id}}">
                            <div class="d-flex align-center w-100 justify-content-between inner-li-ac">
                                <div class="sub_menu_p" style="width:90%">
                                    <a class="menus sub_menu_mobile tooltips text-decoration-none" data-workspace="{{d.name}}" data-custom-route="{{d.custom_route or ""}}">
                                        <div class="d-flex align-center" style="gap:10px">
                                            <span class="icon">
                                                {%if d.custom_menu_icon%}
                                                    {{d.custom_menu_icon}}
                                                {%else%}
                                                <svg class="icon  icon-md" style="">
                                                    <use class="" href="#icon-{{d.icon}}"></use>
                                                </svg>
                                                {%endif%}
                                            </span>
                                            <span>{{d.name}}</span>
                                        </div>
                                    </a>
                                </div>
                                {% if 'sub_menus' in d %}
                                <div>
                                    <div class="arrow-drop-down">
                                        <div>
                                            <svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M19 9L12 15L10.25 13.5M5 9L7.33333 11" stroke="#000000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>
                                        </div>
                                    </div>
                                </div>
                                {% endif %}
                            </div>
                            <ul>
                                {%if 'sub_menus' in d%}
                                    <div class="submenu-content" id="{{d.id}}">
                                        <div class="shortcut_menu">
                                            {%for s in d.sub_menus.shortcut_menu%}
                                                <div class="d-flex align-center sub-hover my-1">
                                                    <div class="ml-4">
                                                        <?xml version="1.0" encoding="utf-8"?>
                                                        <!-- Generator: Adobe Illustrator 26.0.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
                                                        <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                                            width="18.8px" height="18.8px" viewBox="0 0 18.8 18.8" style="enable-background:new 0 0 18.8 18.8;" xml:space="preserve">
                                                        <style type="text/css">
                                                            .st0{fill:#EAECEE;}
                                                            .st1{fill:#495057;}
                                                        </style>
                                                        <g>
                                                            <path class="st0" d="M15.6,18.8H3.2c-1.7,0-3.2-1.4-3.2-3.2L0,3.2C0,1.4,1.4,0,3.2,0l12.4,0c1.7,0,3.2,1.4,3.2,3.2v12.4
                                                                C18.8,17.4,17.4,18.8,15.6,18.8z"/>
                                                            <circle class="st1" cx="9.4" cy="9.4" r="2.1"/>
                                                        </g>
                                                        </svg>
                                                    </div>
                                                    <div class="ml-2"><a class="sub_menu_link" data-name="{{s.name}}" data-doc-view="{{s.doc_view}}" data-link-to="{{s.link_to}}" data-type="{{s.type}}">{{s.name}}</a></div>
                                                </div>
                                            {%endfor%}
                                            <div class="accordion ml-3" id="accordionExample">
                                                {% for g in d.sub_menus.workspace_links%}
                                                <div class="card">
                                                    <div class="card-header" id="head_{{g.name}}">
                                                    <h2 class="mb-0">
                                                        <button class="btn btn-link btn-block text-left p-0" type="button" data-toggle="collapse" data-target="#collapse{{g.name}}" aria-expanded="true" aria-controls="collapse{{g.name}}">
                                                            <div class="d-flex align-center">
                                                                <div><svg width="20px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M18 10L13 10" stroke="#000000" stroke-width="1.5" stroke-linecap="round"></path> <path d="M10 3H16.5C16.9644 3 17.1966 3 17.3916 3.02567C18.7378 3.2029 19.7971 4.26222 19.9743 5.60842C20 5.80337 20 6.03558 20 6.5" stroke="#000000" stroke-width="1.5"></path> <path d="M22 11.7979C22 9.16554 22 7.84935 21.2305 6.99383C21.1598 6.91514 21.0849 6.84024 21.0062 6.76946C20.1506 6 18.8345 6 16.2021 6H15.8284C14.6747 6 14.0979 6 13.5604 5.84678C13.2651 5.7626 12.9804 5.64471 12.7121 5.49543C12.2237 5.22367 11.8158 4.81578 11 4L10.4497 3.44975C10.1763 3.17633 10.0396 3.03961 9.89594 2.92051C9.27652 2.40704 8.51665 2.09229 7.71557 2.01738C7.52976 2 7.33642 2 6.94975 2C6.06722 2 5.62595 2 5.25839 2.06935C3.64031 2.37464 2.37464 3.64031 2.06935 5.25839C2 5.62595 2 6.06722 2 6.94975M21.9913 16C21.9554 18.4796 21.7715 19.8853 20.8284 20.8284C19.6569 22 17.7712 22 14 22H10C6.22876 22 4.34315 22 3.17157 20.8284C2 19.6569 2 17.7712 2 14V11" stroke="#000000" stroke-width="1.5" stroke-linecap="round"></path> </g></svg></div>
                                                                <div class="ml-2 dir-menu">{{_(g.label)}}</div>
                                                            </div>
                                                        </button>
                                                    </h2>
                                                    </div>

                                                    <div id="collapse{{g.name}}" class="collapse {{'show' if g.show else ''}}" aria-labelledby="head_{{g.name}}" data-parent="#accordionExample">
                                                    <div class="card-body">
                                                        {%for l in g.links%}
                                                            <div class="sub__menu d-flex align-center my-1">
                                                                <div style="margin-left:20px">
                                                                    <div>
                                                                        <?xml version="1.0" encoding="utf-8"?>
                                                                            <!-- Generator: Adobe Illustrator 26.0.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
                                                                            <svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                                                                width="18.8px" height="18.8px" viewBox="0 0 18.8 18.8" style="enable-background:new 0 0 18.8 18.8;" xml:space="preserve">
                                                                            <style type="text/css">
                                                                                .st0{fill:#EAECEE;}
                                                                                .st1{fill:#495057;}
                                                                            </style>
                                                                            <g>
                                                                                <path class="st0" d="M15.6,18.8H3.2c-1.7,0-3.2-1.4-3.2-3.2L0,3.2C0,1.4,1.4,0,3.2,0l12.4,0c1.7,0,3.2,1.4,3.2,3.2v12.4
                                                                                    C18.8,17.4,17.4,18.8,15.6,18.8z"/>
                                                                                <circle class="st1" cx="9.4" cy="9.4" r="2.1"/>
                                                                            </g>
                                                                            </svg>
                                                                    </div>
                                                                </div>
                                                                <div class="ml-2"><a class="sub_menu_link"  data-link-to="{{l.link_to}}" data-type="{{l.link_type}}">{{_(l.label)}}</a></div>
                                                            </div>
                                                        {%endfor%}
                                                    </div>
                                                    </div>
                                                </div>
                                            {%endfor%}
                                            </div>
                                        </div>
                                    </div>
                                {%endif%}
                            </ul>
                        </li>
                    {%endfor%}
                </ul>
            </div>
        </div>
    </div>
    """
    user = {
        "username":frappe.get_cached_value("User",frappe.session.user,"full_name"),
        "profile" : frappe.get_cached_value("User",frappe.session.user,"user_image"),
        "name" : frappe.get_cached_value("User",frappe.session.user,"name"),
        "email" : frappe.get_cached_value("User",frappe.session.user,"email")
    }
    
    
    return frappe.render_template(template,{"data":menus,"app_logo":frappe.get_cached_value("Navbar Settings",None,"app_logo"),"user":user})



def get_list_with_permission(data):
    return_data = [d for d in data if d["type"] not in ["DocType","Report","Page"]]
    # doctype
    return_data = return_data + [d for d in data if d["type"]=="DocType" and frappe.has_permission(doctype=d["link_to"], ptype='read', user=frappe.session.user)]
    # report
    return_data = return_data + [d for d in data if d["type"]=="Report" and frappe.has_permission('Report', ptype='read', doc=d["link_to"], user=frappe.session.user)]
    # report
    return_data = return_data + [d for d in data if d["type"]=="Page" and frappe.has_permission('Page', ptype='read', doc=d["link_to"], user=frappe.session.user)]
    
    return return_data
    
    