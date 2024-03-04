<template>
    <ComModal @onClose="onClose(false)" :loading="true" :fullscreen="true" :hide-ok-button="true" :hide-close-button="true">
        <template #title>
            {{ params.title }}
        </template>



        <template #content>
            <div class="search-box my-0 mx-auto" :class="data.length > 0 ? 'w-full' : 'max-w-[350px]'">
                <ComInput autofocus keyboard variant="outlined" :placeholder="$t('Search...')"
                        prepend-inner-icon="mdi-magnify" v-model="keyword" v-debounce="onSearch" /> <br/>
                <template v-if="data.length > 0">
                    <v-row>
                        <v-col cols="3">
                            <div class="invs-det">
                                <v-select clearable chips label="Sort Order" :items="['Name', 'Product Name', 'Product Category']" multiple></v-select>
                            </div>
                        </v-col> 
                        <v-col cols="1">
                            <v-btn class="h-100 w-100">ASC</v-btn>
                        </v-col>
                        <v-col cols="1">
                            <v-btn class="h-100 w-100">DESC</v-btn>
                        </v-col>

                    </v-row>
                    <br/>
                    
                        
                    <hr>
                    <!-- {{ keyword }} -->
                    <v-table>
                        <thead>
                            <tr>
                                <th class="text-left">Photo</th>
                                <th class="text-left">Name</th>
                                <th class="text-left">Product Name</th> 
                                <th class="text-right">Price</th> 
                                <th class="text-left">Product Category</th> 
                                <th></th>
                            </tr> 
                        </thead>
                        <tbody>
                            <tr v-for="(p, index) in data" :key="index" >
                                <td class="text-left">
                                    <div class="">
                                        <div class="p-2">
                                            <v-img :width="50" :height="50" aspect-ratio="16/9" cover :src="p.photo"></v-img>
                                        </div>
                                    </div>
                                </td>
                                <td>{{ p.name }}</td>
                                <td style="max-width: 30rem;" class="overflow-hidden">
                                    <div class="elp-pro-name">
                                        <v-tooltip v-if="p.product_name_en != p.product_name_kh" :text="`${p.product_name_en}${p.product_name_kh}`">
                                            <template v-slot:activator="{ props }">
                                                <div class="elp-pro-name" v-bind="props">{{ p.product_name_en }} <template v-if="p.product_name_en != p.product_name_kh">{{ p.product_name_kh }}</template></div>
                                            </template>
                                        </v-tooltip>
                                        <v-tooltip v-else :text="`${p.product_name_en}`">
                                            <template v-slot:activator="{ props }">
                                                <div class="elp-pro-name" v-bind="props">{{ p.product_name_en }} <template v-if="p.product_name_en != p.product_name_kh">{{ p.product_name_kh }}</template></div>
                                            </template>
                                        </v-tooltip>
                                    </div>
                                </td>
                                <td class="text-right"><CurrencyFormat :value="p.price" /></td> 
                                <td>{{ p.product_category }}</td>
                                <td> 
                                    <v-btn>Select Product</v-btn>
                                </td>


                                
                                <!-- <hr> -->
                                <!-- {{ p }}  -->
                            </tr>
                        </tbody> 
                    </v-table> 
                </template>
            </div> 
            <div>  
                <template v-if="data.length > 0">
                    <div class="text-center">
                        <v-pagination
                        v-model="page"
                        :length="4"
                        rounded="circle"
                        ></v-pagination> 
                    </div> 
                </template>
            </div>
        </template>
    </ComModal>
</template>

<script setup>

import { inject, ref, computed, onUnmounted, reactive, i18n } from '@/plugin'
import { createToaster } from '@meforma/vue-toaster';
const gv = inject("$gv")
const frappe = inject('$frappe');
const db = frappe.db()
const data = ref([])
const { t: $t } = i18n.global;
const keyword = ref("")
const toaster = createToaster({ position: "top" })
const loading = ref(false)

const props = defineProps({
    params: {
        type: Object,
        require: true
    }
})

const emit = defineEmits(["resolve"])

function onSearch() {
    loading.value = true 
    db.getDocList('Product',{
        fields: ['name', 'product_name_en','product_name_kh','price',"photo","product_category",'prices'],
        orFilters:[
            ["name",'like','%' + keyword.value +"%"],
            ["product_name_en",'like','%' + keyword.value +"%"],
            ["product_name_kh",'like','%' + keyword.value +"%"],
            ["Product Price","barcode","like","%" + keyword.value + "%"]
        ] 
    })
        .then((docs) => {
            data.value = docs
            loading.value = true 

        })
        .catch((error) => console.error(error));

}

function onClose(isClose) {
    emit('resolve', isClose);
}



onUnmounted(() => {

})

</script>
<style>
    .elp-pro-name {
        width: 30rem;
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
    }
    .invs-det .v-input__details {
        display: none !important;
    }
</style>