<template>
  <v-dialog v-model="open" persistent>
      <v-card 
        class="mx-auto my-2 py-2"
        :title="params.title"
        :subtitle="params.text"
        >
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn variant="flat" @click="onClose" color="error" v-if="!params.hide_cancel">
              {{ $t('Cancel') }}
            </v-btn>
            <v-btn variant="flat" @click="onOk"  ref="okBtn" color="primary">
                {{ $t('Ok') }}
            </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>

<script setup>
import {ref} from  "@/plugin"
import { onMounted } from "vue";
const okBtn = ref(null);
const props = defineProps({
  params:{
    type:Object,
    require:true
  }
})
const emit = defineEmits(["resolve"])
let open = ref(true)

function onClose(){
  emit('resolve', false);
}
function onOk(){
  emit('resolve', true);
}
onMounted(()=>{
  okBtn.value.$el.focus();
})
</script>
