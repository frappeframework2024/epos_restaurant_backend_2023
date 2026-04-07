<template>  
  <!-- template 2 -->
   <template v-if="is_loading">
    <h1>Loading..</h1>
   </template>
   <template v-else>
    <div v-if="template_menu=='top'">
        <SaleOrderTemplate1 :menu_categories="menu_categories" :menu_products="menu_products" />
    </div>
    <div v-else-if="template_menu=='left'">
        <SaleOrderTemplate2 :menu_categories="menu_categories" :menu_products="menu_products" />
    </div>
    </template>
</template>

<script setup>
  import { ref, inject, onMounted,i18n, useRoute, useRouter} from   '@/plugin';
  import SaleOrderTemplate1 from "@/views/sale_page/SaleOrderTemplate1.vue";
  import SaleOrderTemplate2 from "@/views/sale_page/SaleOrderTemplate2.vue";
  import { createToaster } from '@meforma/vue-toaster';
  import { useDisplay } from 'vuetify';

  const { t: $t } = i18n.global;
  const { mobile } = useDisplay();
  const sale = inject("$sale");
  const gv = inject("$gv");
  const socket = inject("$socket");
  const product = inject("$product"); 

  const frappe = inject("$frappe");

  const call = frappe.call(); 

  const route = useRoute();
  const router = useRouter();

  const toaster = createToaster({ position: "top-center" });
  

  //variables  
  const menu_categories = ref([]);
  const menu_products = ref([]);
  const is_loading = ref(true); 
  const template_menu = ref("left");

  onMounted(async ()=>{      
    is_loading.value = true;
    if(route.query.menu){ 
      template_menu.value = route.query.menu;        
    } 

    const resp = await call.post("epos_restaurant_2023.api.product.get_product_by_menu_1_level", {
      root_menu:"ePOS Menu",
      mobile : 0,
      sort_order_by : "product_name_en",
      sort_menu_order_by:"name"
    }); 
    if(resp.message){
      const data = resp.message;  
      menu_categories.value = data.menu_categories
      menu_products.value = data.menu_products 
    }   
    
    
    //private on mouted
    await _onMounted();

    is_loading.value= false;
  }); 


  async function _onMounted(){
          //check user 
        const make_order_auth = JSON.parse(localStorage.getItem('make_order_auth'));
        if (sale.getString(route.params.name) == "" || make_order_auth == undefined) {
          if(sale.getString(route.params.name) == ""){
            sale.newSale(); 
          }else{
            if (sale.sale.sale_status == undefined) {
                if (sale.setting.table_groups.length > 0) {
                    router.push({ name: 'TableLayout' });
                }
                else {
                    sale.newSale(); 
                }
            }
          }
        }

        let backup_sale = JSON.parse(JSON.stringify(sale.sale))  
  }



</script>

<style scoped>

</style>