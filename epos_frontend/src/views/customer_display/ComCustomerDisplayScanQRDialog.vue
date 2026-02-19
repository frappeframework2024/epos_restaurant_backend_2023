<template lang="">
    <v-dialog v-model="open" width="50rem" persistent>
            <ComPayWayQRDisplayABATemplate :qrData="props.qrData"  :remaining="props.remaining"/>             
    </v-dialog>
</template>
<script setup>
  import ComPayWayQRDisplayABATemplate from '@/views/sale/components/ComPayWayQRDisplayABATemplate.vue';
  import { ref } from '@/plugin'; 
  const open = ref(true);
  const props = defineProps({
      qrData: Object,
      remaining:0,
  })
 
</script>
