<template>
    <div @click="onChangeStatus(data.kod_status == 'Done' ? 'Pending' : 'Done') "

        class="cursor-pointer mb-3 rounded-lg px-2 pb-1 relative bg-slate-100" :class="(data.kod_status == 'Done' && !isSummary ) ? 'opacity-75' : '' , data.loading ? 'pointer-events-none' : ''  " >
 <template v-if="isSummary">
        <div  :style="{ 'font-size': kod.setting.font_size - 3 + 'px' }" class="flex gap-2 pt-1 flex-wrap">
            <div class="flex item-center gap-2 bg-slate-300 rounded-full px-2">
                <v-icon class="m-auto" style="font-size:15px;">mdi-table-furniture</v-icon>
                {{ data.table_no }} <template v-if="kod.setting.show_outlet_name" >- {{ data.outlet }} </template> 
            </div> 
            
              <div class="flex item-center gap-2 whitespace-nowrap bg-slate-300 rounded-full px-2">
                <v-icon class="text-black m-auto" style="font-size: 15px;">mdi-tag</v-icon>      
                {{data.sale_type }}
            </div>
            <template v-if="!kod.setting.hide_order_information">
            <div  class="flex item-center gap-2 whitespace-nowrap bg-slate-300 rounded-full px-2">
                <v-icon class="text-black m-auto" style="font-size: 15px;">mdi-calendar-clock</v-icon>      
                {{moment(data.order_time).format('HH:mm:ss') }}
            </div>  
            </template>
            
            <div :class="data.css_class ? data.css_class : 'bg-slate-500'" class="flex item-center gap-1 rounded-full px-2 text-white">
                <v-icon class="text-white m-auto" style="font-size: 12px;" >mdi-timer</v-icon> 
                <div class="m-auto">
                    {{ kod.getHour(data.minute_diff) }} 
                </div>
               
            </div>
        </div> 
      </template>  
        <hr v-if="isSummary" class="my-1"> 
        <div class="relative" :class="(kod.setting.default_group_by != 'order_time' && !isSummary)  ? 'pt-6':'pt-1' " >
        <div v-if="kod.setting.default_group_by != 'order_time'" :class="data.css_class ? data.css_class : 'bg-slate-500'"
            class="whitespace-normal rounded-md text-white px-1 inline-block absolute top-1">
            <div v-if="(kod.setting.default_group_by != 'order_time' && !isSummary)" class="flex">
                <v-icon style="font-size:10px;">mdi-timer</v-icon>
                <span  style="font-size:10px;" class="ms-1">{{ kod.getHour(data.minute_diff) }}</span>
            </div>
        </div>

        <div class="w-5 h-5 rounded-md absolute top-0 right-3 "> 
            <div class="flex">
              
                <div v-if="!data.loading" @click="onChangeStatus(data.kod_status == 'Done' ? 'Pending' : 'Done')">
                    <v-icon v-if="data.kod_status == 'Pending'" style="font-size:15px;"  class="-mr-1 opacity-50">mdi-checkbox-blank-circle-outline</v-icon>
                    <v-icon v-if="data.kod_status == 'Processing'" style="font-size:17px;"  class="-mr-1 opacity-50 text-green-600">mdi-timer</v-icon>
                    <v-icon v-if="data.kod_status == 'Done'" style="font-size:20px;"  class="-mr-1 opacity-70 text-green-500">mdi-checkbox-marked-circle-outline</v-icon>
                </div>
                <div v-else>
                    <v-progress-circular
    indeterminate
    color="blue-lighten-2"
    size="15"
  ></v-progress-circular>
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
            :style="{ 'text-decoration': data.deleted ? 'line-through' : '', 'font-size': kod.setting.font_size + 2 + 'px' }"   :class="(kod.group_order_by == 'order_time' || isSummary) ? 'pe-9' : '' , data.kod_status == 'Done' ? 'text-red-400 text-slate-200' : '' " >
            {{ data.quantity }} <v-icon  style="font-size: 20px;">mdi-close</v-icon> {{
                
                kod.setting.show_menu_language=='khmer'? data.product_name_kh:data.product_name

            }} {{ getPortion() }}         
            <template v-if="data.is_free" > <v-chip size="x-small" class="m-0" color="success" variant="outlined"
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

        <hr v-if="data.note || data.deleted_note" class="my-1">

        <div>
            <div v-if="data.note">
                <div :style="{'font-size':(kod.setting.font_size) + 'px'}" class="w-full bg-white p-2 rounded-lg break-words">
                    {{ data.note }}
                </div>
            </div>
            <div v-if="data.deleted_note">
                <div :style="{'font-size':(kod.setting.font_size) + 'px'}" class="w-full bg-white p-2 rounded-lg break-words">
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
    background: rgb(74 222 128);
    border-color: rgb(74 222 128);
}

.warn {
    background: #ffc107;
    border-color: #ffc107;
}

.error {
    background: #f87171;
    border-color: #f87171;
}
.done{
    background: rgb(160, 160, 160);
    border-color: rgb(160, 160, 160);
}
</style>