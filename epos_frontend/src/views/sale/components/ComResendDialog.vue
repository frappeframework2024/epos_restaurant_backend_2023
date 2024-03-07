<template>
    <ComModal @onClose="onClose(false)" :loading="loading" :fullscreen="false" :hide-ok-button="true"
        :hide-close-button="true"> 
        <template #title>
            Helllo Resend
        </template>
        <template #content>
            <ComResendGroupSaleProductList/>
        </template>
    </ComModal>
</template>
<script setup>
    import ComResendGroupSaleProductList from "@/views/sale/components/ComResendGroupSaleProductList.vue";

</script>