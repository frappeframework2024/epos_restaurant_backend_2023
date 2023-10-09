<template>
          <div class="cart-item p-2 mb-2" v-for="(d, index) in data" :key="index">
                <div class="flex">
                  <div class="profile mr-3">
                    <img class="w-full h-full"
                      :src="d.photo">
                  </div>
                  <div class="profile-info">
                    <h4>
                     {{ d.member_name }}
                    </h4>
                  <p class="m-0"> <strong> {{ d.membership_type }}</strong></p>
                    <p class="m-0">{{ d.membership_name }}  <label class="text-xs text-white bg-green-200 border-round-3xl p-1 " style="background-color: #00949ed0 !important;">Checked-In <span class="bg-green-500 px-1 border-round-xl" style="background-color: #006d75d0 !important;"> {{ d.check_in_number }}</span></label></p>
                    <label class="date">{{ moment(d.creation).format("DD-MM-YYYY hh:mm:ss A") }}</label>
                  </div>
                </div>
              </div>
</template>

<script setup>
  import moment from "moment"
  import { ref, inject } from "vue"
  const data = ref([])
  window.call.get("epos_restaurant_2023.api.gym.get_recent_checked_ins",{"limit":10}).then(res => {
      data.value = res.message
  })
</script>