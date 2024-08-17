<template>
    <ComModal width="800px" @onClose="onClose" @onOk="onPayClick" titleOKButton="Pay">
        <template #title>
            <div>Quick Pay</div>
        </template>
        <template #content>
            <div class="grid gap-1" :class="mobile ? 'grid-cols-3 text-sm' : 'grid-cols-2'">
                <template v-for="(pt, index) in gv.setting?.payment_types" :key="index">
                    <div  @click="onPaymentTypeClick(pt)" class="border rounded-sm px-2 py-4 text-center cursor-pointer bg-orange-100 hover:bg-orange-300 flex justify-center items-center"
                        :class="selectedPaymentType == pt.payment_method ? 'bg-orange-300' : ''">
                        <div>
                            {{ pt.payment_method }}
                        </div>
                    </div>
                </template>

            </div>
        </template>
    </ComModal>
</template>
<script setup>
import { defineEmits, inject } from '@/plugin'
import { payToRoomDialog, createToaster, payToCityLedgerDialog,confirmDialog, payDeskfolioDialog, i18n, computed, keyboardDialog } from '@/plugin';
import { ref } from 'vue';
import { useDisplay } from 'vuetify'
const emit = defineEmits(['resolve'])
const gv = inject('$gv')
const props = defineProps({
    params: Object
})
function onClose() {
    emit('resolve', false)
}
const selectedPaymentType = ref("")
const paymentObject = ref({})
const { mobile } = useDisplay()

const sale = ref({})
const { t: $t } = i18n.global;
const toaster = createToaster({ position: "top-right" });

async function onPaymentTypeClick(pt) {
    selectedPaymentType.value = pt.payment_method
    let room = null;
    let folio_transaction_number = null
    let folio_transaction_type = null
    let folio = null
    let city_ledger_name = null
    let desk_folio = null
    let reservation_stay = null
    if (pt.payment_type_group == "Pay to Room") {
        if (sale.paymentInputNumber <= 0) {
            toaster.warning($t("msg.Please enter payment amount"));
            return
        }

        const result = await payToRoomDialog({
            data: pt
        });

        //
        if (result == false) {
            return
        }
        room = result.room;
        if (pt.use_room_offline == 0) {

            folio = result.folio;
            folio_transaction_number = result.folio;
            folio_transaction_type = "Reservation Folio"
            reservation_stay = result.reservation_stay

            sale.customer = result.guest
            sale.customer_name = result.guest_name
        }

    }
    else if (pt.payment_type_group == "City Ledger") {
        const result = await payToCityLedgerDialog({
            data: pt
        });
        //if close
        if (result == false) {
            return
        }

        folio_transaction_number = result.folio_transaction_number;
        folio_transaction_type = "City Ledger"
        city_ledger_name = result.city_ledger_name
    }
    else if (pt.payment_type_group == "Desk Folio") {
        const result = await payDeskfolioDialog({
            data: pt
        });
        //if close
        if (result == false) {
            return
        }

        folio_transaction_number = result.folio_transaction_number;
        folio_transaction_type = "Desk Folio"
        desk_folio = result.desk_folio
    }


    //check if payment exist manual fee

    let fee_amount = 0;
    if (pt.is_manual_fee == 1) {
        const fee = await keyboardDialog({ title: $t("Enter Fee Amount"), type: 'number', value: 0 });
        if (!fee) {
            return;
        }
        fee_amount = fee;
    }

     paymentObject.value = { paymentType: pt, amount: inputAmount.value * pt.exchange_rate, fee_amount: fee_amount, room: room, folio: folio, folio_transaction_type: folio_transaction_type, folio_transaction_number: folio_transaction_number, city_ledger_name: city_ledger_name, reservation_stay: reservation_stay }
}



const balance = computed(() => {
    if (sale?.balance > 0) {
        return Number(sale.value.balance.toFixed(gv.setting.pos_setting.main_currency_precision));
    } else {
        return 0;
    }
})

const inputAmount = computed(() => {

    let totalSum = props.params.data.reduce((sum, item) => {
        return sum + item.grand_total;
    }, 0);
    return Number(totalSum);

})
async function onPayClick(){
    
    if(await confirmDialog({ title: $t("Quick Pay"), text: $t('are you sure to process quick pay and close order') })){
        emit("resolve", paymentObject.value);
    }
    
}

</script>