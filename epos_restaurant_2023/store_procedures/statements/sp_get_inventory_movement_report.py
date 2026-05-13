SQL = """create procedure `sp_get_inventory_movement_report`( 
	IN p_property TEXT, 
	IN p_start_date DATE,  
	IN p_end_date DATE,          
	IN p_stock_location TEXT,
	IN p_product_category TEXT   
)
BEGIN
	-- STEP 1: Create a temporary table for previous on-hand inventory
	CREATE TEMPORARY TABLE previous_data AS  
	WITH inventory_transaction AS (
		SELECT 
			a.product_code,
			TRIM(
				CONCAT(
					a.product_name,
					' ',
					CASE
						WHEN a.portion = 'Normal' THEN ''
						ELSE COALESCE(NULLIF(a.portion, ''), '')
					END 
				)
			) AS product_name,
			a.stock_unit,
			a.product_category,
			COALESCE(a.product_group, 'None Group') AS product_group,
			a.business_branch,
			a.stock_location,		
			MAX(a.creation) AS _max_creation
		FROM `tabInventory Transaction` AS a 
		where 1 = 1
			and date(a.transaction_date) < date(p_start_date)
			and (FIND_IN_SET(a.business_branch , p_property))
			and (FIND_IN_SET(a.stock_location, p_stock_location))
			and (FIND_IN_SET(a.product_category, p_product_category))
		GROUP BY 
			a.product_code, 
			TRIM(
				CONCAT(
					a.product_name,
					' ',
					CASE
						WHEN a.portion = 'Normal' THEN ''
						ELSE COALESCE(NULLIF(a.portion, ''), '')
					END 
				)
			),
			a.stock_unit, 
			a.product_category, 
			COALESCE(a.product_group, 'None Group'),
			a.business_branch, 
			a.stock_location
	), previous_balance AS (
		SELECT	
			it.product_code,
			it.product_name,
			it.stock_unit,
			it.product_category,
			it.product_group, 
			it.stock_location,
			it.business_branch,
			COALESCE(x.balance, 0)   AS prev_on_hand
		FROM inventory_transaction it
		LEFT JOIN `tabInventory Transaction` x 
			ON x.creation = it._max_creation 
			AND x.stock_location = it.stock_location
		UNION
		SELECT 
			a.product_code,
			TRIM(
			CONCAT(
				a.product_name,
				' ',
				CASE
					WHEN a.portion = 'Normal' THEN ''
					ELSE COALESCE(NULLIF(a.portion, ''), '')
				END 
			)
			) AS product_name,   
			a.stock_unit,
			a.product_category,
			COALESCE(a.product_group, 'None Group') AS product_group, 
			a.stock_location,
			a.business_branch, 
			0 AS prev_on_hand
		FROM `tabInventory Transaction` a 
		where 1 = 1
			and a.transaction_date between p_start_date and p_end_date
			and (FIND_IN_SET(a.business_branch , p_property))
			and (FIND_IN_SET(a.stock_location, p_stock_location))
			and (FIND_IN_SET(a.product_category, p_product_category))
	)
	SELECT
		a.product_code,
		a.product_name, 
		a.stock_unit,
		a.product_category,
		a.product_group, 
		a.stock_location,
		a.business_branch, 
		SUM(a.prev_on_hand) AS prev_on_hand
	FROM previous_balance a
	GROUP BY
		a.product_code, 
		a.product_name, 
		a.stock_unit,
		a.product_category, 
		a.product_group, 
		a.stock_location, 
		a.business_branch;

	-- STEP 2: Create a temporary table for current transactions
	CREATE TEMPORARY TABLE current_data AS  
	SELECT 
		COALESCE(pd.prev_on_hand, 0) AS prev_on_hand,
		SUM(IF(a.transaction_type = 'Purchase Order', a.in_quantity - a.out_quantity, 0)) AS purchase_order,
			sum(if(a.transaction_type = 'Sale', a.in_quantity-a.out_quantity,0)) as sale,
			sum(if(a.transaction_type not in('Sale','Purchase Order'), a.in_quantity,0)) as other_in,
			sum(if(a.transaction_type not in('Sale','Purchase Order'), a.out_quantity,0)) as other_out,
		0 AS balance,
		SUM(a.in_quantity) AS in_quantity,
		SUM(a.out_quantity) AS out_quantity,
		a.product_code,
		TRIM(
			CONCAT(
				a.product_name,
				' ',
				CASE
					WHEN a.portion = 'Normal' THEN ''
					ELSE COALESCE(NULLIF(a.portion, ''), '')
				END 
			)
		) AS product_name,   
		a.stock_unit,
		a.product_category,
		COALESCE(a.product_group, 'None Group') AS product_group, 
		a.stock_location,
		a.business_branch		
	FROM `tabInventory Transaction` a
	LEFT JOIN previous_data pd 
		ON a.product_code = pd.product_code 
		and a.stock_location = pd.stock_location
	where 1 = 1
		and a.transaction_date between p_start_date and p_end_date
		and (FIND_IN_SET(a.business_branch , p_property))
		and (FIND_IN_SET(a.stock_location, p_stock_location))
		and (FIND_IN_SET(a.product_category, p_product_category))
  
	GROUP BY
	a.product_code, 
	TRIM(
		CONCAT(
			a.product_name,
			' ',
			CASE
				WHEN a.portion = 'Normal' THEN ''
				ELSE COALESCE(NULLIF(a.portion, ''), '')
			END 
		)
	) , 
	a.stock_unit,
	a.product_category, 
	a.product_group, 
	a.stock_location, 
	a.business_branch;

	-- STEP 3: Retrieve the data from the final temporary table
	SELECT 
		p.*,
		coalesce(c.purchase_order,0) as purchase_order,
		coalesce(c.sale,0)  as sale,
		coalesce(c.other_in,0) as other_in,
		coalesce(c.other_out,0)  as other_out,
		(p.prev_on_hand + coalesce(c.purchase_order,0) + coalesce(c.other_in,0) + ( coalesce(c.sale,0) + coalesce(c.other_out,0)) ) as balance
	FROM current_data c
	RIGHT join previous_data p   
		ON c.product_code = p.product_code 
		and c.stock_location = p.stock_location;

	-- STEP 4: Clean up temporary tables
	DROP TEMPORARY TABLE IF EXISTS previous_data;
	DROP TEMPORARY TABLE IF EXISTS current_data;
 
END;
"""