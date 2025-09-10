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
const call = frappe.call();

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
            targetSale.custom_bill_number = undefined;
            targetSale.deposit = 0;
            onMoveItem(mt.table, sale.sale, targetSale)
        } else {
            var targetSale = db.getDoc('Sale', mt.sale.new_sale).then((doc) => {
                onMoveItem(mt.table, sale.sale, doc)
            })
        }
    }
}

async function onMoveItem(table, sourceSale, targetSale) {
    sale.move_item = true
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

    generateProductPrinterMoveItem(targetSale, sourceSale.name, sourceSale.tbl_number);
    targetSale.sale_products?.forEach((r) => {
        r.total_selected = 0
        r.move_from_sale = sourceSale.name
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
        if((targetSale.moveItemSaleProducts || []).length > 0){
            sale.onPrintToKitchen(targetSale, targetSale.moveItemSaleProducts, true);
        }
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
        if((targetSale.moveItemSaleProducts || []).length > 0){
            sale.onPrintToKitchen(targetSale, targetSale.moveItemSaleProducts, true);
        }
    }
}

function generateProductPrinterMoveItem(targetSale, old_sale, old_table) {
    targetSale.moveItemSaleProducts = [];
    if (sale.setting.pos_setting.print_sale_product_change_table) {
        targetSale.sale_products?.forEach(async (r) => {

             if(sale.setting.pos_setting.combo_menu_print_captain_by_items_printer && r.is_combo_menu){
                                const combo_data = JSON.parse(r.combo_menu_data)
                let productCodes = combo_data.map(i => i.product_code);
                const res = await call.post("epos_restaurant_2023.api.api.get_product_printer_by_products", {
                     "product_codes":productCodes
                });    
                const printers = JSON.parse(r.printers); 
                const combo_product_printers = res["message"]            
                for(const pro of combo_data ){
                    const p_printers = combo_product_printers.filter(r=>r.product_code == pro.product_code)
                    for(const p of p_printers){ 
                        ///check combo item is exist printer match
                        const match_printers =  printers.filter(r=> r.printer == p.printer_name)                        
                        if( match_printers.length > 0){

                            if((r.total_selected || 0) > 0){
                                targetSale.moveItemSaleProducts.push({
                                    move_from_table: old_table,
                                    move_from_sale: old_sale,
                                    printer: p.printer_name,
                                    group_item_type: p.group_item_type,
                                    is_label_printer: p.is_label_printer == 1,
                                    ip_address: p.ip_address,
                                    port: p.port,
                                    usb_printing: p.usb_printing,
                                    product_code: pro.product_code,
                                    product_name_en: pro.product_name,
                                    product_name_kh: pro.product_name_kh,
                                    kitchen_group:pro.kitchen_group||"",
                                    kitchen_group_sort_order: pro.kitchen_group_sort_order || 0,
                                    seat_number: r.seat_number||"",
                                    portion: r.portion,
                                    unit: r.unit,
                                    modifiers: r.modifiers,
                                    note: r.note,
                                    quantity: r.quantity * (pro.quantity ||1) ,
                                    is_deleted: false,
                                    is_free: r.is_free == 1,
                                    combo_menu: r.product_name,
                                    combo_menu_data: null,
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
                            }
                            

                        }
                    }
                }

             }else{ 
                const pritners = JSON.parse(r.printers);
                pritners.forEach((p) => {
                    if((r.total_selected || 0) > 0){
                        targetSale.moveItemSaleProducts.push({
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
                    }
                });
            
            }
        });
    }
}
</script>