<template>
    <div class="py-2 flex flex-wrap">

        <div class="v-row ga-3">
            <ComSaleInformationbox bgColor="bg-blue-500" title="POS Profile" :value="sale.sale.pos_profile" size="large"
                icon="mdi-cash-register" />
            <ComSaleInformationbox bgColor="bg-blue-500" title="Outlet/WareHouse"
                :value="sale.sale.outlet + '/' + sale.sale.stock_location" size="large" icon="mdi-store" />
            <ComSaleInformationbox bgColor="bg-blue-500" title="Working Day" :value="sale.sale.working_day" size="large"
                icon="mdi-calendar" />
            <ComSaleInformationbox bgColor="bg-blue-500" title="Cashier Shift" :value="sale.sale.cashier_shift"
                size="large" icon="mdi-clock-time-nine-outline" />
            <ComSaleInformationbox bgColor="bg-blue-500" title="Price Rule" :value="sale.sale.price_rule" size="large"
                icon="mdi-currency-usd" />
        </div>
    </div>
</template>

<script setup>
import ComSaleInformationbox from '@/views/sale/components/retail_ui/ComSaleInformationbox.vue';

import { inject, keyboardDialog, changePriceRuleDialog, createToaster, i18n, computed } from '@/plugin';


const { t: $t } = i18n.global;


const toaster = createToaster({ position: 'top-right' })
const sale = inject("$sale")
const product = inject("$product")
const setting = JSON.parse(localStorage.getItem("setting"))



async function onChangeMenuLanguage() {
    sale.onChangeMenuLanguage();
    await setTimeout(function () {
        sale.load_menu_lang = false;
    }, 1);
}

async function onUpdateGuestCover() {
    if (setting.use_guest_cover == 1) {
        const result = await keyboardDialog({ title: $t('Guest Cover'), type: 'number', value: sale.sale.guest_cover });
        if (typeof result != 'boolean' && result != false) {
            sale.sale.guest_cover = parseInt(result);
            if (sale.sale.guest_cover == undefined || isNaN(sale.sale.guest_cover)) {
                sale.sale.guest_cover = 0;
            }

        } else {
            return;
        }
    }
}
async function onUpdateSeatNumber() {
    const result = await keyboardDialog({ title: $t('Change Seat Number'), type: 'number', value: sale.sale.seat_number });
    if (result) {
        if (typeof result != 'boolean' && result != false) {
            sale.sale.seat_number = result;
        }
    }
}
async function onChangePriceRule() {
    if (sale.sale.sale_status != 'New') {
        toaster.warning($t('msg.This bill is not new order'));
        return;
    }
    if (!sale.isBillRequested()) {
        const result = await changePriceRuleDialog({})
        if (result == true) {
            if (product.setting.pos_menus.length > 0) {
                product.loadPOSMenu()
            } else {
                product.loadPOSMenu()
                product.getProductMenuByProductCategory( "All Product Categories")
            }

            toaster.success("msg.Change price rule successfully");
        }
    }
}
</script>