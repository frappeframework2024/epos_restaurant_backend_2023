<template>
    <div class="v-col-12">
        <ComSaleInformation/>
    </div>
    <div class="v-row">
    <div class="v-col-8">
        <ComSaleProductList/> 
        <div class="v-row">
            <div class="v-col-6">
<ComSaleNote/>
            </div>
            <div class="v-col-6">
<ComSaleSummary/> 
            </div>
        </div>
        <ComSaleActionButton/>
    </div>
    <div class="v-col-4">
        <ComExchangeRate/>
        <ComSelectCustomer/>
        <ComSelectedProduct/>
    </div>
    </div>
</template>
<script setup>
    import {ref} from "@/plugin"
    import ComSaleInformation from "@/views/sale/components/retail_ui/ComSaleInformation.vue"
    import ComExchangeRate from "@/views/sale/components/retail_ui/ComExchangeRate.vue"
    import ComSaleActionButton from "@/views/sale/components/retail_ui/ComSaleActionButton.vue"
    import ComSaleNote from "@/views/sale/components/retail_ui/ComSaleNote.vue"
    import ComSaleProductList from "@/views/sale/components/retail_ui/ComSaleProductList.vue"
    import ComSaleSummary from "@/views/sale/components/retail_ui/ComSaleSummary.vue"
    import ComSelectedProduct from "@/views/sale/components/retail_ui/ComSelectedProduct.vue"
    import ComSelectCustomer from "@/views/sale/components/ComSelectCustomer.vue"
    


</script>