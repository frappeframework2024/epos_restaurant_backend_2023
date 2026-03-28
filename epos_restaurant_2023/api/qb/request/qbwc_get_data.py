import frappe
from frappe.model.naming import make_autoname

### API Create Queues
@frappe.whitelist()
def get_qb_chart_of_account():
    frappe.publish_realtime("product_notification", {"message": "Getting QB Chart of Accounts"},user=frappe.session.user)
    doc = frappe.get_single("Quickbooks Desktop Integration") 
    branch_usernames = [d.business_branch for d in doc.available_branch]
    branches = frappe.get_all("Business Branch",fields=["name"], filters={"name":["in", branch_usernames ]})
    for b in branches:
        doc = frappe.new_doc("Quickbooks Sync Queues")
        doc.action = "Get"
        doc.status = "Pending"
        doc.action_type = "Chart Of Account"
        doc.business_branch = b.name
        doc.code = make_autoname("QBCoA.-.####")
        doc.insert()
    frappe.db.commit()
    frappe.publish_realtime("product_notification", {"message": "Finsh Getting QB Chart of Accounts"},user=frappe.session.user)
    
@frappe.whitelist()
def get_qb_payment_type():
    frappe.publish_realtime("product_notification", {"message": "Getting QB Payment Types"},user=frappe.session.user)
    doc = frappe.get_single("Quickbooks Desktop Integration") 
    branch_usernames = [d.business_branch for d in doc.available_branch]
    branches = frappe.get_all("Business Branch",fields=["name"], filters={"name":["in", branch_usernames ]})
    for b in branches:
        doc = frappe.new_doc("Quickbooks Sync Queues")
        doc.action = "Get"
        doc.status = "Pending"
        doc.action_type = "Payment Type"
        doc.business_branch = b.name
        doc.code = make_autoname("QBPT.-.#####")
        doc.insert()
    frappe.db.commit()
    frappe.publish_realtime("product_notification", {"message": "Finsh Getting QB Payment Types"},user=frappe.session.user)
    
@frappe.whitelist()
def get_qb_customer():
    frappe.publish_realtime("product_notification", {"message": "Getting QB Customers"},user=frappe.session.user)
    doc = frappe.get_single("Quickbooks Desktop Integration") 
    branch_usernames = [d.business_branch for d in doc.available_branch]
    branches = frappe.get_all("Business Branch",fields=["name"], filters={"name":["in", branch_usernames ]})
    for b in branches:
        doc = frappe.new_doc("Quickbooks Sync Queues")
        doc.action = "Get"
        doc.status = "Pending"
        doc.action_type = "Customer"
        doc.business_branch = b.name
        doc.code = make_autoname("QBC.-.#####")
        doc.insert()
    frappe.db.commit()
    frappe.publish_realtime("product_notification", {"message": "Finsh Getting QB Customers"},user=frappe.session.user)
    
### End API Create Queues

### XML Builder  
#get chart of account xml
def get_qb_chart_of_account_xml(requestID):
    iterator = "Start"
    iterator_id = ""        
    existing = frappe.db.exists("Quickbooks Sync Queues",  {"request_id": requestID})
    if existing:    
        queue_doc = frappe.get_doc("Quickbooks Sync Queues", existing)        
        if queue_doc.iterator_id:
            iterator = 'Continue'
            iterator_id = f' iteratorID="{queue_doc.iterator_id}"'
        
        
        qbxml = f"""
            <AccountQueryRq requestID="{requestID}">
                <MaxReturned>5000</MaxReturned>
                <ActiveStatus>ActiveOnly</ActiveStatus>
            </AccountQueryRq>
        """
        return qbxml
    
    return ""
 
# get payment type
def get_qb_payment_type_xml(requestID):
    qbxml = f"""
        <PaymentMethodQueryRq requestID="{requestID}">
            <MaxReturned>100</MaxReturned>
        </PaymentMethodQueryRq >
    """
    return qbxml


# get payment type
def get_qb_customer_xml(requestID):
    iterator = "Start"
    iterator_id = ""        
    existing = frappe.db.exists("Quickbooks Sync Queues",  {"request_id": requestID})
    if existing:    
        queue_doc = frappe.get_doc("Quickbooks Sync Queues", existing)        
        if queue_doc.iterator_id:
            iterator = 'Continue'
            iterator_id = f' iteratorID="{queue_doc.iterator_id}"'        
        
        qbxml = f"""
            <CustomerQueryRq requestID="{requestID}" >
                <MaxReturned>5000</MaxReturned>
                <ActiveStatus>ActiveOnly</ActiveStatus>
            </CustomerQueryRq>
        """
        return qbxml
    
    return ""