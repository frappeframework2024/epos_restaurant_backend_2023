import frappe 
from frappe import _
def get_timespan_report_column(filters):
    column_info =  get_column_group_info(filters.column_group) 
    filters = get_filter_date_range(filters)
    
    sql="""
        select 
            {1} as name,
            {0} 
        from `tabDates`
        where
            date between %(start_date)s and %(end_date)s
        group by
            {1}
        order by date
    """.format(column_info["sql_expression"],column_info["group_by_expression"])
 
    data = frappe.db.sql(sql,filters,as_dict=1)
    if len(data)>24:
        frappe.throw(_("Report column must be less than 24 columns"))
    return data

    
def get_column_group_info(key):
    return [d for d in column_group_keys() if d["key"] == key][0]

def column_group_keys():
    return [
        {"key":"Yearly","sql_expression":"date_format(date,'%%Y') as column_group", "group_by_expression":"date_format(date,'%%Y')" },
        {"key":"Monthly","sql_expression":"date_format(date,'%%b %%y') as column_group", "group_by_expression":"date_format(date,'%%b %%y')" },
        {"key":"Quarterly","sql_expression":"concat(date_format(min(date),'%%b %%y'),'-',date_format(max(date),'%%b %%y')) as column_group", "group_by_expression":"concat(QUARTER(date),'-', date_format(date,'%%Y'))" },
        {"key":"Half-Yearly","sql_expression":"concat(date_format(min(date),'%%b %%y'),'-',date_format(max(date),'%%b %%y')) as column_group", "group_by_expression":"concat(floor((month(date)-1)/6),'-', date_format(date,'%%Y'))" },
    ]
    
def get_filter_date_range(filters):
    if filters.filter_based_on =='Fiscal Year':
        filters.start_date =  '{}-01-01'.format(filters.start_year)    
        filters.end_date =  '{}-12-31'.format(filters.end_year)    
    return filters
        
        