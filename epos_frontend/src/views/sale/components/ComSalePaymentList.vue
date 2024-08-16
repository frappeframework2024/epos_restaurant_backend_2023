<template>
    <div>
 
        <ComPlaceholder :is-not-empty="sale.sale?.payment?.length > 0" icon="mdi-currency-usd" icon-size="30px" :text="$t('No Payment')">
            <div v-if="!is_removing" v-for="(p, index) in sale.sale.payment" :key="index">
                <div class="flex items-center p-1 bg-white rounded-sm mb-1 border border-gray-600">
                    <div class="flex-grow">
                     
                        <div class="font-bold">{{ p.payment_type }} </div>
                        <div class="text-xs text-gray-500" v-if="((p.room_number||'') !='')">{{ $t('Room') }}#:   {{ p.room_number }}</div>       
                        <div class="text-xs text-gray-500" v-if="((p.reservation_stay||'') !='')">{{ $t('Stay ') }}#:   {{ p.reservation_stay }}</div>
                        <div class="text-xs text-gray-500" v-if="get_point_to_reduct(p.input_amount) > 0 && p.payment_type_group == 'Point'">{{ $t('Reduct') }}: {{get_point_to_reduct(p.input_amount)}}{{ $t('Point(s)') }}</div>       
                       

                        <div class="text-xs text-gray-500" v-if="((p.folio_transaction_number||'') !='')">
                            {{ p.folio_transaction_number }}  
                            <span v-if="p.folio_transaction_type == 'City Ledger' ">
                                {{ '('+ p.city_ledger_name +')' }}
                            </span>
                            
                        </div> 
                        <div class="text-xs text-gray-500" v-if="p.currency != sale.setting.pos_setting.main_currency_name">{{ $t('Exchange Rate') }}: 
                            <CurrencyFormat :value="p.exchange_rate" :currency="p.currency" v-if="sale.setting.pos_setting.main_currency_name == sale.setting.pos_setting.exchange_rate_main_currency"/>
                            <CurrencyFormat :value="1/p.exchange_rate" :currency="sale.setting.pos_setting.main_currency_name" v-else/>
                        </div>
                    </div>
                    <div class="flex-none text-right">
                        <CurrencyFormat :value="p.input_amount" :currency="p.currency" />
                        <div class="text-xs text-gray-500" v-if="((p.fee_amount||0)>0)">{{ $t('Fee') }}: 
                            <CurrencyFormat :value="(p.fee_amount||0)" :currency="sale.setting.pos_setting.main_currency_name"/>
                            

                        </div>
                    </div>
                    <div class="flex-none">
                        <v-btn size="small" variant="text" color="error" icon="mdi-delete"
                            @click="onRemovePayment(p)"></v-btn>
                    </div>
                </div>
                
            </div>
        </ComPlaceholder>
    </div>
</template>
<script setup>
import { inject, ref,watch } from '@/plugin';
const sale = inject('$sale')
const socket = inject("$socket")
const gv = inject("$gv")
watch(sale.sale.payment, async (newPayment, oldNewPayment) => {
    socket.emit("ShowOrderInCustomerDisplay", sale.sale, "");
})
const is_removing = ref(false);

function get_point_to_reduct(input_amount){
    let total_point = (input_amount - sale.sale.total_tax ) * gv.setting.point_setting.to_point_sale
    return Number(total_point || 0).toFixed(2)
}
async function  onRemovePayment(p) {
    is_removing.value = true;
    sale.sale.payment.splice(sale.sale.payment.indexOf(p), 1);
    sale.updatePaymentAmount();
    sale.paymentInputNumber = sale.sale.balance.toFixed(sale.setting.pos_setting.main_currency_precision);  

    if( sale.sale.payment.length<=0){
        sale.is_payment_first_load = true;
    } 
    await  setTimeout(function() {
        is_removing.value = false;
    },1);
    
}


</script> 