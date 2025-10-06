<template>  
    <div class="flex gap-1 align-items-center">
        <Avatar v-if="data?.user_info?.photo" :image="data?.user_info?.photo" class="mr-2" size="xlarge" shape="circle" />
        <Avatar v-else :label="avatarLetter" class="mr-2" size="xlarge" shape="circle" />
        <div>
            <div class="welcome-label">{{t("Welcome Back")}},</div>
            <h1>{{data?.user_info?.full_name}}</h1>
        </div>
    </div>
     
</template>
<script setup> 
import Avatar from 'primevue/avatar';
import { computed } from 'vue';
const props = defineProps({
    data:Object
})
const t = window.t;
const avatarLetter = computed(() => props.data?.user_info?.full_name.charAt(0) || "")

</script>