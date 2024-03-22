<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
        <template #title>
            {{ $t('Redeem Item') }}
        </template>
        <template #content>
            <v-row cols="12" class="d-flex flex-wrap">
                <v-col lg="4" v-for="(s, index) in parkItemList" :key="index">
                    <v-card >
                        <v-card-title class="!p-0">
                            <v-toolbar height="48">
                                <v-toolbar-title class="text">
                                    <span class="font-bold text-sm">#{{ s.sale }}</span>
                                </v-toolbar-title>
                                <template v-slot:append>
                                    <v-chip size="small" class="ma-2">
                                        {{ $t("EXP") }}:
                                        {{ moment(s.expired_date).format("DD-MMM-YYYY") }}
                                    </v-chip>
                                </template>
                            </v-toolbar>
                        </v-card-title>
                        <v-card-text class="!pt-0 !pr-0 !pb-14 !pl-0">
                            <v-list :lines="false" density="compact" class="pa-0">
                                <template v-for="p in s.products">
                                    <v-list-item :title="`${p.product_code}-${p.product_name}`">
                                        <template v-slot:append>
                                            x {{ p.quantity }}
                                        </template>
                                    </v-list-item>
                                </template>


                            </v-list>
                        </v-card-text>
                        <v-card-actions class="pt-0 flex items-center justify-between absolute bottom-0 w-full">

                            <v-btn v-if="s.arrival_date == current_date" variant="tonal" color="success"
                                @click="onCheckIn(s)">
                                {{ $t('Redeem') }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>

            </v-row>

        </template>
    </ComModal>
</template>
<script setup>
import { defineProps, defineEmits, ref, inject, createToaster, i18n, onMounted } from "@/plugin"
import ComModal from "@/components/ComModal.vue";
const moment = inject("$moment")

const { t: $t } = i18n.global;

const isLoading = ref(true);

const frappe = inject("$frappe");
const emit = defineEmits(["resolve"])
const gv = inject('$gv');
const toaster = createToaster({ position: "top-right" });

const db = frappe.db();
const call = frappe.call();

const props = defineProps({
    params: {
        type: Object,
        required: true,
    }
})
const parkItemList = ref([])

onMounted(() => {
    _onInit()
});


function _onInit() {
    isLoading.value = true;
    call.get("epos_restaurant_2023.selling.doctype.sale.sale.get_park_item_to_redeem", { business_branch: gv.setting.business_branch }).then((res) => {
        parkItemList.value = res.message
        console.log(res.message)
        const result = Object.values(res.message.reduce((acc, curr) => {
            if (!acc[curr.sale]) {
                acc[curr.parent] = { sale: curr.parent,expired_date : moment().format("yyyy-MM-dd") , products: [] };
            }
            acc[curr.parent].expired_date=curr.expired_date;
            acc[curr.parent].products.push(curr);
            return acc;
        }, {}));
        parkItemList.value = result
        isLoading.value = false;
    }).catch((err) => {
        isLoading.value = false;
    });
}

function redeemClick(data){

}

function onClose() {
    emit('resolve', false);
}
</script>