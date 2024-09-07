<template>
    <v-menu>
        <template v-slot:activator="{ props }">
            <v-chip v-bind="props" variant="elevated" color="primary" class="mx-1 grow text-center justify-center"
                size="small">{{ $t('More') }}</v-chip>
        </template>
        <v-list>

            <v-list-item prepend-icon="mdi-pencil" :title="$t('Edit')" v-if="canEdit"
                @click="onEditSaleProduct(saleProduct)"></v-list-item>

        

            <template v-if="gv.device_setting.is_order_station == 0">

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

            </template>

            <template v-if="!(saleProduct.is_require_employee || false) && !saleProduct.is_timer_product">
                <v-list-item v-if="tableLayout.table_groups && tableLayout.table_groups.length > 0"
                    prepend-icon="mdi-chair-school" :title="($t('Seat') + '#')"
                    @click="sale.onSaleProductSetSeatNumber(saleProduct)"></v-list-item>
            </template>

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

            <v-list-item v-if="productPrinter" prepend-icon="mdi-printer-outline" :title="$t('Re-Send')"
                @click="onSelectPrinter()">
            </v-list-item>

        </v-list>
    </v-menu>
    <v-dialog v-model="showDialogSelectPrinter" width="auto">
        <v-card :title="$t('Select Printers')">

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

<script setup>
import { defineProps, inject, keypadWithNoteDialog, i18n, ref, getApi } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
import { computed } from 'vue';
import { useDialog } from 'primevue/usedialog';
import ComEditSaleProduct from '@/views/sale/components/ComEditSaleProduct.vue'

const { t: $t } = i18n.global;

const product = inject('$product');
const sale = inject('$sale');
const numberFormat = inject('$numberFormat');
const gv = inject("$gv");
const tableLayout = inject("$tableLayout");
const dialog = useDialog()

const props = defineProps({
    saleProduct: Object
});

const showDialogSelectPrinter = ref(false);
const printerList = ref([]);

const toaster = createToaster({ position: "top-right" });
function onRemoveNote() {
    props.saleProduct.note = "";
}

const productPrinter = computed(() => {
    if ((gv.device_setting.show_button_resend || 0) == 1) {
        if (sale.sale.sale_status != 'Submitted' || sale.sale.sale_products.find(r => r.sale_product_status != 'Submitted')) {
            return false;
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

})
const canEditVariant = computed(() => {

    if (props.saleProduct.is_timer_product) {
        return false
    }

    if (props.saleProduct.sale_product_status == "New" && props.saleProduct.is_variant) {
        return true
    }

    return false

})

function onReturn(sp) {
    sp.is_return = !sp.is_return
    sale.updateQuantity(sp, sp.quantity * -1)

}

function onSelectPrinter() {
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

function onConfirmSelectPrinter() {
    if (!sale.isBillRequested()) {
        var printers = printerList.value.filter(r => r.selected == true);
        // props.saleProduct.printers = JSON.stringify(printers );
        showDialogSelectPrinter.value = false;

        var r = props.saleProduct;
        //resend product to kot
        var resendProductData = []
        printers.forEach((p) => {
            resendProductData.push({
                sale_product_name: r.name,
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
                is_deleted: false,
                is_free: r.is_free == 1,
                combo_menu: r.combo_menu,
                combo_menu_data: r.combo_menu_data,
                order_by: r.order_by,
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
            })
        });

        if (resendProductData.length > 0) {
            sale.onPrintToKitchen(sale.sale, resendProductData)
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

sale.vue.$onKeyStroke('F8', (e) => {
    e.preventDefault()
    if (sale.dialogActiveState == false && props.saleProduct.selected == true) {
        sale.onSaleProductNote(props.saleProduct)
    }
})

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



</script>