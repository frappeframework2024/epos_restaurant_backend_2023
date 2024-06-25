<template>
  <iframe src="/app/unpaid-customer" id="mainframe" style="height:2000px;width:100%"></iframe>
</template>
<script setup>
import { inject, ref, onMounted, UnpaidBillListDialog, onUnmounted, i18n } from '@/plugin';
const { t: $t } = i18n.global;

onMounted(() => {
  window.addEventListener('message', async function  (event) {
    if (event.data.action == "Customer"){
      const result = await UnpaidBillListDialog({ title: $t("Bill"),data:event.data.customer});
    }
    
  });
})

</script>