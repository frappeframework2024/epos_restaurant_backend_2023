import frappe

from epos_restaurant_2023.api.api import get_sale_list_table_badge


@frappe.whitelist()
def get_data(date):

    tables=frappe.get_all(
        "Tables Number",
        fields=[
            "name",
            "tbl_number",
            "tbl_group",
            "shape",
            "width",
            "height"
        ],
        order_by="sort_order asc"
    )


    api_data=get_sale_list_table_badge(data={"date": date,"pos_profile":"Main POS Profile"})

    reservations=api_data.get("data",[]) if isinstance(api_data,dict) else api_data
    reservations=sorted(reservations, key=lambda x: x.get("sale_status_priority", 0))

    booking_map={}

    for r in reservations:

        booking_map.setdefault(
            r.get("table_id"),
            []
        ).append(r)


    result=[]


    for table in tables:

        bookings=booking_map.get(
            table.name,
            []
        )

        booking=bookings[0] if bookings else None


        bg="#4F9DD9"
        color="#ffffff"
        status="available"


        if booking:

            status="booking"

            bg=booking.get(
                "background_color",
                "#EC864B"
            )

            color=booking.get(
                "color",
                "#ffffff"
            )


        result.append({

            "name":table.name,
            "tbl_number":table.tbl_number,
            "tbl_group":table.tbl_group or "Other",

            "status":status,

            "booking_count":len(bookings),

            "bookings":bookings,
            "width":table.width or 100,
            "height":table.height or 80,

            "border_radius":
                "50%" if table.shape=="Circle" else "10px",

            "background_color":bg,
            "text_color":color,
        })


    return {
        "tables":result
    }