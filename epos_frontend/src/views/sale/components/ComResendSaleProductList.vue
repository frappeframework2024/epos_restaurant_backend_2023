<template>
    <v-list class="!p-0">
        <v-list-item v-for="sp, index in (readonly == true ? getSaleProducts(groupKey) : sale.getSaleProducts(groupKey))"
            :key="index" @click="toggleSelection(sp)"
            class="!border-t !border-gray-300 !mb-0 !p-2"
            :class="{ 'selected': sp.selected, 'submitted relative': sp.sale_product_status == 'Submitted', 'item-list': !readonly }">
            <template v-slot:prepend>
                <v-avatar v-if="sp.product_photo">
                    <v-img :src="sp.product_photo"></v-img>
                </v-avatar>
                <avatar v-else :name="sp.product_name" class="mr-4" size="40"></avatar>

            </template>
            <template v-slot:default>
                <div class="text-sm">  
                    <div class="flex">
                        <div class="grow">
                            <div v-if="!sale.load_menu_lang"> {{ getMenuName(sp) }}<v-chip class="ml-1" size="x-small"
                                    color="error" variant="outlined" v-if="sp.portion">{{ sp.portion }}</v-chip>
                                <v-chip v-if="sp.is_free" size="x-small" color="success" variant="outlined">{{ $t('Free')
                                }}</v-chip>
                                <v-chip v-if="sp.is_park" size="x-small" color="error" variant="outlined">
                                    {{ $t('Park') }}</v-chip>
                                <ComChip :tooltip="sp.happy_hours_promotion_title"
                                    v-if="sp.happy_hour_promotion && sp.discount > 0" size="x-small" variant="outlined"
                                    color="orange" text-color="white" prepend-icon="mdi-tag-multiple">
                                    <span>{{ sp.discount }}%</span>
                                </ComChip>
                                <ComHappyHour :saleProduct="sp" v-if="sp.is_render" />
                            </div>

                            <div v-if="!sp.is_timer_product">
                                {{ sp.quantity }} x
                                <CurrencyFormat :value="sp.price" />
                            </div>
                            <div v-else>
                                <template v-if="sp.time_in">
                                    {{ $t("Time In") }}: {{ moment(sp.time_in).format('hh:mm A') }}
                                    <span v-if="sp.time_out">
                                        {{ $t("Time Out") }}
                                        {{ moment(sp.time_out).format('hh:mm A') }}
                                    </span>

                                </template>

                            </div>
                            <div class="text-xs pt-1">
                                <div v-if="sp.modifiers && !sp.is_timer_product">
                                    <span>{{ sp.modifiers }} (
                                        <CurrencyFormat :value="sp.modifiers_price * sp.quantity" />)
                                    </span>
                                </div>

                                <div v-if="sp.is_combo_menu">
                                    <div v-if="sp.use_combo_group && sp.combo_menu_data">
                                        <ComSaleProductComboMenuGroupItemDisplay :combo-menu-data="sp.combo_menu_data" />
                                    </div>
                                    <span v-else>{{ sp.combo_menu }}</span>
                                </div>
                                <div v-if="sp.discount > 0 && !sp.is_free">
                                    <span class="text-red-500">
                                        {{ $t('Discount') }} :
                                        <span v-if="sp.discount_type == 'Percent'">{{ sp.discount }}%</span>
                                        <CurrencyFormat v-else :value="parseFloat(sp.discount)" />
                                    </span>
                                </div>

                                <div v-if="(sp.is_require_employee || 0) == 1">
                                    <span v-for="emp, idx in getEmployees(sp.employees)" :key="idx" class="text-gray-500">
                                        <v-chip class="m-0.5" size="x-small" variant="outlined" color="primary"
                                            text-color="white">
                                            {{ emp.employee_display_name }}
                                        </v-chip>
                                    </span>

                                </div>
                                <v-chip color="blue" size="x-small" v-if="sp.seat_number"> {{ $t('Seat') + "# " +
                                    sp.seat_number
                                }}</v-chip>
                                <!-- <div class="text-gray-500">
                                    <v-icon icon="mdi-clock" size="small" class="mr-1"></v-icon><span>{{ moment(sp.creation).format('hh:mm:ss A') }}</span>
                                </div> -->
                               
                                <div class="text-gray-500" v-if="sp.note">
                                    {{ $t('Note') }}: <span>{{ sp.note }}</span>
                                </div>
                                <div class="text-gray-500" v-if="sp.is_park">
                                    {{ $t('Expiry') + ": " + moment(sp.expired_date).format('DD-MM-yyyy') }}
                                </div>
                            </div>
                        </div>

                        <div class="flex-none text-right w-36">
                            <div class="text-lg">
                                <ComTimerProductEstimatePrice v-if="sp.is_timer_product && !sp.time_out_price"
                                    :saleProduct="sp" />
                                <CurrencyFormat v-else :value="(sp.amount - sp.total_tax)" />
                            </div>
                            <span v-if="sp.product_tax_rule && sp.total_tax > 0" class="text-xs">
                                {{ $t('Tax') }}:
                                <CurrencyFormat :value="sp.total_tax" />
                            </span>

                            <!-- <ComQuantityInput v-if="!readonly" :sale-product="sp" /> -->
                        </div>
                    </div>
                </div>

            </template>
        </v-list-item>
    </v-list>
</template>
<script setup>
import { computed, inject, defineProps, confirmDialog, createToaster, i18n, ref, SelectDateTime, stopTimerModal } from '@/plugin'

import ComSaleProductButtonMore from './ComSaleProductButtonMore.vue';
import ComQuantityInput from '../../../components/form/ComQuantityInput.vue';
import Enumerable from 'linq';
import ComSaleProductComboMenuGroupItemDisplay from './combo_menu/ComSaleProductComboMenuGroupItemDisplay.vue';
import ComHappyHour from './happy_hour_promotion/ComHappyHour.vue';
import ComTimerProductEstimatePrice from '@/views/sale/components/ComTimerProductEstimatePrice.vue';

const { t: $t } = i18n.global;
const numberFormat = inject('$numberFormat');
const sale = inject('$sale');
const product = inject('$product');
const gv = inject('$gv');
const moment = inject('$moment');
const toaster = createToaster({ position: 'top-right' });
const frappe = inject("$frappe")
const call = frappe.call()

const props = defineProps({
    groupKey: Object,
    readonly: Boolean,
    saleCustomerDisplay: Object
});

function toggleSelection(sp) {
    sp.selected = !sp.selected
}

function getMenuName(sp) {
    const mlang = localStorage.getItem('mLang');
    let code = gv.setting.show_item_code_in_sale_screen == 0 ? "" : `${sp.product_code} - `;

    if (mlang != null) {
        if (mlang == "en") {

            return `${code}${sp.product_name}`;
        } else {
            return `${code}${sp.product_name_kh}`;
        }

    } else {
        localStorage.setItem('mLang', 'en');
        return `${code}${sp.product_name}`;
    }
}
 


function getSaleProducts(groupByKey) {
    if (props.saleCustomerDisplay && props.saleCustomerDisplay.sale_products) {
        if (groupByKey) {
            return Enumerable.from(props.saleCustomerDisplay.sale_products).where(`$.order_by=='${groupByKey.order_by}' && $.order_time=='${groupByKey.order_time}'`).orderByDescending("$.modified").toArray()
        } else {
            return Enumerable.from(props.saleCustomerDisplay.sale_products).orderByDescending("$.modified").toArray();
        }
    }
    return [];
}



function getEmployees(data) {
    if ((data || "") != "") {
        const result = JSON.parse(data);
        if (result) {
            if (result.length > 0) {
                result.forEach((e) => {
                    e.employee_display_name = e.employee_name + '(' + e.duration_title + ')';
                })
            }
        }
        return result;
    }
    return []
}

 
 

</script>


<style scoped>
.selected,
.item-list:hover {
    background-color: #ffebcc !important;
}

.submitted::before {
    content: '';
    position: absolute;
    top: 1px;
    bottom: 1px;
    left: 0px;
    width: 2px;
    background: #75c34a;
    border-radius: 12px;
}
</style>
 