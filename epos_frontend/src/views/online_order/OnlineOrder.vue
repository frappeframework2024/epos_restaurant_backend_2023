<template>
  <component
    :is="isEmbedded ? 'div' : PageLayout"
    ref="rootEl"
    class="oo-full-width"
    :class="isEmbedded ? 'pt-2 pb-1' : 'pb-4'"
    v-bind="isEmbedded ? {} : { title: $t('Online Order'), icon: 'mdi-store-outline' }"
  >
    <v-container fluid class="!py-0" :class="isEmbedded ? 'px-2' : 'px-4'">
      <div class="online-orders-wrapper" :class="{ 'oo-fixed-modal-height': isEmbedded }">

        <ComOrderFilterBar
          :statusTabs="statusTabs"
          :status="filters.status"
          :postingDate="filters.posting_date"
          :viewMode="viewMode"
          :loading="loading"
          :lastUpdated="lastUpdated"
          @update:status="selectStatus"
          @update:postingDate="selectDate"
          @update:viewMode="viewMode = $event"
          @refresh="refreshOrders"
        />

        <!-- MAIN FULL-WIDTH CONTENT PANEL -->
        <div class="oo-content-panel">
          <div v-if="loading && !orders.length" class="oo-state-box">
            <v-icon size="46" color="#d97706" class="mb-2">mdi-loading mdi-spin</v-icon>
            <div>Loading online orders...</div>
          </div>

          <div v-else-if="!loading && error && !orders.length" class="oo-state-box">
            <v-icon size="48" color="#dc2626" class="mb-2">mdi-alert-circle-outline</v-icon>
            <div class="mb-3">Unable to load online orders.</div>
            <button type="button" class="oo-btn oo-btn-small" @click="refreshOrders">
              Retry
            </button>
          </div>

          <div v-else-if="!loading && !orders.length && !error" class="oo-state-box">
            <v-icon size="48" color="#9ca3af" class="mb-2">mdi-package-variant</v-icon>
            <div>No {{ activeStatusLabel.toLowerCase() }} orders found.</div>
          </div>

          <ComOrderCardList
            v-else-if="viewMode === 'card' && orders.length"
            :orders="orders"
            @select="openOrderDetail"
          />

          <ComOrderTableList
            v-else-if="viewMode === 'list' && orders.length"
            :orders="orders"
            @select="openOrderDetail"
          />
        </div>

        <ComOrderPagination
          v-if="orders.length || filters.page > 1"
          :page="filters.page"
          :visiblePages="visiblePages"
          :loading="loading"
          :isNextDisabled="isNextDisabled"
          @changePage="goToPage"
        />
      </div>
    </v-container>

    <!-- ORDER DETAIL MODAL -->
    <ComOrderDetail
      v-if="activeOrderId"
      :orderId="activeOrderId"
      :onNotify="notifyResult"
      @updated="fetchOrders({ silent: true })"
      @resolve="onOrderDetailResolved"
      @close="activeOrderId = null"
    />

  </component>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount,watch } from 'vue';
import { useRouter } from 'vue-router';
import PageLayout from '@/components/layout/PageLayout.vue';

import ComOrderFilterBar from '@/views/online_order/components/ComOrderFilterBar.vue';
import ComOrderCardList from '@/views/online_order/components/ComOrderCardList.vue';
import ComOrderTableList from '@/views/online_order/components/ComOrderTableList.vue';
import ComOrderPagination from '@/views/online_order/components/ComOrderPagination.vue';
import ComOrderDetail from '@/views/online_order/components/ComOrderDetail.vue';
import { extractApiError } from '@/views/online_order/utils/orderHelpers';
import { createToaster ,inject } from '@/plugin';

const props = defineProps({
  hideHeader: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close', 'openSale']);
const router = useRouter();
const toast = createToaster({ position: 'top-right' });
const socket = inject("$socket");


const rootEl = ref(null);
const isEmbedded = ref(props.hideHeader);
const activeOrderId = ref(null);

// Show filter btn
const statusTabs = [
  { label: 'Submitted', value: 'submitted' },
  { label: 'Accepted', value: 'accepted' },
  // { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' },
  { label: 'All', value: null },
];

function getTodayIsoDate() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// const viewMode = ref('card');
const ORDERS_VIEW_MODE_KEY = 'oo_orders_view_mode';

function getInitialOrdersViewMode() {
  try {
    const saved = localStorage.getItem(ORDERS_VIEW_MODE_KEY);
    if (saved === 'list' || saved === 'card') return saved;
  } catch {
    // Ignore storage errors
  }
  return 'card';
}

const viewMode = ref(getInitialOrdersViewMode());

watch(viewMode, (mode) => {
  try {
    localStorage.setItem(ORDERS_VIEW_MODE_KEY, mode);
  } catch {

  }
});




const loading = ref(false);
const error = ref('');
const lastUpdated = ref('');
let isUnmounted = false;
let hasInitializedIds = false;
let navigatingToSale = false;
const knownOrderIds = new Set();
// Show orer each page
const filters = ref({
  status: 'submitted',
  posting_date: getTodayIsoDate(),
  page: 1,
  page_size: 6,
});

const knownLastPage = ref(null);
const orders = ref([]);

const activeStatusLabel = computed(() => {
  const tab = statusTabs.find((t) => t.value === filters.value.status);
  return tab ? tab.label : '';
});

const isNextDisabled = computed(() => {
  if (loading.value) return true;
  if (knownLastPage.value === null) return true;
  return filters.value.page >= knownLastPage.value;
});

const visiblePages = computed(() => {
  const maxWindow = 4;
  let start = Math.max(1, filters.value.page - 2);
  let end = start + maxWindow - 1;

  if (knownLastPage.value !== null) {
    end = Math.min(knownLastPage.value, end);
    start = Math.max(1, end - maxWindow + 1);
  }

  const pages = [];
  for (let p = start; p <= end; p++) {
    pages.push(p);
  }
  return pages;
});

socket.on("NotifyOnlineOrder", async (arg) => { 
  await refreshOrders();
});

function notifyResult(type, msg) {
  if (!msg) return;
  const cleanMsg = String(msg).replace(/<[^>]*>/g, '').trim();
  if (!cleanMsg) return;

  if (type === 'error') {
    toast.error(cleanMsg);
  } else {
    toast.success(cleanMsg);
  }
}

async function fetchOrders({ silent = false } = {}) {
  if (!silent) {
    loading.value = true;
    error.value = '';
  }

  try {
    const context = {
      status: filters.value.status,
      page: filters.value.page,
      page_size: filters.value.page_size,
    };
    if (filters.value.posting_date) {
      context.posting_date = filters.value.posting_date;
    }

    const res = await app.postApi(
      'emenu_integration.order.get_order',
      { context },
      '',
      false
    );

    if (res?.error) {
      throw new Error(extractApiError(res.error, 'Failed to load orders.'));
    }

    const result = res?.data ?? res?.message ?? res;
    if (
      !Array.isArray(result?.orders) ||
      !Number.isInteger(result.total_record) ||
      result.total_record < 0
    ) {
      throw new Error('The online orders API returned an unexpected response.');
    }

    let hasNewSubmittedOrder = false;
    for (const ord of result.orders) {
      if (!ord?.id) continue;
      if (
        hasInitializedIds &&
        !knownOrderIds.has(ord.id) &&
        String(ord.status || '').toLowerCase() === 'submitted'
      ) {
        hasNewSubmittedOrder = true;
      }
      knownOrderIds.add(ord.id);
    }
    hasInitializedIds = true;

    orders.value = result.orders;
    error.value = '';
    knownLastPage.value = Math.max(1, Math.ceil(result.total_record / filters.value.page_size));
    lastUpdated.value = new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });

    if (silent && hasNewSubmittedOrder) {
      notifyResult('success', 'New online order received.');
    }
  } catch (err) {
    if (!silent) {
      error.value = extractApiError(err, 'Failed to load orders.');
      orders.value = [];
    }
  } finally {
    if (!silent) {
      loading.value = false;
    }
  }
}

async function handleIncomingOrderEvent(payload) {
  const incomingId = payload?.order_id || payload?.id || payload?.data?.order_id;
  const isNewId = incomingId && !knownOrderIds.has(incomingId);

  if (isNewId && filters.value.status !== 'submitted' && filters.value.status !== null) {
    knownOrderIds.add(incomingId);
    notifyResult('success', 'New online order received.');
    return;
  }

  await fetchOrders({ silent: true });

  if (isNewId && !knownOrderIds.has(incomingId)) {
    knownOrderIds.add(incomingId);
    notifyResult('success', 'New online order received.');
  }
}

const onFrappeNotifyOrder = async (payload) => {
  await handleIncomingOrderEvent(payload || {});
};

function openOrderDetail(order) {
  if (!order?.id) return;
  activeOrderId.value = order.id;
}

async function selectStatus(status) {
  filters.value.status = status;
  filters.value.page = 1;
  knownLastPage.value = null;
  await fetchOrders();
}

async function selectDate(postingDate) {
  filters.value.posting_date = postingDate || '';
  filters.value.page = 1;
  knownLastPage.value = null;
  await fetchOrders();
}




async function onOrderDetailResolved(result) {
  activeOrderId.value = null;
  if (result?.closeDialog && isEmbedded.value) {
    emit('close');
    return;
  }
  if (result?.refresh) {
    await refreshOrders();
  }
}

async function refreshOrders() {
  knownLastPage.value = null;
  await fetchOrders();
}

async function goToPage(pageNum) {
  const target = Math.max(1, pageNum);
  if (target === filters.value.page || loading.value) return;
  filters.value.page = target;
  await fetchOrders();
}

onMounted(async () => {
  const el = rootEl.value?.$el || rootEl.value;
  if (props.hideHeader || el?.closest?.('.v-dialog, .v-overlay__content, .p-dialog')) {
    isEmbedded.value = true;
  }

  await fetchOrders();

  const appSocket = window.socket || window.app?.socket;
  if (typeof appSocket?.on === 'function') {
    appSocket.on('NotifyOnlineOrder', onFrappeNotifyOrder);
  }
});

onBeforeUnmount(() => {
  isUnmounted = true;

  const appSocket = window.socket || window.app?.socket;
  if (typeof appSocket?.off === 'function') {
    appSocket.off('NotifyOnlineOrder', onFrappeNotifyOrder);
  }
});
</script>

<style>
/* .oo-full-width.page-container,
.oo-full-width .page-container {
  max-width: 100% !important;
  width: 100% !important;
} */
.oo-full-width,
.oo-full-width.page-container,
.oo-full-width .page-container {
  max-width: 100% !important;
  width: 100% !important;
  min-width: 0;
  overflow-x: hidden;
  box-sizing: border-box;
}

.oo-inline-messages {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.oo-datepicker.p-datepicker {
  position: relative;
  width: 185px;
}
.oo-datepicker .p-datepicker-input {
  width: 100% !important;
  padding: 9px 52px 9px 12px !important;
  border-radius: 6px !important;
  border: 1px solid #d1d5db !important;
  background: #ffffff !important;
  color: #1f2937 !important;
  font-size: 0.95rem !important;
}
.oo-datepicker .p-datepicker-input:enabled:focus {
  border-color: #d97706 !important;
  box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.15) !important;
}
.oo-datepicker .p-datepicker-input-icon-container,
.oo-datepicker .p-datepicker-clear-icon {
  color: #6b7280 !important;
}

.oo-datepicker-panel,
.oo-datepicker-panel.p-datepicker-panel {
  --p-datepicker-panel-background: #ffffff;
  --p-datepicker-panel-border-color: #e5e7eb;
  --p-datepicker-panel-color: #1f2937;
  --p-datepicker-header-background: #ffffff;
  --p-datepicker-header-border-color: #f3f4f6;
  --p-datepicker-header-color: #111827;
  --p-datepicker-week-day-color: #6b7280;
  --p-datepicker-date-color: #1f2937;
  --p-datepicker-date-hover-background: #fef3c7;
  --p-datepicker-date-hover-color: #92400e;
  --p-datepicker-date-selected-background: #d97706;
  --p-datepicker-date-selected-color: #ffffff;
  --p-datepicker-today-background: #fef3c7;
  --p-datepicker-today-color: #b45309;

  z-index: 3500 !important;
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1f2937 !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 8px !important;
  padding: 12px !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12) !important;
}
.oo-datepicker-panel .p-datepicker-header {
  background: #ffffff !important;
  color: #111827 !important;
  border-bottom: 1px solid #f3f4f6 !important;
}
.oo-datepicker-panel .p-datepicker-title button,
.oo-datepicker-panel .p-datepicker-select-month,
.oo-datepicker-panel .p-datepicker-select-year,
.oo-datepicker-panel .p-datepicker-prev-button,
.oo-datepicker-panel .p-datepicker-next-button {
  color: #111827 !important;
  background: transparent !important;
}
.oo-datepicker-panel .p-datepicker-title button:not(:disabled):hover,
.oo-datepicker-panel .p-datepicker-select-month:not(:disabled):hover,
.oo-datepicker-panel .p-datepicker-select-year:not(:disabled):hover,
.oo-datepicker-panel .p-datepicker-prev-button:not(:disabled):hover,
.oo-datepicker-panel .p-datepicker-next-button:not(:disabled):hover {
  background: #fef3c7 !important;
  color: #92400e !important;
}
.oo-datepicker-panel table,
.oo-datepicker-panel thead,
.oo-datepicker-panel tbody,
.oo-datepicker-panel tr,
.oo-datepicker-panel tr:nth-child(even),
.oo-datepicker-panel tr:nth-child(odd),
.oo-datepicker-panel th,
.oo-datepicker-panel td {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
}
.oo-datepicker-panel .p-datepicker-weekday {
  color: #6b7280 !important;
  font-weight: 600 !important;
}
.oo-datepicker-panel .p-datepicker-day,
.oo-datepicker-panel .p-datepicker-month,
.oo-datepicker-panel .p-datepicker-year {
  color: #1f2937 !important;
  background: transparent !important;
}
.oo-datepicker-panel .p-datepicker-other-month .p-datepicker-day {
  color: #9ca3af !important;
}
.oo-datepicker-panel .p-datepicker-day:not(.p-datepicker-day-selected):not(.p-disabled):hover,
.oo-datepicker-panel .p-datepicker-month:not(.p-datepicker-month-selected):not(.p-disabled):hover,
.oo-datepicker-panel .p-datepicker-year:not(.p-datepicker-year-selected):not(.p-disabled):hover {
  background: #fef3c7 !important;
  color: #92400e !important;
}
.oo-datepicker-panel .p-datepicker-today > .p-datepicker-day:not(.p-datepicker-day-selected) {
  background: #fef3c7 !important;
  color: #b45309 !important;
  font-weight: 600 !important;
}
.oo-datepicker-panel .p-datepicker-day-selected,
.oo-datepicker-panel [data-p-selected="true"],
.oo-datepicker-panel .p-datepicker-month-selected,
.oo-datepicker-panel .p-datepicker-year-selected {
  background: #d97706 !important;
  color: #ffffff !important;
  font-weight: 600 !important;
}


.online-orders-wrapper {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding-top: 4px;
  font-size: 1rem;
  line-height: 1.5;
  color: #1f2937;
  box-sizing: border-box;
}
.online-orders-wrapper.oo-fixed-modal-height {
  min-height: 490px;
  display: flex;
  flex-direction: column;
}
.oo-toolbar {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}
.oo-status-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.oo-tab {
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #374151;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}
.oo-tab:hover:not(:disabled) {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}
.oo-tab-active {
  background: #d97706;
  color: #ffffff;
  border-color: #d97706;
}
.oo-tab-active:hover:not(:disabled) {
  background: #b45309;
  border-color: #b45309;
  color: #ffffff;
}
.oo-toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}
.oo-date-filter {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.oo-muted {
  font-size: 0.875rem;
  color: #6b7280;
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
.oo-btn-brand {
  background: #d97706;
  color: #ffffff;
  border-color: #d97706;
}
.oo-btn-brand:hover:not(:disabled) {
  background: #b45309;
  border-color: #b45309;
}
.oo-btn.oo-active {
  background: #374151;
  color: #ffffff;
  border-color: #374151;
}
.oo-btn-small {
  padding: 6px 14px;
  font-size: 0.875rem;
}
.oo-toggle-group {
  display: inline-flex;
}
.oo-toggle-group .oo-btn:first-child {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.oo-toggle-group .oo-btn:last-child {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-left: none;
}
.oo-content-panel {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  min-height: 360px;
}
.oo-fixed-modal-height .oo-content-panel {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.oo-state-box {
  margin: auto;
  padding: 40px 20px;
  text-align: center;
  color: #6b7280;
  font-size: 1rem;
}
.oo-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.oo-order-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 18px;
  cursor: pointer;
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.oo-order-card:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.12);
}
.oo-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.oo-order-title {
  font-weight: 700;
  font-size: 1.0625rem;
  color: #111827;
  word-break: break-word;
}
.oo-card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}
.oo-meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  color: #374151;
}
.oo-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f3f4f6;
  padding-top: 12px;
  margin-top: auto;
}
.oo-total {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
}
.oo-view-link {
  display: inline-flex;
  align-items: center;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #d97706;
}
.oo-table-wrap {
  width: 100%;
  overflow-x: auto;
}
.oo-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1rem;
}
.oo-table th,
.oo-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}
.oo-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
}
.oo-table-row {
  cursor: pointer;
}
.oo-table-row:hover {
  background: #fffbeb;
}
.oo-text-right {
  text-align: right !important;
}
.oo-text-center {
  text-align: center !important;
}
.oo-font-semibold {
  font-weight: 600;
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
.oo-pagination {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
}
.oo-page-btn {
  min-width: 42px;
  padding: 10px 14px;
}
.oo-page-active {
  background: #d97706;
  color: #ffffff;
  border-color: #d97706;
}
.oo-page-active:hover:not(:disabled) {
  background: #b45309;
  border-color: #b45309;
}

@media (max-width: 640px) {
  .oo-full-width .v-container {
    padding-left: 8px !important;
    padding-right: 8px !important;
  }

  .online-orders-wrapper.oo-fixed-modal-height {
    min-height: calc(100dvh - 130px);
  }

  .oo-toolbar {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    margin-bottom: 10px;
  }

  /* Fit all 5 status tabs evenly across 100% width with no right-edge clipping */
  .oo-status-tabs {
    display: flex;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    flex-wrap: nowrap;
    gap: 4px;
  }

  .oo-tab {
    flex: 1 1 auto;
    min-width: 0;
    padding: 7px 4px;
    font-size: 0.75rem;
    text-align: center;
    white-space: nowrap;
  }

  /* Row 2: Date picker + List/Card toggle + Refresh */
  .oo-toolbar-actions {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    flex-wrap: nowrap;
    gap: 6px;
    justify-content: space-between;
  }

  .oo-toolbar-actions .oo-muted {
    display: none;
  }

  .oo-date-filter {
    flex: 1 1 auto;
    min-width: 0;
    max-width: 100%;
  }

  .oo-datepicker.p-datepicker {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
  }

  .oo-datepicker .p-datepicker-input {
    width: 100% !important;
    min-width: 0 !important;
    padding: 6px 38px 6px 9px !important;
    font-size: 0.8125rem !important;
  }

  .oo-toggle-group {
    flex-shrink: 0;
  }

  .oo-toggle-group .oo-btn {
    padding: 6px 8px;
    font-size: 0.8125rem;
  }

  .oo-toolbar-actions .oo-btn-brand {
    flex-shrink: 0;
    padding: 6px 9px;
    font-size: 0.8125rem;
    white-space: nowrap;
  }

  /* Content panel & cards */
  .oo-content-panel {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    padding: 10px;
    min-height: 280px;
  }

  .oo-card-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 10px;
  }

  .oo-order-card {
    min-width: 0;
    padding: 14px;
  }

  .oo-card-top {
    margin-bottom: 10px;
  }

  .oo-card-meta {
    gap: 6px;
    margin-bottom: 10px;
  }

  .oo-meta-item {
    font-size: 0.9375rem;
  }

  .oo-pagination {
    gap: 4px;
    margin-top: 10px;
  }

  .oo-page-btn {
    min-width: 34px;
    padding: 6px 10px;
    font-size: 0.875rem;
  }
}

@media (max-width: 430px) {
  .oo-toolbar-actions .oo-btn-brand {
    font-size: 0;
    padding: 6px 9px;
  }
  .oo-toolbar-actions .oo-btn-brand .v-icon {
    margin-right: 0 !important;
    font-size: 18px !important;
  }
}

.c-notices {
  z-index: 9999 !important;
}
</style>