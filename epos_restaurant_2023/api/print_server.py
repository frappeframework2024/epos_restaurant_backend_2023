import requests
import frappe
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

PRINT_SERVER_PORT = 19100
PRINT_SERVER_CACHE_KEY = "epos_restaurant_print_server_url"
PRINT_SERVER_CACHE_SECONDS = 24 * 60 * 60
RETRY_TIMEOUT =[5,15,30]


def _normalize_print_server_url(url):
    if not url:
        return ""

    if isinstance(url, bytes):
        url = url.decode()

    url = url.strip().rstrip("/")
    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"

    return url


def _is_ready_print_server(url, timeout=0.8):
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        if response.status_code != 200:
            return False

        result = response.json()
        return result.get("ok") == True and result.get("status") == "ready"
    except Exception:
        return False


def _get_local_subnets():
    addresses = set()

    try:
        host_name = socket.gethostname()
        addresses.update(socket.gethostbyname_ex(host_name)[2])
    except Exception:
        pass

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        addresses.add(sock.getsockname()[0])
    except Exception:
        pass
    finally:
        try:
            if sock:
                sock.close()
        except Exception:
            pass

    subnets = []
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
            if ip.version == 4 and not ip.is_loopback:
                subnets.append(ipaddress.ip_network(f"{address}/24", strict=False))
        except Exception:
            pass

    return subnets


def _find_print_server_url():
    candidates = []
    for subnet in _get_local_subnets():
        for ip in subnet.hosts():
            candidates.append(f"http://{ip}:{PRINT_SERVER_PORT}")

    with ThreadPoolExecutor(max_workers=64) as executor:
        future_map = {executor.submit(_is_ready_print_server, url): url for url in candidates}
        for future in as_completed(future_map):
            if future.result():
                return future_map[future]

    return ""


def get_print_server_url():
    configured_url = _normalize_print_server_url(frappe.conf.get("print_server_url"))
    if configured_url:
        return configured_url

    cache = frappe.cache()
    cached_url = _normalize_print_server_url(cache.get_value(PRINT_SERVER_CACHE_KEY))
    if cached_url:
        return cached_url

    discovered_url = _find_print_server_url()
    if discovered_url:
        try:
            cache.set_value(
                PRINT_SERVER_CACHE_KEY,
                discovered_url,
                expires_in_sec=PRINT_SERVER_CACHE_SECONDS
            )
        except TypeError:
            cache.set_value(PRINT_SERVER_CACHE_KEY, discovered_url)
            cache.expire(PRINT_SERVER_CACHE_KEY, PRINT_SERVER_CACHE_SECONDS)
        return discovered_url

    raise Exception(f"Print server not found on local subnet port {PRINT_SERVER_PORT}")


def _get_print_queue_names(data):
    if not data:
        return []

    if isinstance(data, dict):
        return [data.get("print_queue")] if data.get("print_queue") else []

    return [x.get("print_queue") for x in data if x.get("print_queue")]


def _mark_success_jobs(success_jobs,retry= 0,print_server_url=""):
    if len(success_jobs)>0:
        sql="update `tabPrint Queue` set status = 'Success',retry = %(retry)s,print_server_url=%(print_server_url)s where name in %(names)s"
        frappe.db.sql(sql,{"names":success_jobs,"retry":retry,"print_server_url":print_server_url})


def _mark_failed_jobs(failed_jobs, retry = 0, failed_jobs_data=None,print_server_url=""):
    for j in failed_jobs:
        sql="update `tabPrint Queue` set status = 'Fail',retry=%(retry)s, error_text=%(error)s,print_server_url=%(print_server_url)s where name = %(name)s"
        frappe.db.sql(sql,{"name":j.get("print_queue"),"retry":retry,"error":j.get("error"),"print_server_url":print_server_url})
    
    if failed_jobs_data and retry<3:
        time.sleep(RETRY_TIMEOUT[retry])

        frappe.enqueue(
            "epos_restaurant_2023.api.print_server.process_print",
            queue="long",
            data=failed_jobs_data,
            retry=retry + 1
        )




def _get_error_jobs(data, error):
    return [{"print_queue": name, "error": error} for name in _get_print_queue_names(data)]


def _request_print(data,print_server_url=None):
    if not print_server_url:
        print_server_url = get_print_server_url()
    
    response = requests.post(
        f"{print_server_url}/print",
        json=data,
        timeout=30
    )

    result = response.json()
    if not result:
        return [], []

    results = result.get("results") or []

    success_jobs = [x.get("print_queue") for x in results if x.get("ok") == True]
    failed_jobs = [x for x in results if x.get("ok") == False]

    return success_jobs, failed_jobs


def process_print(data=None,retry = 0, run_commit = True):
    # data is list of print queue
    
    if isinstance(data,dict):
        data = [data]
    print_server_url = get_print_server_url()
    try:
        
        success_jobs, failed_jobs = _request_print(data,print_server_url)
     
        _mark_success_jobs(success_jobs,retry,print_server_url)
        
        fail_jobs_names = [x.get("print_queue") for x in failed_jobs]
        failed_jobs_data = [x for x in data if x.get("print_queue") in fail_jobs_names ]
        _mark_failed_jobs(failed_jobs,retry,failed_jobs_data, print_server_url)



    except Exception as e:
        failed_jobs = _get_error_jobs(data, str(e))
        fail_jobs_names = [x.get("print_queue") for x in failed_jobs]
        failed_jobs_data = [x for x in data if x.get("print_queue") in fail_jobs_names ]
        _mark_failed_jobs(failed_jobs,retry,failed_jobs_data,print_server_url)
        

    finally:
        if run_commit:
            frappe.db.commit()
