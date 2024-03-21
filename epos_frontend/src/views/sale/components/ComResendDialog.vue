<template>
    <ComModal @onClose="onClose" :loading="loading" :fullscreen="false">
        <template #title>
            Resend
        </template>
        <template #content>
            <ComResendGroupSaleProductList />
        </template>
    </ComModal>
</template>
<script setup>
import ComResendGroupSaleProductList from "@/views/sale/components/ComResendGroupSaleProductList.vue";

const emit = defineEmits(["resolve"]);

function onClose() {
    emit("resolve", false);
}

</script>