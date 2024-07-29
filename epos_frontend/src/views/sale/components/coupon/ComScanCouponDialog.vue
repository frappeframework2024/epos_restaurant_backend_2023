<template>
    <ComModal :fullscreen="mobile" @onClose="onClose" :loading="loading" @onOk="onSeachCoupon()">
      <template #title>
        {{ $t('Scan Coupon Code') }}
      </template>
      <template #content>
        <v-alert icon="mdi-cards-outline" prominent type="success" variant="outlined" class="mb-2">
          {{ $t('msg.Please enter or scan coupon code') }}.
        </v-alert>
        <ComInput v-model="couponCode" autofocus :placeholder="$t('Scan Membership Card Number')" variant="outlined"
          density="default" />
      </template>
    </ComModal>
</template> 
<script setup>
    import { ref, defineEmits, watch,inject,createToaster,i18n, keyboardDialog } from '@/plugin'
    import ComInput from '@/components/form/ComInput.vue';
    const toaster = createToaster({ position: 'top-right' })
    import { useDisplay } from 'vuetify';
    const sale = inject('$sale');

    const saleCoupon = ref()

    const { t: $t } = i18n.global;
    const couponCode = ref("")
    const emit = defineEmits(["resolve", "reject"])

    async function onSeachCoupon () {
        saleCoupon.value = await sale.onRequestCouponCode(couponCode._value)
        if (saleCoupon.value.status == 1) {
            let inputNumber = await keyboardDialog({ title: $t("Claim Amount"), type: 'number', value: saleCoupon.value.balance });
            if (inputNumber) {
                if (inputNumber > saleCoupon.value.balance) {
                    toaster.warning($t("msg.Please input equal or smaller amount"));
                    return;
                }else {
                    alert('smaller')
                    sale.sale.cash_coupon_items = []
                    sale.sale.cash_coupon_items.push({'coupon_code':couponCode._value,'claim_amount':inputNumber})
                    emit("resolve", true)
                    toaster.warning($t("msg.Coupon apply successfully"));
                }
            }
        }
    }

    function onClose() {
        emit("resolve", false);
    }

    function onRequestCouponCode(code){
        sale.onRequestCouponCode(code)
    }
</script>