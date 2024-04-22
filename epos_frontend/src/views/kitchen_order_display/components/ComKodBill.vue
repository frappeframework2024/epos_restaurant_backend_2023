<template>
    <div :class="data.css_class" class="bg-white border-x-2 border-b-2 shadow rounded-lg item" >
    <div :class="data.css_class" class="rounded-t-lg p-2 text-white">
        <div class="flex justify-between">

        <div class="flex item-center gap-2">
       
             <v-icon style="font-size: 20px;">mdi-table-furniture</v-icon>
            {{ data.table_no }} 
            <span v-if="kod.setting.show_outlet_name">- {{ data.outlet }} </span>
            <span v-if="kod.setting.hide_order_information==1">- {{ $t(data.sale_type) }} </span>
            
        </div>
            
         <div class="flex item-center gap-2">
            <v-icon class="text-white" style="font-size: 20px;">mdi-timer</v-icon> 
             {{ kod.getHour(data.minute_diff) }}
         </div>
        
    </div>
    </div>
<div v-if="kod.setting.hide_order_information==0" :style="{ 'font-size': kod.setting.font_size + 'px' }" class="rounded-t-lg p-2 text-black">
        <div class="flex justify-between">
                <div class="flex item-center gap-2 whitespace-nowrap">
                    <v-icon class="text-black" style="font-size: 20px;">mdi-account-outline</v-icon>{{ data.customer }}
                </div>
            <div class="flex item-center gap-2 whitespace-nowrap">
                <v-icon class="text-black" style="font-size: 20px;">mdi-calendar-clock</v-icon>      
                {{moment(data.order_time).format('HH:mm:ss') }}
            </div>
        </div>
        <div class="flex justify-between">
                <div class="flex item-center gap-2 whitespace-nowrap">
                    <v-icon class="text-black" style="font-size: 20px;">mdi-file-document</v-icon>{{ data.sale_number }}
                </div>
            <div class="flex item-center gap-2 whitespace-nowrap">
                <v-icon class="text-black" style="font-size: 20px;">mdi-tag</v-icon>      
                {{ $t(data.sale_type) }}
            </div>
        </div>
        
    </div>
    <hr>
    <div class="p-2">
          <div  v-for="(p, index) in data.items.filter(r=>!r.deleted)" :key="index">
            <ComKodMenuItem :data="p"/>
        </div>
        <div class="border-b-2 border-red-600 mb-2" v-if="data.items.filter(r=>r.deleted).length>0">
            <div  class="w-full border-b-2 border-red-600 mb-2"> <span
                class="bg-red text-white text-xs font-medium me-2 px-2.5 py-0.5 rounded-t-lg dark:bg-red-900 dark:text-red-300"><v-icon
                    class="text-white" style="font-size: 14px;">mdi-delete</v-icon> {{ $t('Deleted') }}</span></div>
            <div  v-for="(p, index) in data.items.filter(r=>r.deleted)" :key="index">
            <ComKodMenuItem :data="p" />
        </div>

        </div>
        
        <v-btn :loading="data.loading" @click="onChangeStatus('Done')" block>
            <template></template>
            <span v-if="data?.items.filter(r=>r.kod_status != 'Done').length>0"> {{ $t('Done all')}} </span>
            <span v-else >{{ $t('Close') }} </span>
            </v-btn>
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
        kod.onCloseOrder({
            status:status,
            data:props.data,
            sale_product_names:props.data.items.map(r => r.name)

        })
    }
    }


</script>
<style scoped>
    .new{
        background: rgb(74 222 128);
        border-color: rgb(74 222 128);
    }
    
    .warn{
        background: #ffc107;
    border-color: #ffc107;
    }
    .error{
        background:#f87171;
        border-color: #f87171;
    }
    .done{
    background: rgb(160, 160, 160);
    border-color: rgb(160, 160, 160);
}
</style>