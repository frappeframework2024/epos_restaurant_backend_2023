<template>
  <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
    <template #title>
      {{ $t('Online Order') }}
    </template>
    <template #content>
      <OnlineOrder @close="onClose" />
    </template>
  </ComModal>
</template>

<script setup>
import {
  defineProps,
  defineEmits,
  i18n,
} from '@/plugin';
import ComModal from '@/components/ComModal.vue';
import OnlineOrder from '@/views/online_order/OnlineOrder.vue';

defineProps({
  params: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['resolve']);
const { t: $t } = i18n.global;
function onClose() {
  emit('resolve', false);
}
</script>