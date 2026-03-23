import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from epos_restaurant_2023.api.qb.qbwc_helper import (is_json,qb_amount)

def add_ar_invoice_xml(requestID, queuesData, RefNumber):
    
    # Parse JSON if needed
    if isinstance(queuesData, str) and is_json(queuesData):
        queues_data = json.loads(queuesData)
        
    posting_date = queues_data.get("posting_date",None) 
    data = queues_data.get("data", [])  
    
    # Group by sale_id
    grouped = defaultdict(list)
    for row in data:
        grouped[row["sale_id"]].append(row)

    # Build full grouped structure with totals
    full_grouped = {}
    for sale_id, lines in grouped.items():
        # total_debit = round(sum(r["debit"] for r in lines),2)
        # total_credit = round(sum(r["credit"] for r in lines),2)
        full_grouped[sale_id] = {
            "qb_cust_list_id": lines[0]["qb_cust_list_id"],
            "ref_number": sale_id,
            "lines": lines
        } 
        
    
    invoices = []
    for inv in full_grouped.values():        
        invoices.append(inv)
    
    invoice = invoices[0]    
    
    itemLine = ""    
    for line in  (invoice.get("lines",None) or []):
        if line.get("account_type",None) not in ["Cash","Bank"]:        
            rate = abs ((line.get("debit",None) or 0) - (line.get("credit",None) or 0))
            itemLine = itemLine + f"""<InvoiceLineAdd>
            <ItemRef>
                <FullName>{line.get("account",None)}</FullName>
            </ItemRef> 
            <Rate>{qb_amount(rate)}</Rate>            
            </InvoiceLineAdd>""" 
    ref = invoice.get("ref_number",None)
    result_ref = ref[-11:] if len(ref) > 11 else ref
    
    xml = f"""<InvoiceAddRq requestID="{requestID}">
      <InvoiceAdd>
        <CustomerRef>
          <ListID>{invoice.get("qb_cust_list_id")}</ListID>
        </CustomerRef>
        <TxnDate>{posting_date}</TxnDate>
        <RefNumber>{result_ref}</RefNumber>
        {itemLine}
      </InvoiceAdd>
    </InvoiceAddRq>"""
        
      
    if itemLine:
        return xml
    
    
    return ""