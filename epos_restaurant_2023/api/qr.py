import frappe
import qrcode
from io import BytesIO
from werkzeug.wrappers import Response

@frappe.whitelist(allow_guest=True)
def generate_qr(data: str, size: int = 4, border: int = 1):
    """
    Generate a QR code as PNG (inline, not saved to File storage).
    
    Args:
        data (str): The data to encode in the QR
        size (int): Box size (default 4, smaller = smaller QR pixels)
        border (int): Border/quiet zone (default 1, minimal white space)
    
    Returns:
        Response: PNG image response
    """
    # Ensure integers
    size = int(size)
    border = int(border)

    # Build QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save in memory
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Return directly as image (not saved to DB/storage)
    return Response(buffer.getvalue(), mimetype="image/png")
