import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import AddSale from "../views/sale/AddSale.vue";
import AddSaleNoTable from "../views/sale/AddSaleNoTable.vue";
import Sale from "../views/sale/Sale.vue";
import POSReservationCalendar from "../views/sale/POSReservationCalendar.vue";
import ClosedSaleList from "../views/sale/ClosedSaleList.vue";
import TableLayout from "../views/sale/TableLayout.vue";
import OpenShift from "../views/shift/OpenShift.vue";
import CloseShift from "../views/shift/CloseShift.vue";
import StartWorkingDay from "../views/shift/StartWorkingDay.vue";
import CloseWorkingDay from "../views/shift/CloseWorkingDay.vue";
import CustomerDetail from "../views/customer/CustomerDetail.vue";
import Customer from "../views/customer/Customer.vue";
import TestPage from "../views/TestPage.vue";
import ToDo from "../views/ToDo.vue";
import Landing from "../views/Landing.vue";
import ReceiptList from "@/views/receipt_list/ReceiptList.vue"
import StartupConfig from "@/views/checking_system/StartupConfig.vue"
import CashDrawer from "@/views/cash_drawer/CashDrawer.vue"
import Report from "@/views/report/Report.vue"
import CustomerCreditBlance from "@/views/credit_balance/CustomerCreditBalance.vue"
import VoucherTopUp from "@/views/voucher_top_up/VoucherTopUp.vue"
import ServerError from "@/views/checking_system/ServerError.vue"
import CustomerDisplay from "@/views/customer_display/CustomerDisplay.vue"
import KitchenOrderDisplay from "@/views/kitchen_order_display/KitchenOrderDisplay.vue"
import authRoutes from './auth';
import Setting from '@/views/setting/Setting.vue';
// import BarcodeBuilder from '@/views/barcode_builder/BarcodeBuilder.vue';

const routes = [
  { path: "/", redirect: '/epos_frontend' },
  { path: "/server-error", redirect: '/epos_frontend/server-error' },
  { path: "/epos_frontend", name: "Home", component: Home, meta: { layout: 'main_layout' } },
  { path: '/epos_frontend/startup-config', name: 'StartupConfig', component: StartupConfig, meta: { isStartupConfig: true }, props: true },
  { path: '/epos_frontend/landing:name?', name: 'Landing', component: Landing, meta: { isStartupConfig: true }, props: true },
  { path: "/epos_frontend/add-sale/:name?", name: "AddSale", component: AddSale, meta: { layout: 'sale_layout' } },
  { path: "/epos_frontend/customer-detail/:name?", name: "CustomerDetail", component: CustomerDetail, },
  { path: "/epos_frontend/customer", name: "Customer", component: Customer, meta: { layout: 'main_layout' } },
  { path: "/epos_frontend/sale", name: "Sale", component: Sale, },
  { path: "/epos_frontend/pos-reservation-calendar", name: "POSReservationCalendar", component: POSReservationCalendar, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/table", name: "TableLayout", component: TableLayout, meta: { layout: 'main_layout' } },
  { path: "/epos_frontend/receipt-list", name: "ReceiptList", component: ReceiptList, meta: { layout: 'main_layout' } },
  { path: "/epos_frontend/open-shift", name: "OpenShift", component: OpenShift, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/close-shift", name: "CloseShift", component: CloseShift, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/start-working-day", name: "StartWorkingDay", component: StartWorkingDay, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/close-working-day", name: "CloseWorkingDay", component: CloseWorkingDay, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/cash-drawer", name: "CashDrawer", component: CashDrawer, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/setting", name: "Setting", component: Setting, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/test-page", name: "TestPage", component: TestPage, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/todo", name: "ToDo", component: ToDo, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/report", name: "Report", component: Report, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/credit-balance", name: "CreditBalance", component: CustomerCreditBlance, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/voucher-top-up", name: "VoucherTopUp", component: VoucherTopUp, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/server-error", name: "ServerError", component: ServerError },
  { path: "/epos_frontend/closed-sale-list", name: "ClosedSaleList", component: ClosedSaleList, meta: { layout: "main_layout" } },
  { path: "/epos_frontend/customer-display", name: "CustomerDisplay", component: CustomerDisplay },
  { path: "/epos_frontend/kod", name: "KitchenOrderDisplay", component: KitchenOrderDisplay, meta: { layout: 'kitchen_order_display_layout' } },
  { path: "/epos_frontend/add-quite-sale/:sale_type?", name: "AddSaleNoTable", component: AddSaleNoTable, meta: { layout: "main_layout" } },
  // { path: "/epos_frontend/barcode-builder", name: "BarcodeBuilder", component: BarcodeBuilder, },
  ...authRoutes,
];

const router = createRouter({
  base: "/epos_frontend/",
  history: createWebHistory(),
  routes,
});

export default router;
