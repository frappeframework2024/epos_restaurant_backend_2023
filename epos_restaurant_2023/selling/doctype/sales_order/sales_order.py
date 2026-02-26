from epos_restaurant_2023.inventory.inventory import check_uom_conversion
import frappe
from frappe import _
from py_linq import Enumerable
from frappe.model.document import Document
from frappe.utils import flt
class SalesOrder(Document):
	def before_insert(self):
		for a in self.products:
			a.delivered_quantity = 0

	def validate(self):
		if self.discount_type =="Percent" and self.discount> 100:
			frappe.throw(_("Discount percent cannot greater than 100%"))
		#validate outlet
		if self.outlet and self.business_branch:
			if frappe.get_value("Outlet",self.outlet,"business_branch") != self.business_branch:
				frappe.throw(_("The outlet {} is not belong to business branch {}".format(self.outlet, self.business_branch)))
		
		#validate stock location
		if self.stock_location and self.business_branch:
			if frappe.get_value("Stock Location",self.stock_location,"business_branch") != self.business_branch:
				frappe.throw(_("The stock location {} is not belong to business branch {}".format(self.stock_location, self.business_branch)))
			
		#validate sale product 
		validate_sale_product(self)		

		total_quantity = Enumerable(self.products).sum(lambda x: x.quantity or 0)
		sub_total = Enumerable(self.products).sum(lambda x: (x.quantity or 0)* (x.price or  0))
		sale_discountable_amount =Enumerable(self.products).where(lambda x:x.allow_discount ==1 and (x.discount_amount or 0)==0).sum(lambda x: (x.quantity or 0)* (x.price or  0))

		self.total_quantity = total_quantity
		self.sale_discountable_amount = sale_discountable_amount
		self.sub_total = sub_total
		# calculate sale discount
		if self.discount:
			if self.discount_type =="Percent":
				self.sale_discount = self.sale_discountable_amount * self.discount / 100
			else:
				self.sale_discount = self.discount or 0

		self.product_discount = Enumerable(self.products).where(lambda x:x.allow_discount ==1).sum(lambda x: x.discount_amount)
		
		self.total_discount = (self.product_discount or 0) + (self.sale_discount or 0)
  
		#tax 
		self.taxable_amount_1  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.taxable_amount_1)
		self.taxable_amount_2  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.taxable_amount_2)
		self.taxable_amount_3  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.taxable_amount_3)
		self.tax_1_amount  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.tax_1_amount)
		self.tax_2_amount  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.tax_2_amount)
		self.tax_3_amount  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.tax_3_amount)
		self.total_tax  = Enumerable(self.products).where(lambda x:x.tax_rule).sum(lambda x: x.total_tax)

		currency_precision = frappe.db.get_single_value('System Settings', 'currency_precision')
		if currency_precision=='':
			currency_precision = "2"

		self.grand_total =( sub_total - (self.total_discount or 0))  + self.total_tax

	def before_submit(self):
		self.append_quantity = None
		self.scan_barcode = None
		for d in self.products:
			if d.is_inventory_product:
				if d.unit !=d.base_unit:
					if not check_uom_conversion(d.base_unit, d.unit):
						frappe.throw(_("There is no UoM conversion for product {}-{} from {} to {}".format(d.product_code, d.product_name, d.base_unit, d.unit)))

	def on_cancel(self):
		update_status(self)
	
	def on_submit(self):
		update_status(self)
		
def validate_sale_product(self):
	sale_discount = self.discount  
	if sale_discount>0:
		if self.discount_type=="Amount":
			discountable_amount = Enumerable(self.products).where(lambda x: x.allow_discount==1 and x.discount==0).sum(lambda x: (x.quantity or 0)* (x.price or  0))
			sale_discount=(sale_discount / discountable_amount ) * 100
 
	for d in self.products:
		d.sub_total = (d.quantity or 0) * (d.price or 0)
		if (d.discount_type or "Percent")=="Percent":
			d.discount_amount = d.sub_total * (d.discount or 0) / 100
		else:
			d.discount_amount = d.discount or 0
		# check if sale has discount
		if sale_discount>0 and d.allow_discount and d.discount==0:
			
			d.sale_discount_percent = sale_discount  
			d.sale_discount_amount = (sale_discount/100) * d.sub_total
		else:
			d.sale_discount_percent = 0  
			d.sale_discount_amount = 0

		d.total_discount = (d.sale_discount_amount or 0) + (d.discount_amount or 0)
		validate_tax(d)
		d.amount = (d.sub_total - d.discount_amount) + d.total_tax

def validate_tax(doc):
		if doc.tax_rule:
			if doc.calculate_tax_1_after_discount==1:
				doc.taxable_amount_1 =   doc.sub_total - doc.total_discount
			else:
				doc.taxable_amount_1 = doc.sub_total 
    
			doc.tax_1_amount =  doc.taxable_amount_1 * doc.tax_1_rate/100

			#tax 2
			if   doc.calculate_tax_2_after_discount==1:
				doc.taxable_amount_2 = doc.sub_total  - doc.total_discount
			else:
				doc.taxable_amount_2 = doc.sub_total  
			
			if doc.calculate_tax_2_after_adding_tax_1==1:
					doc.taxable_amount_2 = doc.taxable_amount_2 +  doc.tax_1_amount

			doc.tax_2_amount =  (doc.taxable_amount_2 or 0) *  (doc.tax_2_rate or 0) /100

			#tax 3
			if doc.calculate_tax_3_after_discount==1:
				doc.taxable_amount_3 = doc.sub_total - doc.total_discount 
			else:
				doc.taxable_amount_3 =  doc.sub_total
			
			if doc.calculate_tax_3_after_adding_tax_1==1:
				doc.taxable_amount_3 =   doc.taxable_amount_3 +  doc.tax_1_amount 
			
			if doc.calculate_tax_3_after_adding_tax_2==1:
				doc.taxable_amount_3 = doc.taxable_amount_3 +  doc.tax_2_amount 
			
			doc.tax_3_amount =  doc.taxable_amount_3 * doc.tax_3_rate/100
			
			#total tax
			doc.total_tax = doc.tax_1_amount + doc.tax_2_amount + doc.tax_3_amount
		else:
			doc.taxable_amount_1 =0
			doc.tax_1_amount=0
			doc.taxable_amount_2 =0
			doc.tax_2_amount=0
			doc.taxable_amount_3 =0
			doc.tax_3_amount=0
			doc.total_tax =0

@frappe.whitelist()
def update_status(self,status=None):
	if status:
		self.status = status
		return
	if self.docstatus == 0:
		self.status = "Draft"
	elif self.docstatus == 1:
		self.status = "To Deliver and Bill"
	else:
		self.status = "Cancelled"
	frappe.db.set_value("Sales Order", self.name, "status", self.status)
	frappe.db.commit()

@frappe.whitelist()
def get_sale_product(product_code,sales_order):
	p = frappe.db.sql("""select sum(quantity) qty from `tabSale Product` a inner join `tabSale` b on b.name = a.parent where product_code='{0}' and sales_order = '{1}'""".format(product_code,sales_order), as_dict=True)
	return (p[0].qty or 0)

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
	from frappe.model.mapper import get_mapped_doc
	def postprocess(source, target):
		naming_series_list = get_naming_series("Sale")
		if len(naming_series_list) > 0:
			target.naming_series = naming_series_list[0]
		else:
			target.naming_series = ""
		target.sales_order = source.name
		target.status = "Draft"

	def update_item(source, target, source_parent):
		sale_quantity = get_sale_product(source.product_code, source.parent)
		target.quantity = flt(source.quantity) - flt(sale_quantity)

	doclist = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Sale",
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Product": {
				"doctype": "Sale Product",
				"field_map": {
					"name": "products",
					"parent": "sales_order",
				},
				"postprocess": update_item,
			}
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)
	return doclist

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, ignore_permissions=False):
	from frappe.model.mapper import get_mapped_doc
	def postprocess(source, target):
		naming_series_list = get_naming_series("Delivery Note")
		if len(naming_series_list) > 0:
			target.naming_series = naming_series_list[0]
		else:
			target.naming_series = ""
		target.sales_order = source.name
		target.delivery_note = source.name
		target.sub_total = 0
		target.grand_total = 0
		target.status = "Draft"

	def update_item(source, target, source_parent):
		target.quantity = flt(source.quantity) - flt(source.delivered_quantity)

	doclist = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {
				"doctype": "Delivery Note",
				"validation": {"docstatus": ["=", 1]},
			},
			"Sales Order Product": {
				"doctype": "Delivery Note Product",
				"field_map": {
					"name": "products",
					"parent": "sales_order",
				},
				"postprocess": update_item,
			}
		},
		target_doc,
		postprocess,
		ignore_permissions=ignore_permissions,
	)
	return doclist

def get_naming_series(doctype):
    meta = frappe.get_meta(doctype)
    return meta.get_field("naming_series").options.split("\n") if meta.get_field("naming_series") else []