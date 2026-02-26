import frappe
from functools import lru_cache
@frappe.whitelist()
def update_tax_invoice_data_to_tax_invoice(tax_invoice_name,run_commit=True):
    doc = frappe.get_doc("Tax Invoice",tax_invoice_name)
    tax_data = get_tax_invoice_data(folio_number = doc.document_name, document_type=doc.document_type, date= doc.tax_invoice_date)
    doc.sub_total = sum([d["amount"] for d in tax_data["data"]])
    
    # service charge
    doc.service_charge = sum(
                d["value"]
                for entry in tax_data["summary"] if "children" in  entry
                for d in entry["children"] if d["fieldname"] =='service_charge'
            )
    
    # accommodation_tax
    doc.accommodation_tax = sum(
                d["value"]
                for entry in tax_data["summary"] if "children" in  entry
                for d in entry["children"] if d["fieldname"] =='accommodation_tax'
            )
    
    # specific_tax
    doc.specific_tax = sum(
                d["value"]
                for entry in tax_data["summary"] if "children" in  entry
                for d in entry["children"] if d["fieldname"] =='specific_tax'
            )
    
   
    doc.vat = tax_data["vat"]["value"]
    
    doc.grand_total = tax_data["grand_total"]
    doc.flags.ignore_validate = True
    doc.flags.ignore_on_update = True
    
    doc.save(ignore_permissions=True)
    if run_commit:
        frappe.db.commit()
    return doc



@frappe.whitelist()
def get_tax_invoice_data(folio_number,document_type,date ):
    sale=frappe.db.sql("select * from `tabSale` where name='{}'".format(folio_number),as_dict=1)
    
    tax_data = []
 
    tax_data = get_tax_from_sale(sale)
    
    property = frappe.db.get_value("Tax Invoice", {'document_name':folio_number},"property")
    exchange_rate = frappe.db.get_value("Tax Invoice",{'document_name':folio_number},"exchange_rate")

    if (exchange_rate or 0) == 0:
        exchange_rate = get_exchange_rate(property,date)

    total_vat = sale[0]["tax_3_amount"] or 0
        
        
   
    
    grand_total = sum(d["amount"] for d in tax_data)   + total_vat
    
    return_data = {
        "property":property,
        "document_type":document_type,
        "data":tax_data,
        "summary":[],
        "taxable_amount": sum(d["amount"] for d in tax_data),
        "vat":{
            "description":"អាករលើតម្លៃបន្ថែម/VAT (10%)",
            "value":total_vat
        },

        "grand_total":grand_total, 
        "exchange_rate":exchange_rate ,
        "grand_total_second_currency":grand_total*exchange_rate 
    }
    
    return return_data


def get_tax_from_sale(data):
    sql ="""
            select 
                product_name,
                product_name_kh as description ,
                `portion`,
                is_free,
                modifiers,
                discount,
                discount_amount,
                discount_type,
                sum(quantity) as quantity,
                price,
                sum(amount) as amount  
            from `tabSale Product` 
            where 
                parent='{}' and
                total_tax > 0
            group by 
                product_name,
                product_name_kh,
                `portion`,
                is_free,
                modifiers,
                discount,
                discount_amount,
                discount_type, 
                price 
        
            """.format(data[0]['name'])
    
    sale_products = frappe.db.sql(sql, as_dict=1)
    return sale_products


def get_sale_data_group_by_revenue_group(sale_numbers):
    if sale_numbers:
        sql="""
            select 
                sp.revenue_group, 
                s.outlet,
                s.shift_name,
                sum(sp.sub_total) as price, 
                sum(sp.total_discount) as discount,
                1 as quantity ,
                sum(sp.sub_total) as amount,
                sum(sp.tax_1_amount) as tax_1_amount,
                sum(sp.tax_2_amount) as tax_2_amount,
                sum(sp.tax_3_amount) as tax_3_amount,
                9999999 as sort_order
            from `tabSale Product`  sp
                inner join `tabSale` s on s.name = sp.parent
            where 
                sp.parent in %(sale_numbers)s and 
                coalesce(sp.total_tax,0)>0 
            group by 
                revenue_group,
                outlet,
                shift_name
        """
        data = frappe.db.sql(sql,{"sale_numbers":sale_numbers},as_dict=1)
        return data
    else:
        return []


@lru_cache(maxsize=128)
def get_pos_account_code_config(outlet, shift_name):
    data = frappe.db.get_list("POS Account Code Config", filters={"outlet":outlet, "shift_name":shift_name})
    if data:
        return frappe.get_doc("POS Account Code Config", data[0].name)
    return None

@frappe.whitelist(allow_guest=True)
def get_exchange_rate(property,date=None):
        
    main_currency = frappe.db.get_single_value("ePOS Settings","currency")
    second_currency = frappe.db.get_single_value("ePOS Settings","second_currency")    
    data=frappe.db.sql("select exchange_rate from `tabCurrency Exchange` where from_currency='{}' and to_currency='{}' and custom_business_branch='{}' and posting_date<='{}'".format(main_currency, second_currency, property,date),as_dict=1)
    if data:
        return data[0]["exchange_rate"] or 1 
    else:
        return 1