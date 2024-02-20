<template>
    <ComModal @onPrint="onPrint" :mobileFullscreen="true" @onClose="onClose" @onOk="onSave" width="960px">
        <template #title>
            {{ params.title }}
        </template>
        <template #content>
            <div>
                <v-row v-if="customer.customer">
                    <v-col cols="12" xs="12"  md="4">
                       
                        <div class="elevation-2 p-2 bg-primary text-center ">
                            <div>{{ $t('Actual Amount') }}</div>
                            <div><CurrencyFormat :value="actualAmount" /></div>
                        </div>
                       
                    </v-col>
                    <v-col cols="12" xs="12"  md="4">
                        <div class="elevation-2 p-2 bg-warning text-center">
                            <div>{{ $t('Credit Amount') }}</div>
                            <div><CurrencyFormat :value="creditAmount" /></div>
                        </div>
                    </v-col>
                    <v-col cols="12" xs="12" md="4">
                        <div class="elevation-2 p-2 bg-success text-center">
                            <div>{{ $t('Balance') }}</div>
                            <div><CurrencyFormat :value="balance" /></div>
                        </div>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="12" sm="12">
                        <ComAutoComplete :label="$t('Customer')" v-model="customer.customer"
                            :placeholder="$t('Customer')" doctype="Customer" variant="solo" />
                    </v-col>
                </v-row>
                <div class="d-flex justify-space-between m-1 align-center">
                    <p class="font-weight-bold  pt-6 pb-2">
                        {{ $t('Top Up History') }}
                    </p>
                    <v-btn size="small" @click="addTopUp()" prepend-icon="mdi-plus" color="success" class="">
                        Add Top-Up
                    </v-btn>
                </div>
                <v-row>
                    <v-col cols="12" sm="12" md="12">
                       
                        <v-table>
                            <thead>
                                <tr>
                                    <th class="text-left">
                                        {{ $t('Posting Date') }}
                                    </th>
                                    <th class="text-right">
                                        {{ $t('Amount') }}
                                    </th>
                                    <th class="text-right">
                                        {{ $t('Credit Amount') }}
                                    </th>
                                    <th class="text-right">
                                        {{ $t('Balance') }}
                                    </th>
                                    <th class="text-center">
                                        {{ $t('Status') }}
                                    </th>
                                    <th class="text-left">
                                        {{ $t('Action') }}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="vh in voucherTopUps" :key="vh.name">
                                    <td class="text-left">
                                        {{ moment(vh.posting_date).format('DD-MM-YYYY') }}
                                    </td>
                                    <td class="text-right">
                                        <ComInput :readonly="vh.docstatus==1" v-model="vh.actual_amount" type="currency" :label="$t('Actual Amount')" />
                                    </td>
                                    <td class="text-right">
                                        <ComInput :readonly="vh.docstatus==1" v-model="vh.credit_amount" type="currency" :label="$t('Credit Amount')" />
                                    </td>
                                    <td class="text-right">
                                        <CurrencyFormat :value="vh.balance" />
                                    </td>
                                    <td class="text-center">
                                        <v-chip v-if="vh.docstatus == 1" color="success" density="comfortable" size="small">
                                            {{ $t("Submitted") }}
                                        </v-chip>
                                        <v-chip  v-if="vh.docstatus == 0" color="error" density="comfortable" size="small">
                                            {{ $t("Draft") }}
                                        </v-chip>
                                    </td>
                                    <td class="text-left" style="width:65px">
                                        <v-btn v-if="vh.docstatus!=1" icon="mdi-delete" size="small" color="error" variant="text" type="button" @click="deleteTopUp"/>
                                    </td>
                                </tr>
                            </tbody>
                        </v-table>
                        
                        
                    </v-col>
                </v-row>
                <div>
                </div>
            </div>
        </template>
    </ComModal>
</template>

<script setup>
import { ref, inject,onMounted, i18n } from '@/plugin'
import { watch } from 'vue'
import { createToaster } from "@meforma/vue-toaster";
import ComInput from '../../components/form/ComInput.vue';
import ComModal from '../../components/ComModal.vue';
const moment = inject('$moment')

const { t: $t } = i18n.global;
let workingDay=ref({})
let CashierShift=ref({})
const toaster = createToaster({ position: "top" });
const gv = inject('$gv')
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();

const props = defineProps({
    params: {
        type: Object,
        required: true,
    },
})

const emit = defineEmits(["resolve"])

const voucherTopUps = ref({})

let customer = ref({})
let actualAmount = ref({})
let creditAmount = ref({})
let balance = ref({})

onMounted(async () => {   
    call.get("epos_restaurant_2023.api.api.get_current_cashier_shift",{
            pos_profile: localStorage.getItem("pos_profile")
          }).then((_res)=>{
            if(_res.message){
                CashierShift.value = _res.message
            }
    })
    call.get("epos_restaurant_2023.api.api.get_current_working_day",{business_branch: gv.setting?.business_branch})
    .then((_res)=>{
            if(_res.message){
                workingDay.value = _res.message;
        }
    });
})

watch(() => customer.value.customer, (newValue) => {
    db.getDocList(
        'Voucher',{
        fields: ['posting_date','actual_amount','credit_amount','balance','docstatus'],
        filters: [['customer', '=', customer.value.customer]],
        orderBy: {
                    field: 'modified',
                    order: 'desc',
            }
    }
    ).then((result) => {
        voucherTopUps.value = result
        actualAmount.value = result.reduce((accumulator, currentValue) => {
            return accumulator + currentValue.actual_amount;
        }, 0)
        creditAmount.value = result.reduce((accumulator, currentValue) => {
            return accumulator + currentValue.credit_amount;
        }, 0)
        balance.value = result.reduce((accumulator, currentValue) => {
            return accumulator + currentValue.balance;
        }, 0)
    });
})

function addTopUp(){
    if (customer.value.customer == undefined){
        toaster.warning($t("Please select a customer"))
        return
    }
    voucherTopUps.value.unshift({
        'cashier_shift':CashierShift.value.name,
        'working_day':workingDay.value.name,
        'posting_date':moment(workingDay.value.posting_date).format('YYYY-MM-DD'),
        'customer':customer.value.customer,
        'creation':moment().format('YYYY-MM-DD HH:MM:SS')
    })
}

function onSave(){
    call.post("epos_restaurant_2023.selling.doctype.voucher.voucher.insert_voucher_multiple_row", {
        vouchers: voucherTopUps.value,
       
    }).then((result) => {
      console.log(result)
    }).catch((err) => {
    })
}

function deleteTopUp(){

}
function editTopUp(){

}

function onClose() {
    emit('resolve', false);
}
</script>

