<template>
          <div class="cart-item p-2 mb-2" v-for="(d, index) in data" :key="index">
                <div class="flex">
                  <div class="profile mr-3">
                    <img class="w-full h-full"
                      :src="d.photo">
                  </div>
                  <div class="profile-info">
                    <h4>{{ d.member_name }}</h4>
                    <p class="m-0">Yog</p>
                    <label class="date">Oct 3, 12:00am</label>
                  </div>
                </div>
              </div>
</template>
<script setup>

import { ref, inject } from "vue"
const data = ref()
window.db.getDocList("Membership Check In",
    {
        fields:["name","member_name","photo","gender","date_of_birth"],
        orderBy: {
            field: 'creation',
            order: 'desc',
        },
    }
).then(r => {
    data.value = r
})
</script>