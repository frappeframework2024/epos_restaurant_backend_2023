<template>
    <!-- template 2 -->
    <template v-if="is_loading">
        <div class="overlay">
            <div class="overlay__inner">
                <div class="overlay__content">
                    <span class="spinner"></span>
                </div>
            </div>
        </div>
    </template>
    <template v-else>
        <div v-if="template_menu == 'top-menu'">
            <SaleOrderTemplate1 :menu_categories="menu_categories" :menu_products="menu_products"
                :onSettingClick="onSettingClick" />
        </div>
        <div v-else-if="template_menu == 'left-menu'">
            <SaleOrderTemplate2 :menu_categories="menu_categories" :menu_products="menu_products"
                :onSettingClick="onSettingClick" />
        </div>
        <div v-else-if="template_menu == 'left-menu-2'">
            <SaleOrderTemplate3 :menu_categories="menu_categories" :menu_products="menu_products"
                :onSettingClick="onSettingClick" />
        </div>
    </template>
</template>

<script setup>
import { ref, inject, onMounted, i18n, useRoute, useRouter,watch } from '@/plugin';
import { useDialog } from 'primevue/usedialog';
import ComMenuSetting from '@/views/sale/components/ComMenuSetting.vue';
import SaleOrderTemplate1 from "@/views/sale_page/SaleOrderTemplate1.vue";
import SaleOrderTemplate2 from "@/views/sale_page/SaleOrderTemplate2.vue";
import SaleOrderTemplate3 from "@/views/sale_page/SaleOrderTemplate3.vue";

import { createToaster } from '@meforma/vue-toaster';

const { t: $t } = i18n.global;
const sale = inject("$sale");
const gv = inject("$gv");
const socket = inject("$socket");
const product = inject("$product");

const frappe = inject("$frappe");

const call = frappe.call();

const route = useRoute();
const router = useRouter();
const dialog = useDialog();
const toaster = createToaster({ position: "top-center" });


//variables  
const menu_categories = ref([]);
const menu_products = ref([]);
const is_loading = ref(true);
const template_menu = ref("left-menu");
sale.deletedSaleProducts = [];

if (!localStorage.getItem("item_menu_setting")) {
    localStorage.setItem("item_menu_setting", JSON.stringify(gv.itemMenuSetting))
}

onMounted(async () => {
    is_loading.value = true;
    if (route.query.menu) {
        template_menu.value = route.query.menu;
    }

    //private on mouted
    await _onMounted();
    
 
});


watch(
    () => product.posMenu1LevelData,
    async (data) => {
        if (!data)  return
        is_loading.value = true;
        await _onLoadMenu();
         is_loading.value = false;
    },
    { immediate: true }
)


async function _onMounted() {
    //check user 
    const make_order_auth = JSON.parse(localStorage.getItem('make_order_auth'));
    if (sale.getString(route.params.name) == "" || make_order_auth == undefined) {

        if (sale.sale.sale_status == undefined) {
            if (sale.setting.table_groups.length > 0) {
                router.push({ name: 'TableLayout' });
            }
            else {
                sale.newSale();
            }
        }
    }

    let backup_sale = JSON.parse(JSON.stringify(sale.sale))
    //check working day and cashier shift
    const valid_shift = await call.post("epos_restaurant_2023.api.api.get_current_shift_information", {
        business_branch: sale.setting?.business_branch,
        pos_profile: localStorage.getItem("pos_profile")
    })

    if (valid_shift.message) {
        let data = valid_shift.message;
        if (data.cashier_shift == null) {
            toaster.warning($t("msg.Please start shift first"));
            router.push({ name: "OpenShift" });
        } else if (data.working_day == null) {
            toaster.warning($t('msg.Please start working day first'));
            router.push({ name: "StartWorkingDay" });
        } else {
            sale.sale.working_day = data.working_day.name;
            sale.sale.posting_date = data.working_day.posting_date;
            sale.posting_date = data.working_day.posting_date;
            sale.sale.cashier_shift = data.cashier_shift.name;
            sale.sale.shift_name = data.cashier_shift.shift_name;
            gv.confirm_close_working_day(data.working_day.posting_date);
            onCheckExpireHappyHoursPromotion();
        }
    }

    //load sale data
    if (!sale.getString(route.params.name) == "" && !sale.no_loading) {
        sale.LoadSaleData(route.params.name).then((v) => {
            if (v) {
                if (v.docstatus == 1 || v.docstatus == 2) {
                    if (v.docstatus == 1) {
                        toaster.warning($t('msg.This bill is already closed'));
                    } else {
                        toaster.warning($t('msg.This bill is already cancelled'));
                    }
                    if (gv.setting.table_groups.length > 0) {
                        router.push({ name: 'TableLayout' });
                    }
                    else {
                        router.push({ name: 'Home' });
                    }
                } else {
                    sale.saleNetworkLock(sale.sale)
                }
                //
                socket.emit("ShowOrderInCustomerDisplay", sale.sale, "", sale.customer_display_key);
                sale.getTableSaleList();
            }

        });
    } else {
        sale.getTableSaleList()
        sale.saleNetworkLock(backup_sale)
    }
    //CDS
    socket.emit("ShowOrderInCustomerDisplay", sale.sale, "new", sale.customer_display_key);
}



async function _onLoadMenu() { 
    menu_categories.value = product.posMenu1LevelData["menu_categories"]??[];
    menu_products.value = product.posMenu1LevelData["menu_products"]??[];
}

async function onCheckExpireHappyHoursPromotion() {
    if(sale.promotion){
        const valid_promotion = await call.post("epos_restaurant_2023.api.promotion.check_promotion", {
            check_time: 1,
            business_branch: gv.setting.business_branch || ''
        })
        if (valid_promotion.message) {
            let doc = valid_promotion.message;
            gv.promotion = doc;
            sale.promotion = doc;
        }
    }
}


const onSettingClick = () => {
    dialog.open(ComMenuSetting, {
        props: {
            header: $t("Menu Setting"),
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closable: false
        },
        onClose: async (options) => {
            if (options.data?.reload_menu) {
                is_loading.value = true;
                await _onLoadMenu();
                is_loading.value = false;
            }
        }
    });
}



</script>

<style scoped>
.overlay {
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    position: fixed;
    background: rgb(255, 255, 255);
}

.overlay__inner {
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    position: absolute;
}

.overlay__content {
    left: 50%;
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
}

.spinner {
    width: 50px;
    height: 50px;
    display: inline-block;
    border-width: 3px;
    border-color: rgba(255, 255, 255, 0.05);
    border-top-color: rgb(176 0 32) !important;

    animation: spin 1s infinite linear;
    border-radius: 100%;
    border-style: solid;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}
</style>