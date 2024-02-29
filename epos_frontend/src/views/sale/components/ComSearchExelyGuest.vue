<template>
   <v-row no-gutters>
      <v-col cols="4" sm="4">
         <ComInput requiredAutofocus class="m-1" keyboard v-model="filter.room" :placeholder="$t('Room')"
            v-debounce="searchGuest" @onInput="searchGuest" />
      </v-col>

      <v-col cols="4" sm="4">
         <ComInput keyboard class="m-1" v-model="filter.guest_name" :placeholder="$t('Guest Name')"
            v-debounce="searchGuest" @onInput="searchGuest" />
      </v-col>

      <v-col cols="4" sm="4">
         <ComInput keyboard class="m-1" v-model="filter.guest_phone" :placeholder="$t('Phone Number')"
            v-debounce="searchGuest" @onInput="searchGuest" />
      </v-col>
   </v-row>

   <template v-if="!filter.room && !filter.guest_name && !filter.guest_phone">
      <div class="text-center mt-5">Please enter Room Number,
         Guest Name or Phone
         Number to search Guest Profile " <v-icon icon="mdi-magnify" /> "</div>
   </template>
   <template v-else>
      <div>
         <ComPlaceholder icon="mdi-account-outline" :loading="isLoading" :text="$t('No Guest Found')"
            :isNotEmpty="data.length > 0">
            <v-card v-for="(c, index) in data" :key="index" :title="c.customer_name_en"
            @click="onSelectCustomer(c)"
            class="mb-4">
               <template v-slot:subtitle>
                  <span v-if="c.phone_number">
                     Phone Number: {{ c.phone_number }}
                  </span><br />
                  <span v-if="c.arrival">Stay Date: {{ moment(c.arrival).format("DD-MM-YYYY") }}</span>
                  <template v-if="c.departure"> &#8594; </template>
                  <span v-if="c.departure">{{  moment(c.departure).format("DD-MM-YYYY")  }}</span>
                  <template v-if="c.room"> | </template>
                  <span v-if="c.room">Room: {{ c.room }}</span>
               </template>
               <template v-slot:prepend>
                  <v-avatar v-if="c.photo">
                     <v-img :src="c.photo"></v-img>
                  </v-avatar>
                  <avatar v-else :name="c.customer_name_en" class="mr-4" size="40"></avatar>
               </template>
               <template v-slot:append>
                  <v-chip v-if="c.status" :color="c.status_color">
                     {{c.status}}
                  </v-chip>
               </template>
            </v-card>
         </ComPlaceholder>
      </div>
   </template>
</template>

<script setup>
import { ref, inject } from "@/plugin"
const emit = defineEmits(["onSelectCustomer"])
const data = ref([])
const isLoading = ref(false)
const gv = inject("$gv");
const moment = inject("$moment")
const filter = ref({ guest_name: '', room: "", guest_phone: '' })
const frappe = inject('$frappe');
const call = frappe.call();
function searchGuest() {
   isLoading.value = true
   call.get("epos_restaurant_2023.api.exely.search_guest", filter.value).then(r => {
      data.value = r.message
      isLoading.value = false
   }).catch(err => {
      isLoading.value = false
      console.log(err);
   })

}

function onSelectCustomer(c){
   emit("onSelectCustomer",c)
}


</script>
