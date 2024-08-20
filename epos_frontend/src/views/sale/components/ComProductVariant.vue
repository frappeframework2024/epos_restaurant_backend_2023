<template>
    <ComDialogContent :hideButtonClose="false" :loading="loading" @onOK="onOK" @onClose="onClose">
    <div class="flex flex-col md:flex-row">
        <div v-if="data?.photo" class="flex">
            <v-img :lazy-src="data.photo" :width="350" cover :src="data.photo"></v-img>
        </div>
        <div class="pl-5" cols="8" md="6" sm="12">
            <template v-if="data?.variant" v-for="(item, index) in data.variant" :key="index">
                <h1 v-if="item?.variants.length > 0" class="mb-2 font-semibold">{{ item.variant_name }}</h1>
                <ul class="d-flex gap-2"> 
                    <li style="cursor:pointer;" :class="i.selected? 'bg-black text-white' : ''" @click="getItemsVariant(index,item,i )" v-if="item?.variants" v-for="i in item.variants">{{ i.variant }}</li>
                </ul>
                <br/>
            </template>
        </div>
    </div> 
</ComDialogContent>
</template>

<script setup>
   import {ref,inject, onMounted ,postApi, computed ,createToaster} from "@/plugin"
   import ComDialogContent from "@/components/ComDialogContent.vue"
   const dialogRef = inject('dialogRef');
   const data = ref()
   const selectedData = ref({})
   const toaster = createToaster({ position: 'top-right' })
 
   const loading = ref(false)
    onMounted(()=>{
        data.value = dialogRef.value.data
    })

   

    function getItemsVariant(index,variant, i) {

        selectedData.value['variant_' + (index + 1)] = {variant_name:variant.variant_name,variant_value: i.variant}
        data.value.variant[index].variants.filter(r=>r.selected).forEach(x=>x.selected=false)
        i.selected = true
         

    }
    function onOK(){
  
        if (data.value.variants.flatMap(item => item.variants).filter(r=>r.selected).length!=data.value.variant.length) {
            toaster.warning("Please select all variant")
            return
        }
        loading.value = true
        postApi("product.get_product_by_variant",{
            variant: selectedData.value,
            product_code: data.value.name
        }).then((r)=>{
            r.message.selected_variant = selectedData.value
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