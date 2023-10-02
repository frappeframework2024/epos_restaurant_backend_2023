<template>
    <div>
        <div v-if="type=='textarea'">
    
            <v-textarea
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
                @click:append-inner="emit('onClickAppendInner')"
                :prepend-inner-icon="prependInnerIcon"
                @click:prepend-inner="emit('onClickPrependInner')"
                @input="updateValue">
            </v-textarea>
        </div>
        <div v-else>
            <v-text-field
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
                @input="updateValue"
                :class="type=='date'?'date-input':''">
            </v-text-field>
        </div>
    </div>
</template>
<script setup>
import {computed} from 'vue'

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
    return props.requiredAutofocus ? true : props.autofocus
})
// let data = ref(props.modelValue)
const emit = defineEmits(['update:modelValue'])

const updateValue = (event) => {
    let value = event.target.value;
    if(props.type == 'number'){
        value = parseFloat(value || 0)
    }
    emit('update:modelValue', value)
}


function onClear(){ 
    emit('onInput',"")
    emit('update:modelValue', "")
}
</script>
<style>
    input[type=date]{
        display: initial !important;
    }
</style>