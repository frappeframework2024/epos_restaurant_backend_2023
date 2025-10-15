import frappe
 
from epos_restaurant_2023.api.coupon_transaction_backup_db import backup_table

@frappe.whitelist()
def test_archive():
    archive_transactions()




@frappe.whitelist(methods="POST")
def archive_transactions():
    # validate working day 
    # we we can run this only all working day is closed
    if frappe.db.exists("Working Day",{"is_closed":0}):
        frappe.throw("Please close all working day first.")
    # coupon transactions
    archive_coupon_transaction()
    # coupoon codes 
    archive_coupon_codes()

@frappe.whitelist()
def archive_coupon_transaction():
    if  compare_doctype_schema("Coupon Transaction","Coupon Transaction History" ):
        # insert query must be look like this
        # query_look_like = """
        # insert into `tabCoupon Transaction History`  (name,....)
        # select ct.name, ct..... from `tabCoupon Transaction` ct
        # left join `tabCoupon Transaction History` cth on cth.name = ct.name
        # where  
        #     cth.name is null
        # """

        insert_qery =  generate_insert_query("Coupon Transaction","Coupon Transaction History",from_doctype_alias="ct")
        # add skip query 
        insert_qery = insert_qery + " left join `tabCoupon Transaction History` cth on cth.name = ct.name where cth.name is null"
        # frappe.throw(insert_qery)
        frappe.db.sql(insert_qery)

        frappe.db.commit()


@frappe.whitelist(methods="POST")
def delete_archive_transaction():
        # validate working day 
    # we we can run this only all working day is closed
    if frappe.db.exists("Working Day",{"is_closed":0}):
        frappe.throw("Please close all working day first.")

    delete_archive_coupon_transaction()
    delete_archive_coupon_codes()



def delete_archive_coupon_transaction():
    backup_table("tabCoupon Transaction")

    sql = """DELETE ct
            FROM `tabCoupon Transaction` AS ct
                JOIN `tabCoupon Transaction History` AS cth ON cth.name = ct.name
    """
    # find skip deleted record
    skip_delete_record_data = frappe.db.sql("""
        select name from `tabCoupon Transaction` ct
        where 
            ct.coupon_code in (
                select 
                    x.coupon_code 
                from `tabCoupon Transaction` x 
                    join `tabCoupon Codes` cc on cc.name = x.coupon_code 

                where 
                    x.transaction_type = 'Coupon Issue' and 
                    cc.coupon_status = 'Used'

            )
    """,as_dict = 1)

    # manager coupon will delete from transaction table after coupon expired
    if skip_delete_record_data:
        sql = sql + " where ct.name not in %(skip_transactions)s"
        frappe.db.sql(sql,{"skip_transactions":[d.get("name") for d in skip_delete_record_data]})
    else:
        frappe.db.sql(sql)
    frappe.db.commit()



@frappe.whitelist()
def archive_coupon_codes():
     
    if  compare_doctype_schema("Coupon Codes","Coupon Codes History" ):
        # insert query must be look like this
        # query_look_like = """
        # insert into `tabCoupon Codes History`  (name,....)
        # select ct.name, ct..... from `tabCoupon Codes` cc
        # left join `tabCoupon Codes History` cch on cch.name = cc.name
        # where  
        #     cch.name is null and 
        #      cc.coupon_status <> 'Unused'
        # """

        insert_qery =  generate_insert_query("Coupon Codes","Coupon Codes History",from_doctype_alias="cc")
        # add skip query 
        insert_qery = insert_qery + """
             left join `tabCoupon Codes History` cch on cch.name = cc.name 
             where 
                cch.name is null  and
                cc.coupon_status <> 'Unused'"""
 

        # frappe.throw(insert_qery)
        frappe.db.sql(insert_qery)



        # update coupon issue use amount and status to coupon history bedore deleted
        # update coupon use amount before delete 
        sql = """
                UPDATE `tabCoupon Codes History` cch
                    JOIN `tabCoupon Codes` cc ON cc.name = cch.name
                SET 
                    cch.use_amount = cc.use_amount,
                    cch.use_coupon_value = cc.use_coupon_value,
                    cch.top_up_amount = cc.top_up_amount,
                    cch.top_up_coupon_value = cc.top_up_coupon_value,
                    cch.redeem_amount = cc.redeem_amount,
                    cch.redeem_coupon_value = cc.redeem_coupon_value,
                    cch.balance_amount = cc.balance_amount,
                    cch.coupon_status = cc.coupon_status
                WHERE
                    cc.reference_doctype = 'Coupon Issue';
        """
        frappe.db.sql(sql)
        

        frappe.db.commit()


def delete_archive_coupon_codes():
    backup_table("tabCoupon Codes")


    


    sql = """DELETE cc
            FROM `tabCoupon Codes` AS cc
                JOIN `tabCoupon Codes History` AS cch ON cch.name = cc.name
            where
                cc.coupon_status <> 'Unused'
            
    """
    
    # skip record for coupon manager by check coupon that still exists in coupon transaction
    skip_delete_record_data = frappe.db.sql("""
        select distinct coupon_code from `tabCoupon Transaction`
    """,as_dict =1)

    # manager coupon will delete from transaction table after coupon expired
    if skip_delete_record_data:
        sql = sql + "  and cc.name not in %(skip_coupon_codes)s"
        frappe.db.sql(sql,{"skip_coupon_codes":[d.get("coupon_code") for d in skip_delete_record_data]})
    else:
        frappe.db.sql(sql)
    frappe.db.commit()
    




        




        
        


 
@frappe.whitelist()
def generate_insert_query(from_doctype: str, to_doctype: str,from_doctype_alias= None) -> str:
    """
    Generate an SQL insert query:
    INSERT INTO `tabToDoctype` (fields...)
    SELECT fields... FROM `tabFromDoctype`
    Ignores layout-only fields and only includes matching fieldnames.
    """

    IGNORE_TYPES = {"Tab Break", "Column Break", "Section Break"}
    INCLUDE_FIELDS =["name","creation","modified","docstatus","owner","modified_by"]

    def get_field_dict(doctype_name):
        meta = frappe.get_meta(doctype_name)
        return {
            f.fieldname: f.fieldtype
            for f in meta.fields
            if f.fieldname and not f.fieldname.startswith("_") and f.fieldtype not in IGNORE_TYPES
        }

    # Get fields
    from_fields = get_field_dict(from_doctype)
    to_fields = get_field_dict(to_doctype)

    # Keep only matching fields (by fieldname)
    common_fields = [f for f in from_fields if f in to_fields]

    if not common_fields:
        frappe.throw("No matching fields found between the two DocTypes.")
    common_fields =  INCLUDE_FIELDS + common_fields
    # Generate SQL query
    insert_fields_str = ", ".join(f"`{f}`"   for f in common_fields)
    select_fields_str = ", ".join(f"`{f}`" if not from_doctype_alias else f"{from_doctype_alias}.`{f}`"  for f in common_fields)
    query = (
        f"INSERT INTO `tab{to_doctype}` ({insert_fields_str}) "
        f"SELECT {select_fields_str} FROM `tab{from_doctype}` {from_doctype_alias or ''}"
    )

    return query

@frappe.whitelist()
def compare_doctype_schema(doctype1: str, doctype2: str) -> bool:
    """
    Compare two Frappe DocTypes by fieldname and fieldtype.
    Skips layout-only fields (Tab Break, Column Break, Section Break).
    Returns True if both have identical schema (fieldnames & datatypes).
    """

    IGNORE_TYPES = {"Tab Break", "Column Break", "Section Break"}

    def get_schema(doctype_name):
        """Fetch fields as {fieldname: fieldtype} dict, ignoring system & layout fields."""
        meta = frappe.get_meta(doctype_name)
        return {
            f.fieldname: f.fieldtype
            for f in meta.fields
            if f.fieldname and not f.fieldname.startswith("_") and f.fieldtype not in IGNORE_TYPES
        }

    # Get both schemas
    schema1 = get_schema(doctype1)
    schema2 = get_schema(doctype2)

    # Compare
    if schema1 == schema2:
        return True
    else:
        # Find differences
        diff1 = {k: schema1[k] for k in schema1 if k not in schema2 or schema2[k] != schema1[k]}
        diff2 = {k: schema2[k] for k in schema2 if k not in schema1 or schema1[k] != schema2[k]}

        frappe.msgprint(
            f"❌ Schema mismatch detected:\n\n"
            f"Fields only in {doctype1} or with different type:\n{diff1}\n\n"
            f"Fields only in {doctype2} or with different type:\n{diff2}"
        )
        return False
