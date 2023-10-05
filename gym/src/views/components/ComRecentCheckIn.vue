<template>
          <div class="cart-item p-2 mb-2" v-for="(d, index) in data" :key="index">
                <div class="flex">
                  <div class="profile mr-3">
                    <img class="w-full h-full"
                      :src="d.photo">
                  </div>
                  <div class="profile-info">
                    <h4>{{ d.member_name }}</h4>
                    <p class="m-0"> <strong> {{ d.membership_type }}</strong></p>
                    <p class="m-0">{{ d.membership_name }}</p>
                    <label class="date">{{ moment(d.creation).format("DD-MM-YYYY hh:mm:ss A") }}</label>
                  </div>
                </div>
              </div>
</template>

<script setup>
  import moment from "moment"
  import { ref, inject } from "vue"
  const data = ref([])
  window.call.get("epos_restaurant_2023.api.gym.get_recent_checked_ins").then(res => {
      data.value = res.message
  })
</script>