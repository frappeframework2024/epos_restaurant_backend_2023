<template>
 
    <div :class="small ? 'px-2' : 'px-6'">
        <div class="search-box my-0 mx-auto" :class="small ? 'w-full' : 'max-w-[350px]'">
            
            <ComInput
                :autofocus="!getIsMobile()"
                keyboard
                variant="outlined"
                :placeholder="$t('Search...')"
                prepend-inner-icon="mdi-magnify"
                v-model="product.searchProductKeywordStore"
                v-debounce="onSearch"
                @onInput="onSearch"
                @keydown="onKeyDown"
                ref="txtSearch"
                :listening-focus="true"
                />
 

        </div>
        
    </div>

</template>

<script setup>
import { inject, ref, defineProps, createResource, addModifierDialog, onUnmounted, onMounted,nextTick,getApi } from '@/plugin';
import { onKeyStroke } from '@vueuse/core'
import ComInput from '../../../components/form/ComInput.vue';
import { createToaster } from '@meforma/vue-toaster';
import ComAutoComplete from '@/components/form/ComAutoComplete.vue';
import { useDisplay } from 'vuetify';
import { computed } from 'vue';
import { useDialog } from 'primevue/usedialog';
const dialog = useDialog()
const product = inject("$product")
const sale = inject("$sale")
import {onSelectProduct} from "@/utils/sale.js"


const { mobile } = useDisplay();

let control = ref(null)

const toaster = createToaster({ position: 'top-right', maxToasts: 2, duration: 1000 });
const props = defineProps({
    small: {
        type: Boolean,
        default: false
    }
});
const txtSearch = ref(null);

const selected_product = ref()

const doSearch = ref(true)

function getIsMobile() {
    return  localStorage.getItem("flutterWrapper")==1 || mobile;
}


function onSearch(key) {
    if(key.length > 2 || key.length == 0){
    if (sale.setting.use_retail_ui == 0) {


        if (key) {
            doSearch.value = true
        }
        if (product.setting.pos_menus.length > 0) {
            product.searchProductKeyword = key;

        } else {
            //search product from db

            if (doSearch.value) {
                product.getProductFromDbByKeyword(key)
            }
        }
    }
    }
}
 
function onKeyDown(event) {
    if (event.key == "Enter") {
        if (!sale.isBillRequested()) {
            onSearchProductByBarcode(product.searchProductKeywordStore)
        }
    }
}

function onSearchProductByBarcode(barcode){
    getApi("product.get_products",{
        limit:1,
        page:1,
        product_code: barcode,
        include_product_category:0
    }).then(result=>{
        if(result.message.products.length>0){
           
            onSelectProduct(result.message.products[0],sale,product,dialog)
        }else{
            toaster.warning("Product code is not exist in the system")
        }
      
    }).catch(error=>{

    })
    

    product.searchProductKeywordStore = ""
}


const actionClickHandler = async function (e) {

    if (e.isTrusted) {
        if (e.data.action == "set_focus_in_search_product") {
            const el = document.querySelector(".search-box input");
            if (el) {

                el.focus();
            }
        }
    }
}

onMounted(() => {
    window.addEventListener('message', actionClickHandler, false);
})

onUnmounted(() => {
    window.removeEventListener('message', actionClickHandler, false);
})


</script>