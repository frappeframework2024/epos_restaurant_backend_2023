import hashlib
import base64
from io import BytesIO
import os

from PIL import Image
import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def resize_image(image_path, width=None, height=None):
        # Determine if the file is private or public

 
    try:
        # Validate input parameters
        width = int(width) if width else None
        height = int(height) if height else None
    except ValueError:
        frappe.throw(_("Width and height must be integers"), exc=frappe.ValidationError)

    if not width and not height:
        frappe.throw(_("Please provide either width or height"), exc=frappe.ValidationError)

    if (width and width <= 0) or (height and height <= 0):
        frappe.throw(_("Dimensions must be positive integers"), exc=frappe.ValidationError)

    # Generate unique cache key
    cache_key = hashlib.sha256(f"{image_path}-{width}-{height}".encode()).hexdigest()

    # Check cache
    cached_data = frappe.cache().get(cache_key)
    if cached_data:
        return {
            'status': 'success',
            'image': cached_data.decode('utf-8'),
            'cached': True
        }

    # Fetch and process image
    try:
        base64_image = process_local_image(image_path, width, height)
    except Exception as e:
        frappe.throw(_(f"Error processing image: {str(e)}"), exc=frappe.ValidationError)

    # Store in cache for 24 hours
    frappe.cache().set(cache_key, base64_image, ex=86400)

    return {
        'status': 'success',
        'image': base64_image,
        'cached': False
    }

def process_local_image(image_path, target_width, target_height):
    file_path = ""
    if image_path.startswith("/private/files/"):
        file_path = frappe.get_site_path("private", "files", os.path.basename(image_path))
    else:
        file_path = frappe.get_site_path("public", "files", os.path.basename(image_path))

    # Validate file path
    if not os.path.exists(file_path):
        raise Exception(_("File does not exist"))

    # Process image
    try:
        with Image.open(file_path) as img:
            original_width, original_height = img.size
            format = img.format or 'JPEG'

            # Calculate target dimensions
            if not target_width and target_height:
                target_width = int(original_width * (target_height / original_height))
            elif not target_height and target_width:
                target_height = int(original_height * (target_width / original_width))

            # Maintain aspect ratio using thumbnail
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

            # Convert to base64
            output = BytesIO()
            img.save(output, format=format, quality=85)
            base64_image = base64.b64encode(output.getvalue()).decode('utf-8')

            # Format the base64 string with proper prefix
            mime_type = f'image/{format.lower()}'
            return f"data:{mime_type};base64,{base64_image}"

    except Exception as e:
        raise Exception(_("Invalid image file")) from e