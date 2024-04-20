<template>
    <div @click="onChangeStatus(data.kod_status == 'Done' ? 'Pending' : 'Done') "
        class=" mb-3 rounded-lg px-2 pb-1 relative bg-slate-100" :class="data.kod_status == 'Done' ? 'opacity-75' : ''  " >
 <template v-if="isSummary">
        <div  :style="{ 'font-size': kod.setting.font_size + 'px' }" class="flex justify-between ">
            <div class="flex item-center gap-2">
                <v-icon class="m-auto" style="font-size:15px;">mdi-table-furniture</v-icon>
                {{ data.table_no }} - {{ data.outlet }} 
            </div> 
            <div class="flex item-center gap-1">
                <v-icon class="text-black m-auto" style="font-size: 15px;">mdi-timer</v-icon> 
                {{ kod.getHour(data.minute_diff) }}
            </div>
           
        </div> 
        <div  :style="{ 'font-size': kod.setting.font_size + 'px' }" class="flex justify-between">
            <div class="flex item-center gap-2 whitespace-nowrap">
                <v-icon class="text-black m-auto" style="font-size: 15px;">mdi-tag</v-icon>      
                {{data.sale_type }}
            </div>
            <div class="flex item-center gap-2 whitespace-nowrap">
                <v-icon class="text-black m-auto" style="font-size: 15px;">mdi-calendar-clock</v-icon>      
                {{moment(data.order_time).format('HH:mm:ss') }}
            </div>
           
        </div>  
      </template>   
        <hr v-if="isSummary" class="my-1">  
        <div class="relative" :class="(kod.group_order_by != 'order_time' && !isSummary)  ? 'pt-6':'pt-1' " >
        <div v-if="kod.group_order_by != 'order_time'" :class="data.css_class ? data.css_class : 'bg-slate-500'"
            class="whitespace-normal rounded-md text-white px-1 inline-block absolute top-1">
            <div v-if="!isSummary" class="flex">
                <v-icon style="font-size:10px;">mdi-timer</v-icon>
                <span style="font-size:10px;" class="ms-1">{{ kod.getHour(data.minute_diff) }}</span>
            </div>
        </div>
        <div class="w-5 h-5 rounded-md absolute top-0 right-3 ">
            <div class="flex">
                <div @click="onChangeStatus(data.kod_status == 'Done' ? 'Pending' : 'Done')">
                    <v-icon v-if="data.kod_status == 'Pending'" style="font-size:15px;"  class="-mr-1 opacity-50">mdi-checkbox-blank-circle-outline</v-icon>
                    <v-icon v-if="data.kod_status == 'Done'" style="font-size:15px;"  class="-mr-1 opacity-70 text-green-500">mdi-checkbox-marked-circle-outline</v-icon>
                </div>
                <div>
                <v-menu >
                    <template v-slot:activator="{ props }">
                        <v-icon v-bind="props">mdi-dots-vertical</v-icon>
                    </template>
                    <v-list>
                        <v-list-item @click="onChangeStatus('Done')"
                            v-if="(data.kod_status === 'Pending' || data.kod_status === 'Processing') && !data.deleted">
                            <v-list-item-title>Done</v-list-item-title>
                        </v-list-item>
                        <v-list-item v-if="data.kod_status == 'Done' && data.deleted == 0"
                            :loading="data.loading && data.change_status == 'Pending'" @click="onChangeStatus('Pending')">
                            <v-list-item-title>Recall</v-list-item-title>
                        </v-list-item>
                        <v-list-item v-if="data.kod_status == 'Pending' && data.deleted == 0"
                            :loading="data.loading && data.change_status == 'Processing'"
                            @click="onChangeStatus('Processing')">
                            <v-list-item-title>Processing</v-list-item-title>
                        </v-list-item>
                        <v-list-item v-if="data.kod_status == 'Processing' && data.deleted == 0"
                            :loading="data.loading && data.change_status == 'Pending'" @click="onChangeStatus('Pending')">
                            <v-list-item-title>Pending</v-list-item-title>
                        </v-list-item>

                        <v-list-item v-if="data.deleted == 1 || data.kod_status == 'Done'"
                            :loading="data.loading && data.change_status == 'Done'" @click="onHideOrder('Done')">
                            <v-list-item-title>{{ $t("Hide") }}</v-list-item-title>
                        </v-list-item>

                    </v-list>
                </v-menu>
            </div>
            </div>
        </div>
        <div
            :style="{ 'text-decoration': data.deleted ? 'line-through' : '', 'font-size': kod.setting.font_size + 2 + 'px' }">
            {{ data.quantity }} <v-icon class="text-black" style="font-size: 20px;">mdi-close</v-icon> {{
                
                kod.setting.show_menu_language=='khmer'? data.product_name_kh:data.product_name

            }} {{ getPortion() }}         
            <template v-if="data.is_free" > <v-chip size="x-small" class="ma-2" color="success" variant="outlined"
    >
    {{ $t('Free') }}
    </v-chip></template>
        </div>
        <div class="ms-3" :style="{'font-size':(kod.setting.font_size) + 'px'}">

            <div v-if="data.modifiers">{{ data.modifiers }}</div>
            <div v-if="data.combo_menu">
                <div v-for="(c, index) in data.combo_menu.split('|')" :key="index">
                    {{ c }}
                </div>
            </div>

        </div>

        <hr v-if="data.note || data.deleted_note" class="my-2">

        <div>
            <div v-if="data.note">
                <div class="w-full bg-white text-sm p-2 rounded-lg">
                    {{ data.note }}
                </div>
            </div>
            <div v-if="data.deleted_note">
                <div class="w-full bg-white text-sm p-2 rounded-lg">
                    {{ data.deleted_note }}
                </div>
            </div>


        </div>

    </div>
</div>
</template>
<script setup>
import moment from '@/utils/moment.js';
import { i18n, inject, ref } from '@/plugin';

const props = defineProps({
    data: Object ,
    isSummary: {
    type: Boolean,
    default: false
  }
})
const kod = inject("$kod")
const { t: $t } = i18n.global;

function getPortion() {
    if (!props.data.portion || props.data.portion == "Normal") {
        return ""
    } else {
        return " - " + props.data.portion
    }
}

function onChangeStatus(status) {
    if (props.data.deleted == 1)
        return
    kod.onChangeStatus({
        data: props.data,
        status: status,
        sale_product_names: [props.data.name]
    })
}
function onHideOrder(status) {

    kod.onChangeStatus({
        data: props.data,
        status: status,
        sale_product_names: [props.data.name],
        hide_in_kod: 1
    })
}

</script>
<style scoped>
.new {
    background: green;
    border-color: rgba(0, 128, 0, 0.609);
}

.warn {
    background: #ffc107;
    border-color: #ffc107;
}

.error {
    background: red;
    border-color: rgba(255, 0, 0, 0.71);
}
.done{
    background: rgb(160, 160, 160);
    border-color: rgb(160, 160, 160);
}
</style>