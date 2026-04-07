<template>  
    <div class="category-wrapper">  
        <!-- Categories Pills + Cart -->
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
            <v-badge :content="totalItems" :model-value="totalItems > 0" color="#b91c1c">
                <v-icon size="28">mdi-cart-plus</v-icon>
            </v-badge>
            </div>
        </div>
    </div>

  <div class="products-container" ref="containerRef" @scroll="onScroll">
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
  </div>

  <div v-if="screenWidth < 768" class="footer-payment">
    <ComSmallAddSale />
  </div>
</template>

<script setup>
import { ref,inject, computed, nextTick,onMounted} from '@/plugin';
import ComSmallAddSale from "@/views/sale/components/mobile_screen/ComSmallAddSale.vue";
import ComProductCard from "@/views/sale_page/components/ComProductCard.vue";
import { useDialog } from 'primevue/usedialog';
import {onSelectProduct} from "@/utils/sale.js";


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


// Flag to suppress onScroll updates while a programmatic scroll is in flight
let isScrollingProgrammatically = false
const CATEGORY_BAR_HEIGHT = 56 // px — height of .category-bar
let isMenuItemClick = false;

onMounted(()=>{ 
    categories.value = [...props.menu_categories]
    products.value = [...props.menu_products]
    activeCategory.value = props.menu_categories[0]?.name
    window.addEventListener("resize", () => {
        screenWidth.value = window.innerWidth;
    });
})

 



const productsByCategory = (menu) => products.value.filter(p => p.parent === menu);

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
  const THRESHOLD = 80

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


const totalItems = computed(() =>
  cart.value.reduce((sum, item) => sum + item.qty, 0)
)


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
  margin-top: 60px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 0 16px 110px;
  /* padding: 0 16px 120px; */
}

/* Section */
.category-section {
  padding-top: 24px;
  scroll-margin-top: 120px;
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
    margin-top: 60px;
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
}

.category-row {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  height: 56px;
}

.category-bar {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-left: 16px;
  scrollbar-width: none;
  user-select: none;
}

.category-bar::-webkit-scrollbar {
  display: none;
}

.cart-icon {
  padding: 0 16px;
  cursor: pointer;
}
</style>