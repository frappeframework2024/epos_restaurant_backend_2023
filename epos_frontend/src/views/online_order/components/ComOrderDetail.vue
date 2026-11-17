<template>
  <ComModal :mobileFullscreen="true" @onClose="onClose()" width="1200px" :hideOkButton="true">
    <template #title>
      {{ $t('Order Detail') }}
    </template>

    <template #content>
      <div class="oo-detail-container">
        <div v-if="loading" class="oo-detail-loading">
          <ProgressSpinner style="width: 48px; height: 48px" strokeWidth="4" />
          <span class="oo-loading-text">Loading order details...</span>
        </div>

        <div v-else-if="errorMessage" class="oo-detail-body">
          <Message severity="error" icon="mdi mdi-alert-circle-outline" :closable="false">
            {{ errorMessage }}
          </Message>
          <div>
            <button type="button" class="oo-btn oo-btn-small" @click="getOrder">Retry</button>
          </div>
        </div>

        <template v-else>
          <div class="oo-detail-body">
            <!-- ORDER SUMMARY HEADER -->
            <div class="oo-detail-header-bar">
              <div class="oo-detail-title-group">
                <h3 class="oo-detail-title">{{ getOrderTitle(detailOrder) }}</h3>
                <span class="oo-status-pill" :class="normalizedStatus(detailOrder.status)">
                  {{ detailOrder.status || 'unknown' }}
                </span>
              </div>

              <div class="oo-detail-chips">
                <div v-if="getOrderTable(detailOrder)" class="oo-detail-chip">
                  <span class="oo-detail-label">Table:</span>
                  <span class="oo-detail-value">{{ getOrderTable(detailOrder) }}</span>
                </div>
                <div v-if="getOrderCustomer(detailOrder)" class="oo-detail-chip">
                  <span class="oo-detail-label">Customer:</span>
                  <span class="oo-detail-value">{{ getOrderCustomer(detailOrder) }}</span>
                </div>
                <div v-if="getOrderTime(detailOrder)" class="oo-detail-chip">
                  <span class="oo-detail-label">Time:</span>
                  <span class="oo-detail-value">{{ getOrderTime(detailOrder) }}</span>
                </div>
                <div
                  v-for="field in extraDetailSummaryFields"
                  :key="field.key"
                  class="oo-detail-chip"
                >
                  <span class="oo-detail-label">{{ field.label }}:</span>
                  <span class="oo-detail-value">{{ field.value }}</span>
                </div>
              </div>
            </div>

            <!-- PRODUCTS TOOLBAR -->
            <div class="oo-items-header">
              <div class="oo-items-title-group">
                <span class="oo-section-title">
                  Order Items ({{ detailProducts.length }})
                </span>
                <span v-if="isSubmittedOrder" class="oo-selection-hint">
                  {{ selectedProducts.length }} of {{ detailProducts.length }} selected
                </span>
              </div>

              <div class="oo-items-controls">
                <button
                  v-if="isSubmittedOrder && detailProducts.length > 0"
                  type="button"
                  class="oo-btn oo-btn-small"
                  @click="toggleSelectAll"
                >
                  {{ isAllSelected ? 'Clear All' : 'Select All' }}
                </button>

                <div class="oo-toggle-group" role="group" aria-label="Product display mode">
                  <button
                    type="button"
                    class="oo-btn oo-btn-small"
                    :class="{ 'oo-btn-dark': productViewMode === 'list' }"
                    @click="productViewMode = 'list'"
                  >
                    <v-icon size="16" class="mr-1">mdi-format-list-bulleted</v-icon>
                    List
                  </button>
                  <button
                    type="button"
                    class="oo-btn oo-btn-small"
                    :class="{ 'oo-btn-dark': productViewMode === 'card' }"
                    @click="productViewMode = 'card'"
                  >
                    <v-icon size="16" class="mr-1">mdi-view-grid-outline</v-icon>
                    Card
                  </button>
                </div>
              </div>
            </div>

            <!-- SUBMITTED ORDER: SELECTABLE ITEMS -->
            <template v-if="isSubmittedOrder">
              <div v-if="productViewMode === 'card'" class="oo-product-card-section">
                <div v-if="!detailProducts.length" class="oo-empty-items">
                  No items returned for this order.
                </div>

                <div v-else class="oo-product-card-grid">
                  <div
                    v-for="(item, idx) in detailProducts"
                    :key="item.id || item.line_number || idx"
                    class="oo-product-card oo-product-card-selectable"
                    :class="{ 'oo-product-card-selected': isProductSelected(item) }"
                    @click="toggleProductSelection(item)"
                  >
                    <div class="oo-product-card-top">
                      <div class="oo-product-card-title-wrap">
                        <Checkbox
                          :modelValue="isProductSelected(item)"
                          :binary="true"
                          @click.stop
                          @update:modelValue="toggleProductSelection(item)"
                        />
                        <span class="oo-product-card-no">#{{ idx + 1 }}</span>
                        <span class="oo-product-card-name">{{ getItemName(item, idx) }}</span>
                      </div>
                      <span class="oo-product-qty-badge">{{ getItemQty(item) }} &times;</span>
                    </div>

                    <div v-if="item.note || item.remark" class="oo-product-card-note">
                      Note: {{ item.note || item.remark }}
                    </div>

                    <div class="oo-product-card-footer">
                      <span class="oo-product-unit-price">
                        {{ getItemUnitPrice(item, detailOrder.currency) }} each
                      </span>
                      <span class="oo-product-line-total">
                        {{ getItemLineTotal(item, detailOrder.currency) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="oo-detail-table-wrap">
                <table class="oo-detail-table">
                  <thead>
                    <tr>
                      <th class="oo-col-check">
                        <Checkbox
                          :modelValue="isAllSelected"
                          :binary="true"
                          :disabled="!detailProducts.length"
                          @update:modelValue="toggleSelectAll"
                        />
                      </th>
                      <th class="oo-col-no">No.</th>
                      <th>Name</th>
                      <th class="oo-th-center">Quantity</th>
                      <th class="oo-th-right">Price</th>
                      <th class="oo-th-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="!detailProducts.length">
                      <td colspan="6" class="oo-empty-table-cell">
                        No items returned for this order.
                      </td>
                    </tr>

                    <tr
                      v-for="(item, idx) in detailProducts"
                      :key="item.id || item.line_number || idx"
                      class="oo-row-selectable"
                      :class="{ 'oo-row-selected': isProductSelected(item) }"
                      @click="toggleProductSelection(item)"
                    >
                      <td class="oo-col-check" @click.stop>
                        <Checkbox
                          :modelValue="isProductSelected(item)"
                          :binary="true"
                          @update:modelValue="toggleProductSelection(item)"
                        />
                      </td>
                      <td class="oo-row-no">{{ idx + 1 }}</td>
                      <td>
                        <div class="oo-item-name">{{ getItemName(item, idx) }}</div>
                        <div v-if="item.note || item.remark" class="oo-item-note">
                          Note: {{ item.note || item.remark }}
                        </div>
                      </td>
                      <td class="oo-td-center">
                        <span class="oo-item-qty-cell">{{ getItemQty(item) }}</span>
                      </td>
                      <td class="oo-td-right oo-nowrap">
                        {{ getItemUnitPrice(item, detailOrder.currency) }}
                      </td>
                      <td class="oo-td-right oo-nowrap oo-font-semibold">
                        {{ getItemLineTotal(item, detailOrder.currency) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>

            <!-- ACCEPTED / NON-SUBMITTED ORDER: ACCEPT & REJECT SECTIONS -->
            <template v-else>
              <!-- SECTION 1: ACCEPT -->
              <div class="oo-split-section">
                <div class="oo-split-header oo-split-accepted">
                  <span>Accept ({{ acceptedProducts.length }})</span>
                  <span>{{ formatCurrency(displayTotal, detailOrder.currency) }}</span>
                </div>

                <div v-if="productViewMode === 'card'" class="oo-product-card-grid">
                  <div v-if="!acceptedProducts.length" class="oo-empty-items">
                    No accepted items.
                  </div>

                  <div
                    v-for="(item, idx) in acceptedProducts"
                    :key="item.id || item.line_number || idx"
                    class="oo-product-card oo-product-card-accepted"
                  >
                    <div class="oo-product-card-top">
                      <div class="oo-product-card-title-wrap">
                        <span class="oo-product-card-no">#{{ idx + 1 }}</span>
                        <span class="oo-product-card-name">{{ getItemName(item, idx) }}</span>
                      </div>
                      <span class="oo-product-qty-badge">{{ getItemQty(item) }} &times;</span>
                    </div>

                    <div v-if="item.note || item.remark" class="oo-product-card-note">
                      Note: {{ item.note || item.remark }}
                    </div>

                    <div class="oo-product-card-footer">
                      <span class="oo-product-unit-price">
                        {{ getItemUnitPrice(item, detailOrder.currency) }} each
                      </span>
                      <span class="oo-product-line-total">
                        {{ getItemLineTotal(item, detailOrder.currency) }}
                      </span>
                    </div>
                  </div>
                </div>

                <div v-else class="oo-detail-table-wrap">
                  <table class="oo-detail-table">
                    <thead>
                      <tr>
                        <th class="oo-col-no">No.</th>
                        <th>Name</th>
                        <th class="oo-th-center">Quantity</th>
                        <th class="oo-th-right">Price</th>
                        <th class="oo-th-right">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="!acceptedProducts.length">
                        <td colspan="5" class="oo-empty-table-cell">
                          No accepted items.
                        </td>
                      </tr>

                      <tr
                        v-for="(item, idx) in acceptedProducts"
                        :key="item.id || item.line_number || idx"
                      >
                        <td class="oo-row-no">{{ idx + 1 }}</td>
                        <td>
                          <div class="oo-item-name">{{ getItemName(item, idx) }}</div>
                          <div v-if="item.note || item.remark" class="oo-item-note">
                            Note: {{ item.note || item.remark }}
                          </div>
                        </td>
                        <td class="oo-td-center">
                          <span class="oo-item-qty-cell">{{ getItemQty(item) }}</span>
                        </td>
                        <td class="oo-td-right oo-nowrap">
                          {{ getItemUnitPrice(item, detailOrder.currency) }}
                        </td>
                        <td class="oo-td-right oo-nowrap oo-font-semibold">
                          {{ getItemLineTotal(item, detailOrder.currency) }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- SECTION 2: REJECT -->
              <div v-if="rejectedProducts.length > 0" class="oo-split-section">
                <div class="oo-split-header oo-split-rejected">
                  <span>Reject ({{ rejectedProducts.length }})</span>
                  <span class="oo-rejected-note">Excluded from total</span>
                </div>

                <div v-if="productViewMode === 'card'" class="oo-product-card-grid">
                  <div
                    v-for="(item, idx) in rejectedProducts"
                    :key="item.id || item.line_number || idx"
                    class="oo-product-card oo-product-card-rejected"
                  >
                    <div class="oo-product-card-top">
                      <div class="oo-product-card-title-wrap">
                        <span class="oo-product-card-no">#{{ idx + 1 }}</span>
                        <span class="oo-product-card-name oo-rejected-text">
                          {{ getItemName(item, idx) }}
                        </span>
                      </div>
                      <span class="oo-product-qty-badge oo-qty-pill-rejected">
                        {{ getItemQty(item) }} &times;
                      </span>
                    </div>

                    <div v-if="item.note || item.remark" class="oo-product-card-note">
                      Note: {{ item.note || item.remark }}
                    </div>

                    <div class="oo-product-card-footer">
                      <span class="oo-product-unit-price">
                        {{ getItemUnitPrice(item, detailOrder.currency) }} each
                      </span>
                      <span class="oo-product-line-total oo-rejected-text">
                        {{ getItemLineTotal(item, detailOrder.currency) }}
                      </span>
                    </div>
                  </div>
                </div>

                <div v-else class="oo-detail-table-wrap">
                  <table class="oo-detail-table">
                    <thead>
                      <tr>
                        <th class="oo-col-no">No.</th>
                        <th>Name</th>
                        <th class="oo-th-center">Quantity</th>
                        <th class="oo-th-right">Price</th>
                        <th class="oo-th-right">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(item, idx) in rejectedProducts"
                        :key="item.id || item.line_number || idx"
                        class="oo-rejected-row"
                      >
                        <td class="oo-row-no">{{ idx + 1 }}</td>
                        <td>
                          <div class="oo-rejected-text">{{ getItemName(item, idx) }}</div>
                          <div v-if="item.note || item.remark" class="oo-item-note">
                            Note: {{ item.note || item.remark }}
                          </div>
                        </td>
                        <td class="oo-td-center oo-rejected-text">{{ getItemQty(item) }}</td>
                        <td class="oo-td-right oo-nowrap oo-rejected-text">
                          {{ getItemUnitPrice(item, detailOrder.currency) }}
                        </td>
                        <td class="oo-td-right oo-nowrap oo-rejected-text">
                          {{ getItemLineTotal(item, detailOrder.currency) }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </template>

            <!-- TOTAL FOOTER (CALCULATED ONLY FROM ACCEPT / SELECTED ITEMS) -->
            <div v-if="detailProducts.length > 0" class="oo-product-cards-total-bar">
              <span class="oo-footer-label">Total</span>
              <span class="oo-footer-total">
                {{ formatCurrency(displayTotal, detailOrder.currency) }}
              </span>
            </div>
          </div>
        </template>

        <!-- CANCEL ORDER CONFIRMATION -->
        <ComModal
          v-if="showCancelConfirm"
          :mobileFullscreen="false"
          @onClose="!cancelling && (showCancelConfirm = false)"
          width="500px"
          height="auto"
          class="oo-compact-modal"
          :hideOkButton="true"
          :closeButtonText="$t('No')"
        >
          <template #title>
            Cancel Order
          </template>
          <template #content>
            <div class="oo-submodal-body">
              <p class="oo-submodal-msg">
                Are you sure you want to cancel order <strong>{{ getOrderTitle(detailOrder) }}</strong>?
              </p>
            </div>
          </template>
          <template #action>
            <v-btn
              variant="flat"
              color="success"
              :loading="cancelling"
              :disabled="cancelling"
              @click="executeCancelOrder"
            >
              Yes
            </v-btn>
          </template>
        </ComModal>

        <!-- CREATE NEW SALE CONFIRMATION -->
        <ComModal
          v-if="showNewSaleConfirm"
          :mobileFullscreen="false"
          @onClose="!confirming && (showNewSaleConfirm = false)"
          width="500px"
          height="auto"
          class="oo-compact-modal"
          :hideOkButton="true"
          :closeButtonText="$t('Cancel')"
        >
          <template #title>
            Confirm New Sale
          </template>
          <template #content>
            <div class="oo-submodal-body">
              <p class="oo-submodal-msg">
                Create a new sale with <strong>{{ selectedProducts.length }}</strong> selected item(s)?
              </p>
            </div>
          </template>
          <template #action>
            <v-btn
              variant="flat"
              color="success"
              :loading="confirming"
              :disabled="confirming"
              @click="submitNewSaleConfirm"
            >
              Confirm
            </v-btn>
          </template>
        </ComModal>

        <!-- EXISTING TABLE SALES MODAL -->
        <ComConfirmAcceptOrder
          v-if="showConfirmAcceptModal"
          :order="detailOrder"
          :allProducts="detailProducts"
          :selectedProducts="selectedProducts"
          :existingSales="existingTableSales"
          :onNotify="resolvedNotify"
          @resolve="onConfirmAcceptResolved"
        />
      </div>
    </template>

    <template #action>
      <template v-if="!loading && !errorMessage && detailOrder.id">
        <v-btn
          v-if="canCancelOrder"
          variant="flat"
          color="warning"
          :loading="cancelling"
          :disabled="submittingAction"
          @click="showCancelConfirm = true"
        >
          Cancel Order
        </v-btn>

        <v-btn
          v-if="canConfirmOrder"
          variant="flat"
          color="success"
          :loading="checkingTables || confirming"
          :disabled="submittingAction || selectedProducts.length === 0"
          @click="onAcceptOrder"
        >
          Confirm Order
        </v-btn>
      </template>
    </template>
  </ComModal>
</template>

<script setup>
import {ref,computed,inject,onMounted,useRouter,createToaster,smallViewSaleProductListModal,watch,} from '@/plugin';
import { useDisplay } from 'vuetify';

import Checkbox from 'primevue/checkbox';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import ComModal from '@/components/ComModal.vue';
import ComConfirmAcceptOrder from './ComConfirmAcceptOrder.vue';
import { getPosContextDefaults, parseServerMessages, extractApiError, normalizedStatus, 
  getOrderTitle, getOrderTable, getOrderCustomer, getOrderTime, getItemQty, getItemName,
  getItemUnitPrice, getItemLineTotal, formatLabel, formatCurrency, formatValue,} from '../utils/orderHelpers';

const toast = createToaster({ position: 'top-right' });

const props = defineProps({
  orderId: {
    type: [String, Number],
    default: '',
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

const emit = defineEmits(['resolve', 'updated', 'close']);
const gv = inject('$gv');
const tableLayout = inject('$tableLayout');
const sale = inject('$sale');
const socket = inject('$socket');
const { mobile } = useDisplay();
const router = useRouter();
const resolvedOrderId = computed(() => props.orderId || props.params?.order_id || '');
const resolvedNotify = computed(() => props.onNotify || props.params?.onNotify || null);
const loading = ref(false);
const errorMessage = ref('');
const checkingTables = ref(false);
const confirming = ref(false);
const cancelling = ref(false);
const showNewSaleConfirm = ref(false);
const showCancelConfirm = ref(false);
const showConfirmAcceptModal = ref(false);
const existingTableSales = ref([]);
const PRODUCT_VIEW_MODE_KEY = 'oo_detail_product_view_mode';

function getInitialProductViewMode() {
  try {
    const saved = localStorage.getItem(PRODUCT_VIEW_MODE_KEY);
    if (saved === 'list' || saved === 'card') return saved;
  } catch {
    // Ignore storage errors
  }
  return typeof window !== 'undefined' && window.innerWidth < 640 ? 'card' : 'list';
}

const productViewMode = ref(getInitialProductViewMode());

watch(productViewMode, (mode) => {
  try {
    localStorage.setItem(PRODUCT_VIEW_MODE_KEY, mode);
  } catch {
  }
});

const orderDetail = ref({});
const selectedProducts = ref([]);
const submittingAction = computed(
  () => checkingTables.value || confirming.value || cancelling.value
);

const detailOrder = computed(() => orderDetail.value?.order || {});
const detailProducts = computed(() => {
  if (Array.isArray(orderDetail.value?.products)) return orderDetail.value.products;
  if (Array.isArray(orderDetail.value?.order?.products)) return orderDetail.value.order.products;
  return [];
});

const isSubmittedOrder = computed(
  () => normalizedStatus(detailOrder.value?.status) === 'submitted'
);

const canConfirmOrder = computed(() => isSubmittedOrder.value);

const canCancelOrder = computed(() => {
  const st = normalizedStatus(detailOrder.value?.status);
  return st === 'submitted' || st === 'accepted';
});

const acceptedProducts = computed(() =>
  detailProducts.value.filter((p) => {
    const st = String(p.status || '').trim().toLowerCase();

    return st !== 'rejected' && st !== 'reject';
  })
);

const rejectedProducts = computed(() =>
  detailProducts.value.filter((p) => {
    const st = String(p.status || '').trim().toLowerCase();

    return st === 'rejected' || st === 'reject';
  })
);

function calcProductsTotal(items) {
  return (items || []).reduce((sum, item) => {
    const rawLine =
      item.amount != null
        ? Number(item.amount)
        : item.total_amount != null
          ? Number(item.total_amount)
          : Number(item.price ?? item.unit_price ?? 0) * Number(getItemQty(item) || 1);
    return sum + (Number.isFinite(rawLine) ? rawLine : 0);
  }, 0);
}

const displayTotal = computed(() => {
  if (isSubmittedOrder.value) {
    return calcProductsTotal(selectedProducts.value);
  }
  return calcProductsTotal(acceptedProducts.value);
});

const isAllSelected = computed(
  () =>
    detailProducts.value.length > 0 &&
    selectedProducts.value.length === detailProducts.value.length
);

function isProductSelected(item) {
  return selectedProducts.value.includes(item);
}

function toggleProductSelection(item) {
  if (!canConfirmOrder.value) return;
  const idx = selectedProducts.value.indexOf(item);
  if (idx === -1) {
    selectedProducts.value = [...selectedProducts.value, item];
  } else {
    selectedProducts.value = selectedProducts.value.filter((_, i) => i !== idx);
  }
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedProducts.value = [];
  } else {
    selectedProducts.value = [...detailProducts.value];
  }
}

const HIDDEN_DETAIL_KEYS = new Set([
  'id',
  'status',
  'products',
  'items',
  'order_number',
  'order_no',
  'posting_date',
  'submitted_at',
  'created_at',
  'updated_at',
  'order_date',
  'total_quantity',
  'total_amount',
  'grand_total',
  'total',
  'amount',
  'currency',
  'branch_id',
  'branch_slug',
  'branch_name',
  'table_id',
  'table_code',
  'table_label',
  'table_name',
  'table',
  'table_group_id',
  'table_group_name',
  'customer_name',
  'customer',
  'guest_name',
]);

const extraDetailSummaryFields = computed(() => {
  return Object.entries(detailOrder.value)
    .filter(([key, val]) => !HIDDEN_DETAIL_KEYS.has(key) && val !== null && val !== undefined && val !== '')
    .map(([key, val]) => ({
      key,
      label: formatLabel(key),
      value: formatValue(val),
    }));
});

function notifySuccess(msg) {
  const cleanMsg = String(msg || '').replace(/<[^>]*>/g, '').trim();
  if (cleanMsg) {
    toast.success(cleanMsg);
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
  if (submittingAction.value) return;
  emit('resolve', false);
}

async function getOrder() {
  loading.value = true;
  errorMessage.value = '';
  try {
    const res = await app.postApi(
      'emenu_integration.order.get_order',
      {
        context: {
          order_id: resolvedOrderId.value,
        },
      },
      '',
      false
    );

    if (res?.error) {
      errorMessage.value = extractApiError(res.error, 'Failed to load order details.');
      return;
    }

    const payload = res?.data ?? res?.message ?? res;
    if (payload?.order) {
      orderDetail.value = payload;
      selectedProducts.value = [];
    } else {
      errorMessage.value = 'Failed to load order details.';
    }
  } catch (err) {
    errorMessage.value = extractApiError(err, 'Failed to load order details.');
  } finally {
    loading.value = false;
  }
}

function buildOrderConfirmPayload(extraContext = {}) {
  const { pos_station, pos_profile } = getPosContextDefaults(gv);
  const rawSelectedIds = (selectedProducts.value || [])
    .map((p) => p.id)
    .filter((id) => id !== undefined && id !== null);
  const selectedIdSet = new Set(rawSelectedIds.map((id) => String(id)));

  const allProductsWithStatus = (detailProducts.value || []).map((p) => {
    const isSelected =
      selectedProducts.value.includes(p) ||
      (p.id !== undefined && p.id !== null && selectedIdSet.has(String(p.id)));
    return {
      ...p,
      status: isSelected ? 'accepted' : 'rejected',
    };
  });

  const acceptedTotal = calcProductsTotal(
    allProductsWithStatus.filter((p) => p.status === 'accepted')
  );

  return {
    context: {
      pos_station,
      pos_profile,
      order: {
        ...detailOrder.value,
        total: acceptedTotal,
        products: allProductsWithStatus,
      },
      selected_product_ids: rawSelectedIds,
      sale: {},
      ...extraContext,
    },
  };
}

async function submitNewSaleConfirm() {
  if (confirming.value) return;
  confirming.value = true;

  try {
    const conf = await gv.authorize('open_order_required_password', 'make_order');
    if (!conf) {
      showNewSaleConfirm.value = false;
      return;
    }

    const make_order_auth = {
      username: conf.username,
      name: conf.user,
      discount_codes: conf.discount_codes,
    };

    const payload = buildOrderConfirmPayload();
    const res = await app.postApi('emenu_integration.order.confirm_order', payload, '', false);

    if (res?.error) {
      showNewSaleConfirm.value = false;
      showErrorOnce(extractApiError(res.error, 'Failed to confirm order.'));
      return;
    }

    const resp = res?.data ?? res?.message ?? res;
    const saleName = resp?.sale?.name || resp?.sale_name;

    showNewSaleConfirm.value = false;
    notifySuccess(
      (typeof resp?.message === 'string' ? resp.message : '') ||
        parseServerMessages(res) ||
        'Order confirmed successfully.'
    );

    if (mobile.value) {
      await sale.LoadSaleData(saleName);
      localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
      const result = await smallViewSaleProductListModal({
        title: saleName,
        data: { from_table: false },
      });

      if (result) {
        tableLayout?.getSaleList?.();
      } else {
        localStorage.removeItem('make_order_auth');

        socket?.emit('ShowOrderInCustomerDisplay', {}, '', sale.customer_display_key);
      }

      emit('resolve', { refresh: true, closeDialog: true });
    } else {
      localStorage.setItem('make_order_auth', JSON.stringify(make_order_auth));
      const template = gv.device_setting?.main_sale_screen ?? 'Default';
      if (template === 'Default') {
        router.push({
          name: 'AddSale',
          params: { name: saleName },
        });
      } else {
        const _template = template.toLowerCase().replace(/\s+/g, '-');
        router.push({
          name: 'SaleOrder',
          params: { name: saleName },
          query: { menu: _template },
        });
      }

      emit('resolve', { refresh: true, closeDialog: true });
    }
  } catch (err) {
    showNewSaleConfirm.value = false;
    showErrorOnce(extractApiError(err, 'Failed to confirm order.'));
  } finally {
    confirming.value = false;
  }
}

async function onAcceptOrder() {
  if (!selectedProducts.value.length) return;

  checkingTables.value = true;

  try {
    const { pos_profile } = getPosContextDefaults(gv);
    const res = await app.postApi(
      'emenu_integration.order.get_current_table_orders',
      {
        pos_profile,
        table_id: detailOrder.value.table_id,
      },
      '',
      false
    );

    if (res?.error) {
      showErrorOnce(extractApiError(res.error, 'Failed to check current table orders.'));
      return;
    }

    const rawList = res?.data ?? res?.message ?? res;
    const existingSales = Array.isArray(rawList) ? rawList : [];

    if (existingSales.length === 0) {
      showNewSaleConfirm.value = true;
      return;
    }

    existingTableSales.value = existingSales;
    showConfirmAcceptModal.value = true;
  } catch (err) {
    showErrorOnce(extractApiError(err, 'Failed to check current table orders.'));
  } finally {
    checkingTables.value = false;
  }
}

function onConfirmAcceptResolved(result) {
  showConfirmAcceptModal.value = false;
  if (result?.confirmed) {
    emit('resolve', {
      refresh: true,
      closeDialog: result.closeDialog ?? true,
      sale: result.sale || {},
    });
  }
}

async function executeCancelOrder() {
  cancelling.value = true;
  try {
    const res = await app.postApi(
      'emenu_integration.order.cancell_order',
      {
        order_id: detailOrder.value.id,
        reason: null,
      },
      '',
      false
    );

    if (res?.error) {
      showCancelConfirm.value = false;
      showErrorOnce(extractApiError(res.error, 'Failed to cancel order.'));
      return;
    }

    const msg =
      parseServerMessages(res) ||
      (typeof res?.message === 'string' ? res.message : '') ||
      (typeof res?.data === 'string' ? res.data : '') ||
      'Order cancelled successfully.';

    showCancelConfirm.value = false;
    notifySuccess(msg);

    emit('resolve', { refresh: true });
  } catch (err) {
    showCancelConfirm.value = false;

    showErrorOnce(extractApiError(err, 'Failed to cancel order.'));
  } finally {
    cancelling.value = false;
  }
}

onMounted(async () => {
  await getOrder();
});
</script>

<style scoped>
.oo-submodal-body {
  display: block;
  height: auto;
  min-height: 0;
  padding: 16px 8px;
  text-align: left;
}
.oo-submodal-msg {
  margin: 0;
  color: #374151;
  font-size: 1rem;
  line-height: 1.5;
}
:deep(.oo-compact-modal .v-card),
:deep(.oo-compact-modal .v-card-text) {
  height: auto !important;
  max-height: 60px !important;
}

.oo-detail-container {
  display: flex;
  flex-direction: column;
  min-height: 490px;
  background: #ffffff;
  color: #1f2937;
  font-size: 1rem;
}

.oo-detail-loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 20px;
}
.oo-loading-text {
  margin-top: 12px;
  color: #6b7280;
}
.oo-detail-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 4px;
}
.oo-detail-header-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 14px 16px;
}
.oo-detail-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
.oo-detail-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}
.oo-status-pill {
  display: inline-block;
  min-width: 96px;
  text-align: center;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: capitalize;
  background: #e5e7eb;
  color: #1f2937;
  white-space: nowrap;
}
.oo-status-pill.submitted {
  background: #fef3c7;
  color: #b45309;
}
.oo-status-pill.accepted {
  background: #ccfbf1;
  color: #0f766e;
}
.oo-status-pill.completed {
  background: #dcfce7;
  color: #15803d;
}
.oo-status-pill.cancelled {
  background: #fee2e2;
  color: #b91c1c;
}
.oo-detail-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 22px;
}
.oo-detail-chip {
  display: flex;
  align-items: center;
  gap: 6px;
}
.oo-detail-label {
  color: #6b7280;
  font-weight: 500;
}
.oo-detail-value {
  font-weight: 700;
  color: #111827;
}
.oo-items-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.oo-items-title-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}
.oo-items-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
.oo-toggle-group {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.oo-section-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: #111827;
}
.oo-selection-hint {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #d97706;
}
.oo-row-no {
  color: #6b7280;
}
.oo-item-name {
  font-weight: 600;
  color: #111827;
}
.oo-item-note {
  margin-top: 4px;
  font-size: 0.9375rem;
  color: #b45309;
}
.oo-item-qty-cell {
  font-weight: 700;
  color: #d97706;
}
.oo-nowrap {
  white-space: nowrap;
}
.oo-font-semibold {
  font-weight: 600;
}

/* LIST VIEW TABLE */
.oo-detail-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
}
.oo-detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1rem;
}
.oo-detail-table th,
.oo-detail-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}
.oo-detail-table thead th {
  background: #f9fafb;
  color: #374151;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}
.oo-detail-table tbody tr.oo-row-selectable {
  cursor: pointer;
}
.oo-detail-table tbody tr.oo-row-selectable:hover {
  background: #fffbeb;
}
.oo-detail-table tbody tr.oo-row-selected {
  background: #fef3c7;
}
.oo-col-check {
  width: 3rem;
  text-align: center !important;
}
.oo-col-no {
  width: 4rem;
}
.oo-empty-table-cell {
  text-align: center !important;
  color: #6b7280;
  padding: 24px 16px !important;
}
.oo-th-center,
.oo-td-center {
  text-align: center !important;
}
.oo-th-right,
.oo-td-right {
  text-align: right !important;
}
.oo-footer-label {
  text-align: right !important;
  font-size: 1rem;
  font-weight: 600;
  color: #4b5563;
}
.oo-footer-total {
  text-align: right !important;
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
  white-space: nowrap;
}

.oo-product-card-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.oo-empty-items {
  padding: 28px 16px;
  text-align: center;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}
.oo-product-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.oo-product-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  background: #ffffff;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  transition: border-color 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease;
  user-select: none;
}
.oo-product-card-selectable {
  cursor: pointer;
}
.oo-product-card-selectable:hover {
  border-color: #f59e0b;
  background: #fffdf7;
}
.oo-product-card-selected {
  border-color: #d97706;
  background: #fffbeb;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.12);
}
.oo-product-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}
.oo-product-card-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.oo-product-card-no {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  flex-shrink: 0;
}
.oo-product-card-name {
  font-weight: 600;
  color: #111827;
  word-break: break-word;
}
.oo-product-qty-badge {
  flex-shrink: 0;
  padding: 2px 10px;
  border-radius: 999px;
  background: #fef3c7;
  color: #b45309;
  font-size: 0.875rem;
  font-weight: 700;
}
.oo-product-card-note {
  font-size: 0.875rem;
  color: #b45309;
  background: #fef3c7;
  padding: 6px 10px;
  border-radius: 6px;
}
.oo-product-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #f3f4f6;
  margin-top: auto;
}
.oo-product-unit-price {
  font-size: 0.875rem;
  color: #6b7280;
}
.oo-product-line-total {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
}
.oo-product-cards-total-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

/* ACCEPT / REJECT SECTIONS */
.oo-split-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.oo-split-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
}
.oo-split-accepted {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}
.oo-split-rejected {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}
.oo-rejected-note {
  font-size: 0.78rem;
  font-weight: 500;
  opacity: 0.85;
}
.oo-product-card-accepted {
  border-color: #a7f3d0;
}
.oo-product-card-rejected {
  background: #fafafa;
  border-color: #fecaca;
  opacity: 0.82;
}
.oo-qty-pill-rejected {
  background: #fee2e2;
  color: #991b1b;
}
.oo-rejected-text {
  color: #6b7280;
}
.oo-rejected-row {
  background: #fafafa;
}

/* PRIMEVUE CHECKBOX OVERRIDES */
:deep(.p-checkbox) {
  --p-checkbox-checked-background: #d97706;
  --p-checkbox-checked-hover-background: #b45309;
  --p-checkbox-checked-border-color: #d97706;
  --p-checkbox-checked-hover-border-color: #b45309;
  --p-checkbox-icon-checked-color: #ffffff;
  --p-checkbox-icon-checked-hover-color: #ffffff;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
:deep(.p-checkbox .p-checkbox-box) {
  width: 20px;
  height: 20px;
  background: #ffffff !important;
  border: 2px solid #d1d5db !important;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}
:deep(.p-checkbox.p-highlight .p-checkbox-box),
:deep(.p-checkbox.p-checkbox-checked .p-checkbox-box),
:deep(.p-checkbox[data-p-checked="true"] .p-checkbox-box),
:deep(.p-checkbox .p-checkbox-box[data-p-checked="true"]),
:deep(.p-checkbox .p-checkbox-box.p-checked),
:deep(.p-checkbox:has(input:checked) .p-checkbox-box) {
  background: #d97706 !important;
  border-color: #d97706 !important;
  color: #ffffff !important;
}
:deep(.p-checkbox .p-checkbox-icon) {
  width: 14px !important;
  height: 14px !important;
  color: #ffffff !important;
  display: block;
}

.oo-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #1f2937;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}
.oo-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.oo-btn-small {
  padding: 6px 14px;
  font-size: 0.875rem;
}
.oo-btn-dark {
  background: #1f2937;
  color: #ffffff;
  border-color: #1f2937;
}

@media (max-width: 640px) {
  .oo-detail-container {
    min-height: calc(100dvh - 130px);
  }
  .oo-detail-body {
    gap: 10px;
    padding: 0;
  }
  .oo-detail-header-bar {
    padding: 10px 12px;
    gap: 8px;
  }
  .oo-detail-title {
    font-size: 1.1rem;
  }
  .oo-detail-chips {
    gap: 6px 14px;
    font-size: 0.9rem;
  }
  .oo-items-header {
    gap: 8px;
  }
  .oo-section-title {
    font-size: 0.975rem;
  }
  .oo-product-card-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .oo-product-card {
    padding: 12px;
  }
}
</style>