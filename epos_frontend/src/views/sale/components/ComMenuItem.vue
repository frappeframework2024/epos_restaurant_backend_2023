<template>
    <div v-if="data.type == 'back'" class="h-full rounded-lg shadow-lg cursor-pointer bg-gray-500">
        <div v-ripple class="relative p-2 w-full h-full flex justify-center items-center" @click="onBack(data)">
            <div>
                <v-icon color="white" size="large">mdi-reply</v-icon>
                <div class="text-white">{{ $t('Back') }}</div>
            </div>
        </div>
    </div>
    <div v-if="data.type == 'menu'" v-ripple
        class="relative h-full bg-cover bg-no-repeat rounded-lg shadow-lg cursor-pointer overflow-auto" v-bind:style="{
        'background-color': data.background_color,
        'color': data.text_color,
        'background-image': 'url(' + encodeURIComponent(data.photo).replace(/%2F/g, '/').replace(/%3A/g, ':').replace(/%3F/g, '?').replace(/%3D/g, '=').replace(/%26/g, '&')  + ')',
        'background-size': 'contain', 'background-position': 'center center'
    }" @click="onClickMenu(data)">
        <div class="absolute top-0 bottom-0 right-0 left-0">
            
            <avatar class="!h-full !w-full" :name="data.name_en" :rounded="false" :background="data.background_color"
                :color="data.text_color" v-if="!data.photo"></avatar>
        </div>
        <div class="block relative p-2 w-full h-full">
            <div class="absolute right-1 top-1">
                <v-icon :color="data.text_color">mdi-folder-open</v-icon>
            </div>
            <div class="p-1 rounded-md absolute bottom-1 right-1 left-1 bg-gray-50 bg-opacity-70 text-sm text-center">
                <span class="text-black" v-if="!sale.load_menu_lang">{{ getMenuName(data) }}</span>
            </div>
        </div>
    </div>
    <!-- Product -->

    <div v-else-if="data.type == 'product'" v-ripple
        class="relative overflow-hidden h-full bg-cover bg-no-repeat rounded-lg shadow-lg cursor-pointer bg-gray-300 "
        v-bind:style="{ 'background-image': 'url(' + encodeURIComponent(image).replace(/%2F/g, '/').replace(/%3A/g, ':').replace(/%3F/g, '?').replace(/%3D/g, '=').replace(/%26/g, '&') + ')', 'background-size': 'contain', 'background-position': 'center center' }"
        @click="onClickProduct()">
        <div class="absolute top-0 bottom-0 right-0 left-0" v-if="!image">

            <avatar class="!h-full !w-full" :name="data.name_en" :rounded="false" background="#f1f1f1"></avatar>
        </div>
        <div class="block relative p-2 w-full h-full">
            <div>
                <div :style="{fontSize:gv.itemMenuSetting.font_price_size+ 'px' }" class="absolute left-0 top-0 bg-red-700 text-white p-1 rounded-tl-lg rounded-br-lg text-sm">
                    <div>
                        <span v-if="productPrices.length > 1">
                            <span>
                                <CurrencyFormat :value="minPrice" />
                            </span> <v-icon icon="mdi-arrow-right" size="x-small" /> <span>
                                <CurrencyFormat :value="maxPrice" />
                            </span>
                        </span>
                        <CurrencyFormat v-else :value="showPrice" />
                    </div>

                </div>
                <div class="menu-dropdown-icon">
                    <v-menu transition="scale-transition">
                        <template v-slot:activator="{ props }">
                            <v-btn size="small" variant="text" :id="data.menu_product_name" v-bind="props"
                                icon="mdi-dots-vertical">
                            
                            </v-btn>
                        </template>

                        <v-list>
                            <v-list-item @click="open">
                                <v-list-item-title>{{ $t("Upload Local Image") }}</v-list-item-title>
                            </v-list-item>
                            <v-list-item @click="uploadImage(data)">
                                <v-list-item-title>{{ $t("Upload Online Image") }}</v-list-item-title>
                            </v-list-item>
                            <v-list-item @click="onOpenChangePrice">
                                <v-list-item-title>{{ $t("Change Price") }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </div>
            </div>

            <div class="p-1 rounded-md absolute bottom-1 right-1 left-1 bg-gray-50 bg-opacity-90 text-sm text-center">

                <span v-if="!sale.load_menu_lang" :style="{fontSize:gv.itemMenuSetting.item_font_size+ 'px' }">{{ getMenuName(data, true) }}</span> <span
                    style="color:red; font-weight: bold;">
                    {{ getTotalQuantityOrder(data) }}</span>
            </div>
        </div>
    </div> 
</template>
<script setup>
import { ref,computed, addModifierDialog, SelectDateTime, i18n, inject, keypadWithNoteDialog, SelectGoogleImageDialog, SaleProductComboMenuGroupModal, createToaster, EmptyStockProductDialog } from '@/plugin'
import Enumerable from 'linq'
import { useDialog } from 'primevue/usedialog';
 
const { t: $t } = i18n.global;
import {onSelectProduct} from "@/utils/sale.js"
const props = defineProps({ data: Object })
const sale = inject("$sale");
const gv = inject("$gv");
const product = inject("$product");
const toaster = createToaster({ position: 'top-right' })
const frappe = inject("$frappe")
const db = frappe.db();
import { useFileDialog } from '@vueuse/core'
const dialog = useDialog()

// get image
const image = computed(() => {
    return props.data.photo
})
// price menu
const productPrices = computed(() => {
    if (product.prices) {
        const r = JSON.parse(props.data.prices)
        return r.filter(r => (r.branch == sale.sale.business_branch || r.branch == '') && r.price_rule == sale.sale.price_rule)
    }
    return []
})
 
const showPrice = computed(() => {
    if (props.data.is_combo_menu) {
        return props.data.price || 0
    }
    if (productPrices.value.length == 1) {
        return productPrices.value[0].price
    }
    else if (productPrices.value.length == 0) {
        return props.data.price || 0
    }
    return 0
})
const maxPrice = computed(() => {
    if (productPrices.value.length > 1) {
        return Enumerable.from(productPrices.value).max("$.price")
    }
    return 0
})
const minPrice = computed(() => {
    if (productPrices.value.length > 1) {
        return Enumerable.from(productPrices.value).min("$.price")
    }
    return 0
})

function getMenuName(menu, is_item = false) {
    const mlang = gv.itemMenuSetting.show_menu_language
    let code = !is_item ? "" : (gv.itemMenuSetting.show_item_code == 0 ? "" : `${menu.name} - `);
    if (mlang != null) {
        if (mlang == "en") {
            return `${code}${menu.name_en}`;
        } else {
            return `${code}${menu.name_kh}`;
        }

    } else {
        localStorage.setItem('mLang', 'en');
        return `${code}${menu.name_en}`;
    }
}

function getTotalQuantityOrder(data) {
    const qty = sale.sale?.sale_products?.filter(r => r.product_code == data.name).reduce((n, d) => n + (d.quantity || 0), 0);
    if (qty == undefined) {
        return ""
    }
    if (qty == 0) {
        return ""
    } else {
        return " (" + qty + ")"
    }
}

// end price menu

function onClickMenu(menu) {
    if (sale.setting.pos_menus.length > 0) {
        product.parentMenu = menu.name;
        _onPriceRuleChanged(menu);
    } else {
     
        product.getProductMenuByProductCategory(menu.name)
    }

}

const { files, open, reset, onCancel, onChange } = useFileDialog({
        accept: 'image/*', // Set to accept only image files
        directory: false, // Select directories instead of files if set true
    })
onChange((files) => {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/method/upload_file", true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
    let form_data = new FormData();
    form_data.append("file", files[0], files[0].name);
    xhr.send(form_data);
    db.updateDoc('Product', props.data.name, {
            photo: "/files/"+files[0].name,
        }).then((doc) => {
            props.data.photo =  "/files/"+files[0].name
            toaster.success($t("msg.Update successfully"))
        })
})


async function uploadImage(data) {
    const res = await SelectGoogleImageDialog({
        title: $t("Upload Image") + " " + data.name_en,
        keyword: data.name_en
    })
    if (res) {
        db.updateDoc('Product', data.name, {
            photo: res.image,
        }).then((doc) => {
                data.photo = res.image
                toaster.success($t("msg.Update successfully"))
            }
        )
    }
}

async function onOpenChangePrice(data) {
//    alert(123)
    
}



function activate_menu(event) {
    event.stopPropagation();
}

function onBack(menu) {
    const parent_name = product.posMenuResource.data?.find(r => r.name == menu.parent).parent;
    const parent_menu = product.posMenuResource.data?.find(r => r.name == parent_name);
    product.parentMenu = parent_name;
    if (parent_menu != undefined){
        console.log(parent_menu)
        console.log(1)
        _onPriceRuleChanged(parent_menu);
    }
   else{
        get_price_rule()
   }
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

async function onClickProduct() {
    onSelectProduct(props.data,sale,product,dialog)
    
}

 

</script>
<style>
.menu-dropdown-icon {
    position: absolute;
    right: 10px;
    top: -5px;
}
.is-loading-page{
    position: absolute;
    left: 50%;
    top: 50%;
    z-index: 11;
    transform: translate(-50%,-50%);
}

.overlay-loading-dialog {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.4);
    width: 100%;
    height: 100%;
}
</style>