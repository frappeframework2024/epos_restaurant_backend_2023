import frappe
from frappe import _
from functools import wraps
from frappe.rate_limiter import rate_limit
def api_rate_limit(limit=10, seconds=120):
    def decorator(func):
        limited_func = rate_limit(
            limit=limit,
            seconds=seconds
        )(func)

        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                return limited_func(*args, **kwargs)

            except frappe.exceptions.ValidationError as e:

                message = str(e)

                if "rate limit" in message.lower():
                    return api_error(
                        _(message),
                        429
                    )

                    return

                raise

        return wrapper

    return decorator

def api_error(message, status_code=422):
    frappe.local.message_log = []
    frappe.local.response.pop("_server_messages", None)    
    frappe.local.response.pop("message", None)
    frappe.local.response.update({
        "status":False,
        "error": message,
        "http_status_code": status_code
    })
    return

def api_response(response, limit_start=None):
    frappe.local.message_log = []
    frappe.local.response.pop("_server_messages", None)
    frappe.local.response.pop("message", None)
    _response = {
        "http_status_code": 200,
        "status":True
    } 
    if limit_start:
        _response.update({
            "limit_start":limit_start,
        })
        
    _response.update({
         **_response,
        "data":response,
    })
    
        
    frappe.local.response.update(_response)
    return


