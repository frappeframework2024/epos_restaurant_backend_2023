import frappe

def execute():
    # Add a new column to an existing table

    query = """
    DROP PROCEDURE IF EXISTS sp_get_account_ar_aging_report;

    DELIMITER $$
    CREATE PROCEDURE sp_get_account_ar_aging_report(
            IN customer VARCHAR(255),  -- Input parameter for customer search
            IN end_date DATE,          -- Input parameter for the end date
            IN property VARCHAR(255)   -- Input parameter for the property
        )
        BEGIN
            -- The query you want to execute
            SELECT 
                c.name,
                c.customer_name_en,
                c.phone_number,
                IF(a.posting_date = DATE(end_date), SUM(a.debit_amount - a.credit_amount), 0) AS current,
                IF(DATEDIFF(NOW(), a.posting_date) BETWEEN 1 AND 30, SUM(a.debit_amount - a.credit_amount), 0) AS balance_30_day,
                IF(DATEDIFF(NOW(), a.posting_date) BETWEEN 31 AND 60, SUM(a.debit_amount - a.credit_amount), 0) AS balance_60_day,
                IF(DATEDIFF(NOW(), a.posting_date) BETWEEN 61 AND 90, SUM(a.debit_amount - a.credit_amount), 0) AS balance_90_day,
                IF(DATEDIFF(NOW(), a.posting_date) > 90, SUM(a.debit_amount - a.credit_amount), 0) AS balance_over_90        
            FROM `tabGeneral Ledger` a
            INNER JOIN `tabChart Of Account` b ON b.name = a.account
            INNER JOIN `tabCustomer` c ON c.name = a.party
            WHERE b.account_type = 'Receivable'
            AND a.party_type = 'Customer'
            AND a.business_branch = property  
            AND a.posting_date <= DATE(end_date)
            AND CONCAT(c.name, COALESCE(c.customer_name_en, ''), COALESCE(c.phone_number, '')) 
                LIKE CONCAT('%', customer, '%')
            GROUP BY c.name, c.customer_name_en, c.phone_number;
        END $$
    DELIMITER ;"""
    frappe.db.sql(query)

    # Commit the change
    frappe.db.commit()