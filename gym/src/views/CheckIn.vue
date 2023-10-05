<template>
  <div>  
    <input v-model="input">
    <Button :disabled="is_busy"  @click="onEnter" >Search</Button >  
  </div>
</template>

<script setup>
  import moment from 'moment';
  import {inject ,ref} from 'vue';
  import ComCheckInMembership from '@/views/components/ComCheckInMembership.vue';
  import { useDialog } from 'primevue/usedialog';
  const frappe = inject("$frappe")
  const call = frappe.call();
  const input =ref("")
  const data = ref(null);
  const dialog = useDialog();
  const is_busy = ref(false)
 
 
  function onEnter(){ 
  
    if(is_busy.value){
      return
    }
    const param = {
      'code':input.value, 
      check_in_date : moment().format('YYYY-MM-DD')
    }  
    is_busy.value = true;
 
    call.get("epos_restaurant_2023.api.gym.membership_check_in",param)
    .then((res)=>{
      is_busy.value = false
      if(res.message){ 
        data.value = res.message;
        data.value.membership.forEach((r)=>{
          r.selected = false
        });    

        const dialogRef = dialog.open(ComCheckInMembership, {
              data: data.value,
              props: {
                      header: 'Check-In',
                      style: {
                          width: '80vw'
                      },
                      modal: true,
                      position:"top"
                  
                },
              onClose: (options) => {
               
                  const data = options.data;
                  if (data) {
                    console.log(data)
                  }
              }
          });

      }else{
        data.value = null
      }     
    })
  } 

   



 
   

</script>
