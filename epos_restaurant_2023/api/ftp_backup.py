# Copyright (c) 2023, ratha and contributors
# For license information, please see license.txt

import frappe
import os, shutil
import shlex, subprocess
from frappe.model.document import Document
from frappe.utils import cstr,password
import asyncio
from datetime import datetime
from frappe import conf
import os
import requests

@frappe.whitelist()
def run_on_startup():
    key = "startup_backup_ran"
    if frappe.cache().get_value(key):
        return "not run"
    frappe.cache().set_value(key, 1, expires_in_sec=60 * 60 * 24)
    site_name = cstr(frappe.local.site)
    command = "bench --site " + site_name + " backup"
    asyncio.run(run_bench_command(command))
    frappe.enqueue(upload_to_ftp,timeout=3600)
    return "run"


@frappe.whitelist()
def get_current_site_name(): 
    return cstr(frappe.local.site)

@frappe.whitelist()
def execute_backup_command(): 
    frappe.publish_realtime("backup_database", {"message": "Backing Up Database"},user=frappe.session.user)
    frappe.enqueue(run_backup_command,queue="long")

@frappe.whitelist()
def execute_repair_table():
    frappe.enqueue(method=repair_table,queue="long",show_msg=1)

def repair_table(show_msg=0):
    if show_msg == 1:
        frappe.publish_realtime("repair_database", {"message": "Repairing Database"},user=frappe.session.user)
    data = frappe.db.sql("SELECT concat('REPAIR Table `',TABLE_NAME,'`;') script FROM information_schema.TABLES WHERE table_schema='{0}' AND table_type='BASE TABLE'".format(frappe.conf.get("db_name")),as_dict=1)
    for a in data:
        frappe.db.sql(a.script)
    frappe.db.commit()
    if show_msg == 1:
        frappe.publish_realtime("repair_database", {"message": "Database Repaired"},user=frappe.session.user)

@frappe.whitelist()
def check_table():
    frappe.publish_realtime("check_database", {"message": "Checking Database"},user=frappe.session.user)
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
    if setting.enabled_clear_logs:
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
    repair_table()
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
            frappe.throw('Failed to delete %s. Reason: %s' % (file_path, e))
    command = ""
    if backup_type == "Simple":
        command = "bench --site " + site_name + " backup"
    elif backup_type == "Full":
        command = "bench --site " + site_name + " backup --with-files"
    else:
        command = "bench --site " + site_name + " backup"
    asyncio.run(run_bench_command(command))
    frappe.enqueue(upload_to_ftp,timeout=3600)

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
    folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    setting = frappe.get_doc('FTP Backup')
    site_name = setting.ftp_folder_name if setting.ftp_folder_name != '' else cstr(frappe.local.site)
    backup_folder = setting.ftp_backup_path
    if backup_folder is None or backup_folder == '' :
        backup_folder = frappe.utils.get_site_path(conf.get("backup_path", "private/backups"))
    ftp_password = password.get_decrypted_password("FTP Backup", "FTP Backup", fieldname="ftp_password",raise_exception=False)
    ftp_port = 21
    if frappe.get_meta("FTP Backup").has_field("ftp_port"):
        ftp_port = setting.ftp_port or 21
    session = connect_ftp(setting.ftp_url, ftp_port, setting.ftp_user, ftp_password)
    try:
        if site_name in session.nlst():
            session.cwd(site_name)
            for folder in session.nlst():
                if folder != "." and folder != ".." and "_" in folder:
                    created_date = folder.split("_", 1)[0]
                    if len(created_date) == 10 :
                        d1 = datetime.strptime(created_date, "%Y-%m-%d")
                        d2 = datetime.today()
                        if (d2-d1).days >= setting.delete_after:
                            session.cwd(folder)
                            for file in session.nlst():
                                if file != "." and file != "..":
                                    session.delete(file)
                            session.cwd("../")
                            session.rmd(folder)
            if folder_name not in session.nlst():
                session.mkd(folder_name)
            session.cwd(folder_name)
        else : 
            session.mkd(site_name)
            session.cwd(site_name)
            session.mkd(folder_name)
            session.cwd(folder_name)
        for filename in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, filename)
            with open(file_path, 'rb') as file:
                session.storbinary(f'STOR {filename}', file, blocksize=64 * 1024)
    finally:
        try:
            session.quit()
        except Exception:
            session.close()
    frappe.publish_realtime("backup_database", {"message": "Database Backup Successfully"},user=frappe.session.user)

def connect_ftp(host, port, user, password):
    from ftplib import FTP, FTP_TLS, error_perm
    timeout = 120
    try:
        ftps = FTP_TLS()
        ftps.connect(host, port, timeout=timeout)
        ftps.login(user, password)
        ftps.prot_c()
        ftps.encoding = "latin-1"
        return ftps
    except (error_perm, OSError):
        ftp = FTP()
        ftp.connect(host, port, timeout=timeout)
        ftp.login(user, password)
        ftp.encoding = "latin-1"
        return ftp