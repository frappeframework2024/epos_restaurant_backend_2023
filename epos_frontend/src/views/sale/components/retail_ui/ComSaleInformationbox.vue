<template>
    <div class="v-col rounded-lg mx-1 p-1 clickable-box raised-box " :class="bgColor" @click="onClick">
        <div class="flex items-center h-100">
            <div class="v-row px-2">
                <div class="v-col text-white" style="padding: 0 !important;">
                    <small>
                        {{ title }}
                    </small>
                    <div>
                        {{ value }}
                    </div>
                </div>
                <div class="v-col-auto flex justify-center align-center v-ps-5" style="padding: 0 !important;">
                    <v-icon :size="size" :icon="icon" color="white"></v-icon>
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
.clickable-box {
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.clickable-box:hover {
  background-color: #5d9bff;
}
.raised-box {
  padding: 1rem 2rem;
  border-radius: 10px;
  cursor: pointer;
  transition:
    transform 0.1s ease,
    box-shadow 0.2s ease;
  box-shadow: 0 3px 3px rgba(0, 0, 0, 0.2);
}

.raised-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 6px rgba(0, 0, 0, 0.25);
}
</style>
<script setup>
import { defineProps, inject } from 'vue'
const emit = defineEmits(["onClick"])
const props = defineProps({
    title: String,
    value: String,
    bgColor: String,
    icon: String,
    size: String
})
function onClick() {
    emit('onClick')
}
</script>

<style lang="">

</style>