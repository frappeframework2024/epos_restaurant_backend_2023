import frappe
import requests
import json
import frappe
from frappe import _
from rq.job import Job
from rq.queue import Queue
import re
from frappe.model.document import Document
from frappe.utils import (
	cint,
	compare,
	convert_utc_to_system_timezone,
	create_batch,
	make_filter_dict,
)
from frappe.utils.background_jobs import get_queues, get_redis_conn

QUEUES = ["default", "long", "short"]
JOB_STATUSES = ["queued", "started", "failed", "finished", "deferred", "scheduled", "canceled"]

@frappe.whitelist()
def generate_data_for_sync_record(doc, method=None, *args, **kwargs):
    if doc.doctype != "Data For Sync":
        if not frappe.db.exists("DocType","ePOS Sync Setting"):
            return
        
        setting =frappe.get_doc("ePOS Sync Setting")
        if setting.enable ==1:
            if doc.doctype in [d.document_type for d in setting.sync_to_client]:
                for b in setting.sync_business_branches:
                    if not frappe.db.exists("Data For Sync",{"business_branch":b.business_branch,"document_type":doc.doctype,"document_name":doc.name}):
                        frappe.get_doc({
                            "doctype":"Data For Sync",
                            "business_branch":b.business_branch,
                            "document_type":doc.doctype,
                            "document_name":doc.name
                        }).insert(ignore_permissions=True)

            if doc.doctype in [d.document_type for d in setting.sync_to_server]:
                if doc.doctype in [d.document_type for d in setting.sync_to_server if d.event == 'on_update']:
                    frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc,action="update")
            
                # frappe.db.commit()
@frappe.whitelist()
def generate_data_for_sync_record_on_delete(doc, method=None, *args, **kwargs):
    if not frappe.db.exists("DocType","ePOS Sync Setting"):
        return
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_client]:
            frappe.db.sql("delete from `tabData For Sync` where document_type='{}' and document_name='{}'".format(doc.doctype,doc.name))
            if doc.get("business_branch"):
                frappe.get_doc({
                            "doctype":"Data For Sync",
                            "business_branch":doc.business_branch,
                            "document_type":doc.doctype,
                            "document_name":doc.name,
                            "is_deleted":1
                        }).insert(ignore_permissions=True)
            else:
                for b in setting.sync_business_branches:
                    if not frappe.db.exists("Data For Sync",{"business_branch":b.business_branch,"document_type":doc.doctype,"document_name":doc.name}):
                        frappe.get_doc({
                            "doctype":"Data For Sync",
                            "business_branch":b.business_branch,
                            "document_type":doc.doctype,
                            "document_name":doc.name,
                            "is_deleted":1
                        }).insert(ignore_permissions=True)

@frappe.whitelist()
def generate_data_for_sync_record_on_rename(doc ,method=None, *args, **kwargs):
    if not frappe.db.exists("DocType","ePOS Sync Setting"):
        return
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable == 1:
        doc_name = {'old_name': args[0], 'name': args[1]}
        frappe.db.sql("delete from `tabData For Sync` where document_type='{}' and document_name='{}' ".format(doc.doctype,doc.name))
        if doc.get("business_branch"):
            frappe.get_doc({
                        "doctype":"Data For Sync",
                        "business_branch":doc.business_branch,
                        "document_type":doc.doctype,
                        "old_name":doc_name['old_name'],
                        "document_name":doc_name['name'],
                        "is_renamed":1
                    }).insert(ignore_permissions=True)
        else:
            for b in setting.sync_business_branches:
                if not frappe.db.exists("Data For Sync",{"business_branch":b.business_branch,"document_type":doc.doctype,"document_name":doc.name}):
                    frappe.get_doc({
                        "doctype":"Data For Sync",
                        "business_branch":b.business_branch,
                        "document_type":doc.doctype,
                        "old_name":doc_name['old_name'],
                        "document_name":doc_name['name'],
                        "is_renamed":1
                    }).insert(ignore_permissions=True)
            
@frappe.whitelist()
def sync_data_to_server_on_submit(doc, method=None, *args, **kwargs):
    if not frappe.db.exists("DocType","ePOS Sync Setting"):
        return
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.doctype in [d.document_type for d in setting.sync_to_server if d.event == 'on_submit']:
            doctype = [d for d in setting.sync_to_server if d.event == 'on_submit' and d.document_type==doc.doctype][0] 
            frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc,extra_action=doctype.extra_action or [],action="submit") 


@frappe.whitelist()
def sync_data_to_server_on_delete(doc, method=None, *args, **kwargs):
    if not frappe.db.exists("DocType","ePOS Sync Setting"):
        return
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='short', doc=doc,action="delete") 



 

@frappe.whitelist()
def sync_comment_to_server(doc, method=None, *args, **kwargs):
    if not frappe.db.exists("DocType","ePOS Sync Setting"):
        return
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable ==1:
        if doc.reference_doctype in [d.document_type for d in setting.sync_to_server]:
          
            frappe.enqueue("epos_restaurant_2023.api.utils.sync_data_to_server", queue='long', doc=doc,action="update")  
 
                          
@frappe.whitelist()
def sync_data_to_server(doc,extra_action=None,action="update"):
    sync_sync_to_server_enable = frappe.db.get_single_value('ePOS Sync Setting','enable')
    client_side = frappe.db.get_single_value('ePOS Sync Setting','client_side')
    if sync_sync_to_server_enable == 1 and client_side == 1:
        server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
        token = frappe.db.get_single_value('ePOS Sync Setting','access_token')
        headers = {
                    'Authorization': 'token {}'.format(token),
                    "Content-Type":"application/json"
                }
        server_url = server_url + "/api/method/epos_restaurant_2023.api.utils.save_sync_data"

        response = requests.post(server_url,headers=headers,json={"doc":frappe.as_json(doc),"extra_action":extra_action,"action":action })
        if response.status_code==200:
            meta = frappe.get_meta(doc.get("doctype"))
            if len([d for d in meta.fields if d.fieldname=="is_synced"])>0:
                frappe.db.sql("update `tab{}` set is_synced = 1 where name = '{}'".format(doc.get("doctype"),doc.get('name')))
                frappe.db.commit()
        else:
            frappe.throw(str(response.text))
     
    
    
    

@frappe.whitelist(methods="POST")
def save_sync_data(doc,extra_action=None,action="update"):
    
    doc = json.loads(doc)
    doc["__newname"] = doc["name"]

    doc = frappe.get_doc(doc) 
    
    doc.flags.ignore_validate = True
    doc.flags.ignore_insert = True
    doc.flags.ignore_after_insert = True
    doc.flags.ignore_on_update = True
    doc.flags.ignore_before_submit = True
    doc.flags.ignore_on_submit = True
    doc.flags.ignore_on_cancel = True
    doc.flags.ignore_before_update_after_submit = True
    if action =="cancel":
        doc.docstatus= 0

    delete_doc(doc.doctype, doc.name)

    if action != "delete":
        doc.insert(ignore_permissions=True, ignore_links=True)
        if extra_action:
            # action is string
           
            for act in json.loads(extra_action):
                frappe.enqueue(act, queue='short', self=doc)


    if action =="cancel":
        frappe.db.sql("update tabSale set docstatus = 2 where name = '{}'".format(doc.name))
    frappe.db.commit()


def delete_doc(doctype,name):
    frappe.db.sql("delete from `tab{}` where name='{}'".format(doctype,name))
    meta = frappe.get_meta(doctype)

    for child in [d for d in meta.fields if d.fieldtype=="Table"]:
        frappe.db.sql("delete from `tab{}` where parent='{}'".format(child.options,name))
    frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def ping():
    return "pong"

@frappe.whitelist()
def re_run_fail_jobs():
    server_url = frappe.db.get_single_value('ePOS Sync Setting','server_url')
    response = requests.post(f"{server_url}/api/method/epos_restaurant_2023.api.utils.ping")
    
    if response.status_code == 200:
        args = {'doctype': 'RQ Job', 'fields': ['`tabRQ Job`.`name`', '`tabRQ Job`.`owner`', '`tabRQ Job`.`creation`', '`tabRQ Job`.`modified`', '`tabRQ Job`.`modified_by`', '`tabRQ Job`.`_user_tags`', '`tabRQ Job`.`_comments`', '`tabRQ Job`.`_assign`', '`tabRQ Job`.`_liked_by`', '`tabRQ Job`.`docstatus`', '`tabRQ Job`.`idx`', '`tabRQ Job`.`queue`', '`tabRQ Job`.`status`', '`tabRQ Job`.`job_name`'], 'filters': [['RQ Job', 'status', '=', 'failed']], 'order_by': '`tabRQ Job`.`modified` desc', 'start': '0', 'page_length': '20', 'group_by': '`tabRQ Job`.`name`', 'with_comment_count': '1', 'save_user_settings': True, 'strict': None}
        start = cint(args.get("start"))
        page_length = cint(args.get("page_length")) or 20

        order_desc = "desc" in args.get("order_by", "")

        matched_job_ids = get_matching_job_ids(args)[start : start + page_length]

        conn = get_redis_conn()
        jobs = [
            serialize_job(job) for job in Job.fetch_many(job_ids=matched_job_ids, connection=conn) if job
        ]

        jobs =  sorted(jobs, key=lambda j: j.modified, reverse=order_desc)
        jobs = [d for d in jobs if "exc_info" in d]
        job_names=["epos_restaurant_2023.api.utils."]
        jobs = [d for d in jobs  if  ( d["job_name"] in job_names or  "Deadlock found when trying"  in  d["exc_info"] or 'Network is unreachable' in d['exc_info'] or "Lock wait timeout exceeded"  in  d["exc_info"] or "Document has been modified after you have opened it" in d["exc_info"] or "zerobalance" in d["exc_info"] or "Task exceeded maximum timeout value" in d["exc_info"] or "timeout" in d["exc_info"] or "object has no attribute" in d["exc_info"] or "object is not subscriptable" in d["exc_info"]) ]
        job_ids = []
        
        for j in jobs:
            try:
                job =   json.loads(j["arguments"])
                #Retry Here
                if job['job_name'] == "epos_restaurant_2023.api.utils.sync_data_to_server":
                    frappe.enqueue('epos_restaurant_2023.api.utils.sync_data_to_server',doc=frappe.get_doc(job['kwargs']['doc']),extra_action=job['kwargs']['extra_action'] if job['kwargs'].get('extra_action') else '[]',action=job['kwargs']['action'])
                    # sync_data_to_server(frappe.get_doc(job['kwargs']['doc']),extra_action=job['kwargs']['extra_action'] if job['kwargs'].get('extra_action') else '[]',action=job['kwargs']['action'])
                       

                job_ids.append(j["job_id"])
            except Exception as e:
                frappe.throw(str(e))
            
        
        remove_failed_jobs(job_ids)

        return job_ids


def serialize_job(job: Job) -> frappe._dict:
	modified = job.last_heartbeat or job.ended_at or job.started_at or job.created_at
	job_kwargs = job.kwargs.get("kwargs", {})
	job_name = job_kwargs.get("job_type") or str(job.kwargs.get("job_name"))
	if job_name == "frappe.utils.background_jobs.run_doc_method":
		doctype = job_kwargs.get("doctype")
		doc_method = job_kwargs.get("doc_method")
		if doctype and doc_method:
			job_name = f"{doctype}.{doc_method}"

	# function objects have this repr: '<function functionname at 0xmemory_address >'
	# This regex just removes unnecessary things around it.
	if matches := re.match(r"<function (?P<func_name>.*) at 0x.*>", job_name):
		job_name = matches.group("func_name")

	return frappe._dict(
		name=job.id,
		job_id=job.id,
		queue=job.origin.rsplit(":", 1)[1],
		job_name=job_name,
		status=job.get_status(),
		started_at=convert_utc_to_system_timezone(job.started_at) if job.started_at else "",
		ended_at=convert_utc_to_system_timezone(job.ended_at) if job.ended_at else "",
		time_taken=(job.ended_at - job.started_at).total_seconds() if job.ended_at else "",
		exc_info=job.exc_info,
		arguments=frappe.as_json(job.kwargs),
		timeout=job.timeout,
		creation=convert_utc_to_system_timezone(job.created_at),
		modified=convert_utc_to_system_timezone(modified),
		_comment_count=0,
		owner=job.kwargs.get("user"),
		modified_by=job.kwargs.get("user"),
	)


def get_matching_job_ids(args) -> list[str]:
    filters = make_filter_dict(args.get("filters"))

    queues = _eval_filters(filters.get("queue"), QUEUES)
    statuses = _eval_filters(filters.get("status"), JOB_STATUSES)

    matched_job_ids = []
    for queue in get_queues():
        if not queue.name.endswith(tuple(queues)):
            continue
        for status in statuses:
            matched_job_ids.extend(fetch_job_ids(queue, status))

    return filter_current_site_jobs(matched_job_ids)
    
def _eval_filters(filter, values: list[str]) -> list[str]:
	if filter:
		operator, operand = filter
		return [val for val in values if compare(val, operator, operand)]
	return values


def fetch_job_ids(queue: Queue, status: str) -> list[str]:
	registry_map = {
		"queued": queue,  # self
		"started": queue.started_job_registry,
		"finished": queue.finished_job_registry,
		"failed": queue.failed_job_registry,
		"deferred": queue.deferred_job_registry,
		"scheduled": queue.scheduled_job_registry,
		"canceled": queue.canceled_job_registry,
	}

	registry = registry_map.get(status)
	if registry is not None:
		job_ids = registry.get_job_ids()
		return [j for j in job_ids if j]

	return []


@frappe.whitelist()
def remove_failed_jobs(failed_jobs):
    frappe.only_for("System Manager")

    for queue in get_queues():
        
        fail_registry = queue.failed_job_registry
         
        # Delete in batches to avoid loading too many things in memory
        conn = get_redis_conn()
        for job_ids in create_batch(failed_jobs, 100):
            for job in Job.fetch_many(job_ids=job_ids, connection=conn):
                job and fail_registry.remove(job, delete_job=True)


def filter_current_site_jobs(job_ids: list[str]) -> list[str]:
	site = frappe.local.site

	return [j for j in job_ids if j.startswith(site)]

@frappe.whitelist()
def remove_failed_jobs(failed_jobs):
    frappe.only_for("System Manager")

    for queue in get_queues():
        
        fail_registry = queue.failed_job_registry
         
        # Delete in batches to avoid loading too many things in memory
        conn = get_redis_conn()
        for job_ids in create_batch(failed_jobs, 100):
            for job in Job.fetch_many(job_ids=job_ids, connection=conn):
                job and fail_registry.remove(job, delete_job=True)


@frappe.whitelist()
def update_temp_menu_product_photo_schedule():
    setting =frappe.get_doc("ePOS Sync Setting")
    if setting.enable == 1 and setting.client_side == 1: 
        data = frappe.db.sql("""
                            Update `tabTemp Product Menu`
                                set photo = concat('{}',photo)
                            where 
                                photo is not null and 
                                photo not like 'http://%' and 
                                photo not like 'https://%'
                            """.format(setting.server_url))
        frappe.db.commit()
        return data