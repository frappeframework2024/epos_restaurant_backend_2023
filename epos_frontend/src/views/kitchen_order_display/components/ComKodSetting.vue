<template>
  <div class="text-center pa-4">
    <v-dialog v-model="isOpen" max-width="400" persistent>
      <template v-slot:activator="{ props: activatorProps }">

        <v-icon v-bind="activatorProps" @click="onOpen">mdi-cog</v-icon>
      </template>

      <v-card :title="$t('Setting')">
        <v-card-text>
          <v-select label="Menu Language" :items="['khmer', 'english']"
            v-model="kod.setting.show_menu_language"></v-select>
          <v-select v-model="kod.setting.default_group_by"
            :items="[{ key: 'order_time', title: 'Order Time' }, { key: 'sale_number', title: 'Sale Number' }]"
            item-title="title" item-value="key" label="Group Order By"></v-select>

          <div>Font Size <span class="px-3 bg-slate-100 rounded-lg">{{ kod.setting.font_size.toFixed(2) }}</span> px </div>

          <div>
            <v-slider v-model="kod.setting.font_size" :max="kod.setting.max_font_size" :min="kod.setting.min_font_size"
            class="align-center p-0">
          </v-slider>
          </div>
          <div class="-mt-4">
            <div>Font Size <span class="px-3 bg-slate-100 rounded-lg">{{ kod.setting.column_width.toFixed(2) }}</span> px </div>
           <v-slider v-model="kod.setting.column_width" :max="500" :min="200" class="align-center">
          </v-slider> 
          </div>
          <div class="grid grid-cols-2 -mt-8">
<div>
  <v-checkbox v-model="kod.setting.show_outlet_name" label="Show outlet name" hide-details></v-checkbox>
</div>
<div>
  <v-checkbox v-model="kod.setting.show_item_status" label="Show Item Status" hide-details></v-checkbox>
</div>
          </div>
        </v-card-text>
        <template v-slot:actions>
          <v-spacer></v-spacer>

          <v-btn rounded="lg" color="deep-orange-lighten-1" @click="onCancelSetting">
            Cancel
          </v-btn>

          <v-btn rounded="lg" color="green-lighten-2" @click="onSaveSetting">
            Save
          </v-btn>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>
<script setup>
import { inject, ref, i18n } from '@/plugin';
const { t: $t } = i18n.global;
const kod = inject("$kod")

const isOpen = ref(false)
const backup_setting = ref({})

function onOpen() {

  backup_setting.value = JSON.parse(JSON.stringify(kod.setting))

}
function onSaveSetting() {
  isOpen.value = false
  localStorage.setItem("kod_setting", JSON.stringify(kod.setting))
  kod.getKODData()
}
function onCancelSetting() {

  isOpen.value = false
  kod.setting = backup_setting.value

}



</script>