import xml.etree.ElementTree as ET
import frappe
import json
from collections import defaultdict
from epos_restaurant_2023.api.qb.qbwc_helper import (is_json,qb_amount)

def add_receive_payment_xml(queueID,invTxnID,ARListID, queuesData):    
    
    # Parse JSON if needed
    if isinstance(queuesData, str) and is_json(queuesData):
        queues_data = json.loads(queuesData)
        
    posting_date = queues_data.get("posting_date",None) 
    _data = queues_data.get("data", [])  
    if len(_data) > 0:
        data = _data[0]  
                    
        total_amount = round(data["debit"],2)  
        cust_list_id = data.get("qb_cust_list_id",None) or ""
        qb_acc = data.get("qb_account",None) or ""            
        qbxml = f"""<ReceivePaymentAddRq requestID="{queueID}">
                <ReceivePaymentAdd>
                    <CustomerRef>
                        <ListID>{cust_list_id}</ListID>
                    </CustomerRef>
                     <ARAccountRef>   <!-- 🔥 REQUIRED -->
                        <ListID>{ARListID}</ListID>
                    </ARAccountRef>        
                    <TxnDate>{posting_date}</TxnDate>
                    <TotalAmount>{qb_amount(total_amount)}</TotalAmount>
                    <DepositToAccountRef>
                        <FullName>{qb_acc}</FullName>
                    </DepositToAccountRef>
                    <AppliedToTxnAdd>
                        <TxnID>{invTxnID}</TxnID>
                        <PaymentAmount>{qb_amount(total_amount)}</PaymentAmount>
                    </AppliedToTxnAdd>
                </ReceivePaymentAdd>
            </ReceivePaymentAddRq>
        """
        return qbxml
    
    return ""
    