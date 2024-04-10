<template>
    <v-dialog :scrollable="false" :loading="loading" v-model="open" :fullscreen="mobile"
        :style="mobile ? '' : 'width: 100%;max-width:800px'">
        <v-card>
            <ComToolbar @onClose="onClose">
                <template #title>
                    <div class="flex justify-between align-center">
                        <div>
                            {{ `${(params._is_reservation || false) ? $t('Assign Table') : $t('Change or Merge Table')}` }}
                            <br /><span style="font-size:14px;">{{ params.pos_profile }}</span>
                        </div>
                        <div v-if="gv.device_setting.allow_switch_pos_profile == 1">
                            <v-select @update:modelValue="switchPOSProfil" prepend-inner-icon="mdi-desktop-classic"
                                density="compact" item-title="name" v-model="_pos_profile" :items="switch_pos_station"
                                item-value="name" hide-no-data hide-details variant="solo" class="mx-1"></v-select>
                        </div>
                    </div>
                </template>
            </ComToolbar>
            <div class="overflow-auto p-3 h-full">
                <v-tabs align-tabs="center" v-if="tableLayout.table_groups && tableLayout.table_groups.length > 1"
                    v-model="tableLayout.tab">
                    <v-tab v-for="g in tableLayout.table_groups" :key="g.key" :value="g.key">
                        {{ g.table_group }}
                    </v-tab>
                </v-tabs>
                <template v-if="tableLayout.table_groups">
                    <v-window v-model="tableLayout.tab">
                        <template v-for="g in tableLayout.table_groups">
                            <v-window-item :value="g.key">
                                <div class="pa-4">
                                    <ComInput v-model="g.search_table_keyword" autofocus ref="searchTextField" keyboard
                                        class="my-2 mb-4" :placeholder="$t('Search')" />
                                    <div
                                        class="grid gap-4 grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-5 xl:grid-cols-5 2xl:grid-cols-6">
                                        <template v-for="(t, index) in getTable(g.tables, g.search_table_keyword)"
                                            :key="index">
                                            <template v-if="(params._is_reservation || false)">
                                                <v-btn color="rgb(79, 157, 217)" @click="onSelectTable(t)" width="100%"
                                                    height="100">
                                                    <span class="text-white"> {{ t.tbl_no }} </span>

                                                </v-btn>
                                            </template>
                                            <template v-else>
                                                <v-badge :content="t.sales?.length" color="error"
                                                    v-if="t.sales?.length > 0">
                                                    <v-btn :color="t.background_color" @click="onSelectTable(t)"
                                                        width="100%" height="100">
                                                        {{ t.tbl_no }}
                                                    </v-btn>
                                                </v-badge>
                                                <v-btn v-else :color="t.background_color" @click="onSelectTable(t)"
                                                    width="100%" height="100">
                                                    {{ t.tbl_no }}
                                                </v-btn>
                                            </template>
                                        </template>
                                    </div>
                                </div>
                            </v-window-item>
                        </template>
                    </v-window>
                </template>
            </div>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, defineEmits, inject, changeTableSelectSaleOrderDialog, i18n, onMounted, } from '@/plugin'
import ComToolbar from '@/components/ComToolbar.vue';
import { createToaster } from '@meforma/vue-toaster';
import ComInput from '../../../components/form/ComInput.vue';
import { useDisplay } from 'vuetify';
const { t: $t } = i18n.global;
const frappe = inject('$frappe');
const db = frappe.db();

const call = frappe.call();

const gv = inject('$gv')

const { mobile } = useDisplay()

const switch_pos_station = ref([])

const tableLayout = inject("$tableLayout");
const sale = inject("$sale");
const toaster = createToaster({ position: "top-right" })

const _pos_profile = ref('')

const loading = ref(false)

const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

const tableTab = ref([])


const emit = defineEmits(["resolve", "reject"])

let open = ref(true);
tableLayout.getSaleList();


function onClose() {
    emit("resolve", false)
}

function getTable(tables, keyword) {
    if ((props.params?._is_reservation || false)) {
        tables = tables.filter((r) => {
            return (r.sales?.length || 0) == 0
        });
    }

    if (keyword == "") {
        return tables;
    } else {
        return tables.filter((r) => {
            return String(r.tbl_no).toLocaleLowerCase().includes(keyword.toLocaleLowerCase());
        });
    }
}



async function onSelectTable(t) {
    if ((props.params?._is_reservation || false)) {
        emit("resolve", t);
    }
    else {
        if (t.sales?.length == 0) {
            generateProductPrinterChangeTable(sale.sale.sale_products, sale.sale.name, sale.sale.tbl_number);
            sale.sale.sale_products?.forEach((r) => {
                r.move_from_table = sale.sale.tbl_number;
            });
            sale.sale.table_id = t.id;
            sale.sale.tbl_number = t.tbl_no;
            toaster.success($t('msg.Change to table') + ": " + t.tbl_no);
            emit("resolve", true)
        }
        else {
            const result = await changeTableSelectSaleOrderDialog({ data: t });
            if (result) {
                if (result.action == "create_new_bill") {
                    //
                    generateProductPrinterChangeTable(sale.sale.sale_products, sale.sale.name, sale.sale.tbl_number);

                    sale.sale.sale_products?.forEach((r) => {
                        r.move_from_table = sale.sale.tbl_number;
                    });
                    sale.sale.table_id = t.id;
                    sale.sale.tbl_number = t.tbl_no;
                    toaster.success($t('msg.Change to table') + ": " + t.tbl_no);
                    emit("resolve", true);

                } else if (result.action == "reload_sale") {
                    emit("resolve", result)
                }
            }
        }
    }
}


function generateProductPrinterChangeTable(sale_products, old_sale, old_table) {
    if (sale.setting.pos_setting.print_sale_product_change_table) {
        sale_products?.forEach((r) => {
            const pritners = JSON.parse(r.printers);
            pritners.forEach((p) => {
                sale.changeTableSaleProducts.push({
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

onMounted(() => {
    _pos_profile.value = props.params.pos_profile
    loading.value = true
    call
        .get("epos_restaurant_2023.api.api.get_pos_profile", {})
        .then((result) => {
            switch_pos_station.value = result.message.filter((r) => r.is_edoor_profile != 1)
            loading.value = false
        })
        .catch((error) => {
            loading.value = false
        });
})

function switchPOSProfil(data) {

}

</script>