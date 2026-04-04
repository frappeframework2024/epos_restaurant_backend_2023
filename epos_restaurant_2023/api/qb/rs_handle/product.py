import frappe
from epos_restaurant_2023.api.qb.qbwc_helper import pretty_xml

## handle response customer
def handle_item_query(res, company_name):
    """
    Handle QuickBooks QBWC response for Items/Products
    and save them into Frappe Quickbooks Data DocType.
    
    Args:
        res (xml ElementTree): QBWC response root
        company_name (str): Company identifier
    """

    # 1️⃣ Extract response metadata
    request_id = res.get("requestID")
    status_code = res.get("statusCode")
    status_msg = res.get("statusMessage")

    # 2️⃣ Check if corresponding queue exists
    existing_queue = frappe.db.exists("Quickbooks Sync Queues", {"request_id": request_id})
    if not existing_queue:
        msg = f"Queue not found for request_id: {request_id}"
        frappe.log_error(msg, title="QBWC Item Handling")
        print(msg)
        return
    
    queue = frappe.get_doc("Quickbooks Sync Queues", existing_queue)

    # 3️⃣ Avoid duplicate processing
    if queue.status == "Completed":
        print(f"Queue {request_id} already completed")
        return

    # 4️⃣ Handle QBWC error responses
    if status_code != "0":
        frappe.log_error(f"ItemQuery Failed: {status_msg}", title="QBWC Item Handling")
        queue.status = "Error"
        queue.response_message = f"[{status_code}] {status_msg}"
        queue.save(ignore_permissions=True)
        return

    # 5️⃣ Process ItemRet nodes only
    item_nodes = res.findall(".//ItemServiceRet") + res.findall(".//ItemDiscountRet")
    if not item_nodes:
        queue.status = "Completed"
        queue.response_message = "No items found"
        queue.save(ignore_permissions=True)
        return

    for d in item_nodes:
        list_id = d.findtext("ListID")
        full_name = d.findtext("FullName")
        edit_sequence = d.findtext("EditSequence")
        parent = d.findtext("ParentRef/FullName") if d.find("ParentRef/FullName") is not None else None       

        if not list_id:
            continue  # skip invalid record

        # 6️⃣ Check if record already exists
        existing_doc = frappe.db.exists("Quickbooks Data", {
            "qb_list_id": list_id,
            "data_type": "Product"
        })

        if existing_doc:
            doc = frappe.get_doc("Quickbooks Data", existing_doc)
        else:
            doc = frappe.new_doc("Quickbooks Data")

        # 7️⃣ Save raw XML
        data_xml_str = pretty_xml(d)
        doc.qb_raw_xml = data_xml_str

        # 8️⃣ Map fields to Frappe Doc
        doc.qb_list_id = list_id
        doc.code = full_name
        doc.data_type = "Product"
        doc.qb_company = company_name
        doc.qb_edit_sequence = edit_sequence

        # 9️⃣ Save document
        doc.save(ignore_permissions=True)

    # 10️⃣ Mark queue as completed
    queue.status = "Completed"
    queue.response_message = f"Processed {len(item_nodes)} items"
    queue.save(ignore_permissions=True)
