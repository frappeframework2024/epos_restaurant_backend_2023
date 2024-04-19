<template>
 <div class="bg-slate-100 mb-3 rounded-lg p-3 relative ">
    <div class="absolute inline-flex items-center justify-center text-white text-xs font-bold text-white hg-white rounded-full -top-3 -left-0">
        <v-chip v-if="data.is_free" size="x-small" color="success" variant="outlined">
        <span style="color: white !important;">{{$t('Free')}}</span>
        </v-chip>
        <span v-if="data.is_free" class="bg-red-100 text-red-800 text-xs font-medium me-2 px-2.5 py-0.5 rounded-full dark:bg-red-900 dark:text-red-300">{{$t('Free')}}</span>    
        <span v-if="data.deleted" class="bg-red text-white text-xs font-medium me-2 px-2.5 py-0.5 rounded-full dark:bg-red-900 dark:text-red-300"><v-icon class="text-white" style="font-size: 14px;">mdi-delete</v-icon> {{$t('Deleted')}}</span>
    <span v-if="data.deleted_by" class="bg-red text-white text-xs font-medium me-2 px-2.5 py-0.5 rounded-full dark:bg-red-900 dark:text-red-300"><v-icon class="text-white" style="font-size: 14px;">mdi-delete</v-icon> {{$t(data?.deleted_by)}}</span>
    </div>{{data.deleted_by}}
<div class="text-md">
  {{ data.quantity }}   <v-icon class="text-black" style="font-size: 20px;">mdi-close</v-icon>  {{ $t(data.product_name) }} <spna v-if="data.product_name_kh">- {{ $t(data.product_name_kh) }} {{ getPortion() }} </spna>   
</div>

        <div class="ms-3">
            
        <div v-if="data.modifiers">{{ data.modifiers }}</div>
        <div v-if="data.combo_menu">combo:{{ data.combo_menu }}</div>
        <div v-if="data.note">Note:{{ data.note }}</div>
        </div>
        {{ data.loading }}
<hr class="my-2">
<div v-if="!data.deleted" class="flex gap-2">

        <v-btn v-if="data.kod_status=='Pending' || data.kod_status=='Processing' " :loading="data.loading && data.change_status=='Done'"  @click="onChangeStatus('Done')"> <v-icon left>mdi-check-circle</v-icon> </v-btn>
        <v-btn  v-if="data.kod_status=='Done'" :loading="data.loading && data.change_status=='Pending'"  @click="onChangeStatus('Pending')">Recall</v-btn>
        
        <v-btn v-if="data.kod_status=='Pending'" :loading="data.loading && data.change_status=='Processing'" @click="onChangeStatus('Processing')">Processing</v-btn>
        <v-btn  v-if="data.kod_status=='Processing'" :loading="data.loading && data.change_status=='Pending'" @click="onChangeStatus('Pending')">Pending</v-btn>
</div>
<div>
    
<div v-if="data.deleted_note">
    <div class="w-full bg-white text-sm p-2 rounded-lg">
{{data.deleted_note}}
    </div>
</div>

    
</div>
    
    </div>
</template>
<script setup>

import {  i18n ,inject} from '@/plugin';
    const props = defineProps({ 
        data:Object
    })
    const kod = inject("$kod")
    const { t: $t } = i18n.global;

    function getPortion(){
        if(!props.data.portion || props.data.portion=="Normal"){
            return ""
        }else {
            return " - " + props.data.portion
        }
    }

    function onChangeStatus(status){
        kod.onChangeStatus({
            data:props.data,
            status:status,
            sale_product_names:[props.data.name]
        })
    }

</script>
