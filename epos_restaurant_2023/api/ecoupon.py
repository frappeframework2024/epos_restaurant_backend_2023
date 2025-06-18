import json
import frappe

def remove_key(data, keys= None):
    if   keys is None:
        keys = ["owner", "creation", "modified", "modified_by", "docstatus", "idx","_user_tags","_comments","_assign","_liked_by"]
    
    if isinstance(data, dict):
        return {
            k: remove_key(v, keys) if isinstance(v, (dict, list)) else v
            for k, v in data.items() if k not in keys
        }

    elif isinstance(data, list):
        return [remove_key(item, keys) for item in data]


@frappe.whitelist(methods=["POST"])
def app_settings(params): 
    result = {}

    ## get pos station
    ignore = True
    if params.get("station_name"): 
        station = frappe.get_doc("POS Station", params.get("station_name")) 
        
        if not station or station.disabled:
            ignore = False  
    else:
        ignore = False

    if not ignore:
        stations = frappe.db.sql("select name from `tabPOS Station` where device_id = %(device_id)s and platform <> 'Web' and disabled = 0 limit 1", {"device_id":params["device_id"]}, as_dict=1)
  
 
        if not stations or len(stations) == 0:
            frappe.throw("Invalid device station")
           
        station = frappe.get_doc("POS Station", stations[0]["name"])

    station_doc = remove_key(station.as_dict()) 

    ## end get pos station
    ## get shift type
    shift_types = frappe.get_all(
        "Shift Type",
        fields=["*"],
        filters={"show_in_pos": 1},
        order_by="sort asc"
    ) 
    _shift_types = []
    for st in shift_types:
        st_doc = remove_key(st) 
        _shift_types.append(st_doc) 

    result["pos_station"] = station_doc
    result["shift_types"] = _shift_types
    result["socketio"] = {
        "port":frappe.get_conf().get('socketio_port', 9000),
        "site_name": frappe.local.site
    }

    
    return result

@frappe.whitelist(methods=["POST"])
def get_shift_information(params): 
    sql  = "select * from `tabCoupon Shift` where is_closed = 0 and  business_branch = %(business_branch)s and pos_profile = %(pos_profile)s limit 1"
    result = frappe.db.sql(sql, {"business_branch":params["business_branch"], "pos_profile":params["pos_profile"]}, as_dict=1)
    if not result or len(result) == 0:
        return {"data":None, "error": "No shift available"}
    
    doc = remove_key(result[0])
    return {"data":doc, "error":None}