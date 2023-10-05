<template>
    <div v-if="isLoading">
        <div  class="overlay-loading-dialog">
        <span class="is-loading-page text-white flex justify-center flex-col">
            <i  class="pi pi-spin pi-spinner w-4rem h-4rem" style="font-size:4rem"></i>
            <span class="text-sm mt-1 flex align-items-center ml-2">Loading....</span>
        </span>
        </div>    
    </div>
</template>
<script setup>
import ProgressBar from 'primevue/progressbar';

const props = defineProps({
    isLoading: {
        type: Boolean,
        default: false
    }
})
</script>
<style>
.overlay-loading-dialog {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.4);
    width: 100%;
    height: 100%;
}
.is-loading-page{
    position: absolute;
    left: 50%;
    top: 50%;
    z-index: 11;
    transform: translate(-50%,-50%);
}
</style>