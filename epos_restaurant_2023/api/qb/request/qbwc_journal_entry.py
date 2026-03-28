import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from epos_restaurant_2023.api.qb.qbwc_helper import (is_json,qb_amount)
import frappe

def add_journal_xml(requestID, queuesData, RefNumber,JEMemo, companyName):
    # Parse JSON if needed
    if isinstance(queuesData, str) and is_json(queuesData):
        data = json.loads(queuesData)
        
    posting_date = data.get("posting_date",None) 
    lines = data.get("data", [])    
    if lines:
        # 🔹 Group accounts
        debit_map = defaultdict(float)
        credit_map = defaultdict(float)
        
        config = frappe.get_doc("Quickbooks Desktop Integration")
        account_mapping = config.tbl_chart_of_account_mapping
        print(companyName)
        
        for row in lines:
            account = row.get("account")
            qb_accounts = [x for x in account_mapping if  x.reference_name == row.get("account") and  x.qb_company == companyName]            
            if len(qb_accounts) > 0 :                
                row["qb_account"] = qb_accounts[0].qb_name
                row["qb_acc_list_id"] = qb_accounts[0].qb_list_id
                
            if not account:
                raise ValueError("Account name missing")
            
            debit = float(row.get("debit", 0) or 0)
            credit = float(row.get("credit", 0) or 0)
            key = (row["qb_account"], row["qb_acc_list_id"], row["name"])
            if debit > 0:
                debit_map[key] += debit
            elif credit > 0:
                credit_map[key] += credit

        # 🔹 Validate totals
        total_debit = round(sum(debit_map.values()), 2)
        total_credit = round(sum(credit_map.values()), 2)

        if total_debit != total_credit:
            raise ValueError(
                f"Journal not balanced: debit={total_debit}, credit={total_credit}"
            ) 
            
        # 🔹 Build XML lines
        xml_lines = ""
        # Debit lines
        for (acc,acc_list_id,name), amt in debit_map.items():                
            xml_lines += f"""
            <JournalDebitLine>
                <AccountRef>
                    <ListID>{acc_list_id}</ListID>
                </AccountRef>
                <Amount>{qb_amount(amt)}</Amount>
                <Memo> {JEMemo} ~ Debit </Memo> 
            </JournalDebitLine>"""

        # Credit lines
        for (acc,acc_list_id,name), amt in credit_map.items():   
            xml_lines += f"""
            <JournalCreditLine>
                <AccountRef>
                    <ListID>{acc_list_id}</ListID>
                </AccountRef>
                <Amount>{qb_amount(amt)}</Amount>
                <Memo> {JEMemo} ~ Credit </Memo>
            </JournalCreditLine>"""

        # 🔹 Final XML
        
        
        journal_xml_trans= f"""
        <JournalEntryAddRq requestID="{requestID}">
            <JournalEntryAdd>
                <TxnDate>{posting_date}</TxnDate>
                <RefNumber>{RefNumber}</RefNumber>
                {xml_lines}
            </JournalEntryAdd>
        </JournalEntryAddRq>
        """  
        return  journal_xml_trans 