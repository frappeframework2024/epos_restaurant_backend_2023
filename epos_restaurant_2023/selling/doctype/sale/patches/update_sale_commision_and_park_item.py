import frappe


def execute():
	Sale = frappe.qb.DocType("Sale")
	query = (
		frappe.qb.update(Sale)
		.set(Sale.sale_commission_based_on, "Private")
		.set(Sale.sale_commission_amount, 0)
		.set(Sale.sale_commission_percent, 0)
		.set(Sale.is_park, 0)
	)
	query.run()