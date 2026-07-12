frappe.pages['table-booking-box-vi'].on_page_load=function(wrapper){
    new TableBookingBoxView(wrapper);
};

class TableBookingBoxView{
    constructor(wrapper){
        this.page=frappe.ui.make_app_page({
            parent:wrapper,
            title:"Table Booking",
            single_column:true
        });

        let self=this;

        this.date=this.page.add_field({
            label:"Date",
            fieldtype:"Date",
            default:frappe.datetime.get_today(),
            change(){
                self.load();
            }
        });

        this.page.set_secondary_action("Refresh",()=>this.load());

        this.content=$(`<div class="table-booking-wrapper"></div>`).appendTo(this.page.main);

        this.load();
    }

    load(){
        frappe.call({
            method:"epos_restaurant_2023.selling.page.table_booking_box_vi.table_booking_box_vi.get_data",
            args:{
                date:this.date.get_value()
            },
            callback:(r)=>{
                this.render(r.message || {tables:[]});
            }
        });
    }

    format_time(time){
        if(!time) return "";

        let p=time.split(":");
        let h=parseInt(p[0]);
        let m=p[1];

        let ap=h>=12?"PM":"AM";

        h=h%12;
        if(h===0) h=12;

        return `${h}:${m} ${ap}`;
    }

    render(data){
        let groups={};

        data.tables.forEach(t=>{
            let g=t.tbl_group || "Other";
            if(!groups[g]) groups[g]=[];
            groups[g].push(t);
        });

        let html="";

        Object.keys(groups).forEach((g,i)=>{
            html+=`
            <div class="table-group">

                <div class="group-header" data-id="${i}">
                    <span>${g}</span>
                    <span>${groups[g].length} Tables</span>
                </div>

                <div id="group-${i}" class="table-box-container">
                    ${frappe.render_template("table_booking_box_vi",{tables:groups[g]})}
                </div>

            </div>`;
        });

        this.content.html(html);

        $(".group-header").click(function(){
            $("#group-"+$(this).data("id")).slideToggle(150);
        });


        $(".table-box").click((e)=>{

            let id=$(e.currentTarget).data("name");

            let table=data.tables.find(x=>x.name==id);

            if(!table || !table.bookings.length){
                frappe.msgprint("No booking");
                return;
            }


            let rows="";

            table.bookings.forEach(b=>{

                let time=this.format_time(b.arrival_time);

                if(b.check_out_time){
                    time+=" - "+this.format_time(b.check_out_time);
                }


                rows+=`
                <tr class="booking-row" data-name="${b.name}" style="cursor:pointer">

                    <td>
    <a href="#" class="booking-link" data-sale-type-status="${b.sale_type_status}" data-name="${b.name}">
        ${b.name}
    </a>
</td>

                    <td>${b.customer_name || ""}</td>

                    <td>${b.guest_cover || 0} Pax</td>

                    <td>${time}</td>
					<td>${b.sale_type_status}</td>
					
					<td>
    <span class="status-tag"
    style="
        background:${b.status_background || '#64748b'};
        color:${b.status_color || '#fff'};
    ">
        ${b.rs_sale_status || ""}
		
    </span>
</td>

                </tr>`;
            });


            let dialog=new frappe.ui.Dialog({
                title:table.tbl_number+" Booking",
                size:"large",
                fields:[
                    {
                        fieldtype:"HTML",
                        options:`
                        <table class="table table-bordered">

                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Guest</th>
                                    <th>Pax</th>
                                    <th>Time</th>
									<th>Sale Status</th>
									<th>Status</th>
                                </tr>
                            </thead>

                            <tbody>
                                ${rows}
                            </tbody>

                        </table>`
                    }
                ]
            });


            dialog.show();


            $(".booking-row").click(function(){

                frappe.set_route(
                    "Form",
                    "POS Reservation",
                    $(this).data("name")
                );

            });
		$(document).on("click", ".booking-link", function(e){
    e.preventDefault();

    let status=$(this).attr("data-sale-type-status") || "";
    status=status.trim().toLowerCase();

    let doctype=status=="booked" ? "POS Reservation" : "Sale";

    console.log("Status:",status,"Doctype:",doctype);

    frappe.set_route(
        "Form",
        doctype,
        $(this).attr("data-name")
    );
});

        });
    }
}