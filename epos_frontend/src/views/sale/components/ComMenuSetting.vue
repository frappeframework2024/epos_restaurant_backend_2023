<template>
     <ComDialogContent titleButtonClose="Cancel"   :hideButtonClose="false"   @onClose="onCancelSetting" @onOK="onSaveSetting">
      
      <div class="text-center pb-4"> 
      <div class="grid grid-cols-3">
        <v-checkbox v-model=" gv.itemMenuSetting.show_item_code" label="Show Product Code" hide-details></v-checkbox>
        <v-checkbox v-model=" gv.itemMenuSetting.show_short_cut_chip" label="Show Shortcut Chip" hide-details></v-checkbox>
      </div>
      <div class="grid gap-2 grid-cols-2"> 
        <v-select v-model="gv.itemMenuSetting.show_menu_language" label="Menu Language" :items="['kh','en']"></v-select>
        <v-select v-model="gv.itemMenuSetting.sort_order_by"
        
            :items="[
              { key: 'sort_order', title: 'Sort Order' },
    { key: 'product_name_en', title: 'Product Name (EN)' },
    { key: 'product_name_kh', title: 'Product Name (KH)' },
    { key: 'product_code', title: 'Product Code' },
    { key: 'creation', title: 'Creation Date' },
    { key: 'last_modified', title: 'Last Modified Date' }
            ]"
            item-title="title" item-value="key" label="Group Order By"></v-select> 
            <div class="px-3 mt-2">
              <div class="text-start">Price Font Size <span class="px-3 bg-slate-100 rounded-lg">{{ gv.itemMenuSetting.font_price_size ?? gv.itemMenuSetting.font_price_size }}</span> px </div>
              <Slider :step="0.2" class="mt-4 w-full" :max="gv.itemMenuSetting.max_font_size" :min="gv.itemMenuSetting.min_font_size" v-model="gv.itemMenuSetting.font_price_size"  />
            </div>
            <div class="px-3 mt-2">
             <div class="text-start">Product Font Size <span class="px-3 bg-slate-100 rounded-lg">{{ gv.itemMenuSetting.item_font_size ?? gv.itemMenuSetting.item_font_size }}</span> px </div>  
             <Slider :step="0.2" class="mt-4 w-full" :max="gv.itemMenuSetting.max_font_size" :min="gv.itemMenuSetting.min_font_size" v-model="gv.itemMenuSetting.item_font_size"  />
            </div>
            <div class="px-3 mt-2">
             <div class="text-start">Column Product <span class="px-3 bg-slate-100 rounded-lg">{{ gv.itemMenuSetting.show_column_item }}
            </span> Col </div>  
             <Slider class="mt-4 w-full" :max="12" :min="3" v-model="gv.itemMenuSetting.show_column_item"  />
            </div>  
            <div class="px-3 mt-2">
             <div class="text-start">Height Product <span class="px-3 bg-slate-100 rounded-lg">{{ gv.itemMenuSetting.height_item }}
            </span> px </div>  
             <Slider :step="0.1" class="mt-4 w-full" :max="250" :min="100" v-model="gv.itemMenuSetting.height_item"  />
            </div>  
            <div class="px-3 mt-2">
             <div class="text-start">Width Sale Summary<span class="px-3 bg-slate-100 rounded-lg">{{ gv.itemMenuSetting.width_sale_summary }}
            </span> px </div>  
             <Slider :step="1" class="mt-4 w-full" :max="800" :min="300" v-model="gv.itemMenuSetting.width_sale_summary"  />
            </div>  
      </div>
       
           
          
             
    </div>
</ComDialogContent>
  </template>
  <script setup>
  import { inject, ref, i18n , onMounted } from '@/plugin';
  import ComDialogContent from '@/components/ComDialogContent.vue' 
  import Slider from 'primevue/slider';
  const { t: $t } = i18n.global;
  const product = inject("$product")
  const gv = inject("$gv")
  const backup_setting = ref({})
  const dialogRef = inject('dialogRef');
  
  function onSaveSetting() { 
    localStorage.setItem("item_menu_setting", JSON.stringify(gv.itemMenuSetting))
    if (gv.itemMenuSetting.sort_order_by != backup_setting.value.sort_order_by ) {
      if (product.setting.pos_menus.length > 0) {
        product.getProductMenuByProductCategory()
      }else {
        alert("sort order on get from from POS menu for epos restaurant setup")
      }
    }
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