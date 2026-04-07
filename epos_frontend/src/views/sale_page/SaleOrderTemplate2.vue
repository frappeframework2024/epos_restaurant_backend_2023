<template>
  <div class="main-layout">
    <div class="sidebarCategory">
       <div
        @click="filterCat('All')"
        :style="{
          padding: '8px 10px',
          margin: '8px 6px 0px 8px',
          borderRadius: '8px',
          fontSize: '13px',
          cursor: 'pointer',
          textAlign: 'center',
          background: activeCat === 'All' ? '#c0392b' : '#e5e5e5',
          color: activeCat === 'All' ? '#fff' : '#555',
          fontWeight: activeCat === 'All' ? '500' : '400',
          transition: 'background 0.15s',
          flexShrink: 0        
        }"
      >
    <div style="font-size: 22px; margin-bottom: 4px;">🍽️</div>
    {{ $t("All") }}
  </div>
  <div ref="sidebarScrollRef" style="overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 4px;">
    <div
      v-for="cat in categories.filter(c => c.name !== 'All')"
      :key="cat.name"
      :data-cat="cat.name"
      @click="filterCat(cat.name)"
      :style="{
        padding: '8px 10px',
        margin: '4px 6px 0px 8px',
        borderRadius: '8px',
        fontSize: '13px',
        cursor: 'pointer',
        textAlign: 'center',
        background: activeCat === cat.name ? '#c0392b' : (activeCat === 'All' && scrollCat === cat.name) ? 'rgba(192,57,43,0.15)' : 'transparent',
        color: activeCat === cat.name ? '#fff' : (activeCat === 'All' && scrollCat === cat.name) ? '#c0392b' : '#555',
        fontWeight: activeCat === cat.name ? '500' : '400',
        transition: 'background 0.15s'
      }"
    > 
      <img
        v-if="cat.photo"
        :src="cat.photo || cat.emoji"
        :alt="cat.name"
        style="width: 40px; height: 40px; object-fit: contain; border-radius: 50%; margin-bottom: 4px; display: block; margin-left: auto; margin-right: auto;"
      />
      <div v-else style="font-size: 22px; margin-bottom: 4px;">{{ cat.emoji }}</div>

      {{getMenuName(cat)}}
    </div>
  </div>
  <div style="height: 1px; background: #e0e0e0; margin: 4px 0; flex-shrink: 0;"></div>
    </div>
    <div ref="contentRef" @scroll="onScroll" style="flex: 1; overflow-y: auto;  min-width: 0; padding-bottom: 5px;">
        <div 
          style=" position: sticky;
          display: flex;
          justify-content: space-between;
          top: 0;
          background: #fdfdfd;
          z-index: 10;
          color: #ff0000;
          font-size: 18px;
          /* 👇 add this */
          box-shadow: 0 4px 20px  rgb(117 117 117 / 22%);
          "
          class="p-3"
          >
          <div>
            {{scrollCat }}
          </div>

          <div>
            <div class="cart-icon" @click="onViewDetail">
            <v-badge :content="totalItems" :model-value="totalItems > 0" color="#b91c1c">
                <v-icon size="28">mdi-cart-plus</v-icon>
            </v-badge>
            </div>
          </div>
                
        </div>
      
      <div v-for="cat in filteredCategories" :key="cat.name" :id="'section-' + cat.name" style="margin-bottom: 0px;padding: 12px;">       
        <div
          v-if="cat.name !== 'all' && cat.name != scrollCat"
          style="font-size: 18px; font-weight: bold; color: #888; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #e0e0e0;"
        >
          {{getMenuName(cat) }}
        </div>

        <div>
           <ComProductCard :productsByCategory="productsByCategory(cat.name)" :onProductClick="onMenuProductClick" />
        </div>
      </div>
      
    </div>
  </div>

 <div v-if="screenWidth < 768" class="footer-payment">
    <ComSmallAddSale />
  </div>
</template>

<script setup>
import { ref, i18n,computed,inject,onMounted,smallViewSaleProductListModal } from '@/plugin'
import ComProductCard from "../../views/sale_page/components/ComProductCard.vue"
import ComSmallAddSale from "@/views/sale/components/mobile_screen/ComSmallAddSale.vue";

import { useDialog } from 'primevue/usedialog';
import {onSelectProduct} from "@/utils/sale.js";

const { t: $t } = i18n.global;
const dialog = useDialog();

const activeCat = ref('All')
const contentRef = ref(null)
const sidebarScrollRef = ref(null)
const scrollCat = ref('All')
const categories = ref([])
const products = ref([])

const screenWidth = ref(window.innerWidth);

const sale = inject("$sale");
const product = inject("$product");

const props = defineProps({
  menu_categories: Object,
  menu_products: Object,
});

let isMenuItemClick = false;


// filterCategory
const filteredCategories = computed(() => {
  if (activeCat.value === 'All') {
    return categories.value.filter(c => c.name !== 'All')
  }


  return categories.value.filter(c => c.name === activeCat.value)
})

// handle scroll
function onScroll() {
  if (activeCat.value !== 'All') return

  const container = contentRef.value
  if (!container) return

  const THRESHOLD = 80
  const containerTop = container.getBoundingClientRect().top
  let current = ''

  for (const cat of categories.value.filter(c => c.name !== 'All')) {
    const el = document.getElementById('section-' + cat.name)
    if (!el) continue
    const elTop = el.getBoundingClientRect().top - containerTop
    if (elTop <= THRESHOLD) current = cat.name
  }

  scrollCat.value = current

  const sidebar = sidebarScrollRef.value
  const activeEl = sidebar?.querySelector(`[data-cat="${current}"]`)
 
  if (activeEl && sidebar) {
    const scrollTop = activeEl.offsetTop - sidebar.clientHeight / 2 + activeEl.offsetHeight / 2
    sidebar.scrollTo({ top: scrollTop, behavior: 'smooth' })
  }
}

const productsByCategory = (menu) => products.value.filter(p => p.parent === menu)

function filterCat(val) {
  activeCat.value = val;  
  scrollCat.value = val;
  
  // Scroll to section when clicking a category
  if (val !== 'All') {
    const el = document.getElementById('section-' + val)
    if (el && contentRef.value) {
      contentRef.value.scrollTo({ top: el.offsetTop - 10, behavior: 'smooth' })
    }


  } else {
    contentRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

onMounted(() => {
  categories.value =  props.menu_categories.map(c => ({
      ...c,
      emoji: '🍽️'
    }))
 

  products.value = [...props.menu_products]

  window.addEventListener("resize", () => {
        screenWidth.value = window.innerWidth;
    });
})

async function onMenuProductClick(data) { 
    if(isMenuItemClick){
        return
    }

    try{
        isMenuItemClick = true;
        await onSelectProduct(data,sale,product,dialog)
    }
    finally{
        isMenuItemClick = false;
    }

  
   
    
}


function getMenuName(menu){
  return menu.name_en
}




const checkNewSaleNoSaleProducts = computed(()=>{
    if((sale.sale.name||'')=='' && (sale.sale.sale_products||[]).length <=0){
        return true;
    } 
    return false;
    
})

async function onViewDetail(){
    if(checkNewSaleNoSaleProducts.value){
        toaster.warning( $t('msg.Please select a menu item to continue'));
       
        return;
    }
    const result = await smallViewSaleProductListModal ({title: sale.sale.name, value:  ''});
}




</script>

<style scoped>

.main-layout{
  display: flex; 
  height: calc(100vh - 65px); 
  overflow: hidden;
}

.sidebarCategory{
    width: 180px; 
    min-width: 180px; 
    background: #f5f5f5; 
    /* border-right: 1px solid #e0e0e0;  */
    overflow: hidden; 
    
    display: flex; 
    flex-direction: column; 
    gap: 4px;
    box-shadow: 4px 0 20px rgb(117 117 117 / 22%);
}

/* Desktop: auto-fill with min 130px → many columns */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
}

/* Mobile: exactly 2 columns */
@media (max-width: 600px) {

  .main-layout{ 
    height: calc(100vh - 150px);  
  }

  .sidebarCategory{
      width: 100px; 
      min-width: 100px; 
      background: #f5f5f5;  
      overflow-y: auto;  
      padding: 0px;
      margin: 0px;
      display: flex; 
      flex-direction: column; 
      gap: 4px;
      box-shadow: 4px 0 20px rgb(117 117 117 / 22%);
  }
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  } 

  .footer-payment {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: white;
    z-index: 40;
    border-top: 1px solid #e5e7eb;
    padding: 0 16px;
    display: flex;
    align-items: center;
  }

}

.product-card {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: border-color 0.15s;
}
</style>