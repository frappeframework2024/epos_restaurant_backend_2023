SQL = """CREATE   PROCEDURE `sp_generate_flash_manager_report`( IN v_property varchar(100), IN v_posting_date DATE  )
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
		
		
		DECLARE  v_today_room_revenue DECIMAL(18,9) default 0;
		DECLARE  v_mtd_room_revenue  DECIMAL(18,9) default 0;
		DECLARE  v_ytd_room_revenue   DECIMAL(18,9) default 0;
		
		
		DECLARE  v_today_group_room_revenue DECIMAL(18,9) default 0;
		DECLARE  v_mtd_group_room_revenue  DECIMAL(18,9) default 0;
		DECLARE  v_ytd_group_room_revenue   DECIMAL(18,9) default 0;
		
		
		
		
		
		-- this is temp variable and can be use multiple time
		DECLARE  v_today_total DECIMAL(18,9) default 0;
		DECLARE  v_mtd_total DECIMAL(18,9) default 0;
		DECLARE  v_ytd_total  DECIMAL(18,9) default 0;
		
		
		
		
	  IF v_property IS NULL THEN
        SET v_property = 'Angkor Century Resort & Spa';
    END IF;

    IF v_posting_date IS NULL THEN
        SET v_posting_date = '2025-08-07'; -- or any default date
    END IF;
		
		SET v_mtd_start_date = DATE_FORMAT(date(v_posting_date), '%Y-%m-01');
		SET v_ytd_start_date = DATE_FORMAT(date(v_posting_date), '%Y-%01-01');
		
		delete from `tabManager Flash Report Data` where posting_date = v_posting_date and property = v_property;
		

		insert into `tabManager Flash Report Data` (name, posting_date,property, title,idx,`group`)
		select UUID(), v_posting_date, v_property, name,sort_order,`group` from `tabFlash Report Key`;
				
				
				-- update today total
				UPDATE `tabManager Flash Report Data` t
				JOIN (
						SELECT 
								frk.`group`,
								ft.flash_report_revenue_group,
								SUM(ft.amount * if(type='Debit',1,-1)) AS total
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
								SUM(ft.amount * if(type='Debit',1,-1)) AS total
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
								SUM(ft.amount * if(type='Debit',1,-1)) AS total 
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
			today_total = (v_today_paid_rooms + v_today_comp_rooms + v_today_house_use_rooms)/ NULLIF(v_today_total_rooms,0) * 100, 
			mtd_total = (v_mtd_paid_rooms + v_mtd_comp_rooms + v_mtd_house_use_rooms) / NULLIF(v_mtd_total_rooms,0) * 100,
			ytd_total =  (v_ytd_paid_rooms + v_ytd_comp_rooms + v_ytd_house_use_rooms) / NULLIF(v_ytd_total_rooms,0) * 100
		where posting_date = v_posting_date and property = v_property and title = '% of Total Occupancy' and `group` = 'ADR and Occupancy';
		
		-- Average Rate of  Total Occupancy 
		select sum(today_total), sum(mtd_total), sum(ytd_total)
		into v_today_room_revenue, v_mtd_room_revenue, v_ytd_room_revenue
		from `tabManager Flash Report Data` 
		WHERE
			posting_date = v_posting_date and 
			property = v_property and
			`group` = 'Room Revenue'
		limit 1;
		
		
		
		update `tabManager Flash Report Data`  set 
			today_total = coalesce(v_today_room_revenue /  NULLIF((v_today_paid_rooms + v_today_comp_rooms + v_today_house_use_rooms),0),0),
			mtd_total =coalesce(v_mtd_room_revenue /  NULLIF((v_mtd_paid_rooms + v_mtd_comp_rooms + v_mtd_house_use_rooms),0),0),
			ytd_total =coalesce(v_ytd_room_revenue /  NULLIF((v_ytd_paid_rooms + v_ytd_comp_rooms + v_ytd_house_use_rooms),0),0)
		where posting_date = v_posting_date and property = v_property and title = 'Average Rate of Total Occupancy' and `group` = 'ADR and Occupancy';
		
		-- update to % of Paid Occupancy 
		update `tabManager Flash Report Data` 
		set 
			today_total = v_today_paid_rooms/ NULLIF(v_today_total_rooms,0) * 100, 
			mtd_total = v_mtd_paid_rooms / NULLIF(v_mtd_total_rooms,0) * 100,
			ytd_total =  v_ytd_paid_rooms  / NULLIF(v_ytd_total_rooms,0) * 100
		where posting_date = v_posting_date and property = v_property and title = '% of Paid Occupancy' and `group` = 'ADR and Occupancy';
		
		
		-- Average Rate of Total Paid Room 
		update `tabManager Flash Report Data`  set 
			today_total = coalesce(v_today_room_revenue /  NULLIF(v_today_paid_rooms,0),0),
			mtd_total =coalesce(v_mtd_room_revenue /  NULLIF(v_mtd_paid_rooms,0) ,0),
			ytd_total =coalesce(v_ytd_room_revenue /  NULLIF(v_ytd_paid_rooms,0) ,0)
		where posting_date = v_posting_date and property = v_property and title = 'Average Rate of Paid Room' and `group` = 'ADR and Occupancy';
		
		
-- Total Group Occupancy
	SET v_today_total = (select count(*) from `tabRoom Occupy` where property = v_property and date = v_posting_date and is_active = 1 and is_active_reservation = 1 and type='Reservation' and reservation_type = 'GIT' );
	SET v_mtd_total = (select count(*) from `tabRoom Occupy` where property = v_property and date between v_mtd_start_date and v_posting_date and is_active = 1 and is_active_reservation = 1 and type='Reservation' and reservation_type = 'GIT' );
	SET v_ytd_total = (select count(*) from `tabRoom Occupy` where property = v_property and date between v_ytd_start_date and v_posting_date and is_active = 1 and is_active_reservation = 1 and type='Reservation' and reservation_type = 'GIT' );
	
	update `tabManager Flash Report Data` set today_total = coalesce(v_today_total,0), mtd_total = coalesce(v_mtd_total,0), ytd_total = COALESCE(v_ytd_total,0) 
	where property = v_property and posting_date = v_posting_date and title = 'Group Rooms'; 
	

	-- total % of group occupancy
	update `tabManager Flash Report Data` 
	set 
			today_total = coalesce(v_today_total / NULLIF(v_today_total_rooms,0),0) * 100 , 
			mtd_total = coalesce(v_mtd_total / NULLIF(v_mtd_total_rooms,0),0) * 100 , 
			ytd_total = coalesce(v_ytd_total / NULLIF(v_ytd_total_rooms,0),0) * 100 
	where property = v_property and posting_date = v_posting_date and title = '% of Total Group Occupancy'; 
	
	-- total group room ADR
	-- get total room revenue for group reservation 
	SET v_today_group_room_revenue = (select sum(amount*if(type='Debit',1,-1))  from `tabFolio Transaction` where property = v_property and  posting_date = v_posting_date and parent_account_name = 'Room Charge' and reservation_type = 'GIT');
	SET v_mtd_group_room_revenue = (select sum(amount*if(type='Debit',1,-1))  from `tabFolio Transaction` where property = v_property and  posting_date between v_mtd_start_date and v_posting_date and parent_account_name = 'Room Charge' and reservation_type = 'GIT');
	
	SET v_ytd_group_room_revenue = (select sum(amount*if(type='Debit',1,-1))  from `tabFolio Transaction` where property = v_property and  posting_date between v_ytd_start_date and v_posting_date and parent_account_name = 'Room Charge' and reservation_type = 'GIT');
	
	-- update to group ADR
	update `tabManager Flash Report Data` 
	SET 
		today_total =coalesce( v_today_group_room_revenue / NULLIF(v_today_total,0),0),
		mtd_total =coalesce( v_mtd_group_room_revenue / NULLIF(v_mtd_total,0),0),
		ytd_total =coalesce( v_ytd_group_room_revenue / NULLIF(v_ytd_total,0),0)
	WHERE	
		property = v_property and posting_date = v_posting_date and title = 'Average Rate of Group Occupancy';
		
	
	
		
 -- ********************* Other Occupancy Total *********************************************
 -- Total Departure
		SET v_today_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date = v_posting_date and is_active_reservation=1 and is_departure = 1);
		SET v_mtd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_mtd_start_date and v_posting_date and is_active_reservation=1 and is_departure = 1);
		SET v_ytd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between  v_ytd_start_date and v_posting_date  and is_active_reservation=1 and is_departure = 1);
		
		update `tabManager Flash Report Data` SET today_total = v_today_total, mtd_total = v_mtd_total, ytd_total = v_ytd_total 
		where posting_date = v_posting_date and property = v_property and title = 'Departures';
		
 -- Total Arrival Guest
		SET v_today_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date = v_posting_date and is_active=1 and is_arrival = 1);
		SET v_mtd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_mtd_start_date and v_posting_date  and is_arrival=1 );
		SET v_ytd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_ytd_start_date  and v_posting_date and is_arrival=1 );
		
		update `tabManager Flash Report Data` SET today_total = v_today_total, mtd_total = v_mtd_total, ytd_total = v_ytd_total 
		where posting_date = v_posting_date and property = v_property and title = 'Arrivals';
		
		
 -- Total Walk In Guest  
		SET v_today_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date = v_posting_date and is_active=1 and is_walk_in = 1);
		SET v_mtd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_mtd_start_date and v_posting_date  and is_walk_in=1 );
		SET v_ytd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_ytd_start_date  and v_posting_date and is_walk_in=1 );
		
		update `tabManager Flash Report Data` SET today_total = v_today_total, mtd_total = v_mtd_total, ytd_total = v_ytd_total 
		where posting_date = v_posting_date and property = v_property and title = 'Walk-Ins';
 
  -- Total Stay Over Guest 
		SET v_today_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date = v_posting_date and is_active=1 and is_stay_over = 1);
		SET v_mtd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_mtd_start_date and v_posting_date  and is_stay_over=1 );
		SET v_ytd_total =  (select count(*) from `tabRoom Occupy` where property = v_property and date between v_ytd_start_date  and v_posting_date and is_stay_over=1 );
		
		update `tabManager Flash Report Data` SET today_total = v_today_total, mtd_total = v_mtd_total, ytd_total = v_ytd_total 
		where posting_date = v_posting_date and property = v_property and title = 'Stayovers';

  -- Total No Show
		SET v_today_total =  (select count(*) from `tabReservation Stay` where property = v_property and arrival_date = v_posting_date and reservation_status = 'No Show');
		SET v_mtd_total =  (select count(*) from `tabReservation Stay` where property = v_property and arrival_date between v_mtd_start_date and v_posting_date  and reservation_status = 'No Show' );
		SET v_ytd_total =  (select count(*) from `tabReservation Stay` where property = v_property and arrival_date between v_ytd_start_date  and v_posting_date and reservation_status = 'No Show');
		
		update `tabManager Flash Report Data` SET today_total = v_today_total, mtd_total = v_mtd_total, ytd_total = v_ytd_total 
		where posting_date = v_posting_date and property = v_property and title = 'No Shows';
		
  -- Total Guests In-House
		SET v_today_total =  (select sum(pax) from `tabRoom Occupy` where property = v_property and date = v_posting_date and is_active=1 and is_active_reservation= 1);
		SET v_mtd_total =  (select sum(pax) from `tabRoom Occupy` where property = v_property and date between v_mtd_start_date and v_posting_date  and is_active_reservation=1 );
		SET v_ytd_total =  (select sum(pax) from `tabRoom Occupy` where property = v_property and date between v_ytd_start_date  and v_posting_date and is_active_reservation=1 );
		
		update `tabManager Flash Report Data` SET today_total = COALESCE(v_today_total,0), mtd_total = COALESCE(v_mtd_total,0), ytd_total = COALESCE(v_ytd_total ,0)
		where posting_date = v_posting_date and property = v_property and title = 'Total Guests In-House';
				
		
		
 -- remove 0 record
		delete from `tabManager Flash Report Data` where coalesce(today_total,0) = 0 and COALESCE(mtd_total,0) = 0 and coalesce(ytd_total,0) = 0;

END;
"""