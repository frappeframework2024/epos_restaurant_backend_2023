import pymysql
import frappe

# ar
def execute_multiple_statements(sql_statements):    
    try:
        # Get DB credentials from Frappe
        db_config = frappe.conf
        connection = pymysql.connect(
            host=db_config.db_host or "127.0.0.1",
            user=db_config.db_name,
            password=db_config.db_password,
            database=db_config.db_name,
            autocommit=True  # Required for executing DDL statements
        )

        with connection.cursor() as cursor:
            for statement in sql_statements:
                cursor.execute(statement)
        connection.close()
        frappe.msgprint("Stored Procedure Created Successfully")

    except Exception as e:
        frappe.log_error(f"Error executing multiple statements: {str(e)}", "SQL Execution Error")
        frappe.throw(f"Failed to execute SQL statements: {str(e)}")
