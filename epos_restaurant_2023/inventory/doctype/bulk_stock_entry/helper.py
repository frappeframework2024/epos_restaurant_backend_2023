import frappe
from frappe.utils import flt


def create_purchase_order(source_doc):
	if not source_doc.vendor:
		frappe.throw("Please select a vendor for Purchase Order")

	products = _get_products(source_doc)
	purchase_order = frappe.new_doc("Purchase Order")
	purchase_order.update(
		{
			"posting_date": source_doc.posting_date,
			"vendor": source_doc.vendor,
			"stock_location": source_doc.stock_location,
			"business_branch": source_doc.business_branch,
			"referance": source_doc.name,
			"note": source_doc.note,
		}
	)

	for row in products:
		product = frappe.get_cached_doc("Product", row.product_code)
		quantity = flt(row.quantity)
		cost = flt(row.cost)
		unit = row.unit or product.unit
		
		purchase_order.append(
			"purchase_order_products",
			{
				"product_code": row.product_code,
				"product_name": row.product_name or product.product_name_en,
				"unit": unit,
				"base_unit": product.unit,
				"quantity": quantity,
				"cost": cost,
				"base_cost": cost,
				
				"sub_total": quantity * cost,
				"amount": quantity * cost,
			},
		)

	return _insert_and_submit(purchase_order)


def create_stock_adjustment(source_doc):
	products = _get_products(source_doc)
	stock_adjustment = frappe.new_doc("Stock Adjustment")
	stock_adjustment.update(
		{
			"posting_date": source_doc.posting_date,
			"stock_location": source_doc.stock_location,
			"business_branch": source_doc.business_branch,
			"reference_number": source_doc.name,
			"note": source_doc.note,
		}
	)

	for row in products:
		product = frappe.get_cached_doc("Product", row.product_code)
		quantity = flt(row.quantity)
		current_quantity = flt(row.current_quantity)
		cost = flt(row.cost)
		current_cost = flt(row.current_cost)
		unit = row.unit or product.unit
	 
		stock_adjustment.append(
			"products",
			{
				"product_code": row.product_code,
				"product_name": row.product_name or product.product_name_en,
				"unit": unit,
				"current_quantity":current_quantity,
				"quantity": quantity,
				"cost": cost,
				"current_cost": current_cost,
				"total_amount": quantity * cost,
				"total_current_cost": current_quantity * current_cost,
				"is_inventory_product": product.is_inventory_product or 0,
			},
		)

	return _insert_and_submit(stock_adjustment)


def _get_products(source_doc):
	products = [row for row in source_doc.products if row.product_code]
	if not products:
		frappe.throw("Please add at least one product")
	return products


def _insert_and_submit(doc):
	doc.flags.ignore_permissions = True
	doc.insert()
	doc.submit()
	return doc.name

