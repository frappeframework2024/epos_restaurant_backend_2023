<template>
     <ComDialogContent   :hideButtonClose="false"   @onClose="onCancelSetting" @onOK="onSaveSetting">
    <div class="text-center">
    {{ gv.itemMenuSetting }}
        <v-checkbox v-model=" gv.itemMenuSetting.show_item_code" label="Show Product Code" hide-details></v-checkbox>
       
        <v-select label="Menu Language" :items="[{ key: 'kh', title: 'Khmer' }, { key: 'en', title: 'English' }]"
        v-model="gv.itemMenuSetting.show_menu_language"></v-select>
        <v-select v-model="gv.itemMenuSetting.group_by"
            :items="[{ key: 'product_name', title: 'Product Name' }, { key: 'creation', title: 'Creation' }, { key: 'product_code', title: 'product code' }]"
            item-title="title" item-value="key" label="Group Order By"></v-select>
        
            <div>Price Font Size<span class="px-3 bg-slate-100 rounded-lg">{{  gv.itemMenuSetting.font_price_size }}</span> px </div>
  
            <div>
              <v-slider v-model="gv.itemMenuSetting.font_price_size">
            </v-slider>
            </div>
            <div>
                <div>Product Font Size<span class="px-3 bg-slate-100 rounded-lg">{{ gv.itemMenuSetting.item_font_size.toFixed(2) }}</span> px </div>  
              <v-slider :max="gv.itemMenuSetting.max_font_size" :min="gv.itemMenuSetting.min_font_size" v-model="gv.itemMenuSetting.item_font_size" 
              class="align-center p-0">
            </v-slider>
            </div>

    </div>
</ComDialogContent>
  </template>
  <script setup>
  import { inject, ref, i18n , onMounted } from '@/plugin';
  import ComDialogContent from '@/components/ComDialogContent.vue' 
  const { t: $t } = i18n.global;
  const gv = inject("$gv")
  const backup_setting = ref({})
  const dialogRef = inject('dialogRef');
  
  function onSaveSetting() {
    localStorage.setItem("item_menu_setting", JSON.stringify(gv.itemMenuSetting))
    dialogRef.value.close()
  }
  function onCancelSetting() {
    
    gv.itemMenuSetting = backup_setting.value
    dialogRef.value.close()
  }
  onMounted(() => {
backup_setting.value = JSON.parse(JSON.stringify(gv.itemMenuSetting))
  })
  
  
  </script>