<template>
    <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
        <template #title>
            {{ $t('Redeem Item') }}
        </template>
        <template #content>
            <v-row cols="12" class="d-flex flex-wrap" v-if="parkItemList.length > 0">
                <v-col lg="4" v-for="(s, index) in parkItemList" :key="index">
                    <v-card >
                        <v-card-title class="!p-0">
                            <v-toolbar height="48">
                                <v-toolbar-title class="text">
                                    <span class="font-bold text-sm">#{{ s.sale }} ({{ s.customer_name }})</span>
                                </v-toolbar-title>
                                <template v-slot:append>
                                    <v-chip size="small" color="success" class="ma-2">
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
                                @click="redeemClick(s)">
                                {{ $t('Redeem') }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>

            </v-row>
            <div v-else class="text-center">
              <h1 class="mt-2">{{ $t("No Data") }}</h1>
              <v-icon size="x-large" icon="mdi-file-document-outline"></v-icon>
            </div>
        </template>
    </ComModal>
</template>
<script setup>
import { defineProps, defineEmits, ref, inject, createToaster, i18n, onMounted } from "@/plugin"
import ComModal from "@/components/ComModal.vue";
const moment = inject("$moment")

const { t: $t } = i18n.global;

const isLoading = ref(true);
const sale = inject("$sale");
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
        
        isLoading.value = false;
    }).catch((err) => {
        isLoading.value = false;
    });
}

function redeemClick(data){
    onConvertToSale(data)
}

async function onConvertToSale(data) {
  const params = {
    business_branch: gv.setting?.business_branch,
    pos_profile: localStorage.getItem("pos_profile")
  };

  call.get('epos_restaurant_2023.api.api.get_current_shift_information', params)
    .then(async (_res) => {
      const _data = _res.message;
      if (_data.cashier_shift == null) {
        toaster.warning($t("msg.Please start shift first"));
      } else if (_data.working_day == null) {
        toaster.warning($t("msg.Please start working day first"));
      } else {
        gv.authorize("open_order_required_password", "make_order").then(async (v) => {
          if (v) {
            isLoading.value = true;
            const make_order_auth = { "username": v.username, "name": v.user, discount_codes: v.discount_codes };
            localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));

            await db.getDoc("Tables Number", data.table_id).then(async (table) => {
              sale.newSale();
              sale.sale.from_data = data.name;

              sale.sale.working_day = _data.working_day.name;
              sale.sale.cashier_shift = _data.cashier_shift.name;
              sale.sale.shift_name = _data.cashier_shift.shift_name;

              sale.sale.table_id = data.table_id;
              sale.sale.tbl_number = data.table_number;

              sale.sale.customer = data.customer;
            //   sale.sale.customer_photo = data.guest_photo;
            //   sale.sale.customer_name = data.guest_name;
            //   sale.sale.customer_group = data.guest_type;
            //   sale.sale.deposit = data.total_deposit;

              if (table.sale_type) {
                sale.sale.sale_type = table.sale_type
              }
              if (table.price_rule) {
                sale.table_price_rule = table.price_rule;
                sale.price_rule = table.price_rule;

                sale.sale.price_rule = table.price_rule;
              }
              else{  
                sale.table_price_rule = gv.setting?.price_rule;
                sale.price_rule = gv.setting?.price_rule;
                sale.sale.price_rule = gv.setting?.price_rule;
              }
              
              if (gv.setting.price_rule != sale.sale.price_rule) {
                toaster.info($t('msg.Your current price rule is', [sale.sale.price_rule]));
              }

              sale.sale.sale_status = "Hold Order";
              sale.action = "hold_order";

              await reservationProductConvert(data);


              await sale.onSubmit().then(async (value) => {
                if (value) {
                  sale.sale = value;
                  call.get("epos_restaurant_2023.api.api.update_pos_reservation_and_sale_payment", {
                    reservation_name: reservation.name,
                    reservation_status: "Dine-in",
                    sale: value.name
                  }).then(() => {
                    router.push({
                      name: "AddSale",
                      params: { name: value.name }
                    }).then(() => {
                      onClose();
                    });

                  }).catch((err) => {
                    _onInit()
                  });
                }
              }).catch(() => {
                isLoading.value = false;
              });
            }).catch(() => {
              isLoading.value = false;
            })

          }
        });
      }
    })
    .catch((error) => {
      isLoading.value = false;
    });
}

function onClose() {
    emit('resolve', false);
}
</script>