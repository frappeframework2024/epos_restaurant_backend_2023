export function getPosContextDefaults(gv) {
  let posStation = gv?.setting?.pos_station || '';
  let posProfile = gv?.setting?.pos_profile || '';

  try {
    const rawDevice = localStorage.getItem('device_setting');
    if (rawDevice) {
      const parsed = JSON.parse(rawDevice);
      posStation = posStation || parsed.station_name || parsed.device_name || parsed.pos_station || '';
      posProfile = posProfile || parsed.pos_profile || '';
    }
    posProfile = posProfile || localStorage.getItem('pos_profile') || '';
    posStation = posStation || localStorage.getItem('pos_station') || '';
  } catch {
    // ignore storage parse errors
  }

  return {
    pos_station: posStation,
    pos_profile: posProfile,
  };
}

export function buildFrappeHeaders() {
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token;
  }
  return headers;
}

export function parseServerMessages(res) {
  const raw = res?._server_messages || res?.data?._server_messages;
  if (!raw) return '';
  try {
    return JSON.parse(raw)
      .map((m) => JSON.parse(m).message || '')
      .map((msg) => msg.replace(/<[^>]*>/g, '').trim())
      .filter(Boolean)
      .join(' | ');
  } catch {
    return '';
  }
}

export function extractApiError(err, fallback = 'Request failed.') {
  if (!err) return fallback;
  if (typeof err === 'string') return err;
  const serverMsg = parseServerMessages(err);
  if (serverMsg) return serverMsg;
  return err.message || err.exception || err.exc_type || fallback;
}

export function parseFrappeError(data, fallback) {
  const serverMsg = parseServerMessages(data);
  if (serverMsg) return serverMsg;
  return data?.exception || data?.message || fallback;
}

export function normalizedStatus(status) {
  return String(status || '').trim().toLowerCase();
}

export function getOrderTitle(order = {}, idx = 0) {
  return (
    order.order_number ||
    order.order_no ||
    order.code ||
    order.reference ||
    order.id ||
    `Order #${idx + 1}`
  );
}

export function getOrderTable(order = {}) {
  return (
    order.table_label ||
    order.table_name ||
    order.table_code ||
    order.table ||
    ''
  );
}

export function getOrderCustomer(order = {}) {
  return order.customer_name || order.customer || order.guest_name || '';
}

export function getOrderTime(order) {
  if (!order) return '';
  const raw =
    order.submitted_at ||
    order.created_at ||
    order.order_date ||
    order.posting_date;
  if (!raw) return '';

  const str = String(raw).trim();

  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
    const [yyyy, mm, dd] = str.split('-');
    return `${dd}/${mm}/${yyyy}`;
  }

  if (/^\d{2}\/\d{2}\/\d{4}/.test(str)) {
    return str.replace(/(\d{2}:\d{2}):\d{2}(\.\d+)?/, '$1');
  }

  const date = new Date(str);
  if (!Number.isNaN(date.getTime())) {
    const dd = String(date.getDate()).padStart(2, '0');
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const yyyy = date.getFullYear();
    const hh = String(date.getHours()).padStart(2, '0');
    const min = String(date.getMinutes()).padStart(2, '0');
    return `${dd}/${mm}/${yyyy}, ${hh}:${min}`;
  }

  return str.replace(/(\d{2}:\d{2}):\d{2}(\.\d+)?/, '$1');
}

export function getOrderTotal(order = {}) {
  return (
    order.total ??
    order.grand_total ??
    order.total_amount ??
    order.amount ??
    null
  );
}

export function getItemQty(item = {}) {
  return item.quantity ?? item.qty ?? 1;
}

export function getItemName(item = {}, idx = 0) {
  return (
    item.product_name ||
    item.name_en ||
    item.name ||
    item.title ||
    item.product_code ||
    `Item ${idx + 1}`
  );
}

export function getItemUnitPrice(item = {}, currency) {
  const qty = Number(getItemQty(item)) || 1;
  const rawTotal = item.total ?? item.line_total ?? item.subtotal;
  const val =
    item.price ??
    item.unit_price ??
    (rawTotal !== null && rawTotal !== undefined ? Number(rawTotal) / qty : null);

  if (val === null || val === undefined) return '-';
  return formatCurrency(val, currency);
}

export function getItemLineTotal(item = {}, currency) {
  const qty = Number(getItemQty(item)) || 1;
  const unitPrice = item.price ?? item.unit_price;
  const val =
    item.total ??
    item.line_total ??
    item.subtotal ??
    (unitPrice !== null && unitPrice !== undefined ? Number(unitPrice) * qty : null);

  if (val === null || val === undefined) return '-';
  return formatCurrency(val, currency);
}

export function formatLabel(key) {
  return String(key)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatAmount(val) {
  const num = Number(val);
  if (Number.isNaN(num)) return String(val);
  return num.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatCurrency(val, currency) {
  const formatted = formatAmount(val);
  if (currency === 'USD') return `$ ${formatted}`;
  if (currency === 'KHR') return `៛ ${formatted}`;
  return currency ? `${currency} ${formatted}` : formatted;
}

export function formatValue(val) {
  if (val === null || val === undefined) return '-';
  if (typeof val === 'boolean') return val ? 'Yes' : 'No';
  if (typeof val === 'object') return JSON.stringify(val);
  return String(val);
}