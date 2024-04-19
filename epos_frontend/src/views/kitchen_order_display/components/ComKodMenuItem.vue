<template>
 <div class="bg-slate-100 mb-3 rounded-lg p-3">
        {{ $t(data.product_name) }} <v-icon class="text-black" style="font-size: 20px;">mdi-close</v-icon>  {{ data.quantity }} <br>
        Portion: {{ getPortion() }}<br/>
        modifier:{{ data.modifiers }}<br/>
        combo:{{ data.combo_menu }}<br/>
        Note:{{ data.note }}<br/>
        {{ data.loading }}
        <v-chip v-if="data.is_free" size="x-small" color="success" variant="outlined">{{
                $t('Free')
            }}</v-chip>

        <v-btn v-if="data.kod_status=='Pending' || data.kod_status=='Processing' " :loading="data.loading && data.change_status=='Done'"  @click="onChangeStatus('Done')">Done</v-btn>
        <v-btn  v-if="data.kod_status=='Done'" :loading="data.loading && data.change_status=='Pending'"  @click="onChangeStatus('Pending')">Recall</v-btn>
        
        <v-btn v-if="data.kod_status=='Pending'" :loading="data.loading && data.change_status=='Processing'" @click="onChangeStatus('Processing')">Mark as Processing</v-btn>
        <v-btn  v-if="data.kod_status=='Processing'" :loading="data.loading && data.change_status=='Pending'" @click="onChangeStatus('Pending')">Mark as Pending</v-btn>

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
