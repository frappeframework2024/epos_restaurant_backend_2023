<template>
  <div>
    <router-view />
  </div>
  <Toast position="top-center">
        <template #message="slotProps">
            <div class="flex flex-column" style="flex: 1">
                <strong class="mb-1" v-if="slotProps.message.summary" v-html="slotProps.message.summary"></strong>
                <p v-if="slotProps.message.detail" v-html="slotProps.message.detail"></p>
            </div>
        </template>
    </Toast>
    <ConfirmDialog></ConfirmDialog>

</template>

<script setup>

import { onMounted, onUnmounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
const toast = useToast();

const actionListeningHandler = async function (e) {
	if (e.isTrusted && e.data.action) {
 

    if (e.data.action == "show_alert") {
                toast.add({ severity: 'warn', summary: e.data.message, detail: '', life: 3000 })
      }
      else if (e.data.action == "show_error") {
          toast.add({ severity: 'error', summary: e.data.message, detail: '', life: 3000 })
      }
      else if (e.data.action == "show_success") {
          toast.add({ severity: 'success', summary: e.data.message, detail: '', life: 3000 })
      }
		
	}
}

 
onMounted(()=>{
  window.addEventListener('message', actionListeningHandler, false);
})
onUnmounted(()=>{
  window.removeEventListener('message', actionListeningHandler, false);
})
</script>
