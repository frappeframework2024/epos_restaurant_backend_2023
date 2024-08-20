<template>
    <div  :class="[isDialog ? 'wrap-dialog' : 'bg-white p-2 relative di-page', dialogClass]">
        <div :class="isDialog ? 'wrap-dialog-content overflow-auto' : ''">
            <slot name="default"></slot>
            <div v-if="loading">
                <div  class="overlay-loading-dialog">
                <div class="is-loading-page text-white flex justify-center flex-col">
                    <div><i class="pi pi-spin pi-spinner" style="font-size:35px"></i></div>
                    <div class="text-sm">Loading....</div>
                </div>
                </div>    
            </div>
        </div>
        <div v-if="!hideFooter" :class="[isDialog == false ? 'p-2 page-footer-fixed':'p-2 footer-fixed dialog-ftt position-fixed bottom-0 left-0 bg-white w-100 ', loading ? 'unset-absolute' : '']">
            <div class="overflow-auto lg:overflow-hidden">
                <slot name="footer-top"></slot>
                <div class="flex gap-1 lg:gap-0 justify-between items-center w-max lg:w-full">
                    <div class="flex gap-2">
                        <slot name="footer-left"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-center"></slot>
                    </div>
                    <div class="flex gap-2">
                        <slot name="footer-right"></slot>
                        <v-btn class="text-white" v-if="!hideButtonClose"  rounded="lg" color="red-lighten-1" @click="close()" :loading="loading">
              {{ titleButtonClose ?? 'Cancel' }}
            </v-btn>            
                        <v-btn class="text-white" :disabled="disabledBtnOk" rounded="lg" color="green-lighten-1" v-if="!hideButtonOK" @click="onOK()" :loading="loading">
              {{ titleButtonOK ?? 'Save' }}
            </v-btn>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

const emit = defineEmits(['onOK', 'onClose', 'onMaximize'])
const props = defineProps({
    loading: {
        type: Boolean,
        default: false
    },
    dialogClass: {
        type: String,
    },
    titleButtonOK: {
        type: String,
        default: 'Save'
    },
    titleButtonClose: {
        type: String,
        default: 'Close'
    },
    hideButtonClose: {
        type: Boolean,
        default: false
    },
    hideButtonOK: {
        type: Boolean,
        default: false
    },
    hideFooter: {
        type: Boolean,
        default: false
    },
    isDialog: {
        type: Boolean,
        default: true
    },
    hideIcon: {
        type: Boolean,
        default:false
    },
    maximizable: {
        type: Boolean,
        default:false
    },
    disabledBtnOk: {
        type: Boolean,
        default:false
    },
    
})
function onOK() { 
    emit('onOK')
}
function close() {
    emit('onClose')
}
function onMaximize(){
    emit('onMaximize')
}
</script>
<style scoped>
    .bg-og-edoor:hover , .bg-og-edoor:active{
        background-color: var(--bg-og-color);
    }
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
}
</style>