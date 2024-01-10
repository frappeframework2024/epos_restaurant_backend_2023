<template>
    <ComModal :loading="is_loading" @onClose="onClose" @onOk="onStopClick" titleOKButton="Stop Timer">
        
        <template #title>
            {{ $t('Stop Timer') }}
        </template>
        <template #content>
            Time IN
            <input type="datetime-local" v-model="data.time_in" >
            Time OUT
            <input type="datetime-local" v-model="data.time_out" >
            <hr/>
            <div class="v-table__wrapper">
                <table>
                <thead>
                    <tr>
                        <th>{{$t("Time In")}}</th>
                        <th>{{$t("Time Out")}}</th>
                        <th>{{$t("Time Duration")}}</th>
                        <th class="text-center">{{$t("Time Minute")}}</th>
                        <th class="text-right">{{$t("Time Price")}}</th>
                        <th class="text-right">{{$t("Time Amount")}}</th>
                    </tr>
                    
                </thead>
                <tbody>
                    <tr  v-for="data in breakdownData">
                        <td>
                            {{ moment(data.time_in).format('DD-MM-YYYY') }}
                            <br/>
                            {{ moment(data.time_in).format('hh:mm A') }}
                        </td>
                        <td>
                            {{ moment(data.time_out_price).format('DD-MM-YYYY') }}
                            <br/>
                            {{ moment(data.time_out_price).format('hh:mm A') }}
                        </td>
                        <td>{{ data.duration }}</td>
                        <td>{{ data.total_minute }}</td>
                        <td><CurrencyFormat :value="data.price" /></td>
                        <td><CurrencyFormat :value="data.amount" /></td>
                    </tr>
                    <tr  >
                        <td>{{$t("Total")}}</td>
                        <td>{{ breakdownData.reduce((n, d) => n + (d.amount || 0), 0) }}</td>
                       
                    </tr>
                </tbody>
            </table>
            </div>
            
        </template>

    </ComModal>
</template>
<script setup>
import { ref,inject,onMounted,watch } from '@/plugin'
import { defineEmits } from 'vue';
import { useDisplay } from 'vuetify';
import moment from '@/utils/moment.js';
import { computed } from 'vue';
const sale = inject("$sale")

const frappe = inject("$frappe")
const call = frappe.call()
const { mobile } = useDisplay()
const props = defineProps({
    params: Object
})

const breakdownData = ref([])

 

const emit = defineEmits(["click"])


const data = ref(JSON.parse(JSON.stringify(props.params)))
let is_loading=ref(false)

if (!data.value.time_out){
    data.value.time_out=moment(new Date).format('YYYY-MM-DD HH:mm')
}

watch(() => data.value.time_in, (newValue, oldValue) => {
    getBreakdownData()
});

watch(() => data.value.time_out, (newValue, oldValue) => {
    getBreakdownData()
});

function onStopClick() {
    is_loading.value=true
    call.post("epos_restaurant_2023.api.timer_product.stop_timer", { sale_product: data.value  }).then((result) => {
        sale.sale = result.message
        emit("resolve",
            { 
                time_in: moment(data.value.time_in).format('yyyy-MM-DD HH:mm:ss'),
                time_out: moment(data.value.time_out).format('yyyy-MM-DD HH:mm:ss'),
        });
        is_loading.value=false
    }).catch((err)=>{
        is_loading.value=false
    })
    
}

function onClose() {
    emit("resolve", false);
}

function getBreakdownData(){
    is_loading.value=true
    data.value.price_rule = sale.sale.price_rule 
    data.value.time_in = moment(data.value.time_in).format('YYYY-MM-DD HH:mm:ss')
    data.value.time_out = moment(data.value.time_out).format('YYYY-MM-DD HH:mm:ss')
    call.post("epos_restaurant_2023.api.timer_product.get_timer_product_breakdown", { sale_product: data.value  }).then((result) => {
        breakdownData.value = result.message
        is_loading.value=false
    }).catch((res)=>{
        is_loading.value=false
    })
}
onMounted(() => {
    getBreakdownData()
})

</script>