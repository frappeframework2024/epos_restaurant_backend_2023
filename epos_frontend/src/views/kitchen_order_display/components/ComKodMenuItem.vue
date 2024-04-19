<template>
 <div class="bg-slate-100 mb-3 rounded-lg px-3 pb-3  ">
    <div class=" inline-flex items-center justify-center gap-2  text-xs font-bold text-white hg-white rounded-full">
        <v-chip v-if="data.is_free" size="x-small" color="success" variant="outlined">{{
                $t('Free')
            }}</v-chip>
            
        <v-chip v-if="data.deleted" size="x-small" color="error" variant="outlined">{{
                $t('Deleted')
            }}</v-chip>
    </div>
<div class="text-md">
     
          {{ $t(data.product_name) }} <spna v-if="data.product_name_kh">- {{ $t(data.product_name_kh) }} {{ getPortion() }} </spna> <v-icon class="text-black" style="font-size: 20px;">mdi-close</v-icon>  {{ data.quantity }}   
</div>

        <div class="ms-3">
            
        <div v-if="data.modifiers">modifier:{{ data.modifiers }}</div>
        <div v-if="data.combo_menu">combo:{{ data.combo_menu }}</div>
        <div v-if="data.note">Note:{{ data.note }}</div>
        </div>
        {{ data.loading }}
<hr class="my-2">
<div class="flex gap-2">

        <v-btn v-if="data.kod_status=='Pending' || data.kod_status=='Processing' " :loading="data.loading && data.change_status=='Done'"  @click="onChangeStatus('Done')"> <v-icon left>mdi-check-circle</v-icon> </v-btn>
        <v-btn  v-if="data.kod_status=='Done'" :loading="data.loading && data.change_status=='Pending'"  @click="onChangeStatus('Pending')">Recall</v-btn>
        
        <v-btn v-if="data.kod_status=='Pending'" :loading="data.loading && data.change_status=='Processing'" @click="onChangeStatus('Processing')">Processing</v-btn>
        <v-btn  v-if="data.kod_status=='Processing'" :loading="data.loading && data.change_status=='Pending'" @click="onChangeStatus('Pending')">Pending</v-btn>
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
