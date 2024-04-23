from __future__ import unicode_literals
import frappe

def execute():
    try:
        # Alter the datatype of the column
        frappe.db.sql("""
            ALTER TABLE `tabPOS Receipt Template`
            MODIFY `header_height` INT,
            MODIFY `footer_height` VARCHAR(255),
            MODIFY `item_height` DATE;
        """)
        frappe.db.commit()
        print("Patch applied successfully!")
    except Exception as e:
        print("Error applying patch:", e)