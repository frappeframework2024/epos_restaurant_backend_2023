<template>
    <div class="bg-white border shadow rounded-lg item" >
    <div :class="data.css_class" class="rounded-t-lg p-2 text-white">
        <div class="flex justify-between">
        <div class="flex item-center gap-2">
       
             <v-icon style="font-size: 20px;">mdi-table-furniture</v-icon>
            {{ data.table_no }} - {{ data.outlet }} 
        </div>
            
         <div class="flex item-center gap-2">
            <v-icon class="text-white" style="font-size: 20px;">mdi-timer</v-icon> 
             {{ kod.getHour(data.minute_diff) }}
         </div>
        
        </div>
        <hr class="my-2">
        <div class="flex justify-between">
            <div class="flex item-center gap-2 whitespace-nowrap">
<v-icon class="text-white" style="font-size: 20px;">mdi-account-outline</v-icon>      {{ data.customer }}
            </div>
            <div class="flex item-center gap-2 whitespace-nowrap">
                <v-icon class="text-white" style="font-size: 20px;">mdi-calendar-clock</v-icon>      
{{moment(data.order_time).format('HH:mm:ss') }}   

 </div>
     </div>
        
    </div>
    <div class="p-2">
          <div  v-for="(p, index) in data.items" :key="index">
            <ComKodMenuItem :data="p"/>
        </div>
       
        <v-btn :loading="data.loading" @click="onChangeStatus('Done')">Done</v-btn>
    </div>
   </div>  
</template>
<script setup>
import moment from '@/utils/moment.js';
import {  i18n ,inject,confirmDialog} from '@/plugin';
import ComKodMenuItem from "@/views/kitchen_order_display/components/ComKodMenuItem.vue"
const props = defineProps({ 
        data:Object
    })
    const kod = inject("$kod")
    const { t: $t } = i18n.global;
    async function onChangeStatus(status){
        if (await confirmDialog({ title: $t("Mark as Done"), text: $t('Are you sure you want to mark as Done for all menus?') })) {
        kod.onChangeStatus({
            status:status,
            data:props.data,
            sale_product_names:props.data.items.map(r => r.name)

        })
    }
    }


</script>
<style scoped>
    .new{
        background: green;
        border-color: rgba(0, 128, 0, 0.609);
    }
    
    .warn{
        background:rgb(236, 236, 1);
        border-color: rgba(236, 236, 1, 0.693);
    }
    .error{
        background:red;
        border-color: rgba(255, 0, 0, 0.71);
    }
    .item {
  width: 33.33%;
  position: relative;
  color: #fff;
  box-sizing: border-box;
}
.item:nth-of-type(4n+1) { order: 1; }
.item:nth-of-type(4n+2) { order: 2; }
.item:nth-of-type(4n+3) { order: 3; }
.item:nth-of-type(4n)   { order: 4; }
</style>