import frappe
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw
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
        current_dir = os.path.dirname(os.path.abspath(__file__))

        filename = "khqr_icon.png"
        logo_path = os.path.join(current_dir, "files", filename)

        if not os.path.isfile(logo_path):
            logo_path = os.path.join(current_dir, "files", "khqr_icon.png")

        logo_img = Image.open(logo_path).convert("RGBA")

        # QR size
        qr_w, qr_h = qr_img.size
        logo_size = int(qr_w * 0.20)

        # Resize logo
        logo_img = logo_img.resize((logo_size, logo_size), Image.LANCZOS)

        # 🔵 Create circular mask
        mask = Image.new("L", (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)

        # Apply mask to logo
        logo_circle = Image.new("RGBA", (logo_size, logo_size))
        logo_circle.paste(logo_img, (0, 0), mask)

        # ⚪ Optional white circular background (recommended)
        padding = 6
        bg_size = logo_size + padding * 2
        bg = Image.new("RGBA", (bg_size, bg_size), (255, 255, 255, 255))

        bg_mask = Image.new("L", (bg_size, bg_size), 0)
        bg_draw = ImageDraw.Draw(bg_mask)
        bg_draw.ellipse((0, 0, bg_size, bg_size), fill=255)

        bg.paste(logo_circle, (padding, padding), logo_circle)

        # Center position
        pos = (
            (qr_w - bg_size) // 2,
            (qr_h - bg_size) // 2
        )

        qr_img.paste(bg, pos, bg_mask)

    # 3️⃣ Output PNG (inline)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    if  not image_base64:
        return Response(buffer.getvalue(), mimetype="image/png")
    
    import base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"