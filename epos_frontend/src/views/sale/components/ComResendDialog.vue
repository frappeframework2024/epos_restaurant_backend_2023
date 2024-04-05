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

function onSend() { 
  if(dataSeletedPrinters.value.length > 0){
    var resendProductData = []
    sale.reSendSaleProductKOT.forEach((r)=> { 
        (r.temp_printers||[]).filter((x)=>x.selected == true).forEach((p)=>{            
            resendProductData.push({
                printer: p.printer,
                group_item_type: p.group_item_type,
                is_label_printer: p.is_label_printer == 1,
                ip_address: p.ip_address,
                port: p.port,
                usb_printing:p.usb_printing,
                product_code: r.product_code,
                product_name_en: r.product_name,
                product_name_kh: r.product_name_kh,
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
                time_out: r.time_out
            })
        }) 
    });   
    if(resendProductData.length>0){
        sale.onPrintToKitchen(sale.sale,resendProductData)
    } 
    toaster.success($t("Product was re-send"));
  }else{
    toaster.warning($t("Select printer for re-send"));
  }
}


</script>