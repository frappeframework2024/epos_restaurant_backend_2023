<template> 
    <div>
        <slot name="default"></slot>
        <div v-if="loading">
            <div  class="overlay-loading-dialog">
            <div class="is-loading-page text-white flex justify-content-center flex-column align-items-center">
                <div><i class="pi pi-spin pi-spinner" style="font-size:35px"></i></div>
                <div class="text-sm">Loading....</div>
            </div>
            </div>    
        </div>
    </div>
    <div>
        <slot name="footer"></slot>
    </div>
</template>
<script setup>  
import { useDialog } from 'primevue/usedialog'
// const dialog = useDialog() 
const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    }
})
</script>
<style>
.is-loading-page{
    position: absolute;
    left: 50%;
    top: 50%;
    z-index: 11;
    transform: translate(-50%,-50%);
}
.overlay-loading-dialog {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.4);
    width: 100%;
    height: 100%;
    border-radius: 12px;
}
</style>