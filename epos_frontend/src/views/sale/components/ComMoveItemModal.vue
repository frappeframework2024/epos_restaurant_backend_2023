<template>
    <ComModal @onClose="onClose" @onOk="onOk" titleOKButton="Move to" :loading="loading" :fullscreen="false">
        <template #title>
            {{ props.params.title }}
        </template>
        <template #content>
            <ComMoveItemSaleProductList />
        </template>
    </ComModal>
</template>
<script setup>
import { MoveItemChangeTable, inject, i18n } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
import ComMoveItemSaleProductList from '@/views/sale/components/ComMoveItemSaleProductList.vue'
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

const toaster = createToaster({ position: "top-right" })
const { t: $t } = i18n.global;

var sale = inject("$sale")
var frappe = inject("$frappe")

const db = frappe.db();

const emit = defineEmits(["resolve"]);
function onClose() {
    emit("resolve", false);
}
async function onOk() {
    const mt = await MoveItemChangeTable({});
    if (mt) {
        if (mt.con == 'new_bill') {
            var targetSale = JSON.parse(JSON.stringify(sale.sale));
            targetSale.name = null;
            targetSale.sale_products = [];
            onMoveItem(mt.table, sale.sale, targetSale)
        } else {
            var targetSale = db.getDoc('Sale', mt.sale.new_sale).then((doc) => {
                onMoveItem(mt.table, sale.sale, doc)
            })
        }
    }
}

async function onMoveItem(table, sourceSale, targetSale) {
    targetSale.table_id = table.id;
    targetSale.tbl_number = table.tbl_no;
    targetSale.tbl_group = table.tbl_group;
    //get pick item from source sale prodcut
    var saleProducts = sale.moveItemSaleProduct.filter((r) => (r.total_selected || 0) > 0);
    saleProducts.forEach(sp => {
        var _sp = JSON.parse(JSON.stringify(sp))
        _sp.parent = targetSale.name;
        if (sp.quantity == (sp.total_selected || 0)) {
            sp.quantity = 0;
            targetSale.sale_products.push(_sp);
        } else {

            sp.quantity -= (sp.total_selected || 0);
            _sp.name = null;
            _sp.quantity = (sp.total_selected || 0);
            targetSale.sale_products.push(_sp);
        }
    });
    sourceSale.sale_products = sale.moveItemSaleProduct.filter((r) => r.quantity > 0);
    sourceSale.sale_products.forEach((sp) => {
        sp.total_selected = 0
        sale.updateQuantity(sp, sp.quantity)
    })

    generateProductPrinterMoveItem(targetSale.sale_products, sourceSale.name, sourceSale.tbl_number);
    targetSale.sale_products?.forEach((r) => {
        r.total_selected = 0
        r.move_from_table = sourceSale.tbl_number;
    });

    //save target
    if ((targetSale.name || '') != '') {
        db.updateDoc('Sale', targetSale.name, targetSale)
            .then((t) => {
                db.updateDoc('Sale', sourceSale.name, sourceSale)
                    .then(async (s) => {
                        emit("resolve", true);
                        await sale.LoadSaleData(sourceSale.name);
                        toaster.success($t('The items were moved to') + ": " + table.tbl_no);

                    })
            }).catch((r) => {
                toaster.error($t('The items have problem with moving'));
            })
    } else {
        db.createDoc('Sale', targetSale)
            .then((t) => {
                db.updateDoc('Sale', sourceSale.name, sourceSale)
                    .then(async (s) => {
                        emit("resolve", true);
                        await sale.LoadSaleData(sourceSale.name);
                        toaster.success($t('The items were moved to') + ": " + table.tbl_no);

                    })
            }).catch((r) => {
                toaster.error($t('The items have problem with moving'));
            })
    }
}

function generateProductPrinterMoveItem(sale_products, old_sale, old_table) {
    if (sale.setting.pos_setting.print_sale_product_change_table) {
        sale_products?.forEach((r) => {
            const pritners = JSON.parse(r.printers);
            pritners.forEach((p) => {
                sale.moveItemSaleProducts.push({
                    move_from_table: old_table,
                    move_from_sale: old_sale,
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
                    time_out: r.time_out
                });
            });
        });

    }
}
</script>