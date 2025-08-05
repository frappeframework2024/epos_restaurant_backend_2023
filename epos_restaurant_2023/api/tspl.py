import struct
import frappe
# Label specifications
label_width_mm = 30.0
label_height_mm = 20.0
gap_mm = 2.0

# Printer DPI (assuming 203 DPI which is common for label printers)
dpi = 203
dots_per_mm = dpi / 25.4

# Calculate dimensions in dots
width_dots = int(label_width_mm * dots_per_mm)
height_dots = int(label_height_mm * dots_per_mm)
gap_dots = int(gap_mm * dots_per_mm)

# TSPL Commands
tspl_commands = [
    f"SIZE {label_width_mm:.1f} mm, {label_height_mm:.1f} mm",
    f"GAP {gap_mm:.1f} mm, 0",
    "CLS",
    # BITMAP command will go here - see below for implementation
    "PRINT 1"
]

@frappe.whitelist()
def get_command():
    # Example usage:
    bitmap_cmd, bitmap_data = image_to_tspl_bitmap("/home/erpuser/frappe_2024/apps/epos_restaurant_2023/epos_restaurant_2023/api/nv_test.bmp")
    tspl_commands.insert(3, bitmap_cmd)
    return (bitmap_cmd,bitmap_data)
    

def image_to_tspl_bitmap(image_path, threshold=128):
    """Convert an image to TSPL bitmap format"""
    from PIL import Image
    
    # Open image and convert to grayscale
    img = Image.open(image_path).convert('L')
    
    # Resize to match your desired dimensions (in pixels)
    width_px = int(label_width_mm * dots_per_mm)
    height_px = int(label_height_mm * dots_per_mm)
    img = img.resize((width_px, height_px))
    
    # Convert to 1-bit monochrome using threshold
    img = img.point(lambda p: 255 if p > threshold else 0, '1')
    
    # Convert image data to bytes in TSPL format
    # Each byte represents 8 pixels (MSB first)
    bytes_per_row = (width_px + 7) // 8
    bitmap_data = bytearray()
    
    for y in range(height_px):
        for x in range(0, width_px, 8):
            byte = 0
            for bit in range(8):
                if x + bit < width_px:
                    pixel = img.getpixel((x + bit, y))
                    if pixel == 0:  # Black pixel
                        byte |= 1 << (7 - bit)
            bitmap_data.append(byte)
    
    # Generate BITMAP command
    x_pos = 0  # X position on label
    y_pos = 0  # Y position on label
    mode = 0   # Overwrite mode
    
    bitmap_cmd = f"BITMAP {x_pos},{y_pos},{bytes_per_row},{height_px},{mode},"
    
    # Return both the command and the binary data
    return bitmap_cmd, bitmap_data


 