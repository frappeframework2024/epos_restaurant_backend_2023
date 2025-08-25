<template>
    <ComModal @onClose="onClose" @onOk="onSend" titleOKButton="Send" :loading="loading" :fullscreen="false">
        <template #title>
            {{$t("Re-Send")  }}
        </template>
        <template #content> 

            <span v-if="selectedPrinters.length > 0" v-for="printer, index in  selectedPrinters"  :key="index" >
                <v-chip size="small" style="margin-right: 5px; margin-bottom: 5px;" >{{ printer }}</v-chip>
            </span> 
            <ComResendGroupSaleProductList />
        </template>
    </ComModal>
</template>
<script setup>
import ComResendGroupSaleProductList from "@/views/sale/components/ComResendGroupSaleProductList.vue";
import {  inject,i18n ,ref} from '@/plugin'
import { computed } from "vue"; 
import {createToaster} from '@meforma/vue-toaster'; 
const toaster = createToaster({ position: "top-right" });

const { t: $t } = i18n.global;  

const sale = inject('$sale')
var frappe = inject("$frappe")
const call = frappe.call();

const emit = defineEmits(["resolve"]);
const dataSeletedPrinters= ref([]);


const selectedPrinters = computed(()=>{
    var printers = []
    dataSeletedPrinters.value = [];
    sale.reSendSaleProductKOT.forEach((r)=> { 
        (r.temp_printers||[]).filter((x)=>x.selected == true).forEach((p)=>{
            if(!printers.includes(p.printer)){
                printers.push(p.printer )
                dataSeletedPrinters.value.push(p.printer)
            }
        }) 
    });  
    return printers;  
}); 
function onClose() {
    emit("resolve", false);
}

async function onSend() { 
  if(dataSeletedPrinters.value.length > 0){
    var resendProductData = []
    for(const r of sale.reSendSaleProductKOT){ 
         if(sale.setting.pos_setting.combo_menu_print_captain_by_items_printer && r.is_combo_menu){
            const combo_data = JSON.parse(r.combo_menu_data)
            let productCodes = combo_data.map(i => i.product_code);
            const res = await call.post("epos_restaurant_2023.api.api.get_product_printer_by_products", {
                    "product_codes":productCodes
            });    
            const printers = (r.temp_printers||[]).filter((x)=>x.selected == true);        
            const combo_product_printers = res["message"]            

            for(const pro of combo_data ){
                const p_printers = combo_product_printers.filter(r=>r.product_code == pro.product_code)
                for(const p of p_printers){ 
                    ///check combo item is exist printer match
                    const match_printers =  printers.filter(r=> r.printer == p.printer_name)                        
                    if( match_printers.length > 0){
                        resendProductData.push({
                            sale_product_name: r.name,
                            printer: p.printer_name,
                            group_item_type: p.group_item_type,
                            is_label_printer: p.is_label_printer == 1,
                            ip_address: p.ip_address,
                            port: p.port,
                            usb_printing:p.usb_printing,
                            product_code: pro.product_code,
                            product_name_en: pro.product_name,
                            product_name_kh: pro.product_name_kh,
                            kitchen_group: pro.kitchen_group||"",
                            kitchen_group_sort_order: pro.kitchen_group_sort_order || 0,
                            seat_number: r.seat_number||"",
                            portion: r.portion,
                            unit: r.unit,
                            modifiers: r.modifiers,
                            note: r.note,
                            quantity: r.quantity * (pro.quantity || 1),
                            is_deleted: false,
                            is_free: r.is_free == 1,
                            combo_menu: r.product_name,
                            combo_menu_data: null,
                            order_by: r.order_by,
                            creation: r.creation,
                            modified: r.modified,
                            is_timer_product: (r.is_timer_product || 0),
                            reference_sale_product: r.reference_sale_product,
                            duration: r.duration,
                            time_stop: (r.time_stop || 0),
                            time_in: r.time_in,
                            time_out_price: r.time_out_price,
                            time_out: r.time_out,
                            reprint:true,
                            amount: r.amount
                        })
                    }
                }
            }

         }else{
            (r.temp_printers||[]).filter((x)=>x.selected == true).forEach((p)=>{ 
                resendProductData.push({
                    sale_product_name: r.name,
                    printer: p.printer,
                    group_item_type: p.group_item_type,
                    is_label_printer: p.is_label_printer == 1,
                    ip_address: p.ip_address,
                    port: p.port,
                    usb_printing:p.usb_printing,
                    product_code: r.product_code,
                    product_name_en: r.product_name,
                    product_name_kh: r.product_name_kh,
                    kitchen_group:r.kitchen_group||"",
                    kitchen_group_sort_order: r.kitchen_group_sort_order || 0,
                    seat_number: r.seat_number||"",
                    portion: r.portion,
                    unit: r.unit,
                    modifiers: r.modifiers,
                    note: r.note,
                    quantity: r.quantity,
                    is_deleted: false,
                    is_free: r.is_free == 1,
                    combo_menu: r.combo_menu,
                    combo_menu_data:r.combo_menu_data,
                    order_by: r.order_by,
                    creation: r.creation,
                    modified: r.modified,
                    is_timer_product: (r.is_timer_product || 0),
                    reference_sale_product: r.reference_sale_product,
                    duration: r.duration,
                    time_stop: (r.time_stop || 0),
                    time_in: r.time_in,
                    time_out_price: r.time_out_price,
                    time_out: r.time_out,
                    reprint:true,
                    amount: r.amount
                })
            }) 


        }
    };   
    if(resendProductData.length>0){
        await   sale.onPrintToKitchen(sale.sale,resendProductData)
    } 
    toaster.success($t("Product was re-send"));
  }else{
    toaster.warning($t("Select printer for re-send"));
  }
}


</script>