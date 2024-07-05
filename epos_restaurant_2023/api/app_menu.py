import frappe
from epos_restaurant_2023.api.api import get_workspace_sidebar_items

@frappe.whitelist()
def get_sidebar_menu_template():
    data = get_workspace_sidebar_items()
    menus = [d for d in data["pages"] if  not d["parent_page"] and d["is_hidden"]==0]
    # return [d["name"] for d in data["pages"]]
    shortcut_menus = frappe.db.sql("select parent,  type,link_to,label, doc_view from `tabWorkspace Shortcut` where parent in %(parent_menu)s",{"parent_menu":[d["name"] for d in  data["pages"]]}, as_dict=1)
    workspace_links = frappe.db.sql("select name,idx, parent,link_to,link_type,label,link_count,type from `tabWorkspace Link` where parent in %(parents)s  order by idx ",{"parents":[d["name"] for d in  data["pages"]]},as_dict=1)
    
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
                                    <a class="menus" data-workspace="{{d.name}}" data-custom-route="{{d.custom_route or ""}}">
                                        <span class="icon">
                                            {%if d.custom_menu_icon%}
                                                {{d.custom_menu_icon}}
                                            {%else%}
                                            <svg class="icon  icon-md" style="">
                                                <use class="" href="#icon-{{d.icon}}"></use>
                                            </svg>
                                            {%endif%}
                                        </span>
                                    </a>
                                </li>
                            {%endfor%}
                        </ul>
                    </div>
                </div>
                <div class="user-profile">
                    <div class="us-pro-inner">
                        <img src="{{app_logo}}" />
                    </div>
                </div>
            </div>
        </div>

        <div class="submenu-panel" id="submenu-panel">
            <input type="text" class="search-input" placeholder="Search...">
            {%for d in data%}
                {%if 'sub_menus' in d%}
                <div class="submenu-content" id="{{d.id}}">
                    <div class="shortcut_menu">
                        {%for s in d.sub_menus.shortcut_menu%}
                    
                            <a  class="sub_menu_link" data-name="{{s.name}}" data-doc-view="{{s.doc_view}}" data-link-to="{{s.link_to}}" data-type="{{s.type}}">{{s.name}}</a>
                            <hr/>
                             
                        {%endfor%}
                          <hr/>
                          <div class="accordion" id="accordionExample">
                            {% for g in d.sub_menus.workspace_links%}
                            <div class="card">
                                <div class="card-header" id="head_{{g.name}}">
                                <h2 class="mb-0">
                                    <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#collapse{{g.name}}" aria-expanded="true" aria-controls="collapse{{g.name}}">
                                        {{g.label}}
                                    </button>
                                </h2>
                                </div>

                                <div id="collapse{{g.name}}" class="collapse {{'show' if g.show else ''}}" aria-labelledby="head_{{g.name}}" data-parent="#accordionExample">
                                <div class="card-body">
                                    {%for l in g.links%}
                                        <a  class="sub_menu_link"  data-link-to="{{l.link_to}}" data-type="{{l.link_type}}">{{l.label}}</a>
                                        <hr/>
                                    {%endfor%}
                                </div>
                                </div>
                            </div>
                           {%endfor%}
                        </div>
                          <hr/>
                    </div>
                </div>
                {%endif%}
            {%endfor%}
        </div>
    </div>
    """
    
    
    return frappe.render_template(template,{"data":menus,"app_logo":frappe.db.get_single_value("Navbar Settings","app_logo")})



