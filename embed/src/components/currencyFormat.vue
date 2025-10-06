<template>
    
 
{{ formatCurrency() }} ៛
 
        
</template>
<script setup>
 
const props = defineProps({
    currency:String,
    value:Number,
   
})
  
function formatCurrency() {
 
   return `${Number(props.value).toLocaleString('en-US', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
      })}`;

 
}
</script>