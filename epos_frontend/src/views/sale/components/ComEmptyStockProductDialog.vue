<template>
    <ComModal @onClose="onClose" titleOKButton="Yes" titleCloseButton="No" @onOk="onOk" width="350px">
        <template #title>
            Confirm
        </template>
        <template #content>
            <p class="text-center"> {{ $t('The product is currently out of stock.') }}<br />
                {{ $t('Would you like to place an order?') }}</p>
        </template>
    </ComModal>
</template>
<script setup>
import { ref } from "@/plugin"
import { useDisplay } from 'vuetify'
const { mobile } = useDisplay()
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})
const emit = defineEmits(["resolve"])
let open = ref(true)

function onClose() {
    emit('resolve', false);
}
function onOk(action) {
    emit('resolve', true);
}

</script>