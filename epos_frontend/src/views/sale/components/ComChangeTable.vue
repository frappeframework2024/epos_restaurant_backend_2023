<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose" :hideOkButton="true" :hideCloseButton="true">
        <template #title>
            <div class="flex justify-between align-center">
                <div>
                    {{ `${(params._is_reservation || false) ? $t('Assign Table') : $t('Change or Merge Table')}`
                    }}
                    <br /><span style="font-size:14px;">{{ params.pos_profile }}</span>
                </div>
                <div v-if="gv.device_setting.allow_switch_pos_profile == 1">
                    <v-select @update:modelValue="switchPOSProfil" prepend-inner-icon="mdi-desktop-classic"
                        density="compact" item-title="name" v-model="_pos_profile" :items="switch_pos_station"
                        item-value="name" hide-no-data hide-details variant="solo" class="mx-1"></v-select>
                </div>
            </div>

        </template>
        <template #content>
            <ComLoadingDialog v-if="loading" />
            <v-tabs align-tabs="center" v-if="tableGroups && tableGroups.length > 1" v-model="tableLayout.tab">
                <v-tab v-for="g in tableGroups" :key="g.key" :value="g.key">
                    {{ g.table_group }}
                </v-tab>
            </v-tabs>
            <template v-if="tableLayout.tempTableGroups">
                <v-window v-model="tableLayout.tab">
                    <template v-for="g in tableLayout.tempTableGroups">
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
        </template>

    </ComModal>
    <!-- <v-dialog :scrollable="false" :loading="loading" v-model="open" :fullscreen="mobile"
        :style="mobile ? '' : 'width: 100%;max-width:800px'">
        <v-card>
            

            
        </v-card>
    </v-dialog> -->
</template>

<script setup>
import { confirm, ref, useRoute, useRouter, defineEmits, inject, changeTableSelectSaleOrderDialog, i18n, onMounted } from '@/plugin'
import ComToolbar from '@/components/ComToolbar.vue';
import { createToaster } from '@meforma/vue-toaster';
import ComInput from '../../../components/form/ComInput.vue';
import ComLoadingDialog from '@/components/ComLoadingDialog.vue';
import { useDisplay } from 'vuetify';
import { computed } from 'vue';
const route = useRoute();
const router = useRouter();

const { t: $t } = i18n.global;
const frappe = inject('$frappe');

const call = frappe.call();

const gv = inject('$gv')

const { mobile } = useDisplay()
const socket = inject("$socket")
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

const emit = defineEmits(["resolve", "reject"])

let open = ref(true);


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
        const screens = sale.getScreenNames(sale.sale.sale_products)
        if (t.sales?.length == 0) {

            generateProductPrinterChangeTable(sale.sale.sale_products, sale.sale.name, sale.sale.tbl_number);
           
           
            sale.sale.sale_products?.forEach((r) => {
                r.move_from_table = sale.sale.tbl_number;
            });
            sale.sale.table_id = t.id;
            const old_table_number = sale.sale.tbl_number 
            sale.sale.tbl_number = t.tbl_no;
            

            if (_pos_profile.value == sale.sale.pos_profile) {
                toaster.success($t('msg.Change to table') + ": " + t.tbl_no);
                emit("resolve", true)
                // add queue message to kod
                if (sale.sale.name){
                    addKODQueueMessage(screens, old_table_number, t.tbl_no)
                }
                
            } else {
                await changeTableBetweenOutlet(t).then(r => {
                    if (sale.sale.name){
                        addKODQueueMessage(screens, old_table_number, t.tbl_no)
                    }
                    emit("resolve", true)
                }).catch((error) => {
                    return
                });
            }
        }
        else {
            const result = await changeTableSelectSaleOrderDialog({ data: t });
            if (result) {
                if (result.action == "create_new_bill") {

                    generateProductPrinterChangeTable(sale.sale.sale_products, sale.sale.name, sale.sale.tbl_number);

                    sale.sale.sale_products?.forEach((r) => {
                        r.move_from_table = sale.sale.tbl_number;
                    });
                    sale.sale.table_id = t.id;
                    const old_table_number = sale.sale.tbl_number
                    sale.sale.tbl_number = t.tbl_no;
                    if (sale.sale.pos_profile == _pos_profile.value) {
                        toaster.success($t('msg.Change to table') + ": " + t.tbl_no);
                        emit("resolve", true);
                        // add queue message to kod
                        if (sale.sale.name){
                          
                            addKODQueueMessage(screens, old_table_number, t.tbl_no)
                        }
                        
                    } else {
                        await changeTableBetweenOutlet(t).then(r => {
                            emit("resolve", true)
                            if (sale.sale.name){
                                addKODQueueMessage(screens, old_table_number, t.tbl_no)
                            }
                        }).catch((error) => {
                            return
                        });
                    }


                } else if (result.action == "reload_sale") {
                    // send message to kod
                    screens.forEach(s => {
                         socket.emit("SubmitKOD",
                         {
                                screen_name: s,
                                message: $t("Order from table") + " " + sale.sale.tbl_number + " " + $t("merge to table") + " " + t.tbl_no
                            }
                        )
                    })

                    if (sale.sale.pos_profile == _pos_profile) {
                        emit("resolve", result)

                    } else {
                        emit("resolve", true)
                        router.push({ name: 'TableLayout' })

                    }


                }
            }
        }
    }
}

function addKODQueueMessage(screens, old_table, new_table) {
    // when change table we not update to db yet, 
    // so this message is alert to kod screen when user submit order
    // or payment
    screens.forEach(s => {
        sale.kod_messages = sale.kod_messages.filter(r=>r.key!="change_table_message")
        sale.kod_messages.push(
            {
                key:"change_table_message",
                screen_name: s,
                message: $t("Change table from") + " " + old_table + " " + $t("to") + " " + new_table
            }
        )
    })


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

tableLayout.getSaleList();
onMounted(() => {

    tableLayout.getTempTableGroup();
    _pos_profile.value = props.params.pos_profile
    setTimeout(() => {
        tableLayout.tab = tableLayout.table_groups[0].key;
    }, 100);


    loading.value = true
    call
        .get("epos_restaurant_2023.api.api.get_pos_profiles")
        .then((result) => {

            switch_pos_station.value = result.message
            loading.value = false
        })
        .catch((error) => {
            loading.value = false
        });
})


const tableGroups = computed(() => {
    return tableLayout.tempTableGroups;
})


function switchPOSProfil(data) {

    let pos_profile = localStorage.getItem("pos_profile")
    if (pos_profile == data) {


        tableLayout.getTempTableGroup();
        tableLayout.getSaleList();
        setTimeout(() => {
            tableLayout.tab = tableLayout.table_groups[0].key
        }, 100);

    } else {
        loading.value = true
        call.post('epos_restaurant_2023.api.api.get_tables_groups_other_pos_profile', { "pos_profile": data })
            .then((res) => {

                loading.value = false
                if (res.message == undefined) {
                    _pos_profile.value = pos_profile;
                    toaster.warning(`${data} shift didn't opened`);
                } else {

                    tableLayout.getTempTableGroup(res.message.table_groups, data);
                    tableLayout.getSaleList(data);

                    setTimeout(() => {
                        tableLayout.tab = res.message.table_groups[0].key;
                    }, 100);
                }
            })
    }

}

async function changeTableBetweenOutlet(t) {
    if (await confirm({ title: $t("Change Table"), text: $t("msg.Are your sure you to change this order to table number " + t.tbl_no) })) {
        return new Promise((resolve, reject) => {
            loading.value = true
            call.post("epos_restaurant_2023.api.api.change_table_between_outlet", {
                sale: sale.sale.name,
                new_pos_profile: _pos_profile.value,
                new_table_id: t.id
            }).then((result) => {
                router.push({ name: 'TableLayout' })
                toaster.success($t('msg.Change to table') + ": " + t.tbl_no);
                loading.value = false
                // send message  to event listener to  close all modal that open  
                window.postMessage("close_modal", "*")
                tableLayout.tab = localStorage.getItem("__tblLayoutIndex")

                //TODO Send change table information to product printer 
                resolve(result)

            }).catch(error => {
                loading.value = false
                gv.showServerMessage(error)
                reject(error)

            })
        });



    } else {
        reject(false)
    }
}


</script>