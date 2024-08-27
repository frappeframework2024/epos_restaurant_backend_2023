<template>
    <div class="border border-gray-600 rounded-md guest-pro-scne" :class="padding ? padding : 'p-1'">
        <div class="flex">
            <div class="flex-auto cursor-pointer" @click="onSearchCustomer">
                <div class="flex items-center">
                    <v-avatar v-if="sale.sale.customer_photo">
                        <v-img :src="sale.sale.customer_photo"></v-img>
                    </v-avatar>
                    <template v-if="sale.sale.customer_name != undefined">
                        <avatar v-if="sale.sale.customer_photo == undefined" :name="sale.sale.customer_name"
                            class="mr-4" size="40"></avatar>
                    </template>
                    <div class="px-2">
                        <div class="font-bold">{{ sale.sale.customer_name || "" }} </div>

                        <div class="text-gray-400 text-sm">{{ subTitle || "" }}</div>

                        <div class="text-gray-400 text-sm" v-if="sale.sale.arrival">
                            {{ $t("Stay") }}: {{ moment(sale.sale.arrival).format("DD-MM-YYYY") }} {{ $t("to") }} {{
                                moment(sale.sale.departure).format("DD-MM-YYYY") }}
                        </div>

                        <div class="text-gray-400 text-sm" v-if="sale.sale.room_number">
                            {{ $t("Room") }}: {{ sale.sale.room_number }}
                        </div>

                    </div>
                    <div>




                    </div>

                </div>
            </div>
            <div class="flex-none" v-if="sale.sale.customer != setting.customer">
                <v-btn size="small" variant="text" color="primary" icon="mdi-account-plus"
                    @click="onAddCustomer()"></v-btn>
                <v-btn size="small" variant="text" color="primary" icon="mdi-account-edit"
                    @click="onViewCustomerDetail()"></v-btn>
                <v-btn size="small" variant="text" color="error" icon="mdi-delete" @click="onRemove()"></v-btn>

            </div>
            <div class="flex-none" v-else>
                <v-btn size="small" variant="text" color="primary" icon="mdi-magnify"
                    @click="onSearchCustomer()"></v-btn>
                <v-btn size="small" variant="text" color="primary" icon="mdi-account-plus"
                    @click="onAddCustomer()"></v-btn>
                <v-btn size="small" variant="text" color="primary" icon="mdi-qrcode-scan"
                    @click="onScanCustomerCode()"></v-btn>
            </div>

        </div>
        <div>

            <template v-if="customerPromotion?.length > 0">
                <ComChip v-for="(item, index) in customerPromotion" :key="index" color="orange"
                    :tooltip="$t('Happy Hour Promotion')" prepend-icon="mdi-tag-multiple">{{
                        item.promotion_name }}</ComChip>
            </template>
            {{ _customer }}
            <template v-if="customer">
                <ComChip :tooltip="$t('Default Discount')"
                    v-if="customerPromotion?.length <= 0 && customer.default_discount > 0" color="error">{{
                        customer.default_discount }}
                    % OFF</ComChip>

                <ComChip v-if="customer.total_point_earn > 0" :tooltip="$t('Current Point(s)')" color="success">{{
                    Number(customer.total_point_earn).toFixed(2) }}</ComChip>
                <ComChip v-if="customer.total_crypto_balance > 0" :tooltip="$t('Crypto Amount')" color="primary">
                    <CurrencyFormat :value="parseFloat(customer.total_crypto_balance)" />
                </ComChip>
            </template>
            <span v-if="sale.sale.pos_note">
                <v-btn variant="text" size="small" @click="show = !show" icon v-bind="props">
                    <v-tooltip  v-model="show" max-width="200px" :opacity="1" location="top">
                    {{ sale.sale.pos_note }}
                    <template v-slot:activator="{ props }">
                        <span variant="text" icon v-bind="props">
                            <v-icon color="red-darken-1" icon="mdi-alert"></v-icon>
                        </span>
                    </template>
                </v-tooltip>
                </v-btn>
                
            </span>
        </div>

    </div>
</template>

<script setup>
import { computed, inject, ref, getCurrentInstance, searchCustomerDialog, createResource, customerDetailDialog, scanCustomerCodeDialog, confirmDialog, onMounted, createToaster, addCustomerDialog } from "@/plugin"
import { whenever, useMagicKeys } from '@vueuse/core';
import { i18n } from "@/plugin";

const props = defineProps({
    padding: String
})



const { t: $t } = i18n.global;

const sale = inject("$sale");
const gv = inject("$gv");
const socket = inject("$socket");
const moment = inject("$moment");
const frappe = inject("$frappe");
const toaster = createToaster({ position: "top-right" });
const db = frappe.db();

const customer = ref(null)
const show = ref([])
sale.vueInstance = getCurrentInstance();
sale.vue = sale.vueInstance.appContext.config.globalProperties
let customerPromotion = computed({
    get() {
        return gv.getPromotionByCustomerGroup(sale.sale.customer_group)
    },
    set(newValue) {
        return newValue
    }
})
const current_customer_point = ref(0)
const { ctrl_m } = useMagicKeys({
    passive: false,
    onEventFired(e) {
        if (e.ctrlKey && e.key === 'm' && e.type === 'keydown')
            e.preventDefault()
    },
})
whenever(ctrl_m, () => onScanCustomerCode())

const _customer = computed(() => {
    if (sale.sale.customer) {
        db.getDoc("Customer", sale.sale.customer).then((r) => {
            customer.value = r;
        })
    }
})


sale.vue.$onKeyStroke('F9', (e) => {
    e.preventDefault()
    if (sale.dialogActiveState == false) {
        onSearchCustomer();
    }
})

async function onSearchCustomer() {
    if (!sale.isBillRequested()) {
        sale.dialogActiveState = true
        const result = await searchCustomerDialog({});
        sale.dialogActiveState = false
        if (result) {
            assignCustomerToOrder(result);
        }
    }
}

function assignCustomerToOrder(result, is_membership = false) {
    sale.sale.card = "";
    sale.sale.customer = result.name || "";
    sale.sale.pos_note = result.pos_note;
    sale.sale.customer_name = result.customer_name_en;
    sale.sale.customer_photo = result.photo;
    sale.sale.phone_number = result.phone_number;
    sale.sale.customer_group = result.customer_group;
    sale.sale.customer_default_discount = 0;
    sale.sale.exely_guest_id = result.guest_id || ""
    sale.sale.exely_room_stay_id = result.stay_room_id || ""
    sale.sale.arrival = result.arrival || ""
    sale.sale.departure = result.departure || ""
    sale.sale.room_number = result.room_number || ""
    if (result.total_point_earn > 0 && result.allow_earn_point == 1) {
        current_customer_point.value = result.total_point_earn
    } else {
        current_customer_point.value = 0
    }

    if (!is_membership) {
        sale.sale.customer_default_discount = result.default_discount;

        if (sale.promotion) {
            customerPromotion.value = gv.getPromotionByCustomerGroup(sale.sale.customer_group)
            //sale.promotion.customer_groups.filter(r=>r.customer_group_name_en == result.customer_group).length > 0
            if (customerPromotion.value && customerPromotion.value.length > 0) {
                customerPromotion.value.forEach((r) => {
                    toaster.info(`${$t('msg.This customer has happy hour promotion')} ${r.promotion_name} : ${((r.percentage_discount || 0))}%`);
                })
                updateProductAfterSelectCustomer(customerPromotion.value)
            }
            else {
                onClearPromotionProduct()
            }

        }
        if (parseFloat(result.default_discount) && (customerPromotion.value || []).length <= 0) {
            sale.sale.discount_type = "Percent";
            sale.sale.discount = parseFloat(result.default_discount);
            toaster.info($t('msg.This customer has default discount') + " " + sale.sale.discount + '%');
        }

    } else {
        if ((result.card?.card_code ?? "") != "") {
            sale.sale.card = result.card.card_code;
            sale.sale.discount_type = result.card.discount_type;
            sale.sale.discount = parseFloat(result.card.discount);
            toaster.info($t('msg.This customer has default discount') + " " + (sale.sale.discount || 0) + '%');
        } else {
            toaster.success(`${result.name}-${result.customer_name_en} ${$t("was assigned to sale")}`);
        }
    }

    sale.updateSaleSummary();

    socket.emit("ShowOrderInCustomerDisplay", sale.sale);
}

const setting = computed(() => {
    return JSON.parse(localStorage.getItem('setting'))
})
const subTitle = computed(() => {
    let title = sale.sale.customer || "";

    if ((sale.sale.card || "") != "") {
        title = title + "(" + sale.sale.card + ")";
    }
    if (sale.sale.phone_number != "" && sale.sale.phone_number != undefined) {
        if (title) {
            title = title + " / " + sale.sale.phone_number
        } else {
            title = sale.sale.phone_number
        }

    }



    return title;
})

function onViewCustomerDetail() {
    customerDetailDialog({
        name: sale.sale.customer
    });
}
function updateProductAfterSelectCustomer(pro) {
    const promotions = JSON.parse(JSON.stringify(pro))
    if (sale.sale.sale_products.length > 0) {
        let product_checks = []
        sale.sale.sale_products.forEach((r) => {
            product_checks.push({
                product_code: r.product_code,
                order_time: r.order_time
            })
        })
        createResource({
            url: 'epos_restaurant_2023.api.promotion.get_promotion_products',
            auto: true,
            params: {
                products: product_checks,
                promotions: promotions
            },
            onSuccess(doc) {
                if (doc) {
                    onClearPromotionProduct()
                    /// update products promotion
                    doc.product_promotions.forEach(r => {
                        let sale_products = sale.sale.sale_products.filter(x => x.product_code == r.product_code)
                        sale_products.forEach((s) => {
                            if (moment(s.order_time).format('HH:mm:ss') == r.order_time && s.is_free == false) {
                                s.discount_type = 'Percent'
                                s.discount = r.percentage_discount
                                s.happy_hours_promotion_title = r.promotion_title
                                s.happy_hour_promotion = r.promotion_name
                            }
                            sale.updateSaleProduct(s)
                        })
                    })

                    // remove expire promotion
                    if (doc.expire_promotion.length > 0) {
                        doc.expire_promotion.forEach((p) => {
                            toaster.warning(`${p.promotion_name} ${$t('msg.was expired')}`)
                            const index = gv.promotion.findIndex(r => r.name == p.name)
                            if (index > -1) {
                                gv.promotion.splice(index, 1);
                                sale.promotion.splice(index, 1);
                            }
                        })

                    }
                } else {
                    gv.promotion = null
                    sale.promotion = null
                }
                sale.updateSaleSummary();
            }
        });
    }
}
async function onScanCustomerCode() {
    if (!sale.isBillRequested()) {
        const result = await scanCustomerCodeDialog({});
        if (result) {
            assignCustomerToOrder(result, true);
        }
    }
}

async function onRemove() {
    if (!sale.isBillRequested()) {
        if (sale.sale.discount > 0) {
            if (await confirmDialog({ title: $t('Remove Discount'), text: $t('msg.are you sure to remove discount from bill') })) {
                sale.sale.discount = 0;
                sale.updateSaleSummary();
            }
        }
        sale.sale.card = "";
        sale.sale.customer = setting.value.customer
        sale.sale.customer_name = setting.value.customer_name
        sale.sale.customer_photo = setting.value.customer_photo
        sale.sale.exely_guest_id = ""
        sale.sale.exely_room_stay_id = ""
        sale.sale.arrival = ""
        sale.sale.departure = ""
        sale.sale.room_number = ""
        sale.sale.pos_noted=""
        current_customer_point.value = 0
    }
}
async function onAddCustomer() {
    if (!sale.isBillRequested()) {
        const result = await addCustomerDialog({ title: $t('New Customer'), value: '' });
        if (result != false) {
            sale.sale.customer = result.name
            sale.sale.customer_name = result.customer_name_en
            sale.sale.customer_photo = result.photo
            sale.sale.phone_number = result.phone_number && result.phone_number_2 ? result.phone_number + ' / ' + result.phone_number_2 : (result.phone_number ? result.phone_number : result.phone_number_2)
            sale.sale.customer_group = result.customer_group
        }
    }
}

function onClearPromotionProduct() {
    // remove old promotion
    sale.sale.sale_products.forEach((s) => {

        if (s.happy_hour_promotion) {
            s.discount_type = ''
            s.discount = 0
            s.happy_hours_promotion_title = ''
            s.happy_hour_promotion = ''
        }
        sale.updateSaleProduct(s)
    });
    sale.updateSaleSummary()
}
onMounted(() => {
    if (!sale.sale.customer) {
        onRemove()
    }
})

</script>
<style>
@media (max-width: 1024px) {
    .guest-pro-scne {
        padding: 5px !important;
    }

    .guest-pro-scne .v-btn--icon {
        font-size: 10px;
    }

    .guest-pro-scne .font-bold {
        font-size: smaller;
    }
}
</style>