import frappe
from barcode import get
from barcode.writer import ImageWriter
from io import BytesIO

@frappe.whitelist()
def generate_barcode(bcid="code128", text=None, show_text="true"):
    if not text:
        frappe.throw("Barcode text is required")
    bcid = bcid.lower()
    supported = ["code128", "code39", "ean13", "ean8"]
    if bcid not in supported:
        frappe.throw("Unsupported barcode type")
    try:
        options = {
            "module_width": 0.4,
            "module_height": 15,
            "quiet_zone": 0.5,
            "font_size": 10,
            "text_distance": 3.5,
            "write_text": True if show_text == "true" else False,
            "dpi": 400
        }
        output = BytesIO()
        barcode = get(
            bcid,
            text,
            writer=ImageWriter()
        )
        barcode.write(output, options)
        frappe.local.response.filename = "barcode.png"
        frappe.local.response.filecontent = output.getvalue()
        frappe.local.response.type = "download"
        frappe.local.response.display_content_as = "inline"
        frappe.local.response.content_type = "image/png"
    except Exception as e:
        frappe.log_error(
            title="Barcode Generation Error",
            message=str(e)
        )
        frappe.throw(str(e))
