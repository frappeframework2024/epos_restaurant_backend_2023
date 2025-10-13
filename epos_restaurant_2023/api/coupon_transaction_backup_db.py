import frappe
from frappe.database.mariadb.database import MariaDBDatabase

def get_conn():
    return MariaDBDatabase(
        user=frappe.conf.get("root_login") or "root",
        password=frappe.conf.get("root_password"),
        host=frappe.conf.get("db_host") or "localhost",
        port=frappe.conf.get("db_port") or 3306,
        
    )
@frappe.whitelist()
def create_backup_db():
    conn=get_conn()

    result = conn.sql(f"SHOW DATABASES like 'coupon_transaction_backup_db';")
    if len(result) == 0:
        conn.sql(f"CREATE DATABASE `coupon_transaction_backup_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")


@frappe.whitelist()
def backup_table(table_name):
    conn=get_conn()
    # coupon transaction
    site_config = frappe.get_site_config()
    db_name = site_config.get("db_name")
    conn.sql(f"use {db_name};")
    create_backup_db()
    from datetime import datetime
    now = datetime.now()
    formatted_date = now.strftime("%Y_%m_%d_%H_%M")

    sql = """
        CREATE TABLE `coupon_transaction_backup_db`.`{table_name}__{date}` AS
        SELECT *
        FROM `{db_name}`.`{table_name}`; 
    """.format(date=formatted_date,db_name = db_name,table_name=table_name)
    
    conn.sql(sql)


@frappe.whitelist(methods="POST")
def delete_last_30_days_data():
    conn=get_conn()
    # coupon transaction
    site_config = frappe.get_site_config()
    conn.sql(f"use `coupon_transaction_backup_db`;")
    table_data = conn.sql("select table_name from information_schema.tables where table_schema = 'coupon_transaction_backup_db' and create_time <=DATE_SUB(NOW(), INTERVAL 30 SECOND);")
    
    for d in table_data:
        conn.sql(f"drop table `{d[0]}`;")
    
    return True
