<template>
    <ComLoadingDialog v-if="isLoading" />
    <div class="two-col-list">
        <v-list-item v-if="device_setting.show_reference_button_in_more_menu == 1" prepend-icon="mdi-format-list-bulleted"
            :title="($t('Reference') + ' #')" @click="onReferenceNumber()" />
        <v-list-item prepend-icon="mdi-eye-outline" :title="$t('View Bill')" @click="onViewBill()"
            v-if="sale.sale.sale_products.length > 0" />

        <v-list-item @click="onRemoveSaleNote()" v-if="sale.sale.note">
            <template v-slot:prepend>
                <v-icon icon="mdi-note-outline" color="error"></v-icon>
            </template>
            <v-list-item-title class="text-red-700">{{ $t('Remove Note') }}</v-list-item-title>
        </v-list-item>
        <v-list-item prepend-icon="mdi-note-outline" :title="$t('Note')" @click="sale.onSaleNote(sale.sale)" v-else />


        <v-list-item prepend-icon="mdi-currency-usd" :title="$t('Commission')"
            v-if="gv.device_setting.show_button_commission == 1" @click="onAddCommission()" />


        <v-list-item v-if="setting.price_rules.length > 1" prepend-icon="mdi-bulletin-board" :title="$t('Change Price Rule')" @click="onChangePriceRule()" />


        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-silverware"
            :title="$t('Change POS Menu')" @click="onChangePOSMenu()" />

        <v-list-item v-if="isWindow && gv.device_setting.is_order_station == 0" prepend-icon="mdi-cash-100"
            :title="$t('Open Cash Drawer')" @click="onOpenCashDrawer()" />

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-grid-large"
            :title="$t('Change or Merge Table')" @click="onChangeTable()" />

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-note-text"
            :title="$t('Split Bill')" @click="onSplitBill()" />

        <v-list-item v-if="device_setting.show_move_item_button" prepend-icon="mdi-folder-move" :title="$t('Move Item(s)')"
            @click="onMoveItem()" />

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0 && setting.use_guest_cover == 1"
            prepend-icon="mdi-account-multiple-outline" :title="`${$t('Change Guest Cover')} (${sale.sale.guest_cover})`"
            @click="onUpdateGuestCover()" />

        <v-list-item v-if="gv.device_setting.show_button_change_sale_type == 1" prepend-icon="mdi-cart"
            :title="$t('Change Sale Type')" @click="onChangeSaleType()" />

        <v-list-item prepend-icon="mdi-translate" :title="($t('Menu Language') + '(' + onLoadMenuLabel + ')')"
            @click="onChangeMenuLanguage()" />

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-chair-school"
            :title="$t('Seat') + '#'" @click="onSeatNumber()" />

        <v-list-item v-if="(device_setting.show_button_resend || 0) == 1" prepend-icon="mdi-printer-outline"
            :title="$t('Re-Send')" @click="onResend()" />

        <v-list-item prepend-icon="mdi-apple-keyboard-command" :title="$t('Tax Setting')" @click="onChangeTaxSetting()"
            v-if="sale.setting.tax_rules.length > 0" />
            
        <v-list-item v-if="device_setting.show_park_button == 1" @click="onRedeemClick()">
            <template #prepend>
                <v-icon icon="mdi-parking"></v-icon>
            </template>
            <v-list-item-title>{{ $t('Redeem Item') }} {{ showSplitBill }}</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="sale.sale.sale_products?.filter(r => r.name == undefined).length > 0" @click="onClearOrder()">
            <template #prepend>
                <v-icon color="error" icon="mdi-autorenew"></v-icon>
            </template>
            <v-list-item-title class="text-orange-700">{{ $t('Cancel Order') }}</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="(device_setting?.show_edit_menu_button || 0) == 1" @click="onEditPOSMenu()">
            <template #prepend>
                <v-icon icon="mdi-file-edit"></v-icon>
            </template>
            <v-list-item-title>{{ $t('Edit Menu Item') }}</v-list-item-title>
        </v-list-item>
        <v-list-item  @click="showMenuSetting()">
            <template #prepend>
                <v-icon icon="mdi-file-edit"></v-icon>
            </template>
            <v-list-item-title>{{ $t('Menu Setting') }}</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="sale.sale.total_cash_coupon_claim > 0" @click="onClaimCouponClick()">
            <template #prepend>
                <v-icon icon="mdi-card-bulleted-outline"></v-icon>
            </template>
            <v-list-item-title>{{ $t('Claim Coupon')}}</v-list-item-title>
        </v-list-item>

        <v-list-item @click="onRateIncludeOrNotIncludeTaxClick" v-if="gv.device_setting.show_rate_include_button==1">
            <template #prepend>
                <v-icon :class="sale.sale.rate_include_tax == 1 ? 'text-red-700':''" :icon="sale.sale.rate_include_tax == 1 ? 'mdi-tag-remove' : 'mdi-tag-plus'"></v-icon>
            </template>
            <v-list-item-title :class="sale.sale.rate_include_tax == 1 ? 'text-red-700':''">{{ $t(sale.sale.rate_include_tax == 1 ? 'Remove Rate Include Tax' : 'Rate Include Tax') }}</v-list-item-title>
        </v-list-item>

        <v-divider inset></v-divider>
        <v-list-item v-if="sale.sale.name" @click="onDeleteBill()">
            <template #prepend>
                <v-icon color="error" icon="mdi-delete"></v-icon>
            </template>
            <v-list-item-title class="text-red-700">{{ $t('Delete Bill') }} {{ showSplitBill }}</v-list-item-title>
        </v-list-item>
    </div>
</template>
<script setup>
import {
    computed, RedeemParkItemDialog,
    useRouter, onMounted, splitBillDialog, addCommissionDialog, ComSaleReferenceNumberDialog, viewBillModelModel, ref, inject, confirm, createResource,
    keyboardDialog, changeTableDialog,
    changePriceRuleDialog,
    changeSaleTypeModalDialog,
    createToaster,
    changePOSMenuDialog,
    i18n, ResendDialog,
    MoveItemModal,
    EditPOSMenuDialog,
    scanCouponDialog
} from "@/plugin"
import { useDisplay } from 'vuetify'
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
import ComMenuSetting from '@/views/sale/components/ComMenuSetting.vue';

import socket from '@/utils/socketio';

const { t: $t } = i18n.global;
const moment = inject("$moment")
const { mobile } = useDisplay()
const toaster = createToaster({ position: 'top-right' })
const router = useRouter();
const sale = inject('$sale')
const gv = inject('$gv')
const product = inject('$product')
const frappe = inject("$frappe")
const db = frappe.db();
const call = frappe.call();
const setting = JSON.parse(localStorage.getItem("setting"))
const isWindow = localStorage.getItem('is_window') == 1
const isLoading = ref(false);
const device_setting = JSON.parse(localStorage.getItem("device_setting"))

let deletedSaleProducts = [];
let productPrinters = [];

let count_sale_type = ref({})
import { useDialog } from 'primevue/usedialog';
const dialog = useDialog();
const showMenuSetting = () => {
    dialog.open(ComMenuSetting, {
        props: {
            header: 'Menu Setting',
            style: {
                width: '50vw',
            },
            breakpoints:{
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        }
    });
}

onMounted(() => {
    db.getCount('Sale Type').then((count) => {
        count_sale_type.value = count;
    })
});

const onLoadMenuLabel = computed(() => {
    const mlang = localStorage.getItem('mLang');
    if (mlang != null) {
        if (mlang == "km") {
            return $t("Default");
        } else {
            return $t("Second");
        }
    } else {
        return $t("Second");
    }
})

function onRateIncludeOrNotIncludeTaxClick(){
    gv.authorize(
      "apply_rate_include_tax_required_password",
      "allow_apply_tax_include_rate",
      "apply_rate_include_tax_required_note",
      "Change Tax Setting"
    ).then((v) => {
      if (v) {
        sale.onRateIncludeOrNotIncludeTaxClick()
      }
    });
    
}


async function onViewBill() {
    const result = await viewBillModelModel({})
}
async function onUpdateGuestCover() {
    if (!sale.isBillRequested()) {
        if (setting.use_guest_cover == 1) {
            const result = await keyboardDialog({ title: $t('Guest Cover'), type: 'number', value: sale.sale.guest_cover });

            if (typeof result != 'boolean' && result != false || result == 0) {

                sale.sale.guest_cover = parseInt(result);
                if (sale.sale.guest_cover == undefined || isNaN(sale.sale.guest_cover)) {
                    sale.sale.guest_cover = 0;
                }
            } else {
                return;
            }
        }
    }
}

async function onChangeMenuLanguage() {
    sale.onChangeMenuLanguage();
    await setTimeout(function () {
        sale.load_menu_lang = false;
    }, 1);
}

async function onChangeTable() {
    if (setting.allow_change_table_after_print_bill == 0){
        if (!sale.isBillRequested()) {

        const result = await changeTableDialog({ pos_profile: localStorage.getItem('pos_profile') });
        if (result) {
            if (result.action == "reload_sale") {
                await sale.LoadSaleData(result.name);
            }
        }
    }
    }else {
        const result = await changeTableDialog({ pos_profile: localStorage.getItem('pos_profile') });
        if (result) {
            if (result.action == "reload_sale") {
                await sale.LoadSaleData(result.name);
            }
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
                product.getProductMenuByProductCategory( "All Product Categories")
            }

            window.postMessage("close_modal", "*");
            toaster.success($t("msg.Change price rule successfully"));
        }
    }
}
async function onChangePOSMenu() {
    const result = await changePOSMenuDialog({})
    if (result == true) {
        if (product.setting.pos_menus.length > 0) {
            product.loadPOSMenu()
        } else {
            product.loadPOSMenu()
            product.getProductMenuByProductCategory( "All Product Categories")
        }
        window.postMessage("close_modal", "*");
        toaster.success($t("msg.Change POS Menu successfully"));
    }

}
function onRemoveSaleNote() {
    if (!sale.isBillRequested()) {
        sale.sale.note = ''
    }
}
async function onChangeSaleType() {
    if (!sale.isBillRequested()) {
    const result = await changeSaleTypeModalDialog({})
    }
}

function onOpenCashDrawer() {
    if (!sale.isBillRequested()) {
    gv.authorize("open_cashdrawer_require_password", "open_cashdrawer").then((v) => {
        if (v) {
            window.chrome.webview.postMessage(JSON.stringify({ action: "open_cashdrawer" }));
        }
    });
}
}
async function onSeatNumber() {
    if (!sale.isBillRequested()) {
        const result = await keyboardDialog({ title: $t('Change Seat Number'), type: 'number', value: sale.sale.seat_number });

        if (typeof result == 'number') {

            sale.sale.seat_number = parseInt(result);
            if (sale.sale.seat_number == undefined || isNaN(sale.sale.seat_number)) {
                sale.sale.seat_number = 0;
            }

        } else {
            return;
        }
    }
}
async function onReferenceNumber() {
    if (!sale.isBillRequested()) {
        const reference_number = await ComSaleReferenceNumberDialog({
            data: sale.sale
        })
        if (typeof (reference_number) != 'boolean')
            sale.sale.reference_number = reference_number
    }
}
async function onDeleteBill() {
    if (!sale.isBillRequested()) {
        //check authorize and     check reason 
        gv.authorize("delete_bill_required_password", "delete_bill", "delete_bill_required_note", "Delete Bill Note").then(async (v) => {
            if (v) {
                if (v.show_confirm == 1) {
                    if (await confirm({ title: $t('Delete Sale Order'), text: $t('msg.are you sure to delete this sale order') }) == false) {
                        // window.postMessage("close_modal", "*");
                        return;
                    }
                }
            
                //cancel payment first
                isLoading.value = true;

                //send deleted sale product to temp deleted
                const _sale = JSON.parse(JSON.stringify(sale.sale));
                generateSaleProductPrintToKitchen(_sale, v.note);

                const deleteSaleResource = createResource({
                    url: "epos_restaurant_2023.api.api.delete_sale",
                    params: {
                        name: sale.sale.name,
                        auth: { full_name: v.user, username: v.username, note: v.note }
                    },
                    onError(err) {
                        isLoading.value = false;
                    }
                });

                await deleteSaleResource.fetch().then((v) => {
                    isLoading.value = false;
                    toaster.success($t("msg.Delete sale order successfully"));
                    //print to kitchen
                    onProcessPrintToKitchen(_sale);
                    sale.newSale();
                    if (sale.setting.table_groups.length > 0) {
                        router.push({ name: 'TableLayout' });
                    } else {
                        router.push({ name: "AddSale" });
                    }
                })
            }
        })
    }
}


// generate print kot when delete bill 
function generateSaleProductPrintToKitchen(doc, note) {
    deletedSaleProducts = [];
    (doc.sale_products || []).forEach((sp) => {
        if (sp.sale_product_status == "Submitted") {
            sp.note = note;
            sp.deleted_item_note = "Bill Deleted";
            deletedSaleProducts.push(sp);
        }
    });

    //generate deleted product to product printer list
    deletedSaleProducts.filter(r => JSON.parse(r.printers).length > 0).forEach((r) => {
        const pritners = JSON.parse(r.printers);
        pritners.forEach((p) => {
            productPrinters.push({
                printer: p.printer,
                group_item_type: p.group_item_type,
                is_label_printer: p.is_label_printer == 1,
                ip_address: p.ip_address,
                port: p.port,
                usb_printing: p.usb_printing,
                product_code: r.product_code,
                product_name_en: r.product_name,
                product_name_kh: r.product_name_kh,
                portion: r.portion,
                unit: r.unit,
                modifiers: r.modifiers,
                note: r.note,
                quantity: r.quantity,
                is_deleted: true,
                is_free: r.is_free == 1,
                combo_menu: r.combo_menu,
                combo_menu_data: r.combo_menu_data,
                deleted_note: r.deleted_item_note,
                order_by: r.order_by,
                creation: r.creation,
                modified: r.modified,
                reference_sale_product: r.reference_sale_product,
                duration: r.duration,
                time_stop: (r.time_stop || 0),
                time_in: r.time_in,
                time_out_price: r.time_out_price,
                time_out: r.time_out
            })
        });
    });
}


function onProcessPrintToKitchen(doc) {
    const data = {
        action: "print_to_kitchen",
        setting: setting?.pos_setting,
        sale: doc,
        product_printers: productPrinters
    }

    if (localStorage.getItem("is_window") == 1) {
        window.chrome.webview.postMessage(JSON.stringify(data));
    } else {
        socket.emit("PrintReceipt", JSON.stringify(data))
    }

    if(productPrinters.length>0){
        [...new Set(productPrinters.map(r=>r.printer))].forEach(p=>{
              
             socket.emit("SubmitKOD",{"screen_name":p})
        })
    }
    

    deletedSaleProducts = [];
    productPrinters = [];
}

async function onClearOrder() {
    if (!sale.isBillRequested()) {
        if (await confirm({ title: $t('Cancel sale order'), text: $t('msg.are your sure to cancel this sale order') })) {
            const sale_products = JSON.parse(JSON.stringify(sale.sale.sale_products.filter(r => r.name != undefined)));
            sale.sale.sale_products = sale_products || [];
            sale.updateSaleSummary();
            //add to audit trail log 
            //future update

        }
    }


}

async function onAddCommission() {
    if (!sale.isBillRequested()) {
        const result = await addCommissionDialog({ title: 'title', name: 'Sale Commission', data: sale.sale });
        if (result != false) {
            sale.sale = result.data
        }
    }
}


//split bills method
async function onSplitBill() {
    if (!sale.isBillRequested()) {
        if (sale.sale.sale_products.length == 0) {
            toaster.warning($t("msg.Please select a menu item to continue"));
            return;
        }
        else if (sale.sale.sale_status != 'Submitted' || sale.sale.sale_products.find(r => r.sale_product_status != 'Submitted')) {
            toaster.warning($t('msg.please save or submit your current order first', [$t('Submit')]))
        } else {
            const res = await splitBillDialog({ title: $t('Split Bill'), name: 'Split Bill', data: sale.sale });
            if (res != false) {
                sale.getTableSaleList()
            }
        }

    }

}

async function onChangeTaxSetting() {
    if (!sale.isBillRequested()) {
        const resp = await sale.onChangeTaxSetting($t('Change Tax Setting'), sale.sale.tax_rule, sale.sale.change_tax_setting_note, gv);
    }
}

function onResend() {
    if (!sale.isBillRequested()) {
        if (sale.sale.sale_products.length == 0) {
            toaster.warning($t("msg.Please select a menu item to continue"));
            return;
        }
        else if (sale.sale.sale_status != 'Submitted' || sale.sale.sale_products.find(r => r.sale_product_status != 'Submitted')) {
            toaster.warning($t('msg.please save or submit your current order first', [$t('Submit')]))
        } else {
            ResendDialog($t('Re-Send'));
        }
    }
}

function onRedeemClick() {
    if (!sale.isBillRequested()) {
        call.get("epos_restaurant_2023.api.api.get_current_shift_information", {
            business_branch: gv.setting?.business_branch,
            pos_profile: localStorage.getItem("pos_profile")
        }).then(async (_res) => {
            const _data = _res.message;
            if (_data.working_day == null) {
                toaster.warning($t("msg.Please start working day first"))
            } else if (_data.cashier_shift == null) {
                toaster.warning($t("msg.Please start shift first"))
            } else {
                const today = moment(new Date()).format('yyyy-MM-DD');
                const result = await RedeemParkItemDialog();
            }
        });
    }
}

async function onMoveItem() {
    if (!sale.isBillRequested()) {
        if (sale.sale.sale_products.length == 0) {
            toaster.warning($t("msg.Please select a menu item to continue"));
            return;
        }
        else if (sale.sale.sale_status != 'Submitted' || sale.sale.sale_products.find(r => r.sale_product_status != 'Submitted')) {
            toaster.warning($t('msg.please save or submit your current order first', [$t('Submit')]))
        } else {
            const res = await MoveItemModal({ title: $t('Move Item') });
        }
    }
}
async function onEditPOSMenu() {


    const res = await EditPOSMenuDialog({ title: $t('Edit Menu Item') });
}

async function onClaimCouponClick(){ 
 
    if (!sale.isBillRequested()) {
        if (sale.sale.sale_products.length == 0) {
            toaster.warning($t("msg.Please select a menu item to continue"));
            return;
        }
        const result = await scanCouponDialog();
    }
}

</script>
<style>
.two-col-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 50px);
    grid-gap: 0px;
}
</style>