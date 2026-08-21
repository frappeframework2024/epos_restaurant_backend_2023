<template>
    <v-menu>
        <template v-slot:activator="{ props }">
            <v-chip v-bind="props" variant="elevated" color="primary" class="mx-1 grow text-center justify-center"
                size="small">{{ $t('More') }}</v-chip>
        </template>
        <v-list style="font-family: Khmer OS Siemreap;">

            <v-list-item prepend-icon="mdi-pencil" :title="$t('Edit')" v-if="canEdit" 
                @click="onEditSaleProduct(saleProduct)"></v-list-item>

            <v-list-item prepend-icon="mdi-note-text" :title="$t('Split Item')" v-if="gv.device_setting.show_split_item_button==1 && saleProduct.quantity > 1"
                @click="sale.onSplitSaleProduct(saleProduct)"></v-list-item>


            <!-- free -->
            <template v-if="!saleProduct.is_timer_product && (saleProduct.allow_free || 0) == 1">
                <v-list-item prepend-icon="mdi-currency-usd-off" :title="$t('Free')" v-if="!saleProduct.is_free"
                    @click="onSaleProductFree()"></v-list-item>

                <v-list-item v-else @click="sale.onSaleProductCancelFree(saleProduct)">
                    <template v-slot:prepend>
                        <v-icon icon="mdi-currency-usd-off" color="error"></v-icon>
                    </template>
                    <v-list-item-title class="text-red-700">{{ $t('Cancel Free') }}</v-list-item-title>
                </v-list-item>
            </template>
            <!-- end free --> 
            <template v-if="!saleProduct.is_free && (saleProduct.allow_discount || 0) == 1">
                <template v-if="!saleProduct.happy_hour_promotion">
                    <v-list-item prepend-icon="mdi-percent" :title="$t('Discount Percent')"
                        @click="onSaleProductDiscount('Percent')"></v-list-item>
                    <v-list-item prepend-icon="mdi-currency-usd" :title="$t('Discount Amount')"
                        @click="onSaleProductDiscount('Amount')"></v-list-item>
                </template>
                <v-list-item v-if="saleProduct.discount > 0" @click="onSaleProductCancelDiscount()">
                    <template v-slot:prepend>
                        <v-icon icon="mdi-tag-multiple" color="error"></v-icon>
                    </template>
                    <v-list-item-title class="text-red-700">{{ $t('Cancel Discount') }}</v-list-item-title>
                </v-list-item>
            </template> 

            <!-- <template v-if="!(saleProduct.is_require_employee || false) && !saleProduct.is_timer_product">
                <v-list-item v-if="tableLayout.table_groups && tableLayout.table_groups.length > 0"
                    prepend-icon="mdi-chair-school" :title="($t('Seat') + '#')"
                    @click="sale.onSaleProductSetSeatNumber(saleProduct)"></v-list-item>
            </template> -->

            <v-list-item prepend-icon="mdi-parking" :title="$t('Park Item')"
                v-if="gv.device_setting.show_park_button == 1" @click="onSaleProductPark(saleProduct)"></v-list-item>
            <v-list-item prepend-icon="mdi-note-outline" :title="$t('Note')" v-if="!saleProduct.note"
                @click="sale.onSaleProductNote(saleProduct)"></v-list-item>
            <v-list-item v-else @click="onRemoveNote">
                <template v-slot:prepend>
                    <v-icon icon="mdi-note-outline" color="error"></v-icon>
                </template>
                <v-list-item-title class="text-red-700">{{ $t('Remove Note') }}</v-list-item-title>
            </v-list-item> 
            <template v-if="gv.device_setting.show_make_return_or_selling_item_button == 1">
                <v-list-item v-if="saleProduct.quantity > 0" @click="onReturn(saleProduct)">
                    <template v-slot:prepend>
                        <v-icon icon="mdi-cash-refund" class="text-orange-700"></v-icon>
                    </template>
                    <v-list-item-title class="text-orange-700">{{ $t("Mark as Return Product") }}</v-list-item-title>
                </v-list-item>
                <v-list-item v-else @click="onReturn(saleProduct)">
                    <template v-slot:prepend>
                        <v-icon icon="mdi-cash"></v-icon>
                    </template>
                    <v-list-item-title>{{ $t("Mark as Selling Product") }}</v-list-item-title>
                </v-list-item>
            </template>
            <v-list-item :prepend-icon="saleProduct.rate_include_tax == 1 ? 'mdi-tag-remove' : 'mdi-tag-plus'"
                @click="addAndRemoveRateIncludeTax(saleProduct)"
                v-if="(saleProduct.tax_rule && gv.device_setting.is_order_station == 0 && gv.device_setting.show_rate_include_button == 1)">
                <v-list-item-title :class="saleProduct.rate_include_tax == 1 ? 'text-red-700' : ''">
                    {{$t(saleProduct.rate_include_tax == 1 ? 'Remove Rate Include Tax' : 'Rate Include Tax')}}</v-list-item-title>
            </v-list-item>
            <v-list-item prepend-icon="mdi-cash-100" :title="$t('Tax Setting')"
                v-if="(saleProduct.product_tax_rule && gv.device_setting.is_order_station == 0)"
                @click="sale.onSaleProductChangeTaxSetting(saleProduct, gv)">
            </v-list-item> 
            <template v-if="gv.device_setting.show_mark_delivered_item_button">
                <v-list-item :prepend-icon="showButtonDelivered? 'mdi-check-circle' : 'mdi-circle-outline'" :title="showButtonDelivered? $t('Mark to Delivered') :  $t('Mark to Processing')"
                @click="onMarkDelivered(saleProduct)"></v-list-item>
            </template>           
            <v-list-item v-if="productPrinter" prepend-icon="mdi-printer-outline" :title="$t('Re-Send')"
                @click="onSelectPrinter()">
            </v-list-item>
        </v-list>
    </v-menu>

    <template v-if="printServerUrl">
        <v-dialog
            v-model="showDialogSelectPrinter"
            width="765"
        >
            <v-card class="printer-dialog">
                <!-- Header -->
                <div class="dialog-header">
                    <div class="dialog-title-wrapper">
                        <div class="dialog-printer-icon">
                            🖨️
                        </div>
                        <div class="dialog-title">
                            {{ $t('Resend to Printer') }}
                        </div>
                    </div>
                    <button
                        class="dialog-close"
                        @click="showDialogSelectPrinter = false"
                    >
                        ×
                    </button>
                </div>    
                
                <!-- Top Select All -->
                <div class="top-select-all">
                    <div class="product-count">
                        <span class="count-icon">▣</span>
                        <strong>
                            {{ saleProductPrinter.length }}
                        </strong>
                        <span>
                            {{ saleProductPrinter.length === 1
                                ? $t('product')
                                : $t('products')
                            }}
                            {{$t("with printers")}}
                        </span>
                    </div>
                    <button class="select-all-btn" @click="selectAllProducts">
                        <span class="double-check">✓✓  </span> 
                        <span v-if="hasAllSelectedPrinter"> {{ $t("Clear all") }}</span>
                        <span v-else>
                             {{ $t("Select all") }}
                        </span>                       
                    </button>
                </div>

                <!-- Products -->
                <div class="products-wrapper">
                    <div
                        v-for="item in saleProductPrinter"
                        :key="item.sale_product_id"
                        class="product-card"
                    > 
                        <!-- Product Header -->
                        <div class="product-header">
                            <!-- Printer Icon -->
                            <div class="product-printer-icon">
                                <span >🖨️</span>
                            </div>
                            <!-- Product Info -->
                            <div class="product-info">
                                <div class="product-name">
                                    {{ item.product_name }}
                                </div>
                                <div class="product-code">
                                    {{ item.product_code }}
                                </div>
                            </div>
                            <!-- Qty / Price -->
                            <div class="product-price">
                                <div>
                                    {{$t("Qty")}} {{ item.quantity }}
                                </div>
                                <strong>
                                    ${{ Number(item.price).toFixed(2) }}
                                </strong>
                            </div>
                        </div>

                        <!-- Select All -->
                        <div class="select-all" @click="selectAll(item)" >
                            <span class="check-icon"  :class="{  checked: isAllSelected(item) }" >
                                ✓✓
                            </span>
                            <span v-if="item.selected_printers && (item.selected_printers?.length??0) == item.printers.length">                                
                                {{ $t("Clear all") }}
                            </span>
                            <span v-else>
                                {{ $t("Select all") }}
                            </span>
                        </div>

                        <!-- Printers -->
                        <div class="printer-list">
                            <button
                                v-for="printer in item.printers"
                                :key="printer.printer"
                                type="button"
                                class="printer-button"
                                :class="{
                                    selected: isPrinterSelected(
                                        item,
                                        printer.printer
                                    )
                                }"
                                @click="togglePrinter(
                                    item,
                                    printer.printer
                                )"
                            >
                                <span
                                    v-if="isPrinterSelected(
                                        item,
                                        printer.printer
                                    )"
                                    class="printer-check"
                                >
                                    ✓
                                </span>
                                {{ printer.printer_name }}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="dialog-footer">
                    <button
                        type="button"
                        class="cancel-button"
                        @click="showDialogSelectPrinter = false"
                    >
                        {{ $t('Cancel') }}
                    </button>

                    <button
                        type="button"
                        class="send-button"
                        :disabled="!hasSelectedPrinter || isSending"
                        @click="sendToPrinter"
                    >
                        <span>➤</span> 
                        {{ $t('Send') }}
                    </button>

                </div>

            </v-card>
        </v-dialog>
    </template>
    <template v-else>
        <v-dialog v-model="showDialogSelectPrinter" width="auto">
            <v-card :title="$t('Resend to Printer')">
                <v-card-text>
                    <v-btn class="mr-2" :color="p.selected ? 'red' : 'default'" v-for="(p, index) in printerList" :key="index"
                        @click="onSelectPritnerForPrint(p)">{{ p.printer }}</v-btn>
                </v-card-text>
                <v-card-actions>
                    <v-btn color="error" @click="showDialogSelectPrinter = false">{{ $t("Close") }}</v-btn>
                    <v-btn color="success" @click="onConfirmSelectPrinter">{{ $t("Confirm") }}</v-btn>
                </v-card-actions> 
            </v-card>
        </v-dialog>
    </template>
   
</template>

<script setup>
import { defineProps, inject, i18n, ref, computed,watch } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster'; 
import { useDialog } from 'primevue/usedialog';
import ComEditSaleProduct from '@/views/sale/components/ComEditSaleProduct.vue'; 

const { t: $t } = i18n.global;
const product = inject('$product');
const sale = inject('$sale');
const gv = inject("$gv");
var frappe = inject("$frappe")
const call = frappe.call();
const dialog = useDialog();
const props = defineProps({
    saleProduct: Object
});

const showDialogSelectPrinter = ref(false);
const printerList = ref([]);
const comboItemResend = ref([]);
const toaster = createToaster({ position: "top-right" });
const printServerUrl = sale.getPrintServerUrl();

function onRemoveNote() {
    props.saleProduct.note = "";
}

const productPrinter = computed(() => {
    if ((gv.device_setting.show_button_resend || 0) == 1) {
        if (sale.sale.sale_status != 'Submitted' || sale.sale.sale_products.find(r => r.sale_product_status != 'Submitted')) {
            return false;
        }

        if(sale.setting.pos_setting.combo_menu_print_captain_by_items_printer && props.saleProduct.is_combo_menu){
            return (!props.saleProduct.is_timer_product && (props.saleProduct.name || '') != '');
        }
        

        if (props.saleProduct.printers) {
            var printers = JSON.parse(props.saleProduct.printers);
            if (printers.length <= 0) {
                return false;
            }

            return (!props.saleProduct.is_timer_product && (props.saleProduct.name || '') != '');
        }
        return false;
    }
    return false;
});

const showButtonDelivered = computed(() => {
    
    if(gv.device_setting.show_mark_delivered_item_button == 1){
        if(!props.saleProduct.is_delivered ){
            return true;
        }
        return false;
    }
    return false;
});


const canEdit = computed(() => {

    if (props.saleProduct.is_timer_product) {
        return false
    }

    if (props.saleProduct.sale_product_status == "New") {
        return true
    }
    if (sale.setting.pos_setting.allow_change_quantity_after_submit == 1 || props.saleProduct.sale_product_status == 'Submitted') {
        return true
    }

    return false

});

const canEditVariant = computed(() => {

    if (props.saleProduct.is_timer_product) {
        return false
    }

    if (props.saleProduct.sale_product_status == "New" && props.saleProduct.is_variant) {
        return true
    }

    return false

});


watch(showDialogSelectPrinter, (newValue, oldValue) => {
    if(newValue){
        onLoadPrinterProduct(); 
    } 
});


function onReturn(sp) {
    if (sp.is_return == 0) {
            gv.authorize("return_product_required_password", "allow_return_product", "return_product_required_note", "Return Product Note", "").then((v) => {
            if (v) {
                sp.is_return = !sp.is_return
                sp.return_note = v.note
                sale.updateQuantity(sp, sp.quantity * -1)
            }
        });
    }
    else{
        sp.is_return = !sp.is_return
        sale.updateQuantity(sp, sp.quantity * -1)
    }
   
}

async function onSelectPrinter() {
    if (!sale.isBillRequested()) {

        if (props.saleProduct.backup_printers) {
            printerList.value = JSON.parse(props.saleProduct.backup_printers)
        }
        else {
            printerList.value = JSON.parse(props.saleProduct.printers)
            props.saleProduct.backup_printers = props.saleProduct.printers
        }
        printerList.value.forEach(r => r.selected = true);
        showDialogSelectPrinter.value = true;
    }
}

function addAndRemoveRateIncludeTax(saleProduct) {
    gv.authorize(
        "apply_rate_include_tax_required_password",
        "allow_apply_tax_include_rate",
        "apply_rate_include_tax_required_note",
        "Change Tax Setting"
    ).then((v) => {
        if (v) {
            sale.onRateIncludeTax(saleProduct)
        }
    });
}

function onSelectPritnerForPrint(p) {
    p.selected = !p.selected
}

async function onConfirmSelectPrinter() {
    if (!sale.isBillRequested()) {
        showDialogSelectPrinter.value = false;
        var r = props.saleProduct;
        var resendProductData = [];
        
        let comboItemPrinters = await sale.getProductPrinterOfComboItem(r);
        if(!comboItemPrinters){
            var printers = printerList.value.filter(r => r.selected == true);
            // props.saleProduct.printers = JSON.stringify(printers );      
            //resend product to kot         
            printers.forEach((p) => {
                resendProductData.push({
                    sale_product_name: r.name,
                    printer: p.printer,
                    actual_printer_name:p.actual_printer_name || p.printer,
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
                    is_deleted: false,
                    is_free: r.is_free == 1,
                    combo_menu: r.combo_menu,
                    combo_menu_data: r.combo_menu_data,
                    order_by: r.order_by,
                    order_time: r.order_time,
                    creation: r.creation,
                    modified: r.modified,
                    is_timer_product: (r.is_timer_product || 0),
                    reference_sale_product: r.reference_sale_product,
                    duration: r.duration,
                    time_stop: (r.time_stop || 0),
                    time_in: r.time_in,
                    time_out_price: r.time_out_price,
                    time_out: r.time_out,
                    reprint: true,
                    amount: r.amount
                });
            });

        }else{
            //
            comboItemPrinters.forEach((p)=>{
                p.reprint =  true;
                resendProductData.push(p);
            });
        }

        if (resendProductData.length > 0) { 
     
                await  sale.onPrintToKitchen(sale.sale, resendProductData)
          
        }
        toaster.success($t("Product was re-send"));

    }
}

function onSaleProductFree() {
    if (!sale.isBillRequested()) {
        gv.authorize("free_item_required_password", "free_item", "free_item_required_note", "Free Item Note", props.saleProduct.product_code).then((v) => {
            if (v) {
                props.saleProduct.free_note = v.note;
                props.saleProduct.free_by = v.user;
                sale.onSaleProductFree(props.saleProduct);
            }
        });

    }
}



function onSaleProductPark() {
    if (!sale.isBillRequested()) {
        gv.authorize("park_item_required_password", "park_item", props.saleProduct.product_code).then((v) => {
            if (v) {
                props.saleProduct.free_note = v.note;
                props.saleProduct.free_by = v.user;
                sale.onSaleProductPark(props.saleProduct);
            }
        });

    }
}

sale.vue?.$onKeyStroke('F8', (e) => {
    e.preventDefault()
    if (sale.dialogActiveState == false && props.saleProduct.selected == true) {
        sale.onSaleProductNote(props.saleProduct)
    }
})


function onMarkDelivered(sp){
    sp.is_delivered = (sp.is_delivered??0)?0:1
}

function onEditSaleProduct(sp) {
    if (!sale.isBillRequested()) {
        if (sp.sale_product_status == "New" || sale.setting.pos_setting.allow_change_quantity_after_submit == 1) {
            if (sale.setting.pos_menus.length > 0) {
                const is_has_product = product.setSelectedProductByMenuID(sp.menu_product_name);
                if (is_has_product) {
                    product.setModifierSelection(sp);
                    if (sp.is_combo_menu && sp.use_combo_group) {
                        product.setComboGroupSelection(sp)
                    }

                    if ((sp.is_combo_menu && sp.use_combo_group) || product.modifiers.length > 0 || product.prices.filter(r => r.price_rule == sale.setting.price_rule && (r.branch == sale.setting.business_branch || r.branch == '')).length > 1) {
                        sale.OnEditSaleProduct(sp)
                    }
                    else {
                        toaster.warning($t("msg.This item has no option to edit"))
                    }

                    return
                }


                toaster.warning($t("msg.This item has no option to edit"))


        }
        else {
            onEditSaleProductRetailPOS(sp)
        }
    }
}
}


function onEditSaleProductRetailPOS(sp) {
    const data = JSON.parse(JSON.stringify(sp))
    dialog.open(ComEditSaleProduct, {
        data: {
            product_code: data.product_code,
            sale_product:  data,
        },
        props: {
            header: $t('Product Option'),
            style: {
                width: '900px',
                background: 'white',
                color: 'black'
            },
            breakpoints: {
                '960px': '90vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {

            const data = options.data;
            if (!data) return
            
           
            if (data.product){
                sp.name = data.product.name
                sp.menu_product_name = data.product.menu_product_name
                sp.portion = data.product.portion
                sp.price = data.product.price
                sp.unit = data.product.unit
                sp.selected_variant = data.product.selected_variant
                sp.quantity = data.product.quantity
                sp.note= data.product.note
                
            }

            if(data.updatedData){
                sp.portion = data.updatedData.portion
                sp.price = data.updatedData.price
                sp.unit = data.updatedData.unit
                sp.quantity = data.updatedData.quantity
                sp.note= data.updatedData.note
                
            }
            sale.updateSaleProduct(sp)
            sale.updateSaleSummary();

         

        }
    });
}



function onSaleProductDiscount(discount_type) {
    if (props.saleProduct.allow_discount) {
        if (!sale.isBillRequested()) {
            gv.authorize("discount_item_required_password", "discount_item", "discount_item_required_note", "Discount Item Note", "", true).then((v) => {
                if (v) {
                    props.saleProduct.temp_discount_by = v.user;
                    props.saleProduct.temp_discount_note = v.note;

                    sale.onDiscount(
                        gv,
                        `${props.saleProduct.product_name} Discount`,
                        props.saleProduct.amount,
                        props.saleProduct.discount,
                        discount_type,
                        v.discount_codes,
                        props.saleProduct.discount_note,
                        props.saleProduct,
                        v.category_note_name
                    );
                }
            });
        }
    }
    else {
        toaster.warning($t('msg.This item is not allow to discount'));
    }
}


function onSaleProductCancelDiscount() {
    if (!sale.isBillRequested()) {
        gv.authorize("cancel_discount_item_required_password", "cancel_discount_item", "cancel_discount_item_required_note", "Cancel Discount Item Note", "", false).then((v) => {
            if (v) {
                let sp = props.saleProduct;
                props.saleProduct.discount = 0;
                props.saleProduct.discount_type = 'Amount'
                props.saleProduct.happy_hour_promotion = ''
                props.saleProduct.happy_hours_promotion_title = ''
                sale.updateSaleProduct(props.saleProduct)
                sale.updateSaleSummary();


                //audit trail
                let item_description = `${sp.product_code}-${sp.product_name}${(sp.portion || "") == "" ? "" : `(${sp.portion})`} ${sp.modifiers}`;
                let msg = `${v.user} remove discount on item: ${item_description} `;
                msg += `${(v.note || "") == "" ? '' : ', Reason: ' + v.note}`;
                sale.auditTrailLogs.push({
                    doctype: "Comment",
                    subject: "Remove Discount Sale Product",
                    comment_type: "Info",
                    reference_doctype: "Sale",
                    reference_name: "New",
                    comment_by: v.user,
                    content: msg,
                    custom_item_description: `${item_description}`,
                    custom_note: v.note
                });
            }
        });
    }
}



const saleProductPrinter = ref([]);
async function onLoadPrinterProduct(){
    saleProductPrinter.value = [];
    if(printServerUrl){
        const resp = await call.post("epos_restaurant_2023.api.mobile.v1.sale.get_sale_product_printers",{
            "sale_products":props.saleProduct,
        });
        if(resp.message){
            saleProductPrinter.value = resp.message;
        }  
    }
}



// ----------------------------------------
// Check printer selected
// ----------------------------------------

function isPrinterSelected(item, printerId) {
    if (!item.selected_printers) {
        return false
    }

    return item.selected_printers.includes(printerId)
}


// ----------------------------------------
// Toggle printer
// ----------------------------------------

function togglePrinter(item, printerId) {

    // Create array if it doesn't exist
    if (!item.selected_printers) {
        item.selected_printers = []
    }

    const index = item.selected_printers.indexOf(printerId)

    if (index === -1) {

        // Select
        item.selected_printers.push(printerId)

    } else {

        // Unselect
        item.selected_printers.splice(index, 1)

    }
}


// ----------------------------------------
// Select all printers for product
// ----------------------------------------

function selectAll(item) {

    if (!item.printers || !item.printers.length) {
        return
    }

    if (!item.selected_printers) {
        item.selected_printers = []
    }

    const allSelected =
        item.selected_printers.length === item.printers.length

    if (allSelected) {

        // Unselect all
        item.selected_printers = []

    } else {

        // Select all
        item.selected_printers = item.printers.map(
            printer => printer.printer
        )

    }
}


// ----------------------------------------
// Check if all printers selected
// ----------------------------------------

function isAllSelected(item) {

    if (!item.printers || !item.printers.length) {
        return false
    }

    if (!item.selected_printers) {
        return false
    }

    return (
        item.selected_printers.length ===
        item.printers.length
    )
}




function selectAllProducts() {

    const allSelected = saleProductPrinter.value.every(
        item => isAllSelected(item)
    )

    saleProductPrinter.value.forEach(item => {

        if (!item.printers) {
            return
        }

        if (allSelected) {

            item.selected_printers = []

        } else {

            item.selected_printers = item.printers.map(
                printer => printer.printer
            )

        }

    })
}


// ----------------------------------------
// Send confirm
// ----------------------------------------
const isSending = ref(false);
async function sendToPrinter() {
    if(isSending.value){
        return;
    }
    isSending.value = true;
    const data = saleProductPrinter.value
    .filter(item =>
        item.selected_printers &&
        item.selected_printers.length > 0
    )
    .map(item => {
        const { selected_printers, ...rest } = item;
        return {
            ...rest,
            printer_ids: selected_printers.join(','),
            printers: selected_printers.join(','),
        };
    });

    const body = {
        "doc":sale.sale,
        "data": data,
        "print_server_url":printServerUrl,
    }

    try{ 
        const resp = await call.post("epos_restaurant_2023.api.mobile.v1.sale.submit_resend_to_printer", body);
        if (resp){
            showDialogSelectPrinter.value = false;
        }

    } finally{
        isSending.value = false;
    } 
}

// ----------------------------------------
// Check if any printer selected
// ----------------------------------------

const hasSelectedPrinter = computed(() => {

    return saleProductPrinter.value.some(
        item =>
            item.selected_printers &&
            item.selected_printers.length > 0
    )

});

const hasAllSelectedPrinter = computed(() => { 
    return saleProductPrinter.value.some(
        item =>
            item.selected_printers &&
            item.selected_printers.length ==  item.printers.length
    );
});



</script>


<style scoped>
/* ============================================================
   RESEND TO PRINTER DIALOG
   Vue 3 + Vuetify
   ============================================================ */


/* ------------------------------------------------------------
   Main Dialog Card
   ------------------------------------------------------------ */

.printer-dialog {
    width: 785px !important;
    max-width: calc(100vw - 30px) !important;
    padding: 20px 22px 18px !important;
    background: #e8eff1 !important;
    border-radius: 28px !important;
    box-shadow:
        0 20px 50px rgba(0, 0, 0, 0.25) !important;
    overflow: hidden;
}


/* ------------------------------------------------------------
   Vuetify Card default overrides
   ------------------------------------------------------------ */

.printer-dialog.v-card {
    color: #111 !important;
}

.printer-dialog .v-card-title {
    padding: 0 !important;
}

.printer-dialog .v-card-text {
    padding: 0 !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.dialog-header {
    width: 100%;

    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 18px;
}


/* Title wrapper */

.dialog-title-wrapper {
    display: flex;
    align-items: center;

    gap: 14px;
}


/* Printer icon */

.dialog-printer-icon {
    width: 40px;
    height: 40px;

    display: flex;
    align-items: center;
    justify-content: center;

    flex-shrink: 0;

    background: #a8f2f6;

    border-radius: 10px;

    font-size: 20px;

    line-height: 1;
}


/* Title */

.dialog-title {
    margin: 0;
    padding: 0;

    color: #111;

    font-size: 24px;
    font-weight: 500;

    line-height: 1.2;
}


/* Close */

.dialog-close {
    width: 32px;
    height: 32px;

    display: flex;
    align-items: center;
    justify-content: center;

    padding: 0;

    border: none;
    outline: none;

    background: transparent;

    color: #4b5659;

    font-size: 30px;
    font-weight: 300;

    line-height: 1;

    cursor: pointer;

    border-radius: 50%;

    transition:
        background-color 0.15s ease,
        color 0.15s ease;
}

.dialog-close:hover {
    background: rgba(0, 0, 0, 0.06);

    color: #111;
}

.dialog-close:active {
    background: rgba(0, 0, 0, 0.1);
}


/* ============================================================
   TOP SELECT ALL BOX
   ============================================================ */

.top-select-all {
    width: 100%;
    height: 50px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    box-sizing: border-box;

    padding: 0 13px;

    background: #f9fbfb;

    border: 1px solid #bdc9cc;

    border-radius: 9px;
}


/* Product count */

.product-count {
    display: flex;
    align-items: center;

    gap: 6px;

    color: #20282a;

    font-size: 14px;

    line-height: 1;
}

.product-count strong {
    font-weight: 700;
}


/* Small printer/count icon */

.count-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    color: #0095a1;

    font-size: 17px;
}


/* Top select all button */

.select-all-btn {
    display: flex;
    align-items: center;

    gap: 7px;

    margin: 0;
    padding: 0;

    border: none;
    outline: none;

    background: transparent;

    color: #0095a1;

    font-size: 14px;
    font-weight: 400;

    line-height: 1;

    cursor: pointer;

    transition: color 0.15s ease;
}

.select-all-btn:hover {
    color: #007780;
}

.select-all-btn:active {
    color: #005f66;
}


/* Double check */

.double-check {
    color: #0095a1;

    font-size: 14px;
    font-weight: 700;

    letter-spacing: -4px;

    margin-right: 3px;
}


/* ============================================================
   PRODUCTS WRAPPER
   ============================================================ */

.products-wrapper {
    width: 100%;

    display: flex;
    flex-wrap: wrap;

    align-items: flex-start;

    gap: 10px;

    margin-top: 10px;

    box-sizing: border-box;
}


/* ============================================================
   PRODUCT CARD
   ============================================================ */

.product-card {
    width: 355px;

    min-width: 355px;

    box-sizing: border-box;

    padding: 10px;

    background: #f1f6f7;

    border: 1px solid #b9c8cb;

    border-radius: 9px;

    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}

.product-card:hover {
    border-color: #aabcc0;
}


/* ============================================================
   PRODUCT HEADER
   ============================================================ */

.product-header {
    width: 100%;

    min-height: 48px;

    display: flex;
    align-items: flex-start;

    box-sizing: border-box;
}


/* Product printer icon */

.product-printer-icon {
    width: 30px;
    height: 30px;

    flex: 0 0 30px;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-right: 9px;

    background: #dce5e6;

    border-radius: 7px;

    font-size: 15px;

    line-height: 1;
}


/* ============================================================
   PRODUCT INFO
   ============================================================ */

.product-info {
    flex: 1 1 auto;

    min-width: 0;

    padding-top: 1px;
}


/* Product name */

.product-name {
    width: 100%;

    color: #15191a;

    font-size: 14px;
    font-weight: 700;

    line-height: 18px;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}


/* Product code */

.product-code {
    margin-top: 1px;

    color: #303839;

    font-size: 12px;
    font-weight: 400;

    line-height: 16px;
}


/* ============================================================
   QUANTITY / PRICE
   ============================================================ */

.product-price {
    flex: 0 0 auto;

    min-width: 70px;

    margin-left: 8px;

    padding-top: 0;

    color: #252b2d;

    font-size: 12px;
    font-weight: 400;

    line-height: 18px;

    text-align: right;

    white-space: nowrap;
}

.product-price strong {
    display: block;

    color: #15191a;

    font-size: 13px;
    font-weight: 700;

    line-height: 17px;
}


/* ============================================================
   PRODUCT SELECT ALL
   ============================================================ */

.select-all {
    display: flex;
    align-items: center;

    gap: 7px;

    width: fit-content;

    margin-top: 3px;
    margin-bottom: 9px;

    color: #0095a1;

    font-size: 14px;
    font-weight: 400;

    line-height: 18px;

    cursor: pointer;

    user-select: none;

    transition: color 0.15s ease;
}

.select-all:hover {
    color: #007780;
}


/* Check icon */

.check-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    min-width: 16px;

    color: #0095a1;

    font-size: 13px;
    font-weight: 700;

    line-height: 1;

    letter-spacing: -3px;
}


/* Selected check */

.check-icon.checked {
    color: #0095a1;
}


/* ============================================================
   PRINTER LIST
   ============================================================ */

.printer-list {
    width: 100%;

    display: flex;
    flex-wrap: wrap;
    align-items: center;

    gap: 7px;

    box-sizing: border-box;
}


/* ============================================================
   PRINTER BUTTON
   ============================================================ */

.printer-button {
    min-height: 35px;

    display: inline-flex;
    align-items: center;
    justify-content: center;

    box-sizing: border-box;

    padding: 0 14px;

    border: 1px solid #b6c5c8;

    border-radius: 8px;

    outline: none;

    background: #f8fbfb;

    color: #364144;

    font-family: inherit;

    font-size: 14px;
    font-weight: 400;

    line-height: 18px;

    cursor: pointer;

    user-select: none;

    transition:
        background-color 0.15s ease,
        border-color 0.15s ease,
        color 0.15s ease,
        box-shadow 0.15s ease;
}


/* Hover */

.printer-button:hover {
    background: #e7f4f5;

    border-color: #78bfc5;

    color: #2b5d61;
}


/* Active */

.printer-button:active {
    transform: translateY(1px);
}


/* Selected */

.printer-button.selected {
    background: #d7f5f6;

    border-color: #00a1aa;

    color: #007b83;

    font-weight: 500;
}


/* Selected hover */

.printer-button.selected:hover {
    background: #c8f0f2;

    border-color: #008f98;

    color: #006c73;
}


/* Printer check */

.printer-check {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    margin-right: 5px;

    color: #00858d;

    font-size: 12px;
    font-weight: 700;
}


/* ============================================================
   FOOTER
   ============================================================ */

.dialog-footer {
    width: 100%;

    display: flex;
    align-items: center;
    justify-content: flex-end;

    gap: 18px;

    margin-top: 12px;

    box-sizing: border-box;
}


/* ============================================================
   CANCEL BUTTON
   ============================================================ */

.cancel-button {
    height: 42px;

    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 0 2px;

    border: none;
    outline: none;

    background: transparent;

    color: #0095a1;

    font-family: inherit;

    font-size: 14px;
    font-weight: 400;

    cursor: pointer;

    transition: color 0.15s ease;
}

.cancel-button:hover {
    color: #007780;
}

.cancel-button:active {
    color: #005f66;
}


/* ============================================================
   SEND BUTTON
   ============================================================ */

.send-button {
    min-width: 100px;
    height: 42px;

    display: inline-flex;
    align-items: center;
    justify-content: center;

    gap: 8px;

    box-sizing: border-box;

    padding: 0 17px;

    border: none;
    outline: none;

    border-radius: 22px;

    background: #00a0aa;

    color: #fff;

    font-family: inherit;

    font-size: 14px;
    font-weight: 500;

    line-height: 1;

    cursor: pointer;

    box-shadow: none;

    transition:
        background-color 0.15s ease,
        opacity 0.15s ease;
}


/* Send hover */

.send-button:hover:not(:disabled) {
    background: #008d96;
}


/* Send active */

.send-button:active:not(:disabled) {
    background: #007b83;

    transform: translateY(1px);
}


/* Send disabled */

.send-button:disabled {
    background: #c9d1d3;

    color: #9aa4a6;

    cursor: not-allowed;

    opacity: 1;
}


/* Send icon */

.send-button > span {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    font-size: 16px;

    line-height: 1;
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 800px) {

    .printer-dialog {
        width: calc(100vw - 30px) !important;

        max-width: calc(100vw - 30px) !important;

        border-radius: 22px !important;

        padding: 18px !important;
    }

    .product-card {
        width: 100%;

        min-width: 0;
    }

}


@media (max-width: 500px) {

    .printer-dialog {
        width: calc(100vw - 20px) !important;

        max-width: calc(100vw - 20px) !important;

        padding: 15px !important;

        border-radius: 18px !important;
    }

    .dialog-title {
        font-size: 20px;
    }

    .dialog-printer-icon {
        width: 36px;
        height: 36px;

        font-size: 18px;
    }

    .top-select-all {
        padding: 0 10px;
    }

    .product-count {
        font-size: 13px;
    }

    .select-all-btn {
        font-size: 13px;
    }

    .dialog-footer {
        gap: 12px;
    }

    .send-button {
        min-width: 90px;
    }

}


/* ============================================================
   VUETIFY DIALOG OVERLAY
   ============================================================ */

/*
 * If you want the background to look like the screenshot,
 * you can increase the overlay opacity.
 */

:deep(.v-overlay__scrim) {
    background: #000 !important;

    opacity: 0.55 !important;
}


/* ============================================================
   VUETIFY DIALOG POSITION
   ============================================================ */

:deep(.v-dialog) {
    margin: 24px !important;
}


/* ============================================================
   REMOVE VUETIFY CARD ROUNDING / EXTRA STYLES
   ============================================================ */

:deep(.printer-dialog.v-card) {
    overflow: hidden !important;

    border-radius: 28px !important;
}


/* ============================================================
   SCROLLING FOR MANY PRODUCTS
   ============================================================ */

.products-wrapper {
    max-height: 400px;

    overflow-y: auto;

    scrollbar-width: thin;

    scrollbar-color: #b6c5c8 transparent;
}


/* Chrome / Edge scrollbar */

.products-wrapper::-webkit-scrollbar {
    width: 5px;
}

.products-wrapper::-webkit-scrollbar-track {
    background: transparent;
}

.products-wrapper::-webkit-scrollbar-thumb {
    background: #b6c5c8;

    border-radius: 10px;
}

.products-wrapper::-webkit-scrollbar-thumb:hover {
    background: #98aaae;
}

</style>