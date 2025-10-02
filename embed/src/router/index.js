import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import BarcodeBuilder from '@/views/barcode-builder/BarcodeBuilder.vue'
import ServerReport from '@/views/server-report/ServerReport.vue'
import DigitalCoupon from '@/views/digital-coupon/Home.vue'
import Transaction from '@/views/digital-coupon/Transaction.vue'
import MyAccount from '@/views/digital-coupon/MyAccount.vue'

const routes = [
  {
	path: "/",
	name: "Home",
	component: Home,
  },
  {
    path: "/embed/barcode-builder",
    name: "BarcodeBuilder",
    component: BarcodeBuilder,
    meta: { layout: "BlankLayout" }
  },
  {
    path: "/embed/server-report",
    name: "ServerReport",
    component: ServerReport,
    meta: { layout: "BlankLayout" }
  },
  {
    path: "/embed/ecoupon",
    name: "DigitalCoupon",
    component: DigitalCoupon,
    meta: { layout: "DigitalCouponLayout" }
  },
  {
    path: "/embed/ecoupon/transaction",
    name: "eCouponTransaction",
    component: Transaction,
    meta: { layout: "DigitalCouponLayout" }
  },
  {
    path: "/embed/ecoupon/my-account",
    name: "eCouponMyAccopunt",
    component: MyAccount,
    meta: { layout: "DigitalCouponLayout" }
  }
];

const router = createRouter({
  base: "/embed/",
  history: createWebHistory(),
  routes,
});

export default router;
