<template>
    <div class="h-full relative bg-cover bg-no-repeat bg-center"
        v-bind:style="{ 'background-image': 'url(' + backgroundImage + ')' }">
        <div class="flex h-full flex-col">
            <ComShortcut v-if="product.setting.pos_menus.length > 0" />
            <ComShortcurMenuFromProductGroup v-else />
            <div ref="scrollContainer" class="pa-2 h-full overflow-y-auto" :class="getCustomerScrollWidth()" id="wrap_menu">
                <ComPlaceholder :loading="product.posMenuResource.loading"
                    :is-not-empty="(product.posMenuResource.data?.length > 0 || product.setting.default_pos_menu =='')" class-color="text-white"
                    :is-placeholder="true">
                    <template #default>
                        <div class="grid gap-2"
                            :class="mobile ? 'grid-cols-2' : ''"
                            :style="!mobile ? 'grid-template-columns: repeat('+ gv.itemMenuSetting.show_column_item +' , 1fr);' : ''"
                           >
                            <template v-if="product.setting.pos_menus.length > 0">

                                <div v-for="(m, index) in product.getPOSMenu()" :key="index" :style="'height:' + gv.itemMenuSetting.height_item + 'px'" class="h-36">
                                    <ComMenuItem :data="m" />
                                </div>
                            </template>
                            <template v-else>
                                <div v-if="product.canBack" class="h-full rounded-lg shadow-lg cursor-pointer bg-gray-500">
                                    <div v-ripple class="relative p-2 w-full h-full flex justify-center items-center" @click="onBack">
                                    <div>
                                    <v-icon color="white" size="large">mdi-reply</v-icon>
                                    <div class="text-white">{{ $t('Back') }}</div>
                                    </div>
                                    </div>
                                </div>
                                <ComMenuItemByProductCategory />
                            </template>
                        </div>
                    </template>
                    <template #empty>
                        <div class="h-full flex items-center justify-center">
                            <div class="p-6 text-center bg-white rounded-sm">
                                <div class="text-sm italic mb-2">{{ $t('msg.Please click Refresh to get menu') }}</div>
                                <div>
                                    <v-btn color="primary" prepend-icon="mdi-refresh" @click="onMenuRefresh()">
                                        {{ $t('Refresh') }}
                                    </v-btn>
                                </div>
                            </div>
                        </div>
                    </template>
                </ComPlaceholder>

                <div class="loading-pr-more" v-if="product.isLoadingProduct">
                    <v-progress-circular indeterminate></v-progress-circular> Loading...
                </div> 
            </div>
            <ComSaleButtonActions v-if="!mobile" />
        </div>
    </div>
</template>
<script setup>
import ComShortcut from './ComShortcut.vue';
import ComShortcurMenuFromProductGroup from './ComShortcurMenuFromProductGroup.vue';
import ComMenuItemByProductCategory from './ComMenuItemByProductCategory.vue';
import ComPlaceholder from '@/components/layout/components/ComPlaceholder.vue';
import ComMenuItem from './ComMenuItem.vue';
import { inject, defineProps ,ref,onUnmounted,onMounted,computed} from '@/plugin';
import { useDisplay } from 'vuetify'
import ComSaleButtonActions from './ComSaleButtonActions.vue';
 
const { mobile } = useDisplay()
const product = inject("$product")
const frappe = inject("$frappe")
const gv = inject("$gv");
const db = frappe.db();

const props = defineProps({
    backgroundImage: String
});

const scrollContainer = ref(null);
 
function onBack(){
    window.history.back();
}

function getCustomerScrollWidth() {
    const is_window = localStorage.getItem('is_window');
    if (is_window == 1) {
        return 'scrollbar';
    }
    return '';
}


function onMenuRefresh() {
    if (product.setting.pos_menus.length > 0) {
        product.loadPOSMenu()
    } else {

        product.getProductMenuByProductCategory( "All Product Categories")
        product.loadPOSMenu();
 
    }

}

const onScroll = () => {
    
    if (scrollContainer.value && product.isLoadingProduct ==false && product.isSearchProduct == false) {
        const container = scrollContainer.value;
        const scrollBottom = container.scrollHeight - container.scrollTop === container.clientHeight;
        if (scrollBottom) {
            product.getProductFromDB()
        }
    }
};
onMounted(() => {
     
    if (scrollContainer.value && product.setting.default_pos_menu=="" ) {
        scrollContainer.value.addEventListener('scroll', onScroll);
    } 

    const item_menu_setting = JSON.parse(localStorage.getItem("item_menu_setting"))
    if (item_menu_setting) {
        gv.itemMenuSetting = item_menu_setting
    }
});
onUnmounted(() => {
    if (window.mobile == true) { 
        if (scrollContainer.value && product.setting.default_pos_menu=="" ) {
            window.addEventListener('scroll', onScroll);
        }
    }else{
        if (scrollContainer.value && product.setting.default_pos_menu=="") {
            scrollContainer.value.removeEventListener('scroll', onScroll);
        }
    }
   
});


</script>

<style>
.scrollbar::-webkit-scrollbar {
    width: 17px;
}
.loading-pr-more {
    text-align: center;
    color: #fff;
    background: #0000008a;
    padding: 10px 0;
    position: absolute;
    bottom: 77px;
    z-index: 9999999;
    left: 50%;
    transform: translateX(-50%);
    width: 131px;
}
@media (max-width:767.98px) {
    #wrap_menu {
        height: calc(100vh - 238px) !important;
    }
    .loading-pr-more {
        bottom: 13px !important;
    }
}
</style>