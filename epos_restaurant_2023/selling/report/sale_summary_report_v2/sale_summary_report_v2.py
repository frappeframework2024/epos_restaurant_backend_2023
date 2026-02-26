# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import fmt_money


def execute(filters=None): 

	sale_sum = get_sale_summary_data(filters)
	sale_ren = get_sale_by_revenue_group(filters)
	report_data = get_report_data(filters,sale_sum,sale_ren)
	return get_columns(filters),report_data,None,None, None

def get_columns(filters):
	columns =   [
		{"fieldname":"revenue_group", "label":"Title",'align':'left',"width":300,},
		{"fieldname":"total_qty", "label":"QTY",'align':'center',},
		{'fieldname':'amount','align':'right','label':'Amount',"width":300,"fieldtype":"Data"},
		
	]
	return columns

def get_sale_summary_data(filters):
	sql = """
		select 
    		coalesce(sum(if(is_foc=0,sub_total,0)),0) as sub_total,
    		coalesce(sum(if(is_foc=0,total_discount,0)),0) as total_discount,
    		coalesce(sum(if(is_foc=0,tax_1_amount,0)),0) as tax_1,
    		coalesce(sum(if(is_foc=0,tax_2_amount,0)),0) as tax_2,
    		coalesce(sum(if(is_foc=0,tax_3_amount,0)),0) as tax_3,
    		coalesce(sum(if(is_foc = 1,grand_total,0)),0) as total_foc_amount,
    		coalesce(sum(if(is_foc = 0,grand_total,0)),0) as grand_total,
    		coalesce(sum(commission_amount),0) as total_commission_amount
    	from `tabSale`
    	where 
			posting_date between %(start_date)s and %(end_date)s and 
        	docstatus = 1
"""
	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_sale_by_revenue_group(filters):
	sql = """
		select 
			revenue_group,
    		sum(sp.quantity) as total_qty,
    		sum(total_revenue) as amount 
		from `tabSale Product` sp
    	inner join tabSale s on s.name = sp.parent
		where 
    		s.posting_date between %(start_date)s and %(end_date)s and 
    		s.is_foc=0 and 
    		s.docstatus = 1
		group by revenue_group
		union
		select
    		'Voucher Top Up',
    		count(name) as total_qty,
    		sum(actual_amount) as amount
		from `tabVoucher`
		where 
			posting_date between %(start_date)s and %(end_date)s
"""

	data1 =   frappe.db.sql(sql,filters,as_dict=1)
	return data1
def get_report_data(filters,data,data1):

	voucher_payments = frappe.db.sql("select coalesce(sum(payment_amount),0)  payment_amount from `tabVoucher Payment` where posting_date between %(start_date)s and %(end_date)s",filters,as_dict=1)

	total_voucher_claim = frappe.db.sql("select coalesce(sum(total_paid),0) as total_paid from `tabSale Payment` where payment_type_group = 'Voucher' and posting_date between %(start_date)s and %(end_date)s and docstatus = 1",filters,as_dict=1)
	sale_transactions = frappe.db.sql("""
    						select 
								revenue_group,
    							sum(total_revenue) as amount 
							from `tabSale Product` sp
    						inner join `tabSale` s on s.name = sp.parent
    						where 
								s.posting_date between %(start_date)s and %(end_date)s and 
								s.is_foc=1 and 
								s.docstatus=1
    						group by revenue_group""",filters,as_dict=1)
	voucher_top_up = frappe.db.sql("""select coalesce(sum(payment_amount),0) payment_amount,coalesce(sum(input_amount),0) as input_amount,payment_type,currency from `tabVoucher Payment` where posting_date between %(start_date)s and %(end_date)s GROUP BY 
	payment_type,
	currency """,filters,as_dict=1) 

	report_data = []

	report_data.append({
		"indent":0,
		"revenue_group":"Sale Summary"
	})
	for d in data:
		report_data.append({
			"indent":1,
			"revenue_group":"Sale Sub Total",
			"amount":fmt_money(d["sub_total"] + d["total_foc_amount"] + voucher_payments[0]["payment_amount"], currency=frappe.db.get_default("currency"))
		})
		if d['total_discount'] > 0:
			report_data.append({
				"indent":1,
				"revenue_group":"Total Discount",
				"amount":fmt_money(d["total_discount"], currency=frappe.db.get_default("currency"))
			})
		if d['total_foc_amount'] > 0:
			report_data.append({
				"indent":1,
				"revenue_group":"Total FOC Amount",
				"amount":fmt_money(d["total_foc_amount"], currency=frappe.db.get_default("currency"))
			})
		if total_voucher_claim[0]["total_paid"]:
			report_data.append({
					"indent":1,
					"revenue_group":"Voucher Claim",
					"amount":fmt_money(total_voucher_claim[0]["total_paid"], currency=frappe.db.get_default("currency"))
			})
		if voucher_payments[0]["payment_amount"]:
			report_data.append({
				"indent":1,
				"revenue_group":"Voucher Top Up",
				"amount":fmt_money(voucher_payments[0]["payment_amount"], currency=frappe.db.get_default("currency"))
			})
		report_data.append({
			"indent":1,
			"revenue_group":"Total Net Sale",
			"amount":fmt_money(d["grand_total"] - total_voucher_claim[0]["total_paid"] + voucher_payments[0]["payment_amount"], currency=frappe.db.get_default("currency"))
		})
		if d['tax_1'] > 0:
			report_data.append({
				"indent":1,
				"revenue_group":"Tax 1",
				"amount":fmt_money(d["tax_1"], currency=frappe.db.get_default("currency"))
			})
		if d['tax_2'] > 0:
			report_data.append({
				"indent":1,
				"revenue_group":"Tax 2",
				"amount":fmt_money(d["tax_2"], currency=frappe.db.get_default("currency"))
			})
		if d['tax_3'] > 0:
			report_data.append({
				"indent":1,
				"revenue_group":"Tax 3",
				"amount":fmt_money(d["tax_3"], currency=frappe.db.get_default("currency"))
			})
		
		report_data.append({
			"indent":1,
			"revenue_group":"Total Sale Revenue",
			"amount":fmt_money((d["grand_total"] - total_voucher_claim[0]["total_paid"] ) + voucher_payments[0]["payment_amount"], currency=frappe.db.get_default("currency"))
		})
		if d['total_commission_amount'] > 0:
			report_data.append({
				"indent":1,
				"revenue_group":"Total Commission Amount",
				"amount":fmt_money(d["total_commission_amount"], currency=frappe.db.get_default("currency"))
			})
	report_data.append({
		"indent":0,
		"revenue_group":"Sale By Revenue Group"
	})
	for d in data1:
		if d["amount"] or 0 > 0:
			report_data.append({
				"indent":1,
				"revenue_group":d["revenue_group"],
				"total_qty": d["total_qty"] ,
				"amount": fmt_money(d["amount"], currency=frappe.db.get_default("currency"))
			})
	if len(sale_transactions)>0:
		report_data.append({
			"indent":0,
			"revenue_group":"FOC By Revenue Group"
		})
		for d in sale_transactions:
			report_data.append({
				"indent":1,
				"revenue_group":d["revenue_group"],
				"amount": fmt_money(d["amount"], currency=frappe.db.get_default("currency"))
			})
	if len(voucher_top_up) > 0:
		report_data.append({
			"indent":0,
			"revenue_group":"Voucher Top Up"
		})
		for d in voucher_top_up:
			report_data.append({
				"indent":1,
				"revenue_group":d["payment_type"],
				"amount": fmt_money(d["input_amount"], currency=frappe.db.get_default("currency"))
			})
		report_data.append({
					"indent":1,
					"revenue_group":"Total Top Up",
					"amount":fmt_money(sum(d["payment_amount"] for d in voucher_top_up), currency=frappe.db.get_default("currency"))
			})
	payment_breakdown = frappe.db.sql("""
						select 
							payment_type,
							symbol,
							currency,
							currency_precision,
							payment_type_group,
							exchange_rate,
							sum(fee_amount) as fee_amount ,
							sum(input_amount) as input_amount ,
							sum(payment_amount) as payment_amount
						from `tabSale Payment`
						where posting_date between %(start_date)s and %(end_date)s and docstatus = 1 and payment_type_group != 'Voucher'
						group by 
							payment_type,
							symbol,
							currency,
							payment_type_group,
							currency_precision,
							exchange_rate
						""",filters,as_dict=1)
	sale_tip = frappe.db.sql("""
                    select 
                        sum(tip_amount) as tip_amount
                    from `tabSale`
                    where posting_date between %(start_date)s and %(end_date)s and docstatus = 1
			""",filters,as_dict=1)
	exch = frappe.db.sql("select exchange_rate,exchange_rate_input,to_currency,from_currency from `tabCurrency Exchange` where posting_date <= %(start_date)s and %(end_date)s and from_currency <> to_currency order by posting_date  desc limit 1",filters,as_dict=1)
	
	report_data.append({
		"indent":0,
		"revenue_group":"Payment Breakdown"
	})
	
	for d in payment_breakdown:
		
		report_data.append({
			"indent":1,
			"revenue_group":"{} {}".format(d["payment_type"], "(+Fee: " + str(fmt_money(d["fee_amount"] * d["exchange_rate"], currency=d["currency"], precision=d["currency_precision"])) + ")" if d["fee_amount"] > 0 else ""),
			"amount": fmt_money(d["input_amount"] + (d["fee_amount"] * d["exchange_rate"]), currency=d["currency"], precision=d["currency_precision"])
		})
	for d in sale_tip:
		if d["tip_amount"] :
			report_data.append({
				"indent":1,
				"revenue_group":"Tip Amount",
				"amount": fmt_money(d["tip_amount"], currency=frappe.db.get_default("currency"))
			})
	total_payment_amount = sum(d["payment_amount"] + d["fee_amount"] for d in payment_breakdown)
	total_payment_float = float(total_payment_amount)
	final_amount = total_payment_float * exch[0]["exchange_rate"]

	report_data.append({
			"indent":1,
			"revenue_group":"Total Payment",
			"amount": "{} / {}".format(fmt_money(total_payment_amount, currency=frappe.db.get_default("currency")),fmt_money(final_amount, currency=frappe.db.get_default("second_currency"),precision=0)),
			"is_total_row":1,
		})
	on_account = frappe.db.sql("""
					select 
						payment_type,
						currency_symbol,
						sum(input_amount) as input_amount ,
						sum(amount) as payment_amount 
						from `tabSale` a
						inner join `tabPOS Sale Payment` b on b.parent = a.name
						where posting_date between %(start_date)s and %(end_date)s and payment_type='On Account'
					group by
						currency_symbol,
						payment_type""",filters,as_dict=1)
	if len(on_account) > 0:
		report_data.append({
			"indent":0,
			"revenue_group":"On Account"
		})
		report_data.append({
				"indent":1,
				"revenue_group":"Total On Account",
				"amount": fmt_money(sum([d["payment_amount"] for d in on_account ]), currency=frappe.db.get_default("currency"))
		})
	return report_data