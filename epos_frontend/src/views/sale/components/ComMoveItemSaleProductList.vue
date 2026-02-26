<template>
    <v-list class="!p-0">
        <v-list-item v-for="sp, index in  sale.getMoveItemSaleProducts(groupKey)" :key="index"
            class="!border-t !border-gray-300 !mb-0 !p-2" @click="onSelected(sp)">
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
                            <div v-if="!sale.load_menu_lang">
                                {{ getMenuName(sp) }}
                                <v-chip v-if="(sp.total_selected || '') != 0" color="success" variant="flat"
                                    size="x-small">{{
            sp.total_selected || 0
        }}</v-chip>
                                <v-chip class="ml-1" size="x-small" color="error" variant="outlined"
                                    v-if="sp.portion">{{ sp.portion }}</v-chip>
                                <v-chip v-if="sp.is_free" size="x-small" color="success" variant="outlined">{{
            $t('Free') }}</v-chip>
                                <v-chip v-if="sp.is_park" size="x-small" color="error" variant="outlined">{{ $t('Park')
                                    }}</v-chip>
                                <ComChip :tooltip="sp.happy_hours_promotion_title"
                                    v-if="sp.happy_hour_promotion && sp.discount > 0" size="x-small" variant="outlined"
                                    color="orange" text-color="white" prepend-icon="mdi-tag-multiple">
                                    <span>{{ sp.discount }}%</span>
                                </ComChip>
                            </div>
                        </div>
                        <!-- <v-btn class="mx-1" size="small" variant="tonal">{{ sp.total_selected || 0 }}</v-btn> -->
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
                    </div>
                </div>
            </template>
        </v-list-item>
    </v-list>
</template>
<script setup>
import { inject, defineProps, i18n, ref } from '@/plugin'

import ComTimerProductEstimatePrice from '@/views/sale/components/ComTimerProductEstimatePrice.vue';

const { t: $t } = i18n.global;
const sale = inject('$sale');
const gv = inject('$gv');
const moment = inject('$moment');

const props = defineProps({
    groupKey: Object,
});

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



function onSelected(sp) {
    if ((sp.total_selected || 0) >= sp.quantity) {
        sp.total_selected = 0;
    } else {
        sp.total_selected = (sp.total_selected || 0) + 1;
    }
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