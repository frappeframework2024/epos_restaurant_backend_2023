<template>
    <v-dialog v-model="open" :width="mobile ? '100%' : '50%'" persistent :fullscreen="mobile">  
      <ComPayWaySuccess @onClose="onClose()" />  
    </v-dialog>
</template>
<script setup>
    import { ref, i18n,onMounted,onUnmounted ,watch} from '@/plugin';
    import ComPayWaySuccess from "@/views/sale/components/ComPayWaySuccess.vue";
    import { useDisplay } from 'vuetify'; 
    const { mobile } = useDisplay();
    const { t: $t } = i18n.global; 
    const open = ref(true); 
   

    function onClose(){
        open.value = false;
    }

    onMounted(async ()=>{ 
     
    });

    onUnmounted(() => {
       open.value = false;
    });

</script>



