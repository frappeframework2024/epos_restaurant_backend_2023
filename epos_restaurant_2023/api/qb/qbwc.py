import time
import threading
import frappe
from spyne import Application, rpc, srpc, ServiceBase, Unicode, Integer, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from wsgiref.simple_server import make_server 
from .qbwc_helper import  qbxml_to_json
from .qbwc_handle_response import  (
    handle_qb_response,
    handle_qb_company_response,
)
from epos_restaurant_2023.api.qb.request.qbwc_journal_entry import add_journal_xml
from epos_restaurant_2023.api.qb.request.qbwc_invoice import add_ar_invoice_xml
from epos_restaurant_2023.api.qb.request.qbwc_receive_payment import add_receive_payment_xml
from epos_restaurant_2023.api.qb.request.qbwc_get_data import ( 
        get_qb_chart_of_account_xml,
        get_qb_payment_type_xml,
        get_qb_customer_xml,
        get_qb_product_xml,
        get_qb_journal_entry_classes_xml
    )

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
        
        
        try:
            init_frappe()
            conf = frappe.db.sql("""
                                 select 
                                    business_branch ,
                                    qb_company_name
                                 from `tabQuickbooks Available Branch` 
                                 where 1=1
                                 and web_connecter_username = %(usr)s 
                                 and web_connecter_password = %(pwd)s""", 
                                {
                                    "usr":strUserName,
                                    "pwd":strPassword
                                }, as_dict= True)
            
            
            if len(conf) > 0:
                ticket = f"session_{strUserName}_{int(time.time()*1000)}"
                sessions[ticket] = {"username": strUserName, "companies":conf, "created": time.time(), "last_seen": time.time()}
                
                print(f"Branchs=> {conf}")
                print(f"Authentication SUCCESS → ticket = {ticket}")
                yield ticket
                yield ""  # use currently open company file
            else:
                print("Authentication FAILED")
                yield "nvu"
                
                
        finally:
            close_frappe()

    # ─── Send requests to QuickBooks (QBXML) ───
    @rpc(Unicode, Unicode, Unicode, Unicode, Unicode, Unicode, _returns=Unicode) 
    def sendRequestXML(ctx, ticket, strHCPResponse, strCompanyFileName, qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
        try:
            init_frappe()
            if ticket not in sessions:
                return ""    
            
            companies = tuple(
                d['business_branch'] 
                for d in (sessions[ticket].get("companies", None) or [])
            )

            if not companies:
                queues = []
            else:
                queues = frappe.db.sql(""" 
                    SELECT 
                        name, 
                        business_branch,
                        request_id,
                        action, 
                        action_type,
                        payload,
                        account_ref_list_id,
                        reference_name,
                        code 
                    FROM `tabQuickbooks Sync Queues` 
                    WHERE business_branch IN %(companies)s 
                    AND status IN ('Pending', 'Error')
                """, {
                    "companies": companies
                }, as_dict=1)
                            
            add_journal_xmls =[]
            add_invoice_xmls = [] # add invoice as credit (pos pay on-account)
            add_receive_payment_xmls = [] # add receive payment of invoice as credit
            
            get_coa_xml = "" #get chart of account
            get_pt_xml = "" # get payment type / payment method           
            get_cus_xml = "" # get customer        
            get_pro_xml = "" # get product      
            get_jec_xml = "" # get journal entry classes  
           
            
            
            config = frappe.get_doc("Quickbooks Desktop Integration")
                
            for q in queues :
                action_type = q.get("action_type",None)
                action = q.get("action",None)   
                requestID = q.get("request_id",None) 
                queueID =  q.get("name",None) 
                
                
                qbCompanyName = ""
                available_branchs  = [x for x in config.available_branch if x.business_branch == q.get("business_branch",None)]
                if len(available_branchs)>0:
                    qbCompanyName = available_branchs[0].get("qb_company_name",None) or ""
                
                if action_type == "Chart Of Account":
                    if action == "Get":
                        get_coa_xml = get_qb_chart_of_account_xml(requestID=requestID)
                        
                elif action_type == "Payment Type":
                    if action == "Get":
                        get_pt_xml = get_qb_payment_type_xml(requestID= requestID)
                        
                elif action_type == "Customer":
                    if action == "Get":
                        get_cus_xml = get_qb_customer_xml(requestID= requestID)
                        
                elif action_type == "Product":
                    if action == "Get":
                        get_pro_xml = get_qb_product_xml(requestID= requestID)

                elif action_type == "Journal Entry Classes":
                    if action == "Get":
                        get_jec_xml = get_qb_journal_entry_classes_xml(requestID= requestID)        
                
                elif action_type == "GL Entry":                    
                    # pass
                    if action == "Add":                                            
                        val = add_journal_xml(
                                queuesData= q.get("payload",None),
                                RefNumber=q.get("code",None),
                                requestID= requestID,
                                JEMemo=q.get("reference_name",None),
                                companyName = qbCompanyName,
                            )                        
                        if val:
                            add_journal_xmls.append(val)
                            
                        pass    
                    
                elif  action_type == "Sale":
                    if action == "Add":
                        val = add_ar_invoice_xml(                            
                            queuesData= q.get("payload",None),
                            companyName= qbCompanyName,
                            requestID= requestID
                        )
                        if val:
                            add_invoice_xmls.append(val)
                            
                            
                elif  action_type == "Sale Payment":
                    ARListID = q.get("account_ref_list_id",None)                     
                    if action == "Add":
                        val = add_receive_payment_xml(      
                            queueID = queueID,
                            invTxnID = requestID,
                            ARListID= ARListID,
                            queuesData= q.get("payload",None),
                        )
                        if val:
                            add_receive_payment_xmls.append(val) 
                        
                else:
                    pass 
                
            qbxmls = f"""
            <?xml version="1.0" encoding="utf-8"?>
            <?qbxml version="15.0"?>
            <QBXML>
                <QBXMLMsgsRq onError="continueOnError">
                    <CompanyQueryRq requestID="getCompany"/>
                    {get_coa_xml}
                    {get_cus_xml}
                    {get_pt_xml}
                    {get_pro_xml}
                    {get_jec_xml}
                    {''.join(add_invoice_xmls)}
                    {''.join(add_receive_payment_xmls)}
                    {''.join(add_journal_xmls)}
                </QBXMLMsgsRq>
            </QBXML>
            """ 
            
            # return f"""<?xml version="1.0" encoding="utf-8"?>
            #             <?qbxml version="15.0"?>
            #         <QBXML>
            #         <QBXMLMsgsRq onError="stopOnError">
            #             <InvoiceQueryRq requestID="1">
            #             <TxnID>1495D-1774587672</TxnID>
            #             </InvoiceQueryRq>
            #             <InvoiceQueryRq requestID="2">
            #             <TxnID>14965-1774587672</TxnID>
            #             </InvoiceQueryRq>
            #         </QBXMLMsgsRq>
            #         </QBXML>""".strip()
            
            # print(f"Request XML: {qbxmls.strip()}")   
            return qbxmls.strip()
            
        
        
        finally:
            close_frappe()

    # ─── Receive responses from QuickBooks ───
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ctx, ticket, response, hresult, message):
        print("=== receiveResponseXML called ===") 
        if response:  
            # print(response)
            try:
                init_frappe()
                company_name = handle_qb_company_response(xml_string=response)   
                
                handle_qb_response(xml_string=response, company_name = company_name )  
                return 100
                
            finally:
                close_frappe()
        else:
            print(f"There're response data xml: {message}")
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
# ============================================================
# Spyne SOAP Application
# ============================================================
application = Application(
    [QuickBooksService],
    tns='http://developer.intuit.com/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

# ============================================================
# Spyne WSGI Application
# ============================================================

spyne_application = WsgiApplication(
    application
)

# ============================================================
# QBWC HTTP / WSGI Wrapper
# ============================================================

def wsgi_application(
    environ,
    start_response
):
    """
    HTTP wrapper around Spyne.

    QuickBooks Web Connector performs:

        GET /

    before adding the QWC application to verify
    the application server certificate.

    Spyne normally expects SOAP POST requests,
    therefore GET / must be handled separately.
    """

    method = environ.get(
        "REQUEST_METHOD",
        "GET"
    )

    path = environ.get(
        "PATH_INFO",
        "/"
    )

    # --------------------------------------------------------
    # QBWC certificate verification
    # --------------------------------------------------------

    if method == "GET" and path == "/":

        body = (
            b"ePOS 2023 QBWC SOAP Service "
            b"QB Web Connector Service"
        )

        start_response(
            "200 OK",
            [
                (
                    "Content-Type",
                    "text/plain; charset=utf-8"
                ),
                (
                    "Content-Length",
                    str(len(body))
                ),
                (
                    "Cache-Control",
                    "no-cache"
                ),
            ],
        )

        return [body]

    # --------------------------------------------------------
    # WSDL / SOAP requests
    # --------------------------------------------------------
    #
    # Everything else goes to Spyne.
    #

    return spyne_application(
        environ,
        start_response
    )
    

# wsgi_application = WsgiApplication(application)

# ============================================================
# Start QBWC Server
# ============================================================
def start_qbwc_server():
    """
    Start QBWC SOAP server.
    Port is loaded from site configuration:
        qbwc_port = 8001
    Default:
        8001
    """

    init_frappe()
    port = frappe.get_conf().get("qbwc_port",8001)

    print("==========================================")
    print("QBWC SERVER")
    print(f"Listening on: 0.0.0.0:{port}")
    print("GET /  -> QBWC certificate verification")
    print("POST / -> SOAP Web Connector")
    print("==========================================")

    server = make_server("0.0.0.0",port, wsgi_application)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("QBWC server stopped.")
    finally:

        server.server_close()

def run_server():
    """
    Start QBWC server in background thread.

    Used with:

        bench --site <site> execute \
        epos_restaurant_2023.api.qb.qbwc.run_server
    """

    thread = threading.Thread(
        target=start_qbwc_server,
        daemon=True
    )

    thread.start()

    print(
        "QBWC server thread started."
    )

    # Keep main thread alive
    while True:

        time.sleep(10)


# -----------------------------
# Frappe endpoint to wrap Spyne WSGI app
# -----------------------------


@frappe.whitelist(allow_guest=True)
def test_me(queues_id):
    
    q = frappe.get_doc("Quickbooks Sync Queues",queues_id)
    
    return add_ar_invoice_xml(
        queuesData= q.get("payload",None),
        RefNumber=q.get("code",None),
        requestID= q.get("request_id",None)
    )
    
    
