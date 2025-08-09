import pymysql
import frappe
def execute_multiple_statements():
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
            # Example: Executing multiple statements
            sql_statements = [
                "DROP PROCEDURE IF EXISTS sp_generate_flash_manager_report;",
                
                """
CREATE   PROCEDURE `sp_generate_flash_manager_report`( IN v_property varchar(100), IN v_posting_date DATE  )
BEGIN
		DECLARE v_mtd_start_date DATE;
		DECLARE v_ytd_start_date DATE;
		DECLARE  v_today_paid_rooms DECIMAL(18,9) default 0;
		DECLARE  v_mtd_paid_rooms DECIMAL(18,9) default 0;
		DECLARE  v_ytd_paid_rooms DECIMAL(18,9) default 0;
		
		DECLARE  v_today_comp_rooms DECIMAL(18,9) default 0;
		DECLARE  v_mtd_comp_rooms DECIMAL(18,9) default 0;
		DECLARE  v_ytd_comp_rooms DECIMAL(18,9) default 0;
		
		DECLARE  v_today_house_use_rooms DECIMAL(18,9) default 0;
		DECLARE  v_mtd_house_use_rooms DECIMAL(18,9) default 0;
		DECLARE  v_ytd_house_use_rooms DECIMAL(18,9) default 0;
		
		DECLARE  v_today_room_block DECIMAL(18,9) default 0;
		DECLARE  v_mtd_room_block DECIMAL(18,9) default 0;
		DECLARE  v_ytd_room_block DECIMAL(18,9) default 0;
		
		DECLARE  v_today_total_rooms DECIMAL(18,9) default 0;
		DECLARE  v_mtd_total_rooms DECIMAL(18,9) default 0;
		DECLARE  v_ytd_total_rooms DECIMAL(18,9) default 0;
		
		
	  IF v_property IS NULL THEN
        SET v_property = 'Angkor Century Resort & Spa';
    END IF;

    IF v_posting_date IS NULL THEN
        SET v_posting_date = '2025-08-07'; -- or any default date
    END IF;
		
		SET v_mtd_start_date = DATE_FORMAT(date(v_posting_date), '%Y-%m-01');
		SET v_ytd_start_date = DATE_FORMAT(date(v_posting_date), '%Y-%m-01');
		
		delete from `tabManager Flash Report Data` where posting_date = v_posting_date and property = v_property;
		

		insert into `tabManager Flash Report Data` (name, posting_date,property, title,idx,`group`)
		select UUID(), v_posting_date, v_property, name,sort_order,`group` from `tabFlash Report Key`;
				
				
				-- update today total
				UPDATE `tabManager Flash Report Data` t
				JOIN (
						SELECT 
								frk.`group`,
								ft.flash_report_revenue_group,
								SUM(ft.amount) AS total
						FROM `tabFolio Transaction` ft
						JOIN `tabFlash Report Key` frk
								ON ft.flash_report_revenue_group = frk.name
						WHERE
								ft.posting_date = v_posting_date
								AND ft.property = v_property
						GROUP BY
								frk.`group`,
								ft.flash_report_revenue_group
				) b  
						ON b.flash_report_revenue_group = t.title and b.`group` = t.`group`
				SET
						t.today_total = b.total
				WHERE
						t.property = v_property
						AND t.posting_date = v_posting_date;
					
				-- update mtd total
				UPDATE `tabManager Flash Report Data` t
				JOIN (
						SELECT 
								frk.`group`,
								ft.flash_report_revenue_group,
								SUM(ft.amount) AS total
						FROM `tabFolio Transaction` ft
						JOIN `tabFlash Report Key` frk
								ON ft.flash_report_revenue_group = frk.name
						WHERE
								ft.posting_date between v_mtd_start_date and  v_posting_date
								AND ft.property = v_property
						GROUP BY
								frk.`group`,
								ft.flash_report_revenue_group
				) b  
						ON b.flash_report_revenue_group = t.title and b.`group` = t.`group`
				SET
						t.mtd_total = b.total
				WHERE
						t.property = v_property
						AND t.posting_date between v_mtd_start_date and  v_posting_date;
						
				-- update ytd total
				UPDATE `tabManager Flash Report Data` t
				JOIN (
						SELECT 
								frk.`group`,
								ft.flash_report_revenue_group,
								SUM(ft.amount) AS total
						FROM `tabFolio Transaction` ft
						JOIN `tabFlash Report Key` frk
								ON ft.flash_report_revenue_group = frk.name
						WHERE
								ft.posting_date between v_ytd_start_date and  v_posting_date
								AND ft.property = v_property
						GROUP BY
								frk.`group`,
								ft.flash_report_revenue_group
				) b  
						ON b.flash_report_revenue_group = t.title and b.`group` = t.`group`
				SET
						t.ytd_total = b.total
				WHERE
						t.property = v_property
						AND t.posting_date between v_ytd_start_date and  v_posting_date;
						 	 
		
		
		
		-- ******************************* Occupancy ***********************************

		SET v_today_paid_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 0 and is_complimentary = 0 and property = v_property and date = v_posting_date);
		SET v_mtd_paid_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 0 and is_complimentary = 0 and property = v_property and date between v_mtd_start_date  and v_posting_date);
		SET v_ytd_paid_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 0 and is_complimentary = 0 and property = v_property and date between v_ytd_start_date  and v_posting_date);
		
		-- update Paid Room  to databases
		update `tabManager Flash Report Data` set today_total = v_today_paid_rooms, mtd_total = v_mtd_paid_rooms, ytd_total = v_ytd_paid_rooms where posting_date = v_posting_date and property = v_property and title = 'Paid Rooms' and `group` = 'Occupancy';
		
		-- Total Complimentary room 
		SET v_today_comp_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 0 and is_complimentary = 1 and property = v_property and date = v_posting_date);
		SET v_mtd_comp_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 0 and is_complimentary = 1 and property = v_property and date between v_mtd_start_date  and v_posting_date);
		SET v_ytd_comp_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 0 and is_complimentary = 1 and property = v_property and date between v_ytd_start_date  and v_posting_date);
		
		-- update Comp Rooms  to databases
		update `tabManager Flash Report Data` set today_total = v_today_comp_rooms, mtd_total = v_mtd_comp_rooms, ytd_total = v_ytd_comp_rooms where posting_date = v_posting_date and property = v_property and title = 'Comp Rooms' and `group` = 'Occupancy';
		
		-- Total House Use Rooms 
		SET v_today_house_use_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 1 and is_complimentary = 0 and property = v_property and date = v_posting_date);
		SET v_mtd_house_use_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 1 and is_complimentary = 0 and property = v_property and date between v_mtd_start_date  and v_posting_date);
		SET v_ytd_house_use_rooms = (select count(*) from `tabRoom Occupy` where type='Reservation' and  is_active = 1 and is_house_use = 1 and is_complimentary = 0 and property = v_property and date between v_ytd_start_date  and v_posting_date);
		
		-- update Comp Rooms  to databases
		update `tabManager Flash Report Data` set today_total = v_today_house_use_rooms, mtd_total = v_mtd_house_use_rooms, ytd_total = v_ytd_house_use_rooms where posting_date = v_posting_date and property = v_property and title = 'House Use Rooms' and `group` = 'Occupancy';
		
	-- Total Room Block
		SET v_today_room_block= (select count(*) from `tabRoom Occupy` where type='Block' and  is_active = 1   and property = v_property and date = v_posting_date);
		SET v_mtd_room_block = (select count(*) from `tabRoom Occupy` where type='Block' and  is_active = 1  and property = v_property and date between v_mtd_start_date  and v_posting_date);
		SET v_ytd_room_block = (select count(*) from `tabRoom Occupy` where type='Block' and  is_active = 1   and property = v_property and date between v_ytd_start_date  and v_posting_date);
		
		-- update Comp Rooms  to databases
		update `tabManager Flash Report Data` set today_total = v_today_room_block, mtd_total = v_mtd_room_block, ytd_total = v_ytd_room_block where posting_date = v_posting_date and property = v_property and title = 'Out of Order Rooms' and `group` = 'Occupancy';
		
		
		-- total Rooms get data from daily property data
			-- Total Room 
		SET v_today_total_rooms = (select sum(total_room) from `tabDaily Property Data` where  property = v_property and date = v_posting_date);
		SET v_mtd_total_rooms = (select sum(total_room) from `tabDaily Property Data` where  property = v_property and date between v_mtd_start_date and  v_posting_date);
		SET v_ytd_total_rooms = (select sum(total_room) from `tabDaily Property Data` where  property = v_property and date between v_ytd_start_date and  v_posting_date);
		
		-- update Comp Rooms  to databases
		update `tabManager Flash Report Data` 
		set 
			today_total = v_today_total_rooms - (v_today_paid_rooms + v_today_comp_rooms + v_today_house_use_rooms + v_today_room_block), 
			mtd_total = v_mtd_total_rooms - (v_mtd_paid_rooms + v_mtd_comp_rooms + v_mtd_house_use_rooms + v_mtd_room_block),
			ytd_total = v_ytd_total_rooms - (v_ytd_paid_rooms + v_ytd_comp_rooms + v_ytd_house_use_rooms + v_ytd_room_block)
		where posting_date = v_posting_date and property = v_property and title = 'Vacant Rooms' and `group` = 'Occupancy';
		
		
		-- update to % of Total Occupancy 
		update `tabManager Flash Report Data` 
		set 
			today_total = (v_today_paid_rooms + v_today_comp_rooms + v_today_house_use_rooms)/ v_today_total_rooms * 100, 
			mtd_total = (v_mtd_paid_rooms + v_mtd_comp_rooms + v_mtd_house_use_rooms) / v_mtd_total_rooms * 100,
			ytd_total =  (v_ytd_paid_rooms + v_ytd_comp_rooms + v_ytd_house_use_rooms) / v_ytd_total_rooms * 100
		where posting_date = v_posting_date and property = v_property and title = '% of Total Occupancy' and `group` = 'ADR and Occupancy';
		
		
		
 
		
			select * from `tabManager Flash Report Data`  ;
END;
"""
            ]

            # Execute each statement separately
            for statement in sql_statements:
                cursor.execute(statement)

        connection.close()
        frappe.msgprint("Stored Procedure Created Successfully")

    except Exception as e:
        frappe.log_error(f"Error executing multiple statements: {str(e)}", "SQL Execution Error")
        frappe.throw(f"Failed to execute SQL statements: {str(e)}")
