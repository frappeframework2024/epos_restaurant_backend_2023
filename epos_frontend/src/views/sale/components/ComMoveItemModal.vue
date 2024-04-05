<template>
    <ComModal @onClose="onClose" @onOk="onOk" titleOKButton="Move to" :loading="loading" :fullscreen="false">
        <template #title>
            {{ props.params.title }}
        </template>
        <template #content>
            <ComMoveItemGroupSaleProductList />
        </template>
    </ComModal>
</template>
<script setup>
import ComMoveItemGroupSaleProductList from '@/views/sale/components/ComMoveItemGroupSaleProductList.vue'
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

const emit = defineEmits(["resolve"]);
function onClose() {
    emit("resolve", false);
}
function onOk() {
    emit("resolve", true);
}
</script>