<template>
<div class="products-grid">
      <div
        v-for="prod in productsByCategory"
        :key="prod.name"
        class="product-card"
        @click="onProductClick(prod)"
      >
        <div class="eye-icon" @click.stop="previewProduct = prod">
          <v-icon>mdi-eye</v-icon>
        </div>
        <div class="product-image"> 
          <img v-if="prod.photo" :src="prod.photo" :alt="prod.name"  @error="onImageError" loading="lazy"/>
          <img v-else :src="getImage(prod.photo)" :alt="prod.name" style="width: 100%;height: 100%; object-fit: cover;" @error="onImageError" loading="lazy"  />
        </div>
            
        <div class="product-info">
          <div class="product-name" :style="{fontSize:gv.itemMenuSetting.item_font_size+ 'px' }"> {{ getProductName(prod) }}<span style="color: red;">{{ getTotalQuantityOrder(prod) }}</span></div>

       
          
          <div class="product-price flex items-center" :style="{fontSize:gv.itemMenuSetting.font_price_size+ 'px' }">
              <span v-if="productPrices(prod).length > 1">
                  <span>
                      <CurrencyFormat :value="minPrice(prod)" />
                  </span> <v-icon icon="mdi-arrow-right" size="x-small" /> <span>
                      <CurrencyFormat :value="maxPrice(prod)" />
                  </span>
              </span>
              <CurrencyFormat v-else :value="showPrice(prod)" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="previewProduct" class="image-overlay" @click="previewProduct = null">
  <div
    class="image-popup"
    @click.stop
    @wheel.prevent="onWheel"
    @touchstart.prevent="onTouchStart"
    @touchmove.prevent="onTouchMove"
    @touchend="onTouchEnd"
    @mousedown="onMouseDown"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
    :style="{
      transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
      transformOrigin: 'center center',
      cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default'
    }"
  >
    <button class="close-btn" @click.stop="previewProduct = null"   @mousedown.stop @touchstart.stop >✕</button>
    <img
      v-if="previewProduct.photo"
      :src="previewProduct.photo"
      :alt="previewProduct.name"
      draggable="false"
      loading="lazy"
      @error="onImageError"
    />
      <img v-else
      class="popup-placeholder"
        :src="getImage"
          @error="onImageError"
          loading="lazy"
      />
  </div>
</div>
</template>

<script setup>
import { ref,watch, reactive, inject } from '@/plugin';
import Enumerable from 'linq'; 
const gv = inject("$gv");
const sale = inject("$sale");
const product = inject("$product");
const previewProduct = ref(null)

const props = defineProps({
  productsByCategory: {
    type: Array,
    required: true
  },
  onProductClick: Function
})

const zoom = ref(1)
const pan = reactive({ x: 0, y: 0 })
const isDragging = ref(false)
let dragStart = { x: 0, y: 0 }
let panStart = { x: 0, y: 0 }
let lastTouchDist = null

watch(previewProduct, (val) => { if (!val) resetZoom() })

function resetZoom() {
  zoom.value = 1
  pan.x = 0 
  pan.y = 0
}

function adjustZoom(delta) {
  zoom.value = Math.min(5, Math.max(1, +(zoom.value + delta).toFixed(2)))
  if (zoom.value === 1) { pan.x = 0; pan.y = 0 }
}

function clampPan() {
  if (zoom.value <= 1) { pan.x = 0; pan.y = 0; return }
  const max = 140 * (zoom.value - 1)
  pan.x = Math.min(max, Math.max(-max, pan.x))
  pan.y = Math.min(max, Math.max(-max, pan.y))
}

function onWheel(e) {
  adjustZoom(e.deltaY > 0 ? -0.15 : 0.15)
  clampPan()
}

function onMouseDown(e) {
  if (zoom.value <= 1) return
  isDragging.value = true
  dragStart = { x: e.clientX, y: e.clientY }
  panStart = { x: pan.x, y: pan.y }   // ← no .value
}

function onMouseMove(e) {
  if (!isDragging.value) return
  pan.x = panStart.x + (e.clientX - dragStart.x)
  pan.y = panStart.y + (e.clientY - dragStart.y)
  clampPan()
}

function onMouseUp() { isDragging.value = false }

function getTouchDist(t) {
  return Math.sqrt((t[0].clientX - t[1].clientX) ** 2 + (t[0].clientY - t[1].clientY) ** 2)
}

function onTouchStart(e) {
  if (e.touches.length === 2) {
    lastTouchDist = getTouchDist(e.touches)
  } else if (e.touches.length === 1 && zoom.value > 1) {
    isDragging.value = true
    dragStart = { x: e.touches[0].clientX, y: e.touches[0].clientY }
    panStart = { x: pan.x, y: pan.y }
  }
}

function onTouchMove(e) {
  if (e.touches.length === 2 && lastTouchDist !== null) {
    const dist = getTouchDist(e.touches)
    adjustZoom((dist - lastTouchDist) * 0.01)
    lastTouchDist = dist
    clampPan()
  } else if (e.touches.length === 1 && isDragging.value) {
    pan.x = panStart.x + (e.touches[0].clientX - dragStart.x)
    pan.y = panStart.y + (e.touches[0].clientY - dragStart.y)
    clampPan()
  }
}

function onTouchEnd() { lastTouchDist = null; isDragging.value = false }

const placeholder = 'https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png' // your default image
const getImage = (img) => {
  if (!img) return placeholder

  // if it's private, try API route
  if (img.startsWith('/private/')) {
    return `/api/method/frappe.utils.file_manager.download_file?file_url=${img}`
  }
  return img
}

const onImageError = (e) => {
  e.target.src = placeholder 

   // force cover style on error
  e.target.style.objectFit = 'cover'
}


function getProductName(p){


  // :style="{fontSize:gv.itemMenuSetting.item_font_size+ 'px' }"
  let product_name = p.name_en;
  if(gv.itemMenuSetting.show_menu_language == "kh"){
     product_name = p.name_kh;
  }

  if(gv.itemMenuSetting.show_item_code){
    product_name = `${p.name} ${product_name}`;
  } 
  return product_name;
}


function getTotalQuantityOrder(data) {  
    const qty = sale.sale?.sale_products?.filter(r => r.product_code == data.name).reduce((n, d) => n + (d.quantity || 0), 0);
    if (qty == undefined) {
        return ""
    }
    if (qty == 0) {
        return ""
    } else {
        return " (" + qty + ")"
    } 
}


// price menu
const productPrices = (p) => {
    if (product.prices) {
        const r = JSON.parse(p.prices)
        return r.filter(r => (r.branch == sale.sale.business_branch || r.branch == '') && r.price_rule == sale.sale.price_rule)
    }
    return []
}


const showPrice = (p) => {
   let prices = productPrices(p);
  if (p.is_combo_menu) {
      return p.price || 0
  }
  if (prices.length == 1) {
      return prices[0].price
  }
  else if (prices.length == 0) {
      return p.price || 0
  }
  return 0
}

const maxPrice = (p) => {
  let prices = productPrices(p);
  if (prices.length > 1) {
      return Enumerable.from(prices).max("$.price")
  }
  return 0
}

const minPrice = (p) => {
  let prices = productPrices(p);
  if (prices.length > 1) {
      return Enumerable.from(prices).min("$.price")
  }
  return 0
}


</script>

<style scoped>

/* Grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  user-select: none;
}
@media (min-width: 768px)  { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1024px) { .products-grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 1366px) { .products-grid { grid-template-columns: repeat(5, 1fr); } }

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
  object-fit: contain;
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
   /* white-space: nowrap; */
    display: flex;
  align-items: center;     /* vertical center */
  
}
.product-price span {
  display: flex;
  align-items: center;
  margin-left: 4px;
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
  overflow: visible;
}

.image-popup {
  position: relative;
  width: 450px;
  border-radius: 12px;
  background: #000;
  display: flex;
  flex-direction: column;
  transition: transform 0.07s ease;
  will-change: transform;
}
.image-popup img {
  width: 100%;
  height: 320px;
  object-fit: contain;
  display: block;
  user-select: none;
  pointer-events: none;
  border-radius: 12px 12px;
}

.popup-placeholder {
  border-radius: 12px 12px 12px 12px;
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
.close-btn:hover { background: rgba(0,0,0,0.8); }
.zoom-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.85);
  border-radius: 0 0 12px 12px;
}
.zoom-bar button {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: none;
  border-radius: 6px;
  width: 32px;
  height: 28px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.zoom-bar button:hover { background: rgba(255,255,255,0.3); }
.zoom-bar span {
  color: #ccc;
  font-size: 13px;
  min-width: 40px;
  text-align: center;
}

@media (max-width: 768px) {
  
}

@media (min-width: 1024px) {
  
}

</style>