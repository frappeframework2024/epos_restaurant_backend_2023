<template>
    <div class="bg-white" :class="mobile ? 'px-2' : 'p-2'" id="shortcut_menu" v-if="shortcut?.length > 0"> 
        
        <div :class="'flex-wrap flex -my-1 justify-center'" v-if="mobile === false && shortcut">
         
            <v-btn 
                class="flex-shrink-0 m-1"
                v-for="(m, index) in shortcut" :key="index"
                rounded="pill"
                variant="tonal"
                size="small"
                v-bind:style="{'background-color':m.background_color}"
                @click="onClick(m)">
                <span v-bind:style="{color:m.text_color}">{{m.name_en}}</span>
            </v-btn> 
        </div>
        <v-slide-group v-if="mobile === true && shortcut">
            <v-slide-group-item v-for="(m, index) in shortcut" :key="index" v-slot="{ isSelected, toggle }">
                <v-btn 
                class="flex-shrink-0 m-1 my-2 px-5"
                rounded="pill"
                variant="tonal"
                height="40"
                v-bind:style="{'background-color':m.background_color}"
                @click="onClick(m)">
                <span v-bind:style="{color:m.text_color}">{{m.name_en}}</span>
            </v-btn> 
            </v-slide-group-item>
        </v-slide-group>
    </div>
</template>
<script setup>
    import { computed, inject } from '@/plugin'
    import {useDisplay}  from 'vuetify'
    const {mobile} = useDisplay()
    const product = inject("$product")
    import Enumerable from 'linq'
    const gv = inject("$gv")
    const sale = inject("$sale");

    const shortcut = computed(()=>{
        let  data = product.posMenuResource.data?.filter(r=>r.shortcut_menu == 1) 
            
        if((gv.itemMenuSetting?.sort_menu_order_by || "name") == "name"){
         
            data = Enumerable.from(data).orderBy("$.name").toArray()
            console.log(data);
        }else {
            data = Enumerable.from(data).orderBy("$.sort_order").toArray()
        }
      
        
        return data
       
    })
  
    function onClick(menu) {
            product.searchProductKeyword="";
            product.parentMenu = menu.name;
            _onPriceRuleChanged(menu)
        }
        function _onPriceRuleChanged(menu){ 
        if((menu.price_rule||"")!="")
        {
            sale.price_rule = menu.price_rule; 
            sale.sale.price_rule = sale.price_rule; 
        } 
        else
        {
            const parent_menu = product.posMenuResource.data?.find(r => r.name == menu.parent);
            if(parent_menu != undefined){
                if((parent_menu.price_rule||"")!=""){
                    sale.price_rule = parent_menu.price_rule
                }
                else{
                    get_price_rule()
                }
            }
            else{
                get_price_rule()
            }
        }
    }
    function get_price_rule(){
        if((sale.table_price_rule||"") != "")
        {
            sale.price_rule = sale.table_price_rule; 
        }
        else
        {
            sale.price_rule = sale.setting?.price_rule;
        }
        sale.sale.price_rule = sale.price_rule; 
    }
</script>
<style scoped>
.wrap-sm {
    width: calc( 100vw - 22px);
}
</style>