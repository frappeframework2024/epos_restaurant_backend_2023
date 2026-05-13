import pymysql
import frappe
import os
import importlib.util


STATEMENTS_DIR = os.path.join(os.path.dirname(__file__), "statements")
@frappe.whitelist()
def execute():
    sql_statements = []
    store_procedure_names = []

    # Loop through all Python files in /statements
    for file_name in os.listdir(STATEMENTS_DIR):
        if file_name.endswith(".py"):
            file_path = os.path.join(STATEMENTS_DIR, file_name)

            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(file_name[:-3], file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Expect each file to have a variable `SQL`
            if hasattr(module, "SQL"):
                store_procedure_name = get_proc_name(module.SQL)
                sql_statements.append(f"DROP PROCEDURE IF EXISTS {store_procedure_name};")
                sql_statements.append(module.SQL)
                
                store_procedure_names.append(store_procedure_name)
            else:
                frappe.logger().warning(f"No SQL found in {file_name}")

    execute_multiple_statements(sql_statements)
    
    return store_procedure_names


def get_proc_name(sql):
    import re
    """Extract procedure name from SQL text (simple parser)."""
    # for line in sql.splitlines():
    #     line = line.strip().lower()
    #     if line.startswith("create procedure") or line.startswith("delimiter"):
            
    #         return line.split()[2].split("(")[0]
    # return "unknown_procedure"
    
    match = re.search(
        r'create\s+procedure\s+`?([a-zA-Z0-9_]+)`?',
        sql,
        re.IGNORECASE
    )
    
    sp_name = match.group(1) if match else "unknown_procedure"
    return sp_name


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
        
        
        frappe.logger().info("✅ All stored procedures created successfully.")
         

    except Exception as e:
        frappe.log_error(f"Error executing multiple statements: {str(e)}", "SQL Execution Error")
        frappe.throw(f"Failed to execute SQL statements: {str(e)}")
        
