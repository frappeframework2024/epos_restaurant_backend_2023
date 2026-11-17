<template>
    <main class="min-h-screen bg-slate-50 px-3 pt-4 pb-[calc(6rem+env(safe-area-inset-bottom))] text-slate-800 sm:px-6 sm:pt-6" :aria-busy="loading">
        <div class="mx-auto max-w-5xl space-y-3 sm:space-y-5">
            <Card v-if="loading" role="status" aria-live="polite">
                <template #content>
                    <div class="flex flex-col items-center gap-3 py-10 text-center">
                        <ProgressSpinner class="!h-10 !w-10" strokeWidth="4" aria-label="Loading order" />
                        <h1 class="text-xl font-semibold">Loading your order</h1>
                        <p class="text-sm text-slate-500">Getting the latest order details.</p>
                    </div>
                </template>
            </Card>

            <Card v-else-if="error">
                <template #content>
                    <Message severity="error" icon="mdi mdi-alert-circle-outline" :closable="false">
                        <h1 class="font-semibold">Unable to load order</h1>
                        <p>{{ error }}</p>
                    </Message>
                    <Button v-if="orderId" label="Try again" icon="mdi mdi-refresh" class="mt-4" type="button" @click="loadOrder" />
                </template>
            </Card>

            <template v-else>
                <section class="flex items-start justify-between gap-2" aria-labelledby="order-title">
                    <div class="min-w-0 flex-1">
                        <h1 id="order-title" class="break-words text-xl font-bold sm:text-3xl">Order {{ order.order_number || 'details' }}</h1>
                        <p v-if="order.branch_name" class="mt-1 flex items-start gap-1 text-xs text-slate-500 sm:text-sm">
                            <i class="mdi mdi-store-outline shrink-0" aria-hidden="true"></i>
                            <span class="min-w-0 break-words">{{ order.branch_name }}</span>
                        </p>
                    </div>
                    <Tag :value="statusLabel" :severity="statusSeverity" :icon="'mdi ' + statusIcon" class="shrink-0" rounded />
                </section>

                <Message v-if="statusMessage" severity="info" :icon="'mdi ' + statusIcon" :closable="false" :pt="{ text: { class: '!text-sm !font-normal' } }" role="status" aria-live="polite">
                    {{ statusMessage }}
                </Message>
                <Message v-if="actionError" severity="error" icon="mdi mdi-alert-circle-outline" :closable="false">{{ actionError }}</Message>
                <Message v-if="actionSuccess" severity="success" icon="mdi mdi-check-circle-outline" :closable="false" role="status" aria-live="polite">{{ actionSuccess }}</Message>

                <Card :pt="compactCardLayout" aria-label="Order information">
                    <template #content>
                        <dl class="grid grid-cols-3 gap-3">
                            <div class="min-w-0">
                                <dt class="flex items-center gap-1 text-xs text-slate-500 sm:text-sm">
                                    <i class="mdi mdi-table-furniture" aria-hidden="true"></i> Table
                                </dt>
                                <dd class="mt-1 break-words text-sm font-semibold">{{ order.table_label || order.table_code || '\u2014' }}</dd>
                                <dd v-if="order.table_group_name" class="break-words text-xs text-slate-500">{{ order.table_group_name }}</dd>
                            </div>
                            <div class="min-w-0">
                                <dt class="flex items-center gap-1 text-xs text-slate-500 sm:text-sm">
                                    <i class="mdi mdi-clock-outline" aria-hidden="true"></i> Placed
                                </dt>
                                <dd class="mt-1 text-xs font-semibold sm:text-sm">{{ orderDate }}</dd>
                                <dd v-if="orderTime" class="text-xs text-slate-500">{{ orderTime }}</dd>
                            </div>
                            <div class="min-w-0">
                                <dt class="flex items-center gap-1 text-xs text-slate-500 sm:text-sm">
                                    <i class="mdi mdi-shopping-outline" aria-hidden="true"></i> Quantity
                                </dt>
                                <dd class="mt-1 text-sm font-semibold">{{ totalQuantity }} {{ Number(totalQuantity) === 1 ? 'item' : 'items' }}</dd>
                                <dd class="text-xs text-slate-500">{{ products.length }} {{ products.length === 1 ? 'line' : 'lines' }}</dd>
                            </div>
                        </dl>
                    </template>
                </Card>

                <div class="grid items-start gap-3 sm:gap-5 lg:grid-cols-3">
                    <Card class="min-w-0 lg:col-span-2" :pt="compactCardLayout" aria-labelledby="items-title">
                        <template #title>
                            <div class="flex items-center justify-between gap-3">
                                <h2 id="items-title" class="text-base font-semibold sm:text-lg">Order items</h2>
                                <Badge :value="products.length" severity="info" />
                            </div>
                        </template>
                        <template #content>
                            <ul v-if="products.length" class="m-0 list-none p-0">
                                <li v-for="(product, index) in products" :key="product.line_number ?? index">
                                    <Divider v-if="index > 0" class="!my-2 sm:!my-4" />
                                    <div class="flex items-start gap-3">
                                        <Avatar :label="String(index + 1).padStart(2, '0')" class="!hidden shrink-0 sm:!inline-flex" aria-hidden="true" />
                                        <div class="min-w-0 flex-1">
                                            <div class="flex items-start justify-between gap-3 text-sm sm:text-base">
                                                <h3 class="min-w-0 break-words font-semibold">{{ product.name || product.name_en || product.product_code || 'Item' }}</h3>
                                                <strong class="shrink-0 whitespace-nowrap"><CurrencyFormat :value="product.total_amount" :currency="order.currency" /></strong>
                                            </div>
                                            <div class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500 sm:text-sm">
                                                <Tag :value="product.quantity + ' \u00d7'" severity="info" :aria-label="'Quantity: ' + product.quantity" />
                                                <span><CurrencyFormat :value="product.price" :currency="order.currency" /> each</span>
                                                <span v-if="product.portion_name" class="min-w-0 break-words">&middot; {{ product.portion_name }}</span>
                                                <span v-if="product.product_code" class="hidden min-w-0 break-words sm:inline">&middot; {{ product.product_code }}</span>
                                            </div>
                                            <ul v-if="product.modifiers?.length" class="mt-1 list-none space-y-1 p-0 text-xs text-slate-500 sm:text-sm" aria-label="Selected options">
                                                <li v-for="(modifier, modifierIndex) in product.modifiers" :key="modifierIndex" class="flex items-start gap-1">
                                                    <i class="mdi mdi-plus shrink-0" aria-hidden="true"></i>
                                                    <span class="min-w-0 break-words">{{ modifierLabel(modifier) }}</span>
                                                </li>
                                            </ul>
                                            <Message v-if="product.note" severity="warn" icon="mdi mdi-note-text-outline" :closable="false" class="mt-2" :pt="{ text: { class: '!text-sm !font-normal' } }">
                                                <span class="whitespace-pre-wrap break-words">{{ product.note }}</span>
                                            </Message>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                            <Message v-else severity="info" icon="mdi mdi-basket-outline" :closable="false">No items in this order.</Message>
                        </template>
                    </Card>

                    <aside class="min-w-0 lg:sticky lg:top-6" aria-labelledby="summary-title">
                        <Card :pt="compactCardLayout">
                            <template #content>
                                <div class="flex flex-wrap items-center justify-between gap-3">
                                    <h2 id="summary-title" class="text-sm font-semibold">Total <span class="ml-1 text-xs font-normal text-slate-500">{{ order.currency || 'USD' }}</span></h2>
                                    <strong class="break-all text-2xl sm:text-3xl"><CurrencyFormat :value="order.total_amount" :currency="order.currency" /></strong>
                                </div>
                                <details class="mt-2 text-xs text-slate-500">
                                    <summary class="cursor-pointer">Order reference</summary>
                                    <p class="mt-1 break-all font-mono">{{ order.id || orderId }}</p>
                                </details>
                            </template>
                        </Card>
                    </aside>
                </div>

                <footer class="hidden items-center justify-center gap-2 py-2 text-xs text-slate-500 sm:flex">
                    <i class="mdi mdi-receipt-text-outline" aria-hidden="true"></i> Online order details &middot; ePOS
                </footer>
                <div class="fixed inset-x-0 bottom-0 z-20 border-t border-slate-200 bg-white px-3 pt-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))] sm:px-6" role="group" aria-label="Order actions">
                    <div class="mx-auto flex max-w-5xl justify-end gap-3">
                        <Button label="Cancel" icon="mdi mdi-close" severity="danger" outlined type="button" class="!h-12 flex-1 sm:w-40 sm:flex-none" />
                        <Button :label="confirmationSent ? 'Confirmed' : 'Accept'" icon="mdi mdi-check" type="button" class="!h-12 flex-1 sm:w-40 sm:flex-none" :loading="checkingTable || confirmingOrder" :disabled="!canAccept || confirmationOpen || orderPickerVisible" @click="onAccept" />
                    </div>
                </div>
                <ConfirmDialog :key="orderId" :group="confirmationGroup" class="w-11/12 max-w-md" :draggable="false" />
                <Drawer
                    v-model:visible="orderPickerVisible"
                    position="bottom"
                    header="Choose an order"
                    class="!h-auto !max-h-[85dvh]"
                    :blockScroll="true"
                    :dismissable="!confirmingOrder"
                    :showCloseIcon="!confirmingOrder"
                    :closeOnEscape="!confirmingOrder"
                    :aria-busy="confirmingOrder"
                >
                    <div class="mx-auto max-w-3xl space-y-4">
                        <p class="text-sm text-slate-500">
                            Table {{ order.table_label || order.table_code }} has {{ tableOrders.length }} open {{ tableOrders.length === 1 ? 'order' : 'orders' }}.
                            Add these items to an existing order or create a new order at this table.
                        </p>
                        <Message v-if="actionError" severity="error" icon="mdi mdi-alert-circle-outline" :closable="false">{{ actionError }}</Message>
                        <div class="max-h-[45vh] space-y-3 overflow-y-auto p-1" role="radiogroup" aria-label="Choose an existing order or create a new order">
                            <Card
                                v-for="(option, index) in tableOrderOptions"
                                :key="option.value"
                                class="border border-slate-200"
                                :class="[
                                    selectedSaleName === option.value ? '!border-emerald-500 !bg-emerald-50' : '',
                                    confirmingOrder ? 'cursor-default opacity-60' : 'cursor-pointer',
                                ]"
                                @click="!confirmingOrder && (selectedSaleName = option.value)"
                            >
                                <template #content>
                                    <div class="flex min-w-0 items-start gap-3">
                                        <RadioButton
                                            v-model="selectedSaleName"
                                            :inputId="'table-order-choice-' + index"
                                            name="online-order-destination"
                                            :value="option.value"
                                            :disabled="confirmingOrder"
                                            class="mt-1 shrink-0"
                                        />
                                        <label :for="'table-order-choice-' + index" class="min-w-0 flex-1 cursor-pointer">
                                            <span class="flex flex-wrap items-center justify-between gap-2">
                                                <strong class="min-w-0 break-words">{{ option.label }}</strong>
                                                <Tag v-if="option.sale?.sale_status" :value="option.sale.sale_status" severity="info" />
                                            </span>
                                            <template v-if="option.sale">
                                                <span class="mt-1 block break-words text-sm">{{ option.sale.customer_name || 'Walk-in customer' }}</span>
                                                <span class="mt-2 flex flex-wrap items-center justify-between gap-3 text-sm">
                                                    <span>{{ option.sale.total_quantity ?? 0 }} items<span v-if="option.sale.seat_number"> &middot; Seat {{ option.sale.seat_number }}</span></span>
                                                    <strong v-if="option.sale.grand_total != null"><CurrencyFormat :value="Number(option.sale.grand_total)" /></strong>
                                                </span>
                                            </template>
                                            <span v-else class="mt-1 block text-sm">Keep this online order separate on the same table.</span>
                                        </label>
                                    </div>
                                </template>
                            </Card>
                        </div>
                    </div>
                    <template #footer>
                        <div class="mx-auto flex max-w-3xl justify-end gap-3 pb-[env(safe-area-inset-bottom)]">
                            <Button label="Not now" severity="secondary" outlined type="button" class="!h-12 flex-1 sm:w-40 sm:flex-none" :disabled="confirmingOrder" @click="orderPickerVisible = false" />
                            <Button label="Confirm" icon="mdi mdi-check" type="button" class="!h-12 flex-1 sm:w-40 sm:flex-none" :loading="confirmingOrder" :disabled="selectedSaleName === null" @click="confirmOrder(selectedSaleName)" />
                        </div>
                    </template>
                </Drawer>
            </template>
        </div>
    </main>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import Avatar from 'primevue/avatar';
import Badge from 'primevue/badge';
import Button from 'primevue/button';
import Card from 'primevue/card';
import ConfirmDialog from 'primevue/confirmdialog';
import ConfirmationEventBus from 'primevue/confirmationeventbus';
import Drawer from 'primevue/drawer';
import RadioButton from 'primevue/radiobutton';
import Divider from 'primevue/divider';
import Message from 'primevue/message';
import ProgressSpinner from 'primevue/progressspinner';
import Tag from 'primevue/tag';

const compactCardLayout = { body: { class: '!gap-3 !p-3 sm:!p-5' } };
const gv = inject("$gv")
const route = useRoute();
const doc = ref(null);
const loading = ref(true);
const error = ref('');
const checkingTable = ref(false);
const confirmingOrder = ref(false);
const confirmationOpen = ref(false);
const confirmationSent = ref(false);
const orderPickerVisible = ref(false);
const tableOrders = ref([]);
const selectedSaleName = ref(null);
const actionError = ref('');
const actionSuccess = ref('');
let requestVersion = 0;

const orderId = computed(() => typeof route.params.order_id === 'string' ? route.params.order_id : '');
const order = computed(() => doc.value?.order || {});
const products = computed(() => Array.isArray(doc.value?.products) ? doc.value.products : []);
const totalQuantity = computed(() => order.value.total_quantity ?? products.value.reduce((total, product) => total + (Number(product.quantity) || 0), 0));
const status = computed(() => String(order.value.status || '').toLowerCase());
const canAccept = computed(() => status.value === 'submitted' && !confirmationSent.value);
const confirmationGroup = computed(() => 'online-order-' + orderId.value);
const tableOrderOptions = computed(() => [
    { label: 'Create a new order', value: '', sale: null },
    ...tableOrders.value.map(sale => ({ label: sale.name, value: sale.name, sale })),
]);
const statusLabel = computed(() => ({
    submitted: 'Submitted', accepted: 'Accepted', completed: 'Completed', cancelled: 'Cancelled',
}[status.value] || (status.value ? status.value.replace(/[_-]/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase()) : 'Status unavailable')));
const statusSeverity = computed(() => ({ submitted: 'warn', accepted: 'info', completed: 'success', cancelled: 'danger' }[status.value] || 'info'));
const statusMessage = computed(() => ({
    submitted: 'Awaiting confirmation.',
    accepted: 'Order accepted.',
    completed: 'Order completed.',
    cancelled: 'Order cancelled.',
}[status.value] || ''));
const statusIcon = computed(() => ({ submitted: 'mdi-clock-outline', accepted: 'mdi-check-circle-outline', completed: 'mdi-check-all', cancelled: 'mdi-close-circle-outline' }[status.value] || 'mdi-information-outline'));
const placedAt = computed(() => {
    const value = order.value.submitted_at || (order.value.posting_date ? `${order.value.posting_date}T00:00:00` : '');
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
});
const orderDate = computed(() => placedAt.value ? new Intl.DateTimeFormat(undefined, { day: 'numeric', month: 'short', year: 'numeric' }).format(placedAt.value) : '—');
const orderTime = computed(() => placedAt.value && order.value.submitted_at ? new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(placedAt.value) : '');
 

 
function modifierLabel(modifier) {
    if (typeof modifier === 'string') return modifier;
    return modifier?.name || modifier?.option_name || modifier?.modifier_name || modifier?.label || 'Option';
}

async function loadOrder() {
    const version = ++requestVersion;
    const id = orderId.value;
    loading.value = true;
    error.value = '';
    doc.value = null;
    checkingTable.value = false;
    confirmingOrder.value = false;
    confirmationOpen.value = false;
    confirmationSent.value = false;
    orderPickerVisible.value = false;
    tableOrders.value = [];
    selectedSaleName.value = null;
    actionError.value = '';
    actionSuccess.value = '';

    if (!id) {
        error.value = 'The order reference is missing. Please open a valid order link.';
        loading.value = false;
        return;
    }

    try {
        const res = await app.postApi('emenu_integration.order.get_order', {
            context: { order_id: id },
        }, '', false);
        if (version !== requestVersion) return;
        if (!res?.data?.order || !Array.isArray(res.data.products)) {
            error.value = 'Order details are unavailable. Please try again.';
            return;
        }
        doc.value = res.data;
    } catch {
        if (version === requestVersion) error.value = 'Could not load the order. Check your connection and try again.';
    } finally {
        if (version === requestVersion) loading.value = false;
    }
}

async function onAccept() {
    if (checkingTable.value || confirmingOrder.value || confirmationOpen.value || orderPickerVisible.value || !canAccept.value) return;
    actionError.value = '';
    actionSuccess.value = '';
    if (!gv?.setting?.pos_profile || !order.value.table_id) {
        actionError.value = 'The POS profile or table reference is missing. Please reload the order.';
        return;
    }

    const version = requestVersion;
    checkingTable.value = true;
    try {
        const res = await app.postApi('emenu_integration.order.get_current_table_orders', {
            pos_profile: gv.setting.pos_profile,
            table_id: order.value.table_id,
        }, '', false);
        if (version !== requestVersion) return;
        if (res?.error || !Array.isArray(res?.data)) throw new Error('Unable to check table orders.');

        tableOrders.value = res.data;
        selectedSaleName.value = null;
        if (res.data.length) {
            orderPickerVisible.value = true;
        } else {
            confirmationOpen.value = true;
            // Use the page's ConfirmDialog without changing the app-wide plugin setup.
            ConfirmationEventBus.emit('confirm', {
                group: confirmationGroup.value,
                header: 'Confirm online order',
                message: 'Create a new order for table ' + (order.value.table_label || order.value.table_code || '') + '?',
                icon: 'mdi mdi-help-circle-outline',
                acceptLabel: 'Confirm',
                rejectLabel: 'Not now',
                rejectProps: { severity: 'secondary', outlined: true },
                accept: () => {
                    confirmationOpen.value = false;
                    if (version === requestVersion) confirmOrder(null);
                },
                reject: () => { confirmationOpen.value = false; },
                onHide: () => { confirmationOpen.value = false; },
            });
        }
    } catch {
        if (version === requestVersion) actionError.value = "Could not check this table's orders. Please try again.";
    } finally {
        if (version === requestVersion) checkingTable.value = false;
    }
}

async function confirmOrder(saleName) {
    if (confirmingOrder.value || !canAccept.value) return;
    if (saleName && !tableOrders.value.some(sale => sale.name === saleName)) {
        actionError.value = 'Please choose an available order.';
        return;
    }
    const version = requestVersion;
    const context = {
        order_id: orderId.value,
        pos_profile: gv.setting.pos_profile,
        table_id: order.value.table_id,
        sale_name: saleName || null,
    };
    confirmingOrder.value = true;
    actionError.value = '';
    try {
        const res = await app.postApi('emenu_integration.order.confirm_order', { context }, '', false);
        if (version !== requestVersion) return;
        if (!res || res.error || res.data === false) throw new Error('Unable to confirm order.');
        orderPickerVisible.value = false;
        confirmationSent.value = true;
        actionSuccess.value = 'Order confirmation sent successfully.';
    } catch {
        if (version === requestVersion) actionError.value = 'Could not confirm the order. Please try again.';
    } finally {
        if (version === requestVersion) confirmingOrder.value = false;
    }
}

watch(orderId, loadOrder, { immediate: true });
onBeforeUnmount(() => { requestVersion += 1; });
let socket;
onMounted(()=>{
    socket = new WebSocket(
    `wss://angkor-emenu-api.pheakdey-micronet.workers.dev/api/integrations/pos/orders/ws`,
  );

  socket.onopen = () => { status.value = "Listening for orders"; };
  socket.onclose = () => { status.value = "Disconnected"; };
  socket.onmessage = ({ data }) => {
    const event = JSON.parse(data);
    console.log(event);
  };
})
</script>
