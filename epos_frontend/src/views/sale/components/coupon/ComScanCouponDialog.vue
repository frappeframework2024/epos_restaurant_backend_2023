<template>
    <ComModal :fullscreen="mobile" @onClose="onClose" :loading="loading"  :titleOKButton="($t('Confirm'))" @onOk="onConfirmCoupon">
      <template #title>
        {{ $t('Scan Coupon Code') }}
      </template>
      <template #content>
        <v-alert icon="mdi-cards-outline" prominent type="success" variant="outlined" class="mb-2">
          {{ $t('Please enter or scan coupon code') }}.
          <span>{{$t('Maximum amount for claim')}}: <CurrencyFormat :value="sale.sale.grand_total || 0" /></span>
         
        </v-alert>
        <div class="position-relative">
            <form v-on:submit.prevent="onSeachCoupon">
                <ComInput v-model="couponCode" autofocus :placeholder="$t('Scan Membership Card Number')" variant="outlined" density="default" />
                <div class="position-absolute" style="right:10px;top:10px;"><v-btn @click="onSeachCoupon" color="success">{{$t('Check')}}</v-btn></div>
            </form>
        </div>
 
            
        <ComTableView v-if="sale.sale.cash_coupon_items?.length > 0">
            <template #header>
                <tr>
                    <th>{{$t('Coupon Code')}}</th>
                    <th class="text-end">{{$t('Coupon Amount')}}</th>
                    <th class="text-center">{{$t('Delete')}}</th>
                </tr>
            </template>
            <template #body>
                <tr v-for="(c, index) in sale.sale.cash_coupon_items" :key="index">
                    <td>{{ c.coupon_code }}</td>
                    <td class="text-end"><CurrencyFormat :value="c.claim_amount" /></td>
                    <td class="text-center"><v-icon @click="onRemoveClaimCoupon(index)" color="red">mdi-delete</v-icon></td>
                </tr>
            </template>
        </ComTableView>
            
          <!-- </div> -->
      </template>
    </ComModal>
</template> 
<script setup>
    import { ref, defineEmits, watch,inject,createToaster,i18n, keyboardDialog,onMounted } from '@/plugin'
    import ComInput from '@/components/form/ComInput.vue';
    const toaster = createToaster({ position: 'top-right' }) 
    const sale = inject('$sale');

    const loading = ref(false)

    const saleCoupon = ref()
    const cashCouponItemsBackup = ref([])

    const { t: $t } = i18n.global;
    const couponCode = ref("")
    const emit = defineEmits(["resolve", "reject"])

    onMounted(()=>{
        if( sale.sale.cash_coupon_items == undefined ){
            sale.sale.cash_coupon_items = []
        }
        cashCouponItemsBackup.value = JSON.parse(JSON.stringify(sale.sale.cash_coupon_items))
    })
    async function onSeachCoupon () {
        const code = couponCode._value;
        if( code == undefined || code == ""){
            toaster.warning($t("Please input coupon code to check"));
            return
        }
        
        saleCoupon.value = await sale.onRequestCouponCode(code)
        if (saleCoupon.value.status == 1) {   
    
            let _cash_coupon =  sale.sale.cash_coupon_items.filter((r)=>r.coupon_code == code) ;
            let _total_claim = 0
            if(_cash_coupon){
                _total_claim = _cash_coupon.reduce((i, v)=> i + v.claim_amount,0)                 
            }
            let remain_amount = saleCoupon.value.balance - _total_claim;
            if(remain_amount<=0){
                toaster.warning($t(`Coupon code not enough balance`));
                return 
            }
            let inputNumber = await keyboardDialog({ title: $t("Claim Amount"), type: 'number', value: remain_amount});
            if (inputNumber) { 
                sale.sale.cash_coupon_items.push({'coupon_code':code,'claim_amount':inputNumber})                
            }
        }else {
            toaster.warning($t(`${saleCoupon.value.message} (${saleCoupon.value.code})`));
            return
        }
    }

    function onClose() {
        sale.sale.cash_coupon_items = cashCouponItemsBackup.value
        emit("resolve", false);
    }

    function onRequestCouponCode(code){
        sale.onRequestCouponCode(code)
    }

    function onRemoveClaimCoupon(index){
        sale.sale.cash_coupon_items.splice(index, 1);
    }

    function onConfirmCoupon(){ 
        loading.value = true;
        if (sale.sale.cash_coupon_items?.length <= 0) {
            toaster.warning($t('Please enter any coupon'));
            return
        }
        let _total_claim_amount = 0;
        _total_claim_amount = sale.sale.cash_coupon_items.reduce((sum,i)=>sum + i.claim_amount,0 )
        if(_total_claim_amount>sale.sale.grand_total){
            toaster.warning($t('Coupon amount cannot be greater than sale balance'));
            return
        }

        sale.sale.total_cash_coupon_claim = _total_claim_amount; 
        sale.updateSaleSummary();
        toaster.success($t('Coupon successfully applied'));
        emit("resolve", true);
        loading.value = false;
    }
</script>