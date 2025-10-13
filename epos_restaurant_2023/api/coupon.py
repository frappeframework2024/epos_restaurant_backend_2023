import frappe
from frappe import _
import datetime
@frappe.whitelist()
def check_coupon_code(coupon_code):
    data = frappe.db.get_list('Coupon Codes', filters={
        'coupon':  coupon_code
    },
    fields=["name","coupon","coupon_status"]
    )
    
    if not data:
        frappe.throw(_("Coupon code not found"))
    else:
        
        if data[0].get("coupon_status") =='Unused': 
            frappe.throw(_("This is an unused coupon code. Please use options Sale Coupon to issue this coupon to customer"))
        elif data[0].get("coupon_status") =='Redeemed':
            frappe.throw(_("This coupon code is already redeemed"))
        elif data[0].get("coupon_status") =='Expired':
            frappe.throw(_("This coupon code is already expired"))

    
    sql = """select 
        coupon_code,
        coupon_number,transaction_date,sale,posting_date,
        input_actual_amount,
        input_coupon_amount,
        currency, 
        product_code
    from `tabCoupon Transaction` 
    where 
        coupon_number=%(coupon_number)s and  
        coalesce(status,'') <> 'Deleted' and 
        transaction_type = "Sale Coupon" 
    limit 1
    """
    coupon_info = frappe.db.sql(sql,{"coupon_number":coupon_code},as_dict=1)
    customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Sale",coupon_info[0].get("sale"),["customer_photo","customer_group","phone_number","customer","customer_name"])  
    coupon_info[0]["customer"] = {
        "name":customer,
        "customer_name":customer_name,
        "customer_group":customer_group,
        "phone_number":phone_number,
        "photo":customer_photo
    }

    if coupon_info:
        if coupon_info[0].get("product_code"):
            product_name,photo = frappe.get_cached_value("Product",coupon_info[0].get("product_code"),["product_name_en","photo"]) 
            
            coupon_info[0]["product_name"] = product_name
            coupon_info[0]["photo"] = photo
            
        coupon_info =  coupon_info[0]
    
    # get balance data
    sql = """
        select 
            transaction_type,
            markup_percentage,
            sum(coupon_amount) as coupon_amount  
        from `tabCoupon Transaction` 
        where 
        coupon_number=%(coupon_number)s and 
        coalesce(status,'') <> 'Deleted'
        group by
            transaction_type,
            markup_percentage
    """
    data = frappe.db.sql(sql,{"coupon_number":coupon_code},as_dict=1)

    coupon_info["coupon_transaction"] = data
    coupon_info["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    coupon_info["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    
    return  coupon_info


@frappe.whitelist()
def get_coupon_detail(coupon_code):
    #coupon code here is primary key
    return_data = {}

    return_data["coupon_info"] = frappe.get_doc("Coupon Codes",coupon_code)
    
    if return_data["coupon_info"].customer:
        customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Customer",return_data["coupon_info"].customer,["photo","customer_group","phone_number","name","customer_name_en"])    
        return_data["customer"] = {
            "name":customer,
            "customer_name":customer_name,
            "customer_group":customer_group,
            "phone_number":phone_number,
            "photo":customer_photo
        }

 
    # get balance data
    sql = """
        select 
            sale,
            creation,
            posting_date,
            created_by,
            transaction_date,
            note,
            transaction_type,
            markup_percentage,
            input_actual_amount,
            coupon_amount ,
            pos_station,
            pos_profile,
            currency,
            exchange_rate
        from `tabCoupon Transaction` 
        where 
        coupon_code=%(coupon_code)s and 
        status not in ('Deleted')
        order by creation
    """
    data = frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict=1)


    return_data["coupon_transaction"] = data
    return_data["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    return_data["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    
    return  return_data

@frappe.whitelist()
def check_coupon_code_for_top_up(coupon_code):
    if not frappe.db.exists("Coupon Codes",{"coupon":coupon_code}):
        frappe.throw(_("Coupon code not found"))


    data = frappe.db.get_list('Coupon Codes', filters={
        'coupon':  coupon_code,
        "coupon_status":"Used"
    },
    fields=["name","coupon","coupon_status","expired_date","reference_doctype"]
    )
    if not data:
        frappe.throw(_("This coupon number is not a used coupon number"))

    if   datetime.datetime.now() > data[0].expired_date:
        frappe.throw(_("This coupon code is expired"))

    if data[0].reference_doctype =="Coupon Issue":
        frappe.throw("គូប៉ុងសម្រាប់បុគ្គលិកមិនអាចបញ្ជូលលុយបានទេ។")


    sql = """select 
        coupon_code,
        coupon_number,transaction_date,sale,posting_date,
        input_actual_amount,
        input_coupon_amount,
        currency, 
        product_code
    from `tabCoupon Transaction` 
    where 
        coupon_code=%(coupon_code)s and  
        transaction_type = "Sale Coupon" and 
        coalesce(status,'') <> 'Deleted'
    limit 1
    """
   
    coupon_info = frappe.db.sql(sql,{"coupon_code":data[0].name},as_dict=1) 
 
    customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Sale",coupon_info[0].get("sale"),["customer_photo","customer_group","phone_number","customer","customer_name"])  
    coupon_info[0]["customer"] = {
        "name":customer,
        "customer_name":customer_name,
        "customer_group":customer_group,
        "phone_number":phone_number,
        "photo":customer_photo
    }

    if coupon_info:
        if coupon_info[0].get("product_code"):
            product_name,photo = frappe.get_cached_value("Product",coupon_info[0].get("product_code"),["product_name_en","photo"]) 
            
            coupon_info[0]["product_name"] = product_name
            coupon_info[0]["photo"] = photo
            
        coupon_info =  coupon_info[0]
    
    # get coupon transaction
    sql = """
        select 
            currency,
            transaction_type,
            markup_percentage,
            sum(input_actual_amount) as input_actual_amount,
            sum(coupon_amount) as coupon_amount 
        from `tabCoupon Transaction` 
        where 
        coupon_code=%(coupon_code)s and 
        coalesce(status,'') <> 'Deleted'
        group by
            currency,
            transaction_type,
            markup_percentage
    """
    data = frappe.db.sql(sql,{"coupon_code":coupon_info.get("coupon_code")},as_dict=1)

    coupon_info["coupon_transaction"] = data
    coupon_info["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    coupon_info["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
    
    return  coupon_info

@frappe.whitelist()
def check_coupon_code_for_redeem(coupon_code):
    if not frappe.db.exists("Coupon Codes",{"coupon":coupon_code}):
        frappe.throw(_("This coupon code does not exist in the system"))

    data = frappe.db.get_list('Coupon Codes', filters={
        'coupon':  coupon_code
    },
    order_by='creation desc',
    page_length=1,
    fields=["name","coupon","coupon_status","expired_date","reference_doctype"]
    )
 
    # validate expiredate
    if not data:
        frappe.throw(_("This coupon code does not exist in the system"))

    if data[0].reference_doctype =="Coupon Issue":
        frappe.throw("គូប៉ុងសម្រាប់បុគ្គលិកមិនអាចដកប្រាក់បានទេ។")

    if data[0].coupon_status =="Unused":
        frappe.throw(_("This coupon number is not a used coupon number"))
    
    if data[0].coupon_status=="Redeemed":
        frappe.throw(_("This coupon code is already redeemed"))
        
    if data[0].coupon_status=="Expired":
        frappe.throw(_("This coupon code is expired"))  



    if data[0].coupon_status=="Used":
        if   datetime.datetime.now() > data[0].expired_date:
            frappe.throw(_("This coupon code is expired"))   
    
    
 

    sql = """select 
        coupon_code,
        coupon_number,transaction_date,sale,posting_date,
        input_actual_amount,
        input_coupon_amount,
        actual_amount,
        currency, 
        product_code
    from `tabCoupon Transaction` 
    where 
        coupon_code=%(coupon_code)s and  
        transaction_type = "Sale Coupon"  and 
        coalesce(status,'') <> 'Deleted'
    limit 1
    """
   
    coupon_info = frappe.db.sql(sql,{"coupon_code":data[0].name},as_dict=1) 
 
    customer_photo,customer_group,phone_number,customer,customer_name = frappe.get_cached_value("Sale",coupon_info[0].get("sale"),["customer_photo","customer_group","phone_number","customer","customer_name"])  
    coupon_info[0]["customer"] = {
        "name":customer,
        "customer_name":customer_name,
        "customer_group":customer_group,
        "phone_number":phone_number,
        "photo":customer_photo
    }

    if coupon_info:
        if coupon_info[0].get("product_code"):
            product_name,photo = frappe.get_cached_value("Product",coupon_info[0].get("product_code"),["product_name_en","photo"]) 
            
            coupon_info[0]["product_name"] = product_name
            coupon_info[0]["photo"] = photo
            
        coupon_info =  coupon_info[0]
    
    # get coupon transaction
    sql = """
        select 
            transaction_type,
            markup_percentage,
            sum(input_actual_amount) as input_actual_amount,
            sum(coupon_amount) as coupon_amount ,
            sum(actual_amount) as actual_amount


        from `tabCoupon Transaction` 
        where 
        coupon_code=%(coupon_code)s and 
        coalesce(status,'') <> 'Deleted'
        group by
            transaction_type,
            markup_percentage
    """
    data = frappe.db.sql(sql,{"coupon_code":coupon_info.get("coupon_code")},as_dict=1)

    coupon_info["coupon_transaction"] = data
    coupon_info["coupon_balance"] = sum([d.get("coupon_amount") for d in data])
    coupon_info["actual_amount_balance"] = get_coupon_actual_amount_balance(data)
  
    coupon_info["used_coupon_value"] = sum([d.get("actual_amount") for d in data if d.get("transaction_type") =="Used"])
    
    return  coupon_info

def get_coupon_actual_amount_balance(coupon_transactions):
    return sum([d.get("coupon_amount") / (1+(d.get("markup_percentage") or 0)/100) for d in coupon_transactions])




@frappe.whitelist(allow_guest=True)
def check_coupon_balance(coupon_code):
    frappe.local.lang = "km"
    sql = "select name, coupon from `tabCoupon Codes` where coupon = %(coupon_code)s order by creation desc limit 1"
    coupon_data = frappe.db.sql(sql,{"coupon_code":coupon_code},as_dict = 1)
    if coupon_data:
        data = get_coupon_detail(coupon_data[0]["name"])
        data["coupon_status_kh"]= _(data["coupon_info"].coupon_status)
        data["coupon_price"]= format_currency(data["coupon_info"].price)
        data["top_up_amount"]= format_currency(data["coupon_info"].top_up_amount)
        data["total_coupon_amount"]= format_currency((data["coupon_info"].price or 0) + (data["coupon_info"].top_up_amount or 0))
        data["redeem_amount"]= format_currency(data["coupon_info"].redeem_amount)
        data["use_amount"]= format_currency(data["coupon_info"].use_amount)
        data["balance_amount"]= format_currency(data["coupon_info"].balance_amount)
        data["sale_date"]= frappe.format(data["coupon_info"].price,{"fieldtype":"Date"})
        data["expired_date"]= frappe.format(data["coupon_info"].expired_date,{"fieldtype":"Datetime"})


        for d in data["coupon_transaction"]:
            d["transaction_type_kh"] = _(d["transaction_type"])
            d["transaction_type"] = d["transaction_type"].replace(" ","")
            d["creation"] = frappe.utils. pretty_date(str(d.get("creation")))
            d["input_actual_amount"] =  format_currency(d.get("input_actual_amount"),d.get("currency"))
            
        # format date and currency
        return data
    return None

def format_currency(value, currency=None):
    if not currency:
        currency = frappe.get_cached_value("ePOS Settings",None,"currency")
        
    precission = frappe.get_cached_value("Currency",currency,"custom_currency_precision")
    return frappe.utils.fmt_money(value,  currency =  currency, precision = precission )

@frappe.whitelist()
def get_store_cashier_shift_info():
    working_day = frappe.db.sql("select posting_date from `tabWorking Day` where is_closed = 0 order by creation desc limit 1",as_dict = 1)
    working_date = frappe.utils.today()
    if working_day:
        working_date = working_day[0].get("posting_date")
    
    sql = """select 
        v.name,
        v.vendor_name,
        cs.name as cashier_shift_number,
        cs.creation,
        cs.is_closed,
        cs.owner
       from `tabVendor` v
       left join `tabCoupon Shift` cs on cs.vendor = v.name and cs.posting_date = %(posting_date)s
         where v.name in (select default_vendor from `tabPOS Profile`)
         
         """
    data = frappe.db.sql(sql,{"posting_date":working_date},as_dict=1)

    return data

@frappe.whitelist()
def update_manager_coupon_status():
    sql = """
        select 
            c.name as coupon_code,
            cs.debit_account as credit_account,
            cs.credit_account as debit_account,
            cs.employee,
            cs.employee_name,
            cs.business_branch,
            cs.expired_date
        from `tabCoupon Codes` c 
        join `tabCoupon Issue` cs on cs.name = c.reference_name
        where 
            c.reference_doctype = 'Coupon Issue' and 
            c.expired_date<=now() and 
            c.coupon_status = 'Used' 
    """
    expired_coupon_codes = frappe.db.sql(sql,as_dict = 1)
    
    if expired_coupon_codes:
        # find coupon balance and debit account and credit account to post to GL
        # we find it in coupon transaction credit and debit account and reverse it
        
        # get all expired coupon code that have balance
        
        sql = """
            select 
                coupon_code,  
                sum(coupon_amount) as balance 
            from `tabCoupon Transaction` 
            where 
                coupon_code in %(coupon_codes)s   and 
                coalesce(status,'') <> 'Deleted'
                group by coupon_code
                having sum(coupon_amount)>0
        """

        balance_data = frappe.db.sql(sql,{"coupon_codes":[d.get("coupon_code") for d in expired_coupon_codes]},as_dict=1)
        
        je_doc = None
        if balance_data:
            # get journal entry doc then submit to gl entry
            # why we post to journal entry because we need voucher type and voucher number in gl entry
            je_doc = get_manager_coupon_balance_journal_entry_doc(expired_coupon_codes,balance_data)
           
            je_doc.flags.ignore_permissions = True
            je_doc.insert(ignore_permissions=1)
            je_doc.submit()


        sql="update `tabCoupon Codes` set coupon_status = 'Expired' where reference_doctype = 'Coupon Issue'  and name in %(coupon_codes)s"
        
        frappe.db.sql(sql,{"coupon_codes":[d.get("coupon_code") for d in expired_coupon_codes]})

    # submit coupon balance to gl entry
        frappe.db.commit()
        return {
            "coupon_codes":[d.get("coupon_code") for d in expired_coupon_codes],
            "coupon_data":expired_coupon_codes,
            "balance_amount":balance_data,
            "journentry":je_doc
        }
        


def get_manager_coupon_balance_journal_entry_doc(coupon_data, balance_data):
    
    docs = []
    # reduce payable account need party employee 
    # we use reverse account here
    # debit account get credit account from coupon issue
    gl_doc={
        "doctype":"Journal Entry",
        "posting_date":coupon_data[0].get("expired_date"),
        "business_branch":coupon_data[0].get("business_branch"),
        "account_entries":[]
    }

    
    debit_accounts = set([
        (
            c.get("debit_account"),
            c.get("employee"),
            c.get("employee_name"),
         )
        for c in coupon_data
    ])
    for dr in debit_accounts:
        coupon_codes = [d.get("coupon_code") for d in coupon_data if d.get("employee") == dr[1] and d.get("debit_account") == dr[0]]
        dr_amount = sum([d.get("balance") for d in balance_data if d.get("coupon_code") in coupon_codes])
        dr_amount = dr_amount or 0
        doc = {
            "account": dr[0],
            "debit":abs(dr_amount),
            "party_type" :"Employee",
            "party" :dr[1], # index 1 in tuple debit account
            "party_name" :  dr[2], # index 2 in tuple debit_account
            "note": "ទឹកប្រាក់សល់គូប៉ុងសម្រាប់អ្នកគ្រប់គ្រង",
         }
        gl_doc["account_entries"].append(doc)
        
        
    # credit account get debit account from coupon issue
    cr_account = set([c.get("credit_account") for c in coupon_data])
  
    for cr in cr_account:
        coupon_codes = [d.get("coupon_code") for d in coupon_data if   d.get("credit_account") == cr]
        
        cr_amount = sum([d.get("balance") for d in balance_data if d.get("coupon_code") in coupon_codes])
        cr_amount = cr_amount or 0
        doc = {
            "account": cr,
            "credit":abs(cr_amount),
            "note": "ទឹកប្រាក់សល់គូប៉ុងសម្រាប់អ្នកគ្រប់គ្រង",
         }
        gl_doc["account_entries"].append(doc)
    return frappe.get_doc(gl_doc)
    


 