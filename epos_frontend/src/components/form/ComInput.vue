<template>
    <div>
        <div v-if="type=='textarea'">
            
            <v-textarea
                v-if="keyboard && !mobile"
                :required="required"
                :type="type"
                :density="density"
                :variant="variant"
                :label="label"
                :single-line = "!label"
                :disabled="disabled"
                :readonly="readonly"
                :no-resize = "noResize"
                :max-rows = "maxRows"
                :rows = "row"
                hide-details
                :placeholder="placeholder"
                append-inner-icon="mdi-keyboard"
                v-model="value"
                @click:append-inner="onDialog()"
                  @click:clear="onClear"
                :prepend-inner-icon="prependInnerIcon"
                ref="txtSearch"
                @input="updateValue">
            </v-textarea>
            <v-textarea
                v-else
                :required="required"
                :type="type"
                :density="density"
                :variant="variant"
                :label="label"
                :single-line = "!label"
                :disabled="disabled"
                :readonly="readonly"
                :no-resize = "noResize"
                :max-rows = "maxRows"
                :rows = "row"
                hide-details
                :append-inner-icon="appendInnerIcon"
                v-model="value"
                ref="txtSearch"
                @click:append-inner="emit('onClickAppendInner')"
                  @click:clear="onClear"
                :prepend-inner-icon="prependInnerIcon"
                @click:prepend-inner="emit('onClickPrependInner')"
                @input="updateValue">
            </v-textarea>
        </div>
        <div v-else>
            
            <v-text-field
                :autofocus="validAutofocus"
                :clearable="!readonly"
                :required="required"
                v-if="keyboard && !mobile"
                :type="type"
                :density="density"
                :variant="variant"
                :label="label"
                :single-line = "!label"
                :disabled="disabled"
                :readonly="readonly"
                hide-details
                :placeholder="placeholder"
                append-inner-icon="mdi-keyboard"
                v-model="value"
                @click:append-inner="onDialog()"
                :prepend-inner-icon="prependInnerIcon"
                @input="updateValue"
                @click:clear="onClear"
                :class="type=='date'?'date-input':''"
                ref="txtSearch"
                >
            </v-text-field>
            <v-text-field
                v-else
                :autofocus="validAutofocus"
                :required="required"
                :type="type"
                :density="density"
                :variant="variant"
                :label="label"
                :single-line = "!label"
                :disabled="disabled"
                :readonly="readonly"
                hide-details
                :append-inner-icon="appendInnerIcon"
                v-model="value"
                :placeholder="placeholder"
                @click:append-inner="emit('onClickAppendInner')"
                :prepend-inner-icon="prependInnerIcon"
                @click:prepend-inner="emit('onClickPrependInner')"
                @click:clear="onClear"
                @input="updateValue"
                ref="txtSearch"
                :class="type=='date'?'date-input':''">
            </v-text-field>
        </div>
    </div>
</template>
<script setup>
import {computed,keyboardDialog,onMounted,ref,nextTick} from '@/plugin'
import { useDisplay } from 'vuetify'
import { onKeyStroke } from '@vueuse/core'
const { mobile } = useDisplay()
const txtSearch = ref(null);

const props = defineProps({
    modelValue: [String, Number],
    type: {
        type: String,
        default: 'text'
    },
    appendInnerIcon: {
        type: String,
        default: ''
    },
    prependInnerIcon: {
        type: String,
        default: ''
    },
    variant: {
        type: String,
        default: 'solo'
    },
    density: {
        type: String,
        default: 'compact'
    },
    placeholder: {
        type: String,
        default: ''
    },
    label: {
        type: String,
        default: ''
    },
    title: {
        type: String
    },
    noResize: {
        type: Boolean,
        default: true
    },
    maxRows: {
        type: Number,
        default: 5
    },
    row: {
        type: Number,
        default: 3
    },
    disabled:{
        type: Boolean,
        default: false
    },
    readonly:{
        type: Boolean,
        default: false
    },
    required: {
        type: Boolean,
        default: false
    },
    keyboard: Boolean,
    autofocus:Boolean,
    listeningFocus:Boolean,
    requiredAutofocus: {
        type: Boolean,
        default: false
    }
})

let value = computed({
    get(){
        return props.modelValue
    },
    set(newValue){
        return newValue
    }
})
const validAutofocus = computed(()=>{ 
    return props.requiredAutofocus ? true : props.autofocus && !mobile.value
})
// let data = ref(props.modelValue)
const emit = defineEmits(['update:modelValue','focus'])

const updateValue = (event) => {
    let value = event.target.value;
    if(props.type == 'number'){
        value = parseFloat(value || 0)
    }
    emit('update:modelValue', value)
}

async function onDialog() { 
    const keys = await keyboardDialog({title: props.title,type: props.type, value:props.modelValue}); 
    if(typeof keys == 'boolean' && keys == false){
        return
    }
    else {         
        emit('onInput',keys)
        emit('update:modelValue', keys)
    }
}
if(props.listeningFocus){
    onKeyStroke('Escape', (e) => {
        // e.preventDefault();
        txtSearch.value.focus()
    }, { dedupe: true })
}


function focus(){
    nextTick(() => {
        if (txtSearch.value) {
            txtSearch.value.focus()
        }
    });
}
function onClear(){ 
    emit('onInput',"")
    emit('onClear',"")
    emit('update:modelValue', "")
}
</script>
<style>
    input[type=date]{
        display: initial !important;
    }
</style>