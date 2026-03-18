import time
import threading
import frappe
from spyne import Application, rpc, srpc, ServiceBase, Unicode, Integer, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from wsgiref.simple_server import make_server 
from .qbwc_helper import qbxml_to_json

# ────────── Frappe Context Helpers ──────────
def init_frappe():


    """Initialize Frappe site context if not already initialized."""
   
    if not getattr(frappe.local, "site", None):
        # This works only if bench --site <site> is used
        # frappe.init will automatically pick the site from bench
        import sys
        # The site name is the 3rd argument in sys.argv when using execute
        # Example: bench --site epos.dev execute path.to.func
        if "--site" in sys.argv:
            site_index = sys.argv.index("--site") + 1
            site_name = sys.argv[site_index]
            print(site_name)
            frappe.init(site=site_name)
            frappe.local.site = site_name
            
        else:
            raise Exception("Site not specified! Use --site <sitename>")
        
    if not frappe.db:
        frappe.connect()

def close_frappe():
    """Close Frappe DB connection."""
    if frappe.db:
        frappe.destroy()

# ────────── In-memory session store ──────────
sessions = {}

# ────────── QuickBooks SOAP Service ──────────
class QuickBooksService(ServiceBase):

    @rpc(_returns=Unicode)
    def serverVersion(ctx):
        return "1.0"

    @rpc(Unicode, _returns=Unicode)
    def clientVersion(ctx, strVersion):
        print(f"clientVersion called: {strVersion}")
        return ""  # accept any version

    @srpc(Unicode, Unicode, _returns=Iterable(Unicode))
    def authenticate(strUserName, strPassword):
        print(f"authenticate called → user: {strUserName}, pass: {strPassword[:4]}...")
        if strUserName == "Admin" and strPassword == "Admin@123":
            ticket = f"session_{strUserName}_{int(time.time()*1000)}"
            sessions[ticket] = {"username": strUserName, "created": time.time(), "last_seen": time.time()}
            print(f"Authentication SUCCESS → ticket = {ticket}")
            yield ticket
            yield ""  # use currently open company file
        else:
            print("Authentication FAILED")
            yield "nvu"

    # ─── Send requests to QuickBooks (QBXML) ───
    @rpc(Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, _returns=Unicode) 
    def sendRequestXML(ctx, ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
 
        try:
            init_frappe()
            if ticket not in sessions:
                return ""     
            
            return """<?xml version="1.0"?>
            <?qbxml version="13.0"?>
            <QBXML>
            <QBXMLMsgsRq onError="continueOnError">
                <CustomerTypeQueryRq requestID="CustomerTypesAll" >
                <MaxReturned>1000</MaxReturned>
                </CustomerTypeQueryRq>
                
                <VendorTypeQueryRq requestID="VendorTypesAll" >
                <MaxReturned>1000</MaxReturned>
                </VendorTypeQueryRq>

                <ClassQueryRq requestID="ClassesAll">
                <MaxReturned>1000</MaxReturned>
                </ClassQueryRq>
                            
                <AccountQueryRq requestID="AccountsAll">
                <MaxReturned>1000</MaxReturned>
                <ActiveStatus>All</ActiveStatus>
                </AccountQueryRq>
                
                <PaymentMethodQueryRq requestID="PaymentMethodsAll">
                <MaxReturned>100</MaxReturned>
                </PaymentMethodQueryRq>
                
                <CustomerQueryRq requestID="CustomerAll" >
                <MaxReturned>1000</MaxReturned>
                <ActiveStatus>All</ActiveStatus>
                </CustomerQueryRq>

            </QBXMLMsgsRq>
            </QBXML>"""
            
            ## get 1000 customers
            # return """<?xml version="1.0"?>
            # <?qbxml version="13.0"?>
            # <QBXML>
            # <QBXMLMsgsRq onError="continueOnError">
            #     <CustomerQueryRq requestID="1" >
            #     <MaxReturned>1000</MaxReturned>
            #     <ActiveStatus>All</ActiveStatus>
            #     </CustomerQueryRq>
            # </QBXMLMsgsRq>
            # </QBXML>"""
            
            
            
            
            
            customer_list = frappe.db.sql("select name from `tabCustomer` where coalesce(note,'') = '' ", as_dict= True)
            print(f"Customers: {len( customer_list)}")
            if len( customer_list) <=0:
                print("No pending customers to sync")
                return ""

            msgs = ""
            for c in customer_list:
                doc = frappe.get_doc("Customer", c.get("name"))
                msgs += f"""
                <CustomerAddRq requestID="{doc.name}">
                    <CustomerAdd>
                        <Name>{doc.name}</Name>
                    </CustomerAdd>
                </CustomerAddRq>
                """ 
                
            qbxml = f"""<?xml version="1.0"?>
                <?qbxml version="13.0"?>
                <QBXML>
                <QBXMLMsgsRq onError="continueOnError">
                    {msgs}
                </QBXMLMsgsRq>
                </QBXML>"""
        
            #onError: continueOnError,stopOnError
            print(f"Sending QBXML for {len(customer_list)} customers")
            return qbxml.strip()
        finally:
            close_frappe()

    # ─── Receive responses from QuickBooks ───
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ctx, ticket, response, hresult, message):
        
        
       
        print("=== receiveResponseXML called ===")        
        json_output = qbxml_to_json(response)
        print(json_output)
        return 100

        try:
            init_frappe()
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response)
            print(root)
            
            
            # Find all CustomerAddRs elements
            for cust_rs in root.findall(".//CustomerAddRs"):
                status_code = cust_rs.attrib.get("statusCode", "")
                status_message = cust_rs.attrib.get("statusMessage", "")
                request_id = cust_rs.attrib.get("requestID")
                if status_code == "0":
                    # Success → mark customer as synced
                    print(f"Customer added successfully: {status_message}")
                    doc = frappe.get_doc("Customer", request_id)
                    doc.db_set("note","Synced")
                    
                elif status_code == "3100":   
                    # Duplicate → ignore and mark as synced
                    doc = frappe.get_doc("Customer", request_id)
                    doc.db_set("note","Synced (duplicate in QB)")                    
                    print(f"{request_id} already exists in QB, marked as Synced")
                
                else:
                    # Error → log for review or retry
                    print(f"Customer add ERROR: {status_code} → {status_message}")
                    # Optional: update customer note for error tracking
                    
                    if request_id:
                        print(f"{request_id} => Error: {status_message}")
                        
                        # frappe.db.set_value("Customer", request_id, "note", f"Error: {status_message}")
            frappe.db.commit()
        except ET.ParseError as e:
            print("Failed to parse QBXML response:", e)
        
        finally:
            close_frappe()

        return 100

    @rpc(Unicode, _returns=Unicode)
    def getLastError(ctx, ticket):
        return "No error description"

    @rpc(Unicode, _returns=Unicode)
    def closeConnection(ctx, ticket):
        if ticket in sessions:
            del sessions[ticket]
        return "OK"

# ────────── Spyne SOAP setup ──────────
application = Application(
    [QuickBooksService],
    tns='http://developer.intuit.com/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)
wsgi_application = WsgiApplication(application)

def start_qbwc_server():
    """Start SOAP server on port from site config or default 8001"""
    init_frappe()
    port = frappe.get_conf().get("qbwc_port", 8001)
    print(f"Starting QBWC SOAP server at http://0.0.0.0:{port}")
    server = make_server('0.0.0.0', port, wsgi_application)
    server.serve_forever()

def run_server():
    thread = threading.Thread(target=start_qbwc_server, daemon=True)
    thread.start()
    print("QBWC server thread started")

    # Keep main thread alive so daemon thread doesn't die
    import time
    while True:
        time.sleep(10)




# -----------------------------
# Frappe endpoint to wrap Spyne WSGI app
# -----------------------------


@frappe.whitelist(allow_guest=True)
def qbwc():
    from werkzeug.wrappers import Response
    
    environ = frappe.request.environ
    response = []

    def start_response(status, headers):
        response.append((status, headers))

    result = wsgi_application(environ, start_response)

    status, headers = response[0]

    body = b"".join(result)

    return Response(
        body,
        status=int(status.split()[0]),
        headers=dict(headers)
    )