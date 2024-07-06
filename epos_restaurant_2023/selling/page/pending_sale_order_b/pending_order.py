import frappe
from frappe import _
from frappe.utils import pretty_date
import json
from urllib.parse import unquote, quote

@frappe.whitelist(allow_guest=1, methods="POST")
def get_pending_order(param): 
    params = json.loads(param)
    doc = frappe.get_doc("POS Profile",params["pos_profile"] )
    table_groups = doc.table_groups 
    result = {"table_groups":[]}
    sale_status = frappe.db.get_all("Sale Status", fields=["sale_status", "priority", "background_color"], order_by="priority")
    for ss in sale_status:
        ss.update({"color":"#ffffff"})
    
    default_background, default_color = frappe.db.get_value("ePOS Settings", None, ["default_table_number_background_color","default_table_number_text_color"])


    for tg in table_groups: 
        
         
        
        tables = frappe.db.get_all("Tables Number",  
                                   filters={"tbl_group":tg.table_group}, 
                                   fields=["name","tbl_number"],
                                   limit_page_length=500
                                )
        for t in tables:
            sales = frappe.db.get_all("Sale", 
                                       filters=[["table_id","=",t.name], ["docstatus","!=",1]],
                                       fields=["name","custom_bill_number","creation","sale_status","sale_status_priority","sale_status_color", "grand_total"],
                                       order_by="creation"
                                    )
            time_ago = "0"
            total_amount = 0
            if len( sales)>0:
                min_creation = min(sales, key=lambda z: z.creation)
                time_ago = pretty_date(min_creation.creation)
                priority = min(sales, key=lambda z: z.sale_status_priority)  
                total_amount = sum(s.grand_total for s in sales)
                for s in sales:
                    s.update({"time_ago":pretty_date(s.creation),
                              "background":s.sale_status_color, 
                              "color":s.sale_status_color, 
                              "status":s.sale_status,
                              "bill_number":s.custom_bill_number or ""
                              })
                    del s["custom_bill_number"]
                    del s["sale_status_priority"]
                    del s["sale_status_color"]
                    del s["sale_status"]
                    del s["creation"]

            
            t.update({
                "table_id":t.name,
                "time_ago":time_ago,
                "background":default_background if len(sales) == 0  else priority.background,
                "color": default_color if len(sales) == 0  else  "#ffffff",
                "total_sales":len(sales),
                "total_amount": total_amount,
                "sales":sales, 
            })
        result["table_groups"].append({"group":tg.table_group,"id":tg.name, "tables":tables })
    if result:
        if len( result["table_groups"])>0:
            result["table_groups"][0]["active"] = "active"
            result["table_groups"][0]["show"] = "show"
    return result