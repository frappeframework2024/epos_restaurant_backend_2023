<template>
    <v-card class="m-2" >
        <v-card-text class="!p-2">
            <div class="flex">
                <div class="flex-none flex items-center">
                    <v-avatar v-if="sale.customer_photo" size="x-large">
                        <v-img :src="sale.customer_photo"></v-img>
                    </v-avatar>
                    <avatar v-else :name="sale.customer_name" class="my-0 mx-auto" size="56"></avatar>
                </div>
                <div class="grow px-2">
                    <div class="flex">
                        <div class="grow">
                            <div class="font-bold">
                                <span :class="mobile ? '' : 'text-lg'">{{ sale.customer }} - {{ sale.customer_name }}</span>
                                <v-chip class="mx-1" prepend-icon="mdi-account-multiple-outline" size="x-small"
                                    v-if="sale.guest_cover > 0">{{ sale.guest_cover }}</v-chip>
                                <v-chip :color="sale.sale_status_color" class="mx-1" size="x-small" v-if="sale.sale_status">{{ sale.sale_status
                                }}</v-chip>
                            </div>
                            <div class="text-xs">
                                {{ sale.phone_number }}
                            </div>

                            <div class="text-sm">
                                <div>{{ $t('Bill') }}#: {{ sale.name }}

                                <v-chip  v-if="(sale.seat_number??0) != 0" color="green" class="mx-1" size="small">
                                    {{`${$t("Seat")} #: ${sale.seat_number}`}}
                                  </v-chip>
                                </div>
                                 
                                
                                <div>
                                    <div v-if="sale.creation" class="text-xs">
                                        <v-icon icon="mdi-clock" size="x-small"></v-icon>
                                        {{ getTimeAgo(sale.creation) }}
                                    </div> 
                                </div>
                            </div> 
                        </div>
                        <div class="flex-none text-right">
                            <div class="font-bold" :class="mobile ? '' : 'text-lg'">
                                <CurrencyFormat :value="sale.grand_total" />
                            </div>
                            <div class="text-sm">
                                {{ $t('Qty') }}: {{ sale.total_quantity }}
                            </div>
                        </div>
                    </div>
                   
                </div>

            </div>
        </v-card-text>
    </v-card>
</template>
<script setup>
import { inject } from '@/plugin';
import { defineProps } from 'vue';
import { useDisplay } from 'vuetify';
const moment = inject("$moment");
const {mobile} = useDisplay();
const props = defineProps({
    sale: Object
})


function getTimeAgo(date) {
    const now = Date.now();
    const diff = now - moment(date).toDate();
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    if (minutes <= 0 && hours <= 0) {
        return "just now"
    } else {
        if (hours == 0) {
            return `${minutes} mn`;
        }
        return `${hours} h ${minutes} mn`;
    }
}

</script>