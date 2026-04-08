<template>  
    <div class="category-wrapper">  
        <div class="category-row">
            <div class="category-bar">
            <button
                v-for="cat in categories"
                :key="cat.name"
                @click="scrollToCategory(cat.name)"
                :class="['category-pill', activeCategory === cat.name ? 'active' : '']"
            >
                {{ cat.name_en }}
            </button>
            </div>
            <div class="cart-icon" @click="showCart = true">
            <v-badge :content="(sale.sale.total_quantity||0)" :model-value="(sale.sale.total_quantity||0) > 0" color="#b91c1c" @click="onViewDetail">
                <v-icon size="28">mdi-cart-plus</v-icon>
            </v-badge>
            </div>
        </div>
    </div>

    
  <div class="products-container" ref="containerRef" @scroll="onScroll">
    <template v-if="!product.searchProductKeyword">
      <div
        v-for="menu in categories"
        :key="menu.name"
        :id="'section-' + menu.name"
        class="category-section"
      >
        <h2 class="section-title">{{ menu.name_en }}</h2>
        <!-- Product Cards -->  
        <ComProductCard :productsByCategory ="productsByCategory(menu.name)" :onProductClick="onMenuProductClick"/>  
      </div>
    </template>

    <template v-else>
      <div class="mt-5">
      <ComSearchProductCard class="" :products="searchedProducts" :onProductClick="onMenuProductClick" />
      </div>
    </template>

    <ComScrollToTop :target="containerRef" />
  </div>

  <div v-if="screenWidth < 768" class="footer-payment">
    <ComSmallAddSale />
  </div>
</template>

<script setup>
import { ref,inject, computed, nextTick,onMounted,smallViewSaleProductListModal} from '@/plugin';
import ComSmallAddSale from "@/views/sale/components/mobile_screen/ComSmallAddSale.vue";
import ComProductCard from "@/views/sale_page/components/ComProductCard.vue";
import { useDialog } from 'primevue/usedialog';
import {onSelectProduct} from "@/utils/sale.js";
import ComScrollToTop from "../../views/sale_page/components/ComScrollToTop.vue"

import ComSearchProductCard from "../../views/sale_page/components/ComSearchProductCard.vue"


const sale = inject("$sale");
const product = inject("$product");

const props = defineProps({
    menu_categories: Object,
    menu_products:Object,
});  

//variables
const dialog = useDialog();

const categories = ref([])
const products = ref([])

const cart = ref([])
const showCart = ref(false)
const screenWidth = ref(window.innerWidth);
 
const activeCategory = ref("");
const containerRef = ref(null);


const searchedProducts = computed(() => {
  return categories.value
    .filter(c => c.name !== 'All')
    .flatMap(cat => productsByCategory(cat.name))
})


// Flag to suppress onScroll updates while a programmatic scroll is in flight
let isScrollingProgrammatically = false
// const CATEGORY_BAR_HEIGHT = 56 // px — height of .category-bar
const CATEGORY_BAR_HEIGHT = 0 // px — height of .category-bar
let isMenuItemClick = false;

onMounted(()=>{ 
    categories.value = [...props.menu_categories]
    products.value = [...props.menu_products]
    activeCategory.value = props.menu_categories[0]?.name
    window.addEventListener("resize", () => {
        screenWidth.value = window.innerWidth;
    });

    const bar = document.querySelector('.category-bar')
  if (!bar) return

  // --- Mouse drag (desktop) ---
  let isDown = false
  let startX, scrollLeft

  bar.addEventListener('mousedown', (e) => {
    isDown = true
    startX = e.pageX - bar.offsetLeft
    scrollLeft = bar.scrollLeft
  })
  bar.addEventListener('mouseleave', () => isDown = false)
  bar.addEventListener('mouseup', () => isDown = false)
  bar.addEventListener('mousemove', (e) => {
    if (!isDown) return
    e.preventDefault()
    const x = e.pageX - bar.offsetLeft
    bar.scrollLeft = scrollLeft - (x - startX)
  })

  // --- Touch drag (mobile) ---
  let touchStartX = 0
  let touchScrollLeft = 0

  bar.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].pageX
    touchScrollLeft = bar.scrollLeft
  }, { passive: true })

  bar.addEventListener('touchmove', (e) => {
    const x = e.touches[0].pageX
    bar.scrollLeft = touchScrollLeft - (x - touchStartX)
  }, { passive: true })
})

const productsByCategory = (menu) =>{
  if(product.searchProductKeyword){
    let k = product.searchProductKeyword.toLowerCase()
    return products.value.filter(p => p.parent === menu  &&  [p.name_en, p.name_kh, p.name].some(name => name?.toLowerCase().includes(k))) 
  }
  return products.value.filter(p => p.parent === menu)
} 

const scrollToCategory = (menu) => {
  activeCategory.value = menu
  const el = document.getElementById('section-' + menu)
  if (!el || !containerRef.value) return

  isScrollingProgrammatically = true

  // Scroll the container so the section top lands just below the category bar
  const container = containerRef.value
  const containerTop = container.getBoundingClientRect().top
  const elTop = el.getBoundingClientRect().top
  const offset = elTop - containerTop - CATEGORY_BAR_HEIGHT + container.scrollTop

  container.scrollTo({ top: offset, behavior: 'smooth' })

  // Re-enable onScroll tracking after animation completes (~600ms)
  setTimeout(() => { isScrollingProgrammatically = false }, 700)
}

const onScroll = () => {
  if (isScrollingProgrammatically) return
  const container = containerRef.value
  if (!container) return

  const containerTop = container.getBoundingClientRect().top
  // Threshold: a section is "active" once its top edge reaches within
  // header (64px) + category bar (56px) = 120px from viewport top
  // const THRESHOLD = 120
  // const THRESHOLD = 80
  const THRESHOLD = 0

  let current = props.menu_categories[0].value

  for (const menu of props.menu_categories) {
    const el = document.getElementById('section-' + menu.name)
    if (!el) continue

    // ✅ Use viewport-relative position so it works regardless of parent offsets
    const elTop = el.getBoundingClientRect().top
    const relativeTop = elTop - containerTop

    if (relativeTop <= THRESHOLD) {
      current = menu.name
    }
  }

  activeCategory.value = current

  // Scroll the category pills bar to keep active pill centered
  nextTick(() => {
    const categoryBar = document.querySelector('.category-bar')
    const activeBtn = categoryBar?.querySelector('.category-pill.active')

    if (activeBtn && categoryBar) {
      const btnLeft = activeBtn.offsetLeft
      const btnWidth = activeBtn.offsetWidth
      const barWidth = categoryBar.clientWidth

      // Scroll so active pill is centered in the bar
      const scrollLeft = btnLeft - (barWidth / 2) + (btnWidth / 2)
      categoryBar.scrollTo({ left: scrollLeft, behavior: 'smooth' })
    }
  })
}

async function onMenuProductClick(data) { 
    if(isMenuItemClick){
        return
    }

    isMenuItemClick = true;
    await onSelectProduct(data,sale,product,dialog)
    isMenuItemClick = false;
    
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
.category-pill {
  flex-shrink: 0;
  white-space: nowrap;
  padding: 6px 18px;
  border-radius: 9999px;
  border: 1px solid #d1d5db;
  background: #fff;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.category-pill:hover {
  border-color: #b91c1c;
  color: #b91c1c;
}
.category-pill.active {
  background: #b91c1c;
  color: #fff;
  border-color: #b91c1c;
}

/* Scrollable products area — sits below POS header (64px) + category bar (56px) */
.products-container {
  margin-top: 60px ;
  height: calc(100vh - 125px);
  overflow-y: auto;
  padding: 0 16px 30px;
}

/* Section */
.category-section {
  padding-top: 24px;
  scroll-margin-top: 10px;
  user-select: none;
}
.section-title {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #fee2e2;
}

/* Grid */
@media (min-width: 768px)  { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px)  {

  .products-container {
  
  height: calc(100vh - 60px);
  padding: 0 16px 100px;
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
@media (min-width: 1024px) { .products-grid { grid-template-columns: repeat(4, 1fr); } }

.category-wrapper {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  z-index: 40;
  touch-action: pan-x;
  overflow: hidden;
}

.category-row {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 10px 0px 15px 0px;
  overflow: hidden;   /* add this to prevent bleed */
  min-width: 0;     
  touch-action: pan-x;  
}

.category-bar {
  /* background-color: green!important; */
  display: flex;
  gap: 10px;
  overflow-x: auto;
   overflow-y: hidden;
  padding-left: 16px;
  scrollbar-width: none;
  user-select: none;
   cursor: grab;             /* add this */
  -webkit-overflow-scrolling: touch; /* smooth on iOS */
  touch-action: pan-x; 
}
.category-bar:active {
  cursor: grabbing;         /* add this */
}

.category-bar::-webkit-scrollbar {
  display: none;
}

.cart-icon {
  padding: 0 16px;
  cursor: pointer;
  margin-right: 10px;
}
</style>