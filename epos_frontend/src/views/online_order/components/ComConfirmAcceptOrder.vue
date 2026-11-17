<template>
  <ComModal
    :mobileFullscreen="true"
    @onClose="onClose()"
    width="1200px"
    :hideOkButton="true"
    :closeButtonText="$t('Cancel')"
  >
    <template #title>
      Confirm Order - Table {{ getOrderTable(order) || '' }}
    </template>

    <template #content>
      <div class="oo-confirm-container">
        <div class="oo-confirm-body">
          <p class="oo-confirm-intro">
            Choose whether to create a new sale or add the selected item(s) to an existing sale.
          </p>

          <div class="oo-options-grid">
            <!-- OPTION 1: CREATE NEW SALE -->
            <div
              class="oo-option-card"
              :class="{ 'oo-option-active': mode === 'new' }"
              @click="mode = 'new'"
            >
              <input
                type="radio"
                name="oo-confirm-mode"
                value="new"
                :checked="mode === 'new'"
                class="oo-radio"
              />
              <div class="oo-option-text">
                <div class="oo-option-title">Create New Sale</div>
                <div class="oo-option-desc">Open a separate sale for the selected items</div>
              </div>
            </div>

            <!-- OPTION 2: ADD TO EXISTING SALE -->
            <div
              class="oo-option-card"
              :class="{ 'oo-option-active': mode === 'existing' }"
              @click="selectExistingMode"
            >
              <input
                type="radio"
                name="oo-confirm-mode"
                value="existing"
                :checked="mode === 'existing'"
                class="oo-radio"
              />
              <div class="oo-option-text">
                <div class="oo-option-title">Add to Existing Sale</div>
                <div class="oo-option-desc">Select an active sale below</div>
              </div>
            </div>
          </div>

          <div v-if="mode === 'existing'" class="oo-sales-list">
            <div
              v-for="(s, idx) in existingSales"
              :key="s.name || idx"
              class="oo-sale-item"
              :class="{ 'oo-sale-selected': selectedSale?.name === s.name }"
              @click="selectedSale = s"
            >
              <input
                type="radio"
                name="oo-existing-sale"
                :checked="selectedSale?.name === s.name"
                class="oo-radio"
              />
              <div class="oo-sale-info">
                <div class="oo-sale-name">{{ s.name || `Sale #${idx + 1}` }}</div>
                <div class="oo-sale-meta">
                  <span v-if="s.customer_name">{{ s.customer_name }}</span>
                  <span v-if="s.total_quantity !== undefined">
                    {{ s.total_quantity }} item(s)
                  </span>
                </div>
              </div>
              <div v-if="s.grand_total !== undefined" class="oo-sale-total">
                {{ formatCurrency(s.grand_total, order.currency) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #action>
      <v-btn
        variant="flat"
        color="success"
        :loading="submitting"
        :disabled="submitting || (mode === 'existing' && !selectedSale)"
        @click="executeConfirm"
      >
        Confirm
      </v-btn>
    </template>
  </ComModal>
</template>

<script setup>
import { ref, computed, inject, createToaster, smallViewSaleProductListModal, useRouter } from '@/plugin';
import ComModal from '@/components/ComModal.vue';
import {
  getPosContextDefaults,
  parseServerMessages,
  extractApiError,
  getOrderTable,
  getItemQty,
  formatCurrency,
} from '../utils/orderHelpers';
import { useDisplay } from 'vuetify';

const toast = createToaster({ position: 'top-right' });

const sale = inject('$sale');

const props = defineProps({
  order: {
    type: Object,
    default: () => ({}),
  },
  allProducts: {
    type: Array,
    default: () => [],
  },
  selectedProducts: {
    type: Array,
    default: () => [],
  },
  existingSales: {
    type: Array,
    default: () => [],
  },
  onNotify: {
    type: Function,
    default: null,
  },
  params: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['resolve']);
const gv = inject('$gv');
const tableLayout = inject('$tableLayout');
const socket = inject('$socket');
const { mobile } = useDisplay();
const router = useRouter();

const order = computed(() => props.order || props.params?.order || {});
const allProducts = computed(() => {
  if (Array.isArray(props.allProducts) && props.allProducts.length) return props.allProducts;
  if (Array.isArray(props.params?.allProducts) && props.params.allProducts.length) {
    return props.params.allProducts;
  }
  if (Array.isArray(order.value?.products) && order.value.products.length) {
    return order.value.products;
  }
  return [];
});
const selectedProducts = computed(
  () => props.selectedProducts || props.params?.selectedProducts || []
);
const existingSales = computed(
  () => props.existingSales || props.params?.existingSales || []
);

const mode = ref('existing');
const selectedSale = ref(existingSales.value[0] || null);
const submitting = ref(false);

function selectExistingMode() {
  mode.value = 'existing';
  if (!selectedSale.value && existingSales.value.length > 0) {
    selectedSale.value = existingSales.value[0];
  }
}

function showErrorOnce(msg) {
  const cleanMsg = String(msg || '').replace(/<[^>]*>/g, '').trim();
  if (!cleanMsg) return;
  setTimeout(() => {
    if (!document.querySelector('.c-toast')) {
      toast.error(cleanMsg);
    }
  }, 50);
}

function onClose() {
  if (submitting.value) return;
  emit('resolve', false);
}

async function executeConfirm() {
  if (submitting.value) return;
  if (mode.value === 'existing' && !selectedSale.value) return;
  if (!selectedProducts.value.length) {
    toast.error('Please select at least one product to confirm.');
    return;
  }
  submitting.value = true;
  try {
    const { pos_station, pos_profile } = getPosContextDefaults(gv);
    const salePayload = mode.value === 'existing' && selectedSale.value ? selectedSale.value : {};
    const conf = await gv.authorize('open_order_required_password', 'make_order');
    if (!conf) return;
    const make_order_auth = {
      username: conf.username,
      name: conf.user,
      discount_codes: conf.discount_codes,
    };

    const sourceProducts = allProducts.value.length ? allProducts.value : selectedProducts.value;
    const rawSelectedIds = selectedProducts.value
      .map((p) => p.id)
      .filter((id) => id !== undefined && id !== null);
    const selectedIdSet = new Set(rawSelectedIds.map((id) => String(id)));

    const allProductsWithStatus = sourceProducts.map((p) => {
      const isSelected =
        selectedProducts.value.includes(p) ||
        (p.id !== undefined && p.id !== null && selectedIdSet.has(String(p.id)));
      return {
        ...p,
        status: isSelected ? 'accepted' : 'rejected',
      };
    });

    const acceptedTotal = allProductsWithStatus
      .filter((p) => p.status === 'accepted')
      .reduce((sum, p) => {
        const lineTotal =
          p.amount != null
            ? Number(p.amount)
            : p.total_amount != null
              ? Number(p.total_amount)
              : Number(p.price ?? p.unit_price ?? 0) * Number(getItemQty(p) || 1);
        return sum + (Number.isFinite(lineTotal) ? lineTotal : 0);
      }, 0);

    const res = await app.postApi(
      'emenu_integration.order.confirm_order',
      {
        context: {
          pos_station,
          pos_profile,
          order: {
            ...order.value,
            total: acceptedTotal,
            products: allProductsWithStatus,
          },
          selected_product_ids: rawSelectedIds,
          sale: salePayload,
        },
      },
      '',
      false
    );

    if (res?.error) {
      showErrorOnce(extractApiError(res.error, 'Failed to confirm order.'));
      return;
    }

    const resp = res?.data ?? res?.message ?? res;

    const msg =
      (typeof resp?.message === 'string' ? resp.message : '') ||
      parseServerMessages(res) ||
      'Order confirmed successfully.';
    toast.success(String(msg).replace(/<[^>]*>/g, '').trim());

    if (mobile.value) {
      await sale.LoadSaleData(resp.sale.name);
      localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));

      const result = await smallViewSaleProductListModal({
        title: resp.sale.name,
        data: { from_table: false },
      });
      if (result) {
        tableLayout.getSaleList();
      } else {
        localStorage.removeItem('make_order_auth');
        socket?.emit('ShowOrderInCustomerDisplay', {}, '', sale.customer_display_key);
      }
      emit('resolve', { confirmed: true, closeDialog: true });
    } else {
      localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
      const template = gv.device_setting?.main_sale_screen ?? 'Default';
      if (template == 'Default') {
        router.push({
          name: 'AddSale',
          params: {
            name: resp.sale.name,
          },
        });
      } else {
        const _template = template.toLowerCase().replace(/\s+/g, '-');
        router.push({
          name: 'SaleOrder',
          params: {
            name: resp.sale.name,
          },
          query: { menu: _template },
        });
      }
      emit('resolve', { confirmed: true, closeDialog: true });
    }
  } catch (err) {
    showErrorOnce(extractApiError(err, 'Failed to confirm order.'));
  } finally {
    submitting.value = false;
  }
}
</script>
<style scoped>
.oo-confirm-container {
  display: flex;
  flex-direction: column;
  min-height: 490px;
  background: #ffffff;
  color: #1f2937;
  font-size: 1rem;
}
.oo-confirm-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 4px;
  min-height: 0;
}
.oo-confirm-intro {
  margin: 0 0 4px 0;
  color: #374151;
  line-height: 1.5;
}
.oo-options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.oo-option-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  background: #ffffff;
  transition: all 0.15s ease;
}
.oo-option-card:hover {
  border-color: #f59e0b;
}
.oo-option-active {
  border-color: #d97706;
  background: #fffbeb;
}
.oo-radio {
  width: 18px;
  height: 18px;
  accent-color: #d97706;
  cursor: pointer;
}
.oo-option-title {
  font-weight: 700;
  color: #111827;
}
.oo-option-desc {
  font-size: 0.9375rem;
  color: #6b7280;
}
.oo-sales-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}
.oo-sale-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #ffffff;
  border: 1.5px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
}
.oo-sale-item:hover {
  border-color: #16a34a;
}
.oo-sale-selected {
  border-color: #16a34a;
  background: #f0fdf4;
}
.oo-sale-info {
  flex: 1;
}
.oo-sale-name {
  font-weight: 700;
  color: #111827;
}
.oo-sale-meta {
  display: flex;
  gap: 12px;
  font-size: 0.875rem;
  color: #6b7280;
}
.oo-sale-total {
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
}

@media (max-width: 600px) {
  .oo-confirm-container {
    min-height: calc(100dvh - 140px);
  }
}
</style>