
<template> 
    <div  class="text-white text-sm px-1 py-1 cursor-pointer">
        <div> 
            <div class="flex items-center justify-end gap-3"> 
                <div style="font-size: 24px; line-height: 1.5;">
                    <div class="text-xl"><span style="color: #ccc">Temporary:</span> <CurrencyFormat :value="sale.sale.grand_total" /></div>
                    <div style="font-size: 12px; color: #ccc">*Note: Total excluding VAT</div>
                </div>
                <button class="bg-teal-600 hover:bg-teal-900 text-white font-bold py-4 px-4 rounded" v-ripple @click="onViewDetail">{{$t('View Ordered items')}}</button>
            </div>
        </div>
    </div> 
    
</template>

<script setup>
import { inject,computed, smallViewSaleProductListModal,i18n  } from '@/plugin' 
import { createToaster } from "@meforma/vue-toaster";
const toaster = createToaster({ position: "top-right" });
const { t: $t } = i18n.global;
const sale = inject('$sale');
const lastProduct = computed(()=>{
    return sale.sale?.sale_products?.find(r=>r.selected == true)
})

const checkNewSaleNoSaleProducts = computed(()=>{
    if((sale.sale.name||'')=='' && (sale.sale.sale_products||[]).length <=0){
        return true;
    } 
    return false;
    
})

async function onViewDetail(){
    if(checkNewSaleNoSaleProducts.value){
        toaster.warning( $t('msg.Please select a menu item to continue'));
       
        return;
    }
    const result = await smallViewSaleProductListModal ({title: sale.sale.name, value:  ''});
}
</script> 