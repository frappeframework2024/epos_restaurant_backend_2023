<template>
  <div> 
  <ComInput  v-model="input"/>
  <v-btn @click="onEnter">Search</v-btn>
 
  <pre>{{ data }}</pre>
  </div>
</template>

<script setup>
  import { onMounted,inject ,ref} from 'vue';
import ComInput from './components/ComInput.vue';
  const frappe = inject("$frappe")
  const call = frappe.call();
  const input =ref("")
  const data = ref(null)

  onMounted(()=>{
    
  })
  function onEnter(){
    call.get("epos_restaurant_2023.api.gym.membership_check_in",{'code':input.value})
    .then((res)=>{
      if(res.message){ 
        data.value = res.message
      }else{
        data.value = {}
      }
     
    })
  }
</script>
