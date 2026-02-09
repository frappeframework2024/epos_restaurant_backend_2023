import frappe
import qrcode
from io import BytesIO
from PIL import Image
from werkzeug.wrappers import Response


@frappe.whitelist(allow_guest=True)
def generate_qr(data: str, size: int = 4, border: int = 1, use_logo=False, currency=None, image_base64=False):
    """
    Generate QR code with optional center logo (PNG, inline response)
    """

    size = int(size)
    border = int(border)

    # 1️⃣ Build QR (HIGH error correction for logo)
    qr = qrcode.QRCode(
        version=None,  # auto
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGBA")

    # 2️⃣ Add logo if provided
    if use_logo:
        import os
        # directory of api.py
        current_dir = os.path.dirname(os.path.abspath(__file__))

        filename ="qr_center_log.png"
        if currency:
            filename = f"{currency.lower()}_icon.png"

        # path to files/my_file_name.pgn
        logo_path = os.path.join(current_dir, "files", filename)
        
        if not os.path.isfile(logo_path):
            logo_path = os.path.join(current_dir, "files", "qr_center_log.png")


        # optional: normalize path
        logo_path = os.path.normpath(logo_path)
        logo_img = Image.open(logo_path).convert("RGBA")
        # Resize logo (15% of QR)
        qr_w, qr_h = qr_img.size
        logo_size = int(qr_w * 0.15)
        logo_img = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
        # Optional: white background for logo (recommended)
        padding = 4
        bg_size = (logo_size + padding*2, logo_size + padding*2)
        bg = Image.new("RGBA", bg_size, (255, 255, 255, 255))
        bg.paste(logo_img, (padding, padding), logo_img)

        # Center position
        pos = (
            (qr_w - bg_size[0]) // 2,
            (qr_h - bg_size[1]) // 2
        )

        qr_img.paste(bg, pos, bg)

    # 3️⃣ Output PNG (inline)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    if  not image_base64:
        return Response(buffer.getvalue(), mimetype="image/png")
    
    import base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"