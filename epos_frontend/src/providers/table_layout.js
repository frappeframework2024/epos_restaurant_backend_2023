import Enumerable from 'linq'

import { createResource, i18n } from "@/plugin"
import { createToaster } from "@meforma/vue-toaster";
import { FrappeApp } from 'frappe-js-sdk';

const frappe = new FrappeApp();
const call = frappe.call()
const { t: $t } = i18n.global;


const toaster = createToaster({ position: "top-right" });
export default class TableLayout {
    constructor() {
        this.isLoading = false;
        this.setting = null;
        this.tab = null;
        this.currentView = "table_group";
        this.table_groups = [];  
        this.tempTableGroups =[];
        this.canArrangeTable = false;
        this.getTableGroups();
        this.saleList = [];
        this.saleLoading = true;
        this.saveTablePositionResource = null;
        this.initSaveTablePositionResource()
    }

    //end constructor
    initSaveTablePositionResource() {
        const parent = this;
        this.saveTablePositionResource = createResource({
            url: "epos_restaurant_2023.api.api.save_table_position",
            onSuccess(d) {
                toaster.success($t("msg.Save successfully"));
                localStorage.setItem("table_groups", JSON.stringify(parent.table_groups));
                parent.onEnableArrangeTable(false);
            }
        })
    }

    getSaleList(pos_profile = "") {
        const parent = this;
        this.saleLoading = true;
        let body = {
            data:{
                pos_profile: pos_profile == ""? localStorage.getItem("pos_profile") : pos_profile,
            }
        }
        
        call.post("epos_restaurant_2023.api.api.get_sale_list_table_badge",body).then((resp)=>{
            const data = resp.message;
            parent.table_groups.forEach(function (g) {
                g.tables.forEach(function (t) {
                    t.sales = data.filter(r => r.tbl_group == g.table_group && r.tbl_number == t.tbl_no)
                    if (t.sales.length > 0) {
                        t.guest_cover = t.sales.reduce((n, r) => n + r.guest_cover, 0)
                        t.grand_total = t.sales.reduce((n, r) => n + r.grand_total, 0)
                        t.background_color = t.sales.sort((a, b) => a.sale_status_priority - b.sale_status_priority)[0].sale_status_color;
                        t.creation = Enumerable.from(t.sales).orderBy("$.creation").select("$.creation").toArray()[0]
                    } else {
                        t.guest_cover = 0;
                        t.grand_total = 0;
                        t.creation = null;
                        t.background_color = t.default_bg_color;
                    } 
                }) 
            })

            if(parent.tempTableGroups){
                parent.tempTableGroups.forEach(function (g) {
                    g.tables.forEach(function (t) {
                        t.sales = data.filter(r => r.tbl_group == g.table_group && r.tbl_number == t.tbl_no)
                        if (t.sales.length > 0) {
                            t.guest_cover = t.sales.reduce((n, r) => n + r.guest_cover, 0)
                            t.grand_total = t.sales.reduce((n, r) => n + r.grand_total, 0)
                            t.background_color = t.sales.sort((a, b) => a.sale_status_priority - b.sale_status_priority)[0].sale_status_color;
                            t.creation = Enumerable.from(t.sales).orderBy("$.creation").select("$.creation").toArray()[0]
                        } else {
                            t.guest_cover = 0;
                            t.grand_total = 0;
                            t.creation = null;
                            t.background_color = t.default_bg_color;
                        } 
                    }) 
                })
            } 

            this.saleList = data;
            this.saleLoading = false;
        }) 
    }


    getTempTableGroup(table_groups = undefined, pos_profile=""){ 
        if(pos_profile==""){
            this.getTableGroups();            
        }else{
            this.tempTableGroups = table_groups
        }

    }

    getTableGroups() { 
        if (localStorage.getItem("table_groups") != 'null' && localStorage.getItem("table_groups") != 'undefined') {
            this.table_groups = JSON.parse(localStorage.getItem("table_groups"));
            this.tempTableGroups = this.table_groups;
        }
    }

    onResizeEnd(t) {
        return function (d) {
            t.h = d.h;
            t.w = d.w;
            t.x = d.x;
            t.y = d.y;

        }
    }

    onEnableArrangeTable(status) {
        this.canArrangeTable = status;
    }
}


