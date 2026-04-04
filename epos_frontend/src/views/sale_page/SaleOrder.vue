<template>
<div class="category-wrapper">
  <!-- Mobile Banner (only on small screens) -->
  <div v-if="screenWidth < 768" class="mobile-banner">
    <ComProductSearch />
  </div>

  <!-- Categories Pills + Cart -->
  <div class="category-row">
    <div class="category-bar">
      <button
        v-for="cat in categories"
        :key="cat.value"
        @click="scrollToCategory(cat.value)"
        :class="['category-pill', activeCategory === cat.value ? 'active' : '']"
      >
        {{ cat.name }}
      </button>
    </div>
    <div class="cart-icon" @click="showCart = true">
      <v-badge :content="totalItems" :model-value="totalItems > 0" color="#b91c1c">
        <v-icon size="28">mdi-cart-plus</v-icon>
      </v-badge>
    </div>
  </div>
</div>

  <!-- Products Grid -->
  <div class="products-container" ref="containerRef" @scroll="onScroll">
    <div
      v-for="cat in realCategories"
      :key="cat.value"
      :id="'section-' + cat.value"
      class="category-section"
    >
      <h2 class="section-title">{{ cat.name }}</h2>
      <div class="products-grid">
        <div
          v-for="prod in productsByCategory(cat.value)"
          :key="prod.name"
          class="product-card"
          @click="addToOrder(prod)"
        >

        <div class="eye-icon" @click.stop="previewProduct = prod">
              <v-icon>mdi-eye</v-icon>
            </div>
          <div class="product-image">
           
            
            <img v-if="prod.image" :src="prod.image" :alt="prod.name" />
            <div v-else class="image-placeholder">
              <span>{{ prod.emoji || '🍽️' }}</span>
            </div>
          </div>
           
          <div class="product-info">
            <div class="product-name">{{ prod.name }}</div>
            <div class="product-price flex items-center">${{ prod.price.toFixed(2) }} 
              <span class="ml-1" v-if="prod.price_2 > 0">
                <v-icon>mdi-arrow-right</v-icon>
                <i class="pi pi-check"></i>
                 ${{ prod.price_2.toFixed(2) }}
              </span>  
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-if="previewProduct" class="image-overlay" @click="previewProduct = null">
    <div class="image-popup" @click.stop>
      <button class="close-btn" @click="previewProduct = null">✕</button>
      <img v-if="previewProduct.image" :src="previewProduct.image" :alt="previewProduct.name" />
      <div v-else class="popup-placeholder">
        <span>{{ previewProduct.emoji || '🍽️' }}</span>
      </div>
    </div>
</div>
  <div v-if="screenWidth < 768" class="footer-payment">
    <ComProductSearch />
  </div>
</template>

<script setup>
import { ref, computed, nextTick,onMounted } from 'vue'
import ComProductSearch from "../../views/sale/components/ComProductSearch.vue"

const previewProduct = ref(null)
const cart = ref([])
const showCart = ref(false)
const screenWidth = ref(window.innerWidth);


const categories = ref([
  { name: "Main Course", value: "main_course" },
  { name: "Snacks", value: "snacks" },
  { name: "Salad & Seafood", value: "salad_seafood" },
  { name: "Soups", value: "soups" },
  { name: "Noodles", value: "noodles" },
  { name: "Rice Dishes", value: "rice_dishes" },
  { name: "Grill & BBQ", value: "grill_bbq" },
  { name: "Fast Food", value: "fast_food" },
  { name: "Desserts", value: "desserts" },
  { name: "Drinks", value: "drinks" },
  { name: "Coffee", value: "coffee" },
  { name: "Milk Tea", value: "milk_tea" },
  { name: "Smoothies", value: "smoothies" },
  { name: "Ice Cream", value: "ice_cream" },
  { name: "Bakery", value: "bakery" }
])

const realCategories = computed(() => categories.value)

const products = ref([

  // MAIN COURSE
  { name: "Fried Rice", category: "main_course", price: 3.5, price_2: 4, emoji: "🍚", image: "" },
  { name: "Beef Steak", category: "main_course", price: 6, price_2: 0, emoji: "🥩", image: "" },
  { name: "Grilled Chicken", category: "main_course", price: 5, price_2: 6, emoji: "🍗", image: "" },
  { name: "Roasted Duck", category: "main_course", price: 7, price_2: 8, emoji: "🦆", image: "" },

  // SNACKS
  { name: "French Fries", category: "snacks", price: 2.5, price_2: 3, emoji: "🍟", image: "" },
  { name: "Chicken Nuggets", category: "snacks", price: 3, price_2: 3.5, emoji: "🍗", image: "" },
  { name: "Onion Rings", category: "snacks", price: 2.8, price_2: 0, emoji: "🧅", image: "" },
  { name: "Spring Rolls", category: "snacks", price: 2.2, price_2: 2.5, emoji: "🥟", image: "" },

  // SALAD
  { name: "Seafood Salad", category: "salad_seafood", price: 4, price_2: 0, emoji: "🥗", image: "" },
  { name: "Shrimp Salad", category: "salad_seafood", price: 4.5, price_2: 5.5, emoji: "🍤", image: "" },
  { name: "Tuna Salad", category: "salad_seafood", price: 4.2, price_2: 0, emoji: "🐟", image: "" },

  // SOUPS
  { name: "Chicken Soup", category: "soups", price: 3, price_2: 0, emoji: "🍲", image: "" },
  { name: "Tom Yum", category: "soups", price: 4, price_2: 4.5, emoji: "🍜", image: "" },
  { name: "Seafood Soup", category: "soups", price: 4.8, price_2: 5.5, emoji: "🦐", image: "" },

  // NOODLES
  { name: "Pad Thai", category: "noodles", price: 4, price_2: 0, emoji: "🍜", image: "" },
  { name: "Beef Noodles", category: "noodles", price: 4.5, price_2: 5, emoji: "🍜", image: "" },
  { name: "Chicken Noodles", category: "noodles", price: 4.2, price_2: 0, emoji: "🍜", image: "" },

  // RICE
  { name: "Chicken Fried Rice", category: "rice_dishes", price: 3.8, price_2: 4.2, emoji: "🍛", image: "" },
  { name: "Pineapple Fried Rice", category: "rice_dishes", price: 4.5, price_2: 0, emoji: "🍍", image: "" },
  { name: "Seafood Fried Rice", category: "rice_dishes", price: 5, price_2: 6, emoji: "🦐", image: "" },

  // BBQ
  { name: "BBQ Pork", category: "grill_bbq", price: 6, price_2: 7, emoji: "🍖", image: "" },
  { name: "Grilled Shrimp", category: "grill_bbq", price: 7, price_2: 8, emoji: "🦐", image: "" },
  { name: "BBQ Chicken Wings", category: "grill_bbq", price: 5, price_2: 6, emoji: "🍗", image: "" },

  // FAST FOOD
  { name: "Cheese Burger", category: "fast_food", price: 4, price_2: 4.5, emoji: "🍔", image: "" },
  { name: "Hot Dog", category: "fast_food", price: 3, price_2: 3.5, emoji: "🌭", image: "" },
  { name: "Pizza Slice", category: "fast_food", price: 3.5, price_2: 4, emoji: "🍕", image: "" },

  // DESSERT
  { name: "Chocolate Cake", category: "desserts", price: 3, price_2: 3.5, emoji: "🍰", image: "" },
  { name: "Pancake", category: "desserts", price: 2.8, price_2: 3.2, emoji: "🥞", image: "" },
  { name: "Fruit Plate", category: "desserts", price: 3.5, price_2: 4, emoji: "🍉", image: "" },

  // DRINKS
  { name: "Coca Cola", category: "drinks", price: 1.5, price_2: 2, emoji: "🥤", image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYFwqjs7rZBIsuMTFPArhmPuaHaK5b-bbQEQ&s" },
  { name: "Orange Juice", category: "drinks", price: 2.5, price_2: 3, emoji: "🍊", image: "" },
  { name: "Lemon Tea", category: "drinks", price: 2, price_2: 2.5, emoji: "🍋", image: "" },

  // COFFEE
  { name: "Americano", category: "coffee", price: 2, price_2: 2.5, emoji: "☕", image: "" },
  { name: "Latte", category: "coffee", price: 2.8, price_2: 3.5, emoji: "☕", image: "" },
  { name: "Cappuccino", category: "coffee", price: 3, price_2: 3.8, emoji: "☕", image: "" },

  // MILK TEA
  { name: "Classic Milk Tea", category: "milk_tea", price: 2.5, price_2: 3, emoji: "🧋", image: "https://img.freepik.com/free-photo/top-view-table-full-food_23-2149209253.jpg?semt=ais_incoming&w=740&q=80" },
  { name: "Brown Sugar Milk Tea", category: "milk_tea", price: 3, price_2: 3.5, emoji: "🧋", image: "" },

  // SMOOTHIES
  { name: "Mango Smoothie", category: "smoothies", price: 3, price_2: 3.5, emoji: "🥭", image: "" },
  { name: "Avocado Smoothie", category: "smoothies", price: 3.2, price_2: 3.8, emoji: "🥑", image: "" },
  { name: "Strawberry Smoothie", category: "smoothies", price: 3, price_2: 3.6, emoji: "🍓", image: "" },

  // ICE CREAM
  { name: "Vanilla Ice Cream", category: "ice_cream", price: 2, price_2: 2.5, emoji: "🍨", image: "https://www.allrecipes.com/thmb/xA0NsqO_lNpSFT3wsgw4LEgzJmM=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/AR-RM-233928-how-to-make-vanilla-ice-cream-ddmfs-3x4-c5b61f092fe14296b52ca364b1446800.jpg" },
  { name: "Chocolate Ice Cream", category: "ice_cream", price: 2.2, price_2: 2.8, emoji: "🍦", image: "" },

  // BAKERY
  { name: "Croissant", category: "bakery", price: 2.5, price_2: 3, emoji: "🥐", image: "" },
  { name: "Donut", category: "bakery", price: 1.8, price_2: 2.2, emoji: "🍩", image: "" },
  { name: "Baguette", category: "bakery", price: 2, price_2: 2.5, emoji: "🥖", image: "" }

])

const activeCategory = ref('main_course')
const containerRef = ref(null)

// Flag to suppress onScroll updates while a programmatic scroll is in flight
let isScrollingProgrammatically = false

const productsByCategory = (catValue) =>
  products.value.filter(p => p.category === catValue)

const CATEGORY_BAR_HEIGHT = 56 // px — height of .category-bar

const scrollToCategory = (catValue) => {
  activeCategory.value = catValue

  const el = document.getElementById('section-' + catValue)
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

  let current = realCategories.value[0].value

  for (const cat of realCategories.value) {
    const el = document.getElementById('section-' + cat.value)
    if (!el) continue

    // ✅ Use viewport-relative position so it works regardless of parent offsets
    const elTop = el.getBoundingClientRect().top
    const relativeTop = elTop - containerTop

    if (relativeTop <= THRESHOLD) {
      current = cat.value
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

function addToOrder(prod){
   const existing = cart.value.find(item => item.name === prod.name)
  if (existing) {
    existing.qty += 1
  } else {
    cart.value.push({ ...prod, qty: 1 })
  }
}

const totalItems = computed(() =>
  cart.value.reduce((sum, item) => sum + item.qty, 0)
)


onMounted(() => {
  window.addEventListener("resize", () => {
    screenWidth.value = window.innerWidth;
  });
});

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
.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
@media (min-width: 768px)  { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px)  {

  .products-container {
    margin-top: 100px;
  height: calc(100vh - 100px);
  padding: 0 16px 10px;
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

/* Card */
.product-card {
  position: relative;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}
.product-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}
.product-card:active {
  transform: scale(0.97);
}

/* Image area */
.product-image {
  width: 100%;
  height: 130px;
  overflow: hidden;
  background: #f9fafb;
}
.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.product-card:hover .product-image img {
  transform: scale(1.06);
}
.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  background: linear-gradient(135deg, #fee2e2, #fef2f2);
}

/* Info */
.product-info {
  padding: 10px 12px 12px;
}
.product-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 4px;
}
.product-price {
  font-size: 15px;
  font-weight: 700;
  color: #b91c1c;
}

.eye-icon {
  position: absolute;
  top: 5px;
    right: 10px;
  z-index: 1;
}
.eye-icon .v-icon {
  color: #ef0c0c;
 
}

.image-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-popup {
  position: relative;
  width: 320px;
  border-radius: 12px;
  overflow: hidden;
  background: #000;
}

.image-popup img {
  width: 100%;
  height: 320px;
  object-fit: cover;
  display: block;
}

.popup-placeholder {
  width: 100%;
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80px;
  background: linear-gradient(135deg, #fee2e2, #fef2f2);
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

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

.mobile-banner {
  width: 100%;
  padding: 4px 16px;
  font-size: 13px;   
  text-align: center;
  margin-top: 6px;
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
}

.category-bar::-webkit-scrollbar {
  display: none;
}

.cart-icon {
  padding: 0 16px;
  cursor: pointer;
}
</style>