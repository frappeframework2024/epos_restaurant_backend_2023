<template>
  <iframe  src="/app/unpaid-customer" id="iframe-page-container" style="width:100%"></iframe>
</template>
<script setup>
import { inject, ref, onMounted, UnpaidBillListDialog, onUnmounted, i18n } from '@/plugin';
const { t: $t } = i18n.global;

onMounted(() => {
  window.addEventListener('message', async function  (event) { 
    if (event.data.action == "Customer"){
      if (event.data.name != undefined){
        const result = await UnpaidBillListDialog({ title: $t("Bill"),data:event.data.name,doctype:event.data.doctype,bulk_sale:event.data.bulk_sale});
      }
    }
    
  });

  const iframe = document.querySelector('#iframe-page-container');
         
         if (iframe){
             iframe.style.minHeight = ( window.innerHeight) +  "px"
         }
 
         iframe.addEventListener('load', function () {
             var observer = new MutationObserver(function (mutationsList) {
                 iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
 
             });
 
             // Observe changes to the body of the document inside the iframe
             observer.observe(iframe.contentWindow.document.body, { attributes: true, childList: true, subtree: true });
         });

         
})



 
</script>