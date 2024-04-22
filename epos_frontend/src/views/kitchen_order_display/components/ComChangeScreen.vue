<template>
     <span v-if="screens.length<=1">{{ kod.screen_name }}</span>
     <v-menu v-else >
      <template v-slot:activator="{ props }">
        <v-btn
         
          v-bind="props"
        >
          {{ kod.screen_name }}
        </v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="(item, index) in screens"
          :key="index"
          :value="index"
        >
          <v-list-item-title @click="onChangeScreen(item.printer_name)">{{ item.printer_name }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
</template>
<script setup>
    import {ref, inject} from "@/plugin"
    const screens = JSON.parse( localStorage.getItem("device_setting")).station_printers

    const kod = inject("$kod")

    function onChangeScreen(screen_name){
        kod.screen_name = screen_name
        kod.getKODData()
    }
</script>