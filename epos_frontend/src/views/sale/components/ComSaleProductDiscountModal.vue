<template>
    <ComModal :persistent="true" :width="categoryNoteName ? '1200px' : '800px'" @onClose="onClose()" @onOk="onOK()" title-ok-button="OK" :fullscreen="mobile">
        <template #title>
            <div>{{ params.title ?? $t("Discount") }}</div>
        </template>
        <template #content>
            <div>  
      <v-chip-group
        v-model="selectedGroup"
        column
        multiple
      >  
        <v-chip
        v-if="(discount_type == 'Percent' && params.data.sale_product == null )"
          filter
          variant="outlined"
          v-for="(d, index) in  revenueGroups" :key="index"
        >
          {{ d }}
        </v-chip>
        <hr/>
        </v-chip-group>

                <v-row :class="categoryNoteName ? '' : '!m-0'">
                    <v-col cols="12" :md="categoryNoteName ? 6 : 12">
                        <div class="mb-2">
                            <div class="mb-2">
                                <v-alert variant="tonal" color="warning" class="!p-2">
                                    <div>{{ $t('Discountable Amount') }} <CurrencyFormat :value="params.value" />. {{ $t('Max discount') }} <span class="mr-2">({{maxDiscountPercent * 100}}%)</span><span>     <CurrencyFormat :value="Number(discountAmount)" /></span></div>
                                </v-alert>
                            </div>
                            <div style="content: '';display: table;clear: both;width:100%">
                                <div style="float: left;width: 84%;"><ComInput 
                                :keyboard="(discount_type == 'Amount' || percent_manual == 1)" 
                                type="number"
                                v-model="discount"
                                :disabled="(discount_type == 'Percent' && percent_manual == 0)"
                                /></div>
                                <div style="float: left;width: 15%;margin-top: 2px;margin-left: 7px;"><v-btn :disabled="discount_type == 'Amount'" variant="flat" type="button" color="primary" @click="manual_percent_discount()">Manual</v-btn></div>
                            </div>
                           
                           
                        </div>
                        <div>
                            <div class="-m-1">
                                    <v-btn
                                    class="p-1 m-1"
                                    v-for="(item, index) in discountCodes" 
                                    :key="index"
                                        size="large"
                                        :color="item.discount_value == (discount_type == 'Percent' ? discount / 100 : discount) ? 'primary' : ''"
                                        @click="onClick(item)">
                                        {{ item.discount_code }}
                                    </v-btn> 
                            </div>
                            <div class="text-sm p-2 mt-4" v-if="discount_note">
                                <div class="font-bold">{{ $t('Note') }}</div>
                                <div>{{ discount_note }}</div>
                            </div>
                        </div>
                    </v-col>
                    <v-col cols="12" v-if="categoryNoteName" md="6">
                        <ComInlineNote :category_note="categoryNoteName" v-model="discount_note"/>
                    </v-col>
                </v-row>
            </div>
        </template>
    </ComModal>
</template>
<script setup>
import { ref, defineEmits, createToaster, computed,i18n,inject } from '@/plugin'
import Enumerable from 'linq'
import ComInlineNote from '../../../components/ComInlineNote.vue';
import { useDisplay } from 'vuetify';
const gv = inject("$gv")
const { t: $t } = i18n.global; 

const sale = inject("$sale")
const selectedGroup = ref([])

const props = defineProps({
    params:Object
})


const revenueGroups = ref([...new Set(sale.sale.sale_products.map(item => item.revenue_group))])


const emit = defineEmits(['resolve'])
 
const { mobile } = useDisplay()


const toaster = createToaster({ position: "top-right" })

let discount_note = ref(props.params.data.discount_note)
let discount_type = ref(props.params.data.discount_type)
let discount = ref(props.params.data.discount_value)
let amount = ref(parseFloat(props.params.value))
let percent_manual = ref(0)

const discountCodes = computed(()=>{
    return Enumerable.from(props.params.data?.discount_codes).where(`$.discount_type=='${discount_type.value}'`).toArray();
})
const maxDiscountPercent = computed(()=>{
    if(props.params.data?.discount_codes){
        return Enumerable.from(props.params.data?.discount_codes).where(`$.discount_type=='Percent'`).max("$.discount_value").toFixed(4)
    }
    return ''
})
const discountAmount = computed(()=>{
    return (amount.value * maxDiscountPercent.value).toFixed(3)
})

const categoryNoteName = computed(()=>{
    return props.params.data?.category_note_name;
})
function manual_percent_discount(){
    gv.authorize("manual_percent_discount_required_password", "allow_manual_percent_discount").then((v) => {
        if (v) { 
            percent_manual.value = 1
        }
    })
}
function onClick(item){
    discount.value = (discount_type.value == 'Amount' ? 1 : 100) * item.discount_value;
}
function onClose() {
    emit('resolve',false)
}
function onOK(){
    let revenues = []
   
    if (selectedGroup.value.length>0){
        selectedGroup.value.forEach(i => {
            revenues.push(revenueGroups.value[i])
        });
        //check if revenue group select all
        if(selectedGroup.value.length == revenueGroups.value.length){
            revenues = [];
        }
    }

    if(discount.value <= 0){
        toaster.warning($t('msg.Discount percent or amount can not be small than zero'));
    }
    else if(discount_type.value == 'Amount' && Math.abs(discountAmount.value) < Math.abs(discount.value)){
        toaster.warning(`${$t('Max discount')} ${maxDiscountPercent.value * 100}% : ${discountAmount.value}$ `);
    }
    else if(discount_type.value == 'Percent' && Math.abs(discount.value)>100){
        toaster.warning($t('msg.Discount percent can not be greater than 100%'));
    }
    else if(categoryNoteName.value && !discount_note.value){
        toaster.warning($t('msg.Please select note'));
    }
    else{
 
        const result = {
            discount: discount.value,
            discount_type: discount_type.value,
            discount_note: discount_note.value,
            revenue_group: revenues
        }
        emit('resolve', result)
    }
}
 
</script>