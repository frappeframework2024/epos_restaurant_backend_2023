import frappe
from frappe import auth

@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }

        return

    api_generate = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "api_secret":api_generate,
        "username":user.username,
        "email":user.email
    }



def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret



@frappe.whitelist()
def test_me():
    product_code = 'BIFO-PGXB-12,Prouctcode2,product_code3'

    sql = """
        WITH RECURSIVE split AS (
            SELECT
                CAST(SUBSTRING_INDEX(%(product_code)s, ',', 1) AS CHAR(255)) AS value,
                CAST(
                    SUBSTRING(
                        %(product_code)s,
                        LENGTH(SUBSTRING_INDEX(%(product_code)s, ',', 1)) + 2
                    ) AS CHAR(1000)
                ) AS remaining

            UNION ALL

            SELECT
                CAST(SUBSTRING_INDEX(remaining, ',', 1) AS CHAR(255)),
                CAST(
                    SUBSTRING(
                        remaining,
                        LENGTH(SUBSTRING_INDEX(remaining, ',', 1)) + 2
                    ) AS CHAR(1000)
                )
            FROM split
            WHERE remaining <> ''
        )
        SELECT a.value as ori_code, p.name as targe_code,p.product_name_en FROM split a left join `tabProduct` p on a.value   COLLATE utf8mb4_unicode_ci = p.name 
        where
         p.name is null

    """

    return frappe.db.sql(
        sql,
        {"product_code": product_code},
        as_dict=True
    )