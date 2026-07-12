<template>

      <ComModal
        :mobileFullscreen="true" 
        @onClose="onClose"
        :hideOkButton="true"
        :hideCloseButton="true"
        >

        <template #title> 
            <v-card-title class="text-h5 text-left py-4">
            {{ $t('Select Action') }}
            </v-card-title>
        </template>
        <template #content>
            <v-card> 
                <v-card-text>
                <v-row>
                    <!-- Booking Information --> 
                    <v-col cols="12" md="6">
                        <v-card class="pa-4" elevation="3" rounded="lg">
                            <div class="d-flex justify-space-between align-center mb-3">
                                <div>
                                    <div class="text-h6 font-weight-bold">
                                        {{ booking.customer_name }}
                                    </div>
                                    <div class="text-caption text-grey">
                                        {{ booking.name }}
                                    </div>
                                </div>

                                <v-chip
                                    :color="booking.sale_status_color"
                                    text-color="white"
                                >
                                    Reserved
                                </v-chip>
                            </div>

                            <v-divider class="mb-3" />

                            <v-row dense>
                                <v-col cols="6">
                                    <div class="text-caption text-grey">Arrival Time</div>
                                    <div class="font-weight-medium">
                                        <v-icon size="16">mdi-clock-outline</v-icon>
                                        {{ booking.arrival_time }}
                                    </div>
                                </v-col>

                                <v-col cols="6">
                                    <div class="text-caption text-grey">Guests</div>
                                    <div class="font-weight-medium">
                                        <v-icon size="16">mdi-account-group</v-icon>
                                        {{ booking.guest_cover }}
                                    </div>
                                </v-col>

                                <v-col cols="12">
                                    <div class="text-caption text-grey">Phone</div>
                                    <div class="font-weight-medium">
                                        <v-icon size="16">mdi-phone</v-icon>
                                        {{ booking.phone_number }}
                                    </div>
                                </v-col>
                            </v-row>

                            <v-btn
                                color="success"
                                size="large"
                                block
                                class="mt-4"
                                prepend-icon="mdi-door-open"
                                @click="checkedIn(booking)"
                            >
                                Checked-In
                            </v-btn>
                        </v-card>
                        </v-col>
                    <!-- New Order -->
                    <v-col cols="12" md="6">
                        <v-card
                            class="pa-6 text-center action-card"
                            elevation="3"
                            @click="newOrder"
                        >
                            <v-icon
                            size="60"
                            color="primary"
                            >
                            mdi-cart-plus
                            </v-icon>

                            <div class="text-h6 mt-4">
                            {{ $t("New Order") }}
                            </div>

                            <div class="text-body-2 text-grey">
                            {{ $t("Create a new dine-in order.") }}
                            </div>
                        </v-card>
                    </v-col>

                </v-row>
                </v-card-text>
            </v-card>
        </template>
       

      </ComModal>
 

 
</template>

<script setup>
    import { ref,defineEmits,createToaster,confirmDialog,onMounted, computed, inject,i18n } from '@/plugin';  
    const { t: $t } = i18n.global;  
    const toaster = createToaster({ position: 'top-right' });
    const props = defineProps({
        params: {
            type: Object,
            require: true
        }
    })

    const emit = defineEmits(["resolve","reject"])

   
     

    const newOrder = () => {
       
        console.log("New Order");
        // router.push(...)
    };

    const bookingInfo = () => {
        
        console.log("Booking Information");
        // router.push(...)
    };


    function onClose() {
        emit('resolve',false);
    }


    const booking = ref({
    name: "PRes2026-0052",
    creation: "2026-07-11 15:30:00",
    guest_cover: 4,
    arrival_time: "15:30:00",
    sale_status_color: "#CB2929",
    customer: "C2026-0524",
    customer_name: "Phalla",
    phone_number: "098465652"
})

const checkedIn = (booking) => {
    console.log("Checked In", booking)

    // Example:
    // await frappe.call(...)
    // dialog.value = false
    // router.push(...)
}
</script>

<style scoped>
.action-card {
  cursor: pointer;
  transition: all 0.25s ease;
  border-radius: 16px;
}

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
}
</style>