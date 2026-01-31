<template lang="">
    <div  class="flex-col flex" style="height: 100vh;width:100%">
        <div  class="d-flex align-center justify-center  flex-col flex" style="height: 100vh;">
            <div>SCAN HERE</div>
            <img width="250" :src="qrGenerateURL" alt="QR Code"/>
        </div>
        <div class="mt-auto bg-green-600 border border-gray-500 text-white rounded-sm px-1 pt-1">
            <div class="mb-1 flex justify-between text-sm">
                <div style="font-size:20px;font-family: Khmer OS Siemreap;">{{$t('Balance')  }} ({{sale.setting.pos_setting.main_currency_name}}):</div>
                <div style="font-size:20px">
                    <CurrencyFormat :value="props.data.balance" />
                </div>
            </div>
            <div class="mb-1 flex justify-between text-sm">
                <div style="font-size:20px;font-family: Khmer OS Siemreap;">{{ $t('Balance') }} ({{sale.setting.pos_setting.second_currency_name}}):</div>
                <div style="font-size:20px">
                    <CurrencyFormat :value="props.data.balance * props.data.exchange_rate" :currency="sale.setting.pos_setting.second_currency_name"/>                
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { inject,computed } from '@/plugin';
const sale = inject('$sale')
const props = defineProps({
    data: Object,
    aba_data: Object
})
const qrGenerateURL = computed(() =>
  `/api/method/epos_restaurant_2023.api.qr.generate_qr?data=${props.aba_data.qrString}`
)

</script>
 