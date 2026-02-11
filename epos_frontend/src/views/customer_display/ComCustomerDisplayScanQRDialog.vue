<template lang="">
    <v-dialog v-model="open" width="50rem" persistent>
            <ComPayWayQRDisplayABATemplate :qrData="props.qrData" />             
    </v-dialog>
</template>
<script setup>
  import ComPayWayQRDisplayABATemplate from '@/views/sale/components/ComPayWayQRDisplayABATemplate.vue';
  import ComPayWayQRDisplay from '@/views/sale/components/ComPayWayQRDisplay.vue';
  import { ref } from '@/plugin'; 
  const open = ref(true);
  const props = defineProps({
      qrData: Object
  })
 
</script>
