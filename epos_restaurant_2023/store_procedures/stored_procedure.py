# create_stored_procedure.py

import frappe


def execute():
    sp_get_account_ar_aging_report()

def sp_get_account_ar_aging_report():
    # Define the stored procedure
    stored_procedure = """
    DELIMITER $$
    DROP PROCEDURE IF EXISTS sp_get_account_ar_aging_report;

    CREATE PROCEDURE sp_get_account_ar_aging_report(
        IN p_customer VARCHAR(255),  -- Input parameter for customer search
        IN p_end_date DATE,          -- Input parameter for the end date
        IN p_property VARCHAR(255)   -- Input parameter for the property
    )
    BEGIN
        -- Declare the temporary variables and set the default values
        DECLARE customer VARCHAR(255);
        DECLARE end_date DATE;
        DECLARE property VARCHAR(255);
        
        -- Set the values from input parameters
        SET customer = p_customer;
        SET end_date = p_end_date;
        SET property = p_property;

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
        AND a.business_branch = property COLLATE utf8mb4_unicode_ci 
        AND a.posting_date <= DATE(end_date)
        AND CONCAT(c.name, COALESCE(c.customer_name_en, ''), COALESCE(c.phone_number, '')) 
            LIKE CONCAT('%', customer COLLATE utf8mb4_unicode_ci, '%')
        GROUP BY c.name, c.customer_name_en, c.phone_number;

    END $$

    DELIMITER ;
    """

    # Run the stored procedure query via Frappe's database connection
    frappe.db.sql(stored_procedure)
