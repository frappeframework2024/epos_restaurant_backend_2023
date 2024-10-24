# Copyright (c) 2023, ratha and contributors
# For license information, please see license.txt

import ftplib, frappe
import os, shutil
import shlex, subprocess
from frappe.model.document import Document
from frappe.utils import cstr,password
import asyncio
from datetime import datetime
from frappe import conf

@frappe.whitelist()
def execute_backup_command(): 
    frappe.enqueue(run_backup_command,queue="long")
    return "Added To Queue"

@frappe.whitelist()
def execute_repair_table():
    frappe.enqueue(method=repair_table,queue="long")
    return 'Repairing Database, Check RQ Job'

def repair_table():
    data = frappe.db.sql("SELECT concat('REPAIR Table `',TABLE_NAME,'`;') script FROM information_schema.TABLES WHERE table_schema='{0}' AND table_type='BASE TABLE'".format(frappe.conf.get("db_name")),as_dict=1)
    for a in data:
        frappe.db.sql(a.script)
    frappe.db.commit()
    frappe.publish_realtime("repair_database", {"message": "Database Repaired"})

@frappe.whitelist()
def check_table():
    site = frappe.conf.get("db_name")
    corrupt_table = ""
    tables = ""
    data = frappe.db.sql("SELECT concat('`',TABLE_NAME,'`') table_name FROM information_schema.TABLES WHERE table_schema='{0}' AND table_type='BASE TABLE'".format(site),as_dict=1)
    for a in data:
        if data.index(a) != len(data)-1:
            tables += a.table_name + ","
        else:
            tables += a.table_name
    check_tables = frappe.db.sql("CHECK TABLE {}".format(tables),as_dict=1)
    for b in check_tables:
        if b.Msg_text != "OK":
            corrupt_table += b.Table.replace(site+".","")+"\n"
    if corrupt_table == "":
        corrupt_table = "No Table Corrupted"
    return corrupt_table

def clear_logs(setting):
    clear_logs = [a.log for a in setting.clear_logs]
    if clear_logs:
        for a in clear_logs:
            sql = "delete from `tab{0}`".format(a)
            frappe.db.sql(sql)
    else:
        frappe.db.sql("delete from `tabError Log`")
        frappe.db.sql("delete from `tabScheduled Job Log`")
    frappe.db.commit()

def run_backup_command():  
    setting = frappe.get_doc('FTP Backup') 
    site_name = cstr(frappe.local.site)
    folder = setting.ftp_backup_path
    backup_type = setting.backup_type

    try:
        clear_logs(setting)
    except:
        pass

    if folder is None or folder == '' :
        folder = frappe.utils.get_site_path(conf.get("backup_path", "private/backups"))       
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    command = ""
    if backup_type == "Simple":
        command = "bench --site " + site_name + " backup"
    elif backup_type == "Full":
        command = "bench --site " + site_name + " backup --with-files"
    else:
        command = "bench --site " + site_name + " backup"

    asyncio.run(run_bench_command(command))
    
    frappe.enqueue(upload_to_ftp,queue="long")

    return "Backup In Queue"

async def run_bench_command(command, kwargs=None):
    site = {"site": frappe.local.site}
    cmd_input = None
    if kwargs:
        cmd_input = kwargs.get("cmd_input", None)
        if cmd_input:
            if not isinstance(cmd_input, bytes):
                raise Exception(f"The input should be of type bytes, not {type(cmd_input).__name__}")
            del kwargs["cmd_input"]
        kwargs.update(site)
    else:
        kwargs = site
    command = " ".join(command.split()).format(**kwargs)
    command = shlex.split(command)
    subprocess.run(command, input=cmd_input, capture_output=True)

def upload_to_ftp():
    folder_name = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    setting = frappe.get_doc('FTP Backup')
    site_name = setting.ftp_folder_name if setting.ftp_folder_name != '' else cstr(frappe.local.site)# if setting.ftp_folder_name==''?
    backup_folder = setting.ftp_backup_path
    if backup_folder is None or backup_folder == '' :
        backup_folder = frappe.utils.get_site_path(conf.get("backup_path", "private/backups"))
    ftp_password = password.get_decrypted_password("FTP Backup", "FTP Backup", fieldname="ftp_password",raise_exception=False)
    session = ftplib.FTP_TLS(setting.ftp_url,setting.ftp_user,ftp_password)
    session.encoding = 'latin-1'
    if site_name in session.nlst():
        session.cwd(site_name)
        for folder in session.nlst():
            if folder != "." and folder != "..":
                created_date = folder.split('_', 1)[0]
                if(len(created_date) >= 10 ):
                    d1 = datetime.strptime(created_date, "%Y-%m-%d")
                    d2 = datetime.today()
                    if (d2-d1).days >= setting.delete_after:
                        session.cwd(folder)
                        for file in session.nlst():
                            if file != "." and file != "..":
                                session.delete(file)
                        session.cwd("../")
                        session.rmd(folder)
        session.mkd(folder_name)
        session.cwd(folder_name)
    else : 
        session.mkd(site_name)
        session.cwd(site_name)
        session.mkd(folder_name)
        session.cwd(folder_name)
    for filename in os.listdir(backup_folder):
        file_path = os.path.join(backup_folder, filename)
        file = open(file_path,'rb')
        session.storbinary('STOR ' + filename, file)
        file.close()
    session.quit()
    return "Backup Completed"


