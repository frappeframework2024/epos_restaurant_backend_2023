import Enumerable from 'linq'
import moment from '@/utils/moment.js';
import {
    ref, i18n
} from "@/plugin"
import { createToaster } from "@meforma/vue-toaster";
import socket from '@/utils/socketio';
import { FrappeApp } from 'frappe-js-sdk';
import NumberFormat from 'number-format.js'

const frappe = new FrappeApp();
const db = frappe.db()
const call = frappe.call()
const { t: $t } = i18n.global;
const toaster = createToaster({ position: "top-right",duration:20 });

export default class KOD {
    constructor() {
        this.business_branch="",
        this.screen_name="",
       this.kpi={}
       this.pending_orders=[],
       this.pending_order_items=[],
       this.loading = false
       this.recent_done_order_items = [],
       this.group_order_by = "sale_number",
        this.setting= {
            default_font_size:14,
            min_font_size:10,
            max_font_size:30,
            font_size:14,
            show_menu_language:"khmer",
            default_group_by:"sale_number"
        }
    }
    

    getKODData(){
        this.loading = true;
        call.get("epos_restaurant_2023.api.kod.get_kod_menu_item",{
            business_branch:this.business_branch,
            screen_name:this.screen_name,
            group_by:this.group_order_by
        }).then(r=>{
            this.kpi = r.message.kpi
            this.pending_orders = r.message.pending_orders
            this.pending_order_items = r.message.pending_order_items
            this.recent_done_order_items = r.message.recent_done
            this.loading = false
        }).catch(err=>{
            this.loading =false
        })
    }

    onChangeStatus(data){
       
        data.data.loading = true
        data.data.change_status=data.status
 
        call.post("epos_restaurant_2023.api.kod.change_status",{
            status:data.status,
            sale_product_names: data.sale_product_names,
            hide_in_kod: data.hide_in_kod || 0
        }).then(r=>{
            data.data.loading = true
            this.getKODData()
        }).catch(err=>{
            data.data.loading = true
        })
    }
    
    onCloseOrder(data){
       
        data.data.loading = true
        data.data.change_status=data.status
        call.post("epos_restaurant_2023.api.kod.close_order",{
            status:data.status,
            sale_product_names: data.sale_product_names
        }).then(r=>{
            data.data.loading = true
            this.getKODData()
        }).catch(err=>{
            data.data.loading = true
        })
    }

    getHour(minutes) {
        if (minutes < 60) {
            return minutes + "mn";
        } else {
            let hours = Math.floor(minutes / 60);
            let remainingMinutes = minutes % 60;
            return hours + "h " + remainingMinutes + "mn";
        }
    }
}
