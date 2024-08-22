<template>
    <ComDialogContent :hideButtonClose="false" :loading="loading" @onOK="onOK" @onClose="onClose">
    <div class="flex flex-col lg:flex-row">
        <div v-if="data?.photo" class="flex">
            <v-img class="rounded" style="box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;" :lazy-src="data.photo" :width="500" aspect-ratio="4/3" cover :src="data.photo"></v-img>
        </div>
        <div class="md:px-5 w-100">
            <div class="border rounded-md w-100 p-3" style="border-color: #ccc !important;background: aliceblue;">
                <template v-if="data?.variants" v-for="(item, index) in data.variants" :key="index">
                    <h1 v-if="item?.variants.length > 0" class="mb-2 font-semibold">{{ item.variant_name }}</h1>
                    <ul class="d-flex gap-2"> 
                        <li style="cursor:pointer;border-radius: 9999px !important;" :class="i.selected? 'bg-black text-white px-2' : 'px-2'" @click="getItemsVariant(index,item,i )" v-if="item?.variants" v-for="i in item.variants">{{ i.variant }}</li>
                    </ul>
                    <br/>
                </template>
            </div>
            <br/>
            <div class="border rounded-md w-100 p-3" style="border-color: #ccc !important;background: aliceblue;">
                <!-- {{ prices }} -->
                <ul class="d-flex gap-2" v-if="data?.prices.length > 0">
                    <template  v-for="(item, index) in data?.prices" :key="index">
                        <li style="cursor:pointer;border-radius: 9999px !important;" :class="item.selected? 'bg-black text-white px-2' : 'px-2'">
                            {{ item.portion }} <CurrencyFormat :value="item.price" />
                        </li>
                    </template>
                </ul>
            </div>
        </div>
    </div> 
</ComDialogContent>
</template>

<script setup>
    import { VDataTable } from 'vuetify/labs/VDataTable'
   import {ref,inject, onMounted ,postApi, computed ,createToaster,getApi} from "@/plugin"
   import ComDialogContent from "@/components/ComDialogContent.vue"
   const dialogRef = inject('dialogRef');
   const data = ref()
   const selectedData = ref({})
   const toaster = createToaster({ position: 'top-right' })
    const saleProduct = ref()
    const sale= inject("$sale")
    const prices = ref()
    const selected =  ref([])


   const loading = ref(false)
    onMounted(()=>{
        loading.value = true
        getApi("product.get_product_option",{
            product_code:dialogRef.value.data.product_code,
            business_branch:sale.sale.business_branch,
            price_rule:sale.sale.price_rule
        }).then(result=>{
            data.value = result.message
            prices.value = data.value.prices
            console.log(prices.value)

            if(dialogRef.value.data.sale_product){
            
            saleProduct.value =  dialogRef.value.data.sale_product
            selectedData.value = saleProduct.value.selected_variant
            data.value.variants.forEach((r, index)=>{

               
                    r.variants.find(r=>r.variant==selectedData.value["variant_" + (index + 1)].variant_value).selected = true
    
            })
            
        }

            loading.value = false
        }).catch(error=>{
            loading.value = false
        })
        

      
        
    })

   

    function getItemsVariant(index,variant, i) {

        selectedData.value['variant_' + (index + 1)] = {variant_name:variant.variant_name,variant_value: i.variant}
        data.value.variants[index].variants.filter(r=>r.selected).forEach(x=>x.selected=false)
        i.selected = true
         

    }
    function onOK(){  
        if (data.value.variants.flatMap(item => item.variants).filter(r=>r.selected).length!=data.value.variants.length) {
            toaster.warning("Please select all variant")
            return
        }
        loading.value = true
        postApi("product.get_product_by_variant",{
            variant: selectedData.value,
            product_code: data.value.variant_of?data.value.variant_of:data.value.name
        }).then((r)=>{
          
            r.message.selected_variant = selectedData.value
            const selected_price = data.value.prices.find(r=>r.selected)

            
            r.message.unit = selected_price.unit
            r.message.price = selected_price.price
            r.message.portion = selected_price.portion

            dialogRef.value.close(r.message)
            loading.value = false
            
        }).catch(error=>{
            loading.value = false
        })
    }
    const onClose = () => {
        dialogRef.value.close()
    }



</script>
<style scoped>
    ul li {
        border: 1px solid #ccc;
        padding: 5px;
        border-radius: 5px;
    }
    ul li.active {
        background: #000;
        color: #fff;
    }
</style>