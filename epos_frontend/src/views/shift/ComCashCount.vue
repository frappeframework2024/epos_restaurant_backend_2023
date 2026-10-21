<template>
    <ComDialogContent :hideButtonClose="true" @onOK="onSave">
        <div v-if="cashCountSetting">
            <div class="flex w-full gap-3">
                <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">{{ $t('Open Cash Float') }} </span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="doc.reduce((n, r) => n + r.opening_amount, 0)" />
                        </span></span>
                </div>
                 <div
                    class="bg-green-50 border-green-edoor flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">{{ $t('Cash In Hand') }} </span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="doc.reduce((n, r) => n + r.input_system_close_amount/r.exchange_rate, 0)" />
                        </span></span>
                </div>
                <div class="bg-white flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">{{ $t('Actual Cash') }} </span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="totalCashCountAmount" />
                        </span></span>
                </div>
                
                <div :class="((totalCashCountAmount - doc.reduce((n, r) => n + r.input_system_close_amount/r.exchange_rate, 0)) || 0).toFixed(2)< 0 ? 'bg-red' : 'bg-green'" class="bg-red flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">{{ $t('Difference') }} </span><span
                        class="text-xl line-height-2 font-semibold text-end">
                        <span>
                            <CurrencyFormat :value="((totalCashCountAmount - doc.reduce((n, r) => n + r.input_system_close_amount/r.exchange_rate, 0)) || 0)" />
                        </span>
                    </span>
                </div>
            </div>
            <table class="w-full mt-4">
                <tbody>
                <tr>
                    <td class="w-auto border-1 p-2 font-semibold">{{ $t('Note Type') }} </td>
                    <td class="w-auto border-1 p-2 font-semibold">{{ $t('Total Note') }} </td>
                    <td class="w-auto border-1 p-2 font-semibold text-right">{{ $t('Total Amount') }} </td>
                </tr> 
                <template v-for="(c, index) in getcurrency" :key="index">
                    <tr>
                        <td colspan="3" style='background: rgb(243, 243, 243);' class="w-auto border-1 p-2 font-semibold">
                            CASH {{ c[0].currency }}
                        </td>
                    </tr>
                    <tr v-for="(n, index) in cashCountSetting.filter(r => r.currency == c[0].currency)" :key="index">
                        <td class="w-auto border-1 p-2" style='background: rgb(243, 243, 243);'>
                            {{ n.label }}
                        </td>
                        <td class="w-auto border-1 p-2" style='background: rgb(243, 243, 243);'>
                            <ComInput v-model="n.total_note"/>
                        </td>
                        <td class="w-auto border-1 p-2 font-semibold text-right" style='background: rgb(243, 243, 243);'>
                            <CurrencyFormat :value="n.value * (n.total_note || 0)" :currency="c[0].currency" />
                        </td>

                    </tr>
                    <tr>
                        <td class="w-auto border-1 p-2"><strong>{{ $t('Total') }} </strong></td>
                        <td class="w-auto border-1 p-2 font-semibold">
                           
                        </td>
                        <td class="w-auto border-1 p-2 font-semibold text-right">
                            <strong>
                            <CurrencyFormat
                                :value="cashCountSetting?.filter(r => r.currency == c[0].currency).reduce((n, d) => n + (d.total_note || 0) * (d.value || 0), 0)"
                                :currency="c[0].currency" />
                            </strong>

                        </td>
                    </tr>
                </template>
            </tbody>
            </table>
             <div style="display: flex; justify-content: end; margin-top: 20px;">
                <v-btn @click="onSave" color="primary" style="font-family: Khmer OS Siemreap;">{{ $t('Save') }}</v-btn>
             </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, computed } from "@/plugin"
const cashCountSetting = ref()

const doc = ref()
const exchangeRates = ref()
import ComInput from '../../components/form/ComInput.vue';
const dialogRef = inject("dialogRef")
const mainCurrency = ref()
const secondCurrency = ref()
const totalCashCountAmount = computed(() => {
    let totalCashCount = 0
    if (cashCountSetting.value?.filter(r => r.total_note > 0 & r.currency == mainCurrency.value).length > 0) {
        totalCashCount = totalMainCashCountAmount.value
    } else {
        totalCashCount = doc.value.main_total_close_amount || 0
    }
    if (cashCountSetting.value?.filter(r => r.total_note > 0 & r.currency == secondCurrency.value).length > 0) {
        const exchange_rate = exchangeRates.value?.find(r => r.to_currency == secondCurrency.value).exchange_rate
        totalCashCount = totalCashCount + totalSecondCashCountAmount.value / exchange_rate
    } else {
        const exchange_rate = exchangeRates.value?.find(r => r.to_currency == secondCurrency.value).exchange_rate
        totalCashCount = totalCashCount + ((doc.value.second_total_close_amount || 0) / exchange_rate)
    }
    return totalCashCount
})

const totalMainCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r => r.currency == mainCurrency.value).reduce((n, d) => n + (d.total_note * d.value || 0) / d.exchange_rate, 0)
})

const totalSecondCashCountAmount = computed(() => {
    return cashCountSetting.value?.filter(r => r.currency == secondCurrency.value).reduce((n, d) => n + (d.total_note * d.value || 0), 0)
})

function onSave(){
     cashCountSetting.value.forEach(function (d) {
        d.total_amount = (d.total_note || 0) * (d.value || 0)
        d.total_base_currency_amount = d.total_amount>0 ? d.total_amount / d.exchange_rate : 0
    });
    dialogRef.value.close({
        cash_count_setting:cashCountSetting.value
    })
}

onMounted(() => {
    cashCountSetting.value = dialogRef.value.data.cash_count_setting
    doc.value = dialogRef.value.data.doc
    exchangeRates.value = dialogRef.value.data.exchange_rates
    mainCurrency.value = dialogRef.value.data.mainCurrency
    secondCurrency.value = dialogRef.value.data.secondCurrency
})

const getcurrency = computed(() => {
    return cashCountSetting.value?.reduce((groups, item) => {
        const key = item.currency;

        if (!groups[key]) {
            groups[key] = [];
        }

        groups[key].push(item);
        return groups;
    }, {});
});
</script>