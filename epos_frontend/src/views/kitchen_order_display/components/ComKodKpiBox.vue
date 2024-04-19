<template>
    <div :class="['flex', 'rounded-lg', 'p-2', bgColorClass]">
      <div style="background-color: rgb(0 0 0 / 13%);" class=" rounded-lg w-14 flex justify-center items-center h-full">
        <!-- Use dynamic style for setting icon size -->
        <v-icon class="m-auto text-white" :style="{ fontSize: iconSize + 'px' }">{{ iconName }}</v-icon>    
      </div>
      <div class="col-span-3 ms-2 text-white">
        <div class="font-semibold">{{ name }}</div>
        <div class="font-semibold text-lg">{{ quantity }}</div>
      </div>
    </div>
  </template>
  
  <script setup>  

  const props = defineProps({
    name: String,
    quantity: [Number, String],
    iconName: String,
    bgColorClass: String,
    iconSize: Number
  })
  </script>