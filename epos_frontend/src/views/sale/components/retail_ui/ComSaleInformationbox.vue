<template>
            <div class="v-col rounded-lg mx-1" :class="bgColor">
                <div class="v-row">
                    <div class="v-col-auto flex justify-center align-center v-ps-5">
                        <v-icon :size="size" :icon="icon" color="white"></v-icon>
                    </div>
                    <div class="v-col text-white">
                        <small>
{{ title }}                            
                        </small>
<div>
  {{ value }}  
</div>
                    </div>
                </div>
            </div>
</template>
<script setup>
    import { defineProps, inject } from 'vue'
    const emit = defineEmits(["onClick"]) 
    const props = defineProps({
        title: String,
        value:String,
        bgColor: String,
        icon: String,
        size:String
    })
    function onClick(){
        emit('onClick')
    }
</script>
<style lang="">
    
</style>