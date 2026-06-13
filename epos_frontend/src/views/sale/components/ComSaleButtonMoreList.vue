<template>
    <ComLoadingDialog v-if="isLoading" />
    <div class="two-col-list">
        <v-list-item v-if="device_setting.show_reference_button_in_more_menu == 1" prepend-icon="mdi-format-list-bulleted" style="font-family: Khmer OS Siemreap;"
            @click="onReferenceNumber()">
             <div style="font-family: Khmer OS Siemreap;">{{ $t('Reference') + ' #' }}</div>
        </v-list-item>
        <v-list-item prepend-icon="mdi-eye-outline" @click="onViewBill()" v-if="sale.sale.sale_products.length > 0">
             <div style="font-family: Khmer OS Siemreap;">{{ $t('View Bill')}}</div>
        </v-list-item>

        <v-list-item @click="onRemoveSaleNote()" v-if="sale.sale.note">
            <template v-slot:prepend>
                <v-icon icon="mdi-note-outline" color="error"></v-icon>
            </template>
            <v-list-item-title class="text-red-700">
                <div style="font-family: Khmer OS Siemreap;">{{ $t('Remove Note') }}</div>
            </v-list-item-title>
        </v-list-item>
        <v-list-item prepend-icon="mdi-note-outline" @click="sale.onSaleNote(sale.sale)" v-else>
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Note') }}</div>
        </v-list-item>

        <v-list-item prepend-icon="mdi-currency-usd" v-if="gv.device_setting.show_button_commission == 1" @click="onAddCommission()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Commission') }}</div>
        </v-list-item>

        <v-list-item v-if="setting.price_rules.length > 1" prepend-icon="mdi-bulletin-board" @click="onChangePriceRule()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Change Price Rule') }}</div>
        </v-list-item>

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-silverware" @click="onChangePOSMenu()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Change POS Menu') }}</div>
        </v-list-item>

        <v-list-item v-if="isWindow && gv.device_setting.is_order_station == 0" prepend-icon="mdi-cash-100" @click="onOpenCashDrawer()">
             <div style="font-family: Khmer OS Siemreap;">{{ $t('Open Cash Drawer') }}</div>
        </v-list-item>

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-grid-large" @click="onChangeTable()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Change or Merge Table') }}</div>
        </v-list-item>

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-note-text" @click="onSplitBill()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Split Bill') }}</div>
        </v-list-item>

        <v-list-item v-if="device_setting.show_move_item_button" prepend-icon="mdi-folder-move" @click="onMoveItem()">
             <div style="font-family: Khmer OS Siemreap;">{{ $t('Move Item(s)') }}</div>
        </v-list-item>

        <v-list-item v-if="setting.table_groups && setting.table_groups.length > 0 && setting.use_guest_cover == 1" prepend-icon="mdi-account-multiple-outline" @click="onUpdateGuestCover()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Change Guest Cover '+'('+sale.sale.guest_cover+')')}}</div>
        </v-list-item>

        <v-list-item v-if="gv.device_setting.show_button_change_sale_type == 1" prepend-icon="mdi-cart" @click="onChangeSaleType()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Change Sale Type') }}</div>
        </v-list-item>

        <v-list-item prepend-icon="mdi-translate" @click="onChangeMenuLanguage()">
                 <div style="font-family: Khmer OS Siemreap;">{{ $t('Menu Language') + '(' + onLoadMenuLabel + ')' }}</div>
        </v-list-item>

        <v-list-item v-if="gv.device_setting.show_seat_number_button == 1 && setting.table_groups && setting.table_groups.length > 0" prepend-icon="mdi-chair-school" @click="onSeatNumber()">
             <div style="font-family: Khmer OS Siemreap;">{{ $t('Seat') + '#' }}</div>
        </v-list-item>

        <v-list-item v-if="(device_setting.show_button_resend || 0) == 1" prepend-icon="mdi-printer-outline" @click="onResend()">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Re-Send') }}</div>
        </v-list-item>

        <v-list-item prepend-icon="mdi-apple-keyboard-command" @click="onChangeTaxSetting()" v-if="sale.setting.tax_rules.length > 0">
            <div style="font-family: Khmer OS Siemreap;">{{ $t('Tax Setting') }}</div>
        </v-list-item>
            
        <v-list-item v-if="device_setting.show_park_button == 1" @click="onRedeemClick()">
            <template #prepend>
                <v-icon icon="mdi-parking"></v-icon>
            </template>
            <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ $t('Redeem Item') }} {{ showSplitBill }}</div></v-list-item-title>
        </v-list-item>

        <v-list-item v-if="sale.sale.sale_products?.filter(r => r.name == undefined).length > 0" @click="onClearOrder()">
            <template #prepend>
                <v-icon color="error" icon="mdi-autorenew"></v-icon>
            </template>
            <v-list-item-title class="text-orange-700"><div style="font-family: Khmer OS Siemreap;">{{ $t('Cancel Order') }}</div></v-list-item-title>
        </v-list-item>

        <v-list-item v-if="(device_setting?.show_edit_menu_button || 0) == 1" @click="onEditPOSMenu()">
            <template #prepend>
                <v-icon icon="mdi-file-edit"></v-icon>
            </template>
            <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ $t('Edit Menu Item') }}</div></v-list-item-title>
        </v-list-item>
        <v-list-item  @click="showMenuSetting()">
            <template #prepend>
                <v-icon icon="mdi-file-edit"></v-icon>
            </template>
            <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ $t('Menu Setting') }}</div></v-list-item-title>
        </v-list-item>

        <v-list-item v-if="sale.sale.total_cash_coupon_claim > 0" @click="onClaimCouponClick()">
            <template #prepend>
                <v-icon icon="mdi-card-bulleted-outline"></v-icon>
            </template>
            <v-list-item-title><div style="font-family: Khmer OS Siemreap;">{{ $t('Claim Coupon')}}</div></v-list-item-title>
        </v-list-item>

        <v-list-item @click="onRateIncludeOrNotIncludeTaxClick" v-if="gv.device_setting.show_rate_include_button==1">
            <template #prepend>
                <v-icon :class="sale.sale.rate_include_tax == 1 ? 'text-red-700':''" :icon="sale.sale.rate_include_tax == 1 ? 'mdi-tag-remove' : 'mdi-tag-plus'"></v-icon>
            </template>
            <v-list-item-title :class="sale.sale.rate_include_tax == 1 ? 'text-red-700':''"><div style="font-family: Khmer OS Siemreap;">{{ $t(sale.sale.rate_include_tax == 1 ? 'Remove Rate Include Tax' : 'Rate Include Tax') }}</div></v-list-item-title>
        </v-list-item>

        <v-divider inset></v-divider>
        <v-list-item v-if="sale.sale.name" @click="onDeleteBill()">
            <template #prepend>
                <v-icon color="error" icon="mdi-delete"></v-icon>
            </template>
            <v-list-item-title class="text-red-700"><div style="font-family: Khmer OS Siemreap;">{{ $t('Delete Bill') }} {{ showSplitBill }}</div></v-list-item-title>
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
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
import ComMenuSetting from '@/views/sale/components/ComMenuSetting.vue';

import socket from '@/utils/socketio';
import Enumerable from 'linq';

const { t: $t } = i18n.global;
const moment = inject("$moment");
const toaster = createToaster({ position: 'top-right' });
const router = useRouter();
const sale = inject('$sale');
const gv = inject('$gv');
const product = inject('$product');
const frappe = inject("$frappe");
const db = frappe.db();
const call = frappe.call();
const setting = JSON.parse(localStorage.getItem("setting"));
const isWindow = localStorage.getItem('is_window') == 1;
const isLoading = ref(false);
const device_setting = JSON.parse(localStorage.getItem("device_setting"));
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
            modal: true,
             closable: false 
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
        if (typeof (reference_number) != 'boolean'){
            sale.sale.reference_number = reference_number
        }
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
                if(sale.setting?.pos_setting?.print_new_deleted_sale_product){
                    generateSaleProductPrintToKitchen(_sale, v.note);
                }
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
                    ///print bill on deleted
                    if(sale.setting?.pos_setting?.allow_print_bill_on_sale_deleted){
                        sale.pos_receipt = gv.setting.default_pos_receipt;
                        sale.onPrintReceipt(sale.pos_receipt, "print_invoice", _sale);
                    }
                    sale.newSale();
                    
                    if (sale.setting.table_groups.length > 0) {
                        router.push({ name: 'TableLayout' });
                        socket.emit("RefreshTable");
                        window.postMessage("close_modal", "*"); 
                        //
                    } else {
                        let template = (gv.device_setting?.main_sale_screen??"Default");
                        if(template == "Default"){
                            router.push({  name: "AddSale"});
                        }else {
                            const result = template.toLowerCase().replace(/\s+/g, '-');
                            let _template = result;
                            router.push({ 
                                name: "SaleOrder",
                                query: { menu: _template }
                            });
                        }                        
                    }
                });                
            }
        })
    }
}


// generate print kot when delete bill 
 function generateSaleProductPrintToKitchen(doc, note) {
    deletedSaleProducts = [];
    (doc.sale_products || []).forEach((sp) => {
        if (sp.sale_product_status == "Submitted" && (sp.is_return || 0) == 0) {
            sp.note = note;
            sp.deleted_item_note = "Bill Deleted";
            deletedSaleProducts.push(sp);
        }
    });

    //generate deleted product to product printer list
    deletedSaleProducts.forEach( async (r) => {
        let comboItemPrinters = await sale.getProductPrinterOfComboItem(r,true);
        if(!comboItemPrinters){
            const pritners = JSON.parse(r.printers);
            pritners.forEach((p) => {
                productPrinters.push({
                    sale_product_name: (r.name || "New"),
                    printer: p.printer,
                    group_item_type: p.group_item_type,
                    is_label_printer: p.is_label_printer == 1,
                    ip_address: p.ip_address,
                    port: p.port,
                    usb_printing: p.usb_printing,
                    product_code: r.product_code,
                    product_name_en: r.product_name,
                    product_name_kh: r.product_name_kh,
                    kitchen_group:r.kitchen_group||"",
                    kitchen_group_sort_order: r.kitchen_group_sort_order || 0,
                    seat_number: r.seat_number||"",
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
                    time_out: r.time_out,
                    amount: r.amount
                });
            });
        }else{
            comboItemPrinters.forEach((p)=>{
                productPrinters.push(p);
            });
        }
    });
}


function onProcessPrintToKitchen(doc) {
    let _productPrinters = productPrinters;
    const data = {
        action: "print_to_kitchen",
        setting: setting?.pos_setting,
        sale: doc,
        product_printers: productPrinters,
        station_device_printing: (sale.setting?.device_setting?.station_device_printing) || "",
        printers: []
    }

    var groupKeys = "{printer:$.printer,group_item_type:$.group_item_type,ip_address:$.ip_address,port:$.port}"
    var groupFields = "$.printer+','+$.group_item_type+','+$.ip_address+','+$.port";
    var printers = Enumerable.from(data.product_printers).groupBy(groupKeys, "", groupKeys, groupFields).toArray();    
    printers.forEach((p) => {
        var _printer = data.product_printers.filter((x) => x.printer == p.printer)
        if (_printer.length > 0) {
            data.printers.push({
                "printer_name": _printer[0].printer,
                "group_item_type": _printer[0].group_item_type,
                "ip_address": _printer[0].ip_address,
                "port": _printer[0].port,
                "is_label_printer": (_printer[0].is_label_printer ?? false) ? 1 : 0,
                "usb_printing": _printer[0].usb_printing ?? 0,
                "products": _printer
            });
        }
        // We send this to refresh kitchen order display
         [...new Set(productPrinters.map(r=>r.printer))].forEach(p=>{              
            socket.emit("SubmitKOD", { "screen_name": _printer[0].printer })
        });        
    });

    let kotProducts = {
            action: "print_to_kitchen",
            setting: sale.setting?.pos_setting,
            sale: doc,
            product_printers: _productPrinters,
            station_device_printing: (sale.setting?.device_setting?.station_device_printing) || "",
            printers: [],
        }
    let productUSBPrinter = JSON.parse(JSON.stringify(kotProducts));
    kotProducts.printers = [];
    productUSBPrinter.printers = [];
    let station_printers = (sale.setting?.device_setting?.station_printers);
    if (station_printers.length <= 0) {
        //
    } else {
        station_printers.forEach((p) => {                
            let temp_sale_products = data.product_printers.filter((x) => x.printer == p.printer_name)
            if (temp_sale_products.length > 0) {
                if (p.usb_printing == 1) {
                    productUSBPrinter.printers.push({
                        "printer_name": p.printer_name,
                        "group_item_type": p.group_item_type,
                        "ip_address": p.ip_address,
                        "port": p.port,
                        "cashier_printer": p.cashier_printer,
                        "is_label_printer": p.is_label_printer,
                        "usb_printing": p.usb_printing,
                        "products": temp_sale_products
                    });
                } else {
                    kotProducts.printers.push({
                        "station": this.setting?.device_setting?.name ?? "",
                        "printer": {
                            "printer_name": p.printer_name,
                            "group_item_type": p.group_item_type,
                            "ip_address": p.ip_address,
                            "port": p.port,
                            "cashier_printer": p.cashier_printer,
                            "is_label_printer": p.is_label_printer,
                            "usb_printing": p.usb_printing,
                        },
                        "products": temp_sale_products
                    });
                }
            }
        });
    }

    if ((sale.setting?.device_setting?.use_server_network_printing || 0) == 1) {
        //printer network
        if (kotProducts.printers.length > 0) {
            call.post("epos_restaurant_2023.api.network_printing_api.print_kot_to_network_printer", { "data": kotProducts });
        }
        //trigger print usb print
        if (productUSBPrinter.printers.length > 0) {
            socket.emit("PrintReceipt", JSON.stringify(productUSBPrinter));
        }
    } else {
        if (localStorage.getItem("is_window") == 1) {
            if ((data.product_printers ?? []).length > 0) {
                window.chrome.webview.postMessage(JSON.stringify(data));
            }
        }
        else if ((localStorage.getItem("flutterWrapper") || 0) == 1) {
            if (_productPrinters.length > 0) {
                //trigger printer network
                if (kotProducts.printers.length > 0) {
                    flutterChannel.postMessage(JSON.stringify(kotProducts));
                }
                //trigger print usb print
                if (productUSBPrinter.printers.length > 0) {
                    socket.emit("PrintReceipt", JSON.stringify(productUSBPrinter));
                }
            }
        }
        else {
            socket.emit("PrintReceipt", JSON.stringify(data));
        }
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