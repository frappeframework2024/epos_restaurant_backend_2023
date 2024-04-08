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
import { MoveItemChangeTable, inject } from '@/plugin'
import ComMoveItemSaleProductList from '@/views/sale/components/ComMoveItemSaleProductList.vue'
const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

var sale = inject("$sale")
var frappe = inject("$frappe")

const db = frappe.db();

const emit = defineEmits(["resolve"]);
function onClose() {
    emit("resolve", false);
}
async function onOk() {

    MoveItemChangeTable();

    return
    // console.log(sale.sale.sale_products.fi)
    var targetSale = JSON.parse(JSON.stringify(sale.sale));
    targetSale.name = null;
    targetSale.sale_products = [];
    targetSale.table_id = "2e6c33af99";
    targetSale.tbl_number = "B1";
    targetSale.tbl_group = "Main Group";
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
    sale.sale.sale_products = sale.moveItemSaleProduct.filter((r) => r.quantity > 0);
    sale.sale.sale_products.forEach((sp) => {
        sale.updateQuantity(sp, sp.quantity)
    })



    //save target
    db.createDoc('Sale', targetSale)
        .then((t) => {
            console.log(t)
            db.updateDoc('Sale', sale.sale.name, sale.sale)
                .then((s) => console.log(s))

        })








    // changeTableDialog({});
    // emit("resolve", false);
}
</script>