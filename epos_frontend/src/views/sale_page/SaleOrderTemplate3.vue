<template>
  <div class="main-layout">
    <div class="sidebarCategory">
      <div class="text-xl font-bold main-cat">
        {{$t('Categories')}}
      </div> 
      <div @click="filterCat('All')" :style="{
        padding: '8px 10px',
        margin: '0px 6px 0px 8px',
        borderRadius: '8px',
        fontSize: gv.itemMenuSetting.shortcut_menu_font_size + 'px',
        cursor: 'pointer',
        background: activeCat === 'All' ? 'rgb(4 117 117)' : 'transparent',
        color: activeCat === 'All' ? '#fff' : '#fff',
        fontWeight: activeCat === 'All' ? '500' : '400',
        transition: 'background 0.15s',
        flexShrink: 0
      }">
        {{ $t("All") }}
      </div>
      <div ref="sidebarScrollRef" style="overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 4px;">
        
        <div v-for="cat in categories.filter(c => c.name !== 'All')" :key="cat.name" :data-cat="cat.name"
          @click="filterCat(cat)" :style="{
            padding: '8px 10px',
            margin: '4px 6px 0px 8px',
            borderRadius: '8px',
            fontSize: gv.itemMenuSetting.shortcut_menu_font_size + 'px',
            cursor: 'pointer',
            background: activeCat === cat.name ? 'rgb(4, 117, 117)' : (activeCat === 'All' && scrollCat === cat.name) ? 'rgb(4 117 117 / 46%)' : 'transparent',
            color: activeCat === cat.name ? '#fff' : (activeCat === 'All' && scrollCat === cat.name) ? '#fff' : '#fff',
            fontWeight: activeCat === cat.name ? '500' : '400',
            transition: 'background 0.15s'
          }">
          {{ getMenuName(cat) }}
        </div>
      </div>
    </div>
    <div ref="contentRef" @scroll="onScroll" style="flex: 1; overflow-y: auto;  min-width: 0; padding-bottom: 5px;"
      class="bg-menu-item">
      <div style=" position: sticky;
        display: flex;
        justify-content: space-between;
        top: 0;
        background: #fdfdfd;
        z-index: 10;
        font-size: 18px;
        box-shadow: 0 4px 20px  rgb(117 117 117 / 22%);
        background: #047575;
        color: #fff;
        " class="p-3">
        <div class="w-full flex flex-wrap" :style="{
          fontSize: gv.itemMenuSetting.shortcut_menu_font_size + 2 + 'px',
          alignItems: 'center'
        }">
          <span class="font-bold">{{ getMenuName(menuTitle) }}</span>

        </div>

        <div class="flex">
          <div class="cart-icon" :style="{
            color: (sale.sale.total_quantity || 0) > 0 || (sale.sale.name || '') != '' ? '#fff' : '#fff',
            cursor: (sale.sale.total_quantity || 0) > 0 || (sale.sale.name || '') != '' ? 'pointer' : 'not-allowed',
          }" @click="onViewDetail">
            <v-badge :content="(sale.sale.total_quantity || 0)" :model-value="(sale.sale.total_quantity || 0) > 0"
              color="#ff0000">
              <v-icon size="28">mdi-cart-plus</v-icon>
            </v-badge>
          </div>
          <div @click="onSettingClick" style="cursor:pointer">
            <v-icon size="28">mdi-cog</v-icon>
          </div>
        </div>

      </div>

      <template v-if="!product.searchProductKeyword">
        <div v-for="cat in filteredCategories" :key="cat.name" :id="'section-' + cat.name"
          style="margin-bottom: 0px;padding: 12px;">
          <div v-if="cat.name !== 'all' && cat.name != menuTitle.name && !product.searchProductKeyword"
            style="font-size: 18px; font-weight: bold; color: #fff; margin-bottom: 8px; padding-bottom: 6px;">
            {{ getMenuName(cat) }}
          </div>
          <ComProductCard2 :productsByCategory="productsByCategory(cat.name)" :onProductClick="onMenuProductClick" />
        </div>
      </template>
      <template v-else>
        <div style="margin-bottom: 0px;padding: 12px;">
          <template v-if="searchedProducts.length > 0">
            <ComProductCard2 :productsByCategory="searchedProducts" :onProductClick="onMenuProductClick" />
          </template>
          <template v-else>
            <EmptyData />
          </template>
        </div>
      </template>
      <div style="height: 60px;"></div>
      <ScrollToTop :target="contentRef" />

      <div class="bottom-price">
        <SaleOrderSammary />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, i18n, computed, inject, onMounted, smallViewSaleProductListModal } from '@/plugin'
import ComProductCard2 from "@/views/sale_page/components/ComProductCard2.vue"
import SaleOrderSammary from "@/views/sale/components/mobile_screen/ComSmallSaleOrderSammary2.vue";
import { useDialog } from 'primevue/usedialog';
import { onSelectProduct } from "@/utils/sale.js";
import ScrollToTop from "@/views/sale_page/components/ComScrollToTop2.vue";
import EmptyData from "@/views/sale_page/components/ComEmptyData.vue";


const sale = inject("$sale");
const gv = inject("$gv");
const product = inject("$product");
const { t: $t } = i18n.global;

const dialog = useDialog();
const activeCat = ref('All');
const contentRef = ref(null)
const sidebarScrollRef = ref(null);
const scrollCat = ref('All');
const menuTitle = ref({});

const categories = ref([]);
const products = ref([]);
const screenWidth = ref(window.innerWidth);
const props = defineProps({
  menu_categories: Object,
  menu_products: Object,
  onSettingClick: Function
});

let isMenuItemClick = false;

// filterCategory
const filteredCategories = computed(() => {
  let cat = []
  if (activeCat.value === 'All') {
    cat = categories.value.filter(c => c.name !== 'All')
  } else {
    cat = categories.value.filter(c => c.name === activeCat.value)
  }
  return cat
})

const searchedProducts = computed(() => {
  return categories.value
    .filter(c => c.name !== 'All')
    .flatMap(cat => productsByCategory(cat.name))
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
    if (elTop <= THRESHOLD) {
      current = cat.name;
      menuTitle.value = cat;
    }
  }

  scrollCat.value = current
  const sidebar = sidebarScrollRef.value
  const activeEl = sidebar?.querySelector(`[data-cat="${current}"]`)

  if (activeEl && sidebar) {
    const scrollTop = activeEl.offsetTop - sidebar.clientHeight / 2 + activeEl.offsetHeight / 2
    sidebar.scrollTo({ top: scrollTop, behavior: 'smooth' })
  }
}

const productsByCategory = (menu) => {
  if (product.searchProductKeyword) {
    let k = product.searchProductKeyword.toLowerCase()
    return products.value.filter(p => p.parent === menu && [p.name_en, p.name_kh, p.name].some(name => name?.toLowerCase().includes(k)))
  }
  return products.value.filter(p => p.parent === menu)
}

function filterCat(param) {
  let val = "All";
  menuTitle.value = categories.value[0]
  if (val != param) {
    val = param.name;
    menuTitle.value = param;
  }
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
  categories.value = props.menu_categories.map(c => ({
    ...c,
    emoji: '🍽️'
  }));
  products.value = [...props.menu_products];

  menuTitle.value = categories.value[0]

  window.addEventListener("resize", () => {
    screenWidth.value = window.innerWidth;
  });
})

async function onMenuProductClick(data) {
  if (isMenuItemClick) {
    return
  }

  try {
    isMenuItemClick = true;
    await onSelectProduct(data, sale, product, dialog)
  }
  finally {
    isMenuItemClick = false;
  }
}

function getMenuName(menu) {
  if (gv.itemMenuSetting.show_menu_language == "kh") {
    return menu.name_kh
  }
  return menu.name_en
}



const checkNewSaleNoSaleProducts = computed(() => {
  if ((sale.sale.name || '') == '' && (sale.sale.sale_products || []).length <= 0) {
    return true;
  }
  return false;
})

async function onViewDetail() {
  if (checkNewSaleNoSaleProducts.value) {
    toaster.warning($t('msg.Please select a menu item to continue'));
    return;
  }
  const result = await smallViewSaleProductListModal({ title: sale.sale.name, value: '' });
}


</script>

<style scoped>
.main-layout {
  display: flex;
  height: calc(100vh - 64px);
  overflow: hidden;
}

.sidebarCategory {
  width: 235px;
  min-width: 180px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 4px 0 20px rgb(117 117 117 / 22%);
  background: #047575c7;
  color: #fff;
}

/* Desktop: auto-fill with min 130px → many columns */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
}

/* Mobile: exactly 2 columns */
@media (max-width: 768px) {

  .main-layout {
    height: calc(100vh - 150px);
  }

  .sidebarCategory {
    width: 100px;
    min-width: 100px;
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

.cart-icon {
  margin-right: 10px;
  cursor: pointer;
}

.bg-menu-item {
  background: linear-gradient(to bottom, #1f9a9a 0%, #6faeb0 40%, #cfd6d8 75%, #f2f2f2 100%);
  position: relative;
}

.bottom-price {
  position: fixed;
  bottom: 0;
  background: #047575;
  /* height: 50px; */
  color: #fff;
  z-index: 10;
  text-align: right;
  left: 235px;
  right: 0;
}

.main-cat {
  padding: 13px 10px;
  cursor: pointer;
  color: rgb(255, 255, 255);
  transition: background 0.15s;
}
</style>