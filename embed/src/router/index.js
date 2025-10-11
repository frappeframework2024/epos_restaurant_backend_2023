import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import BarcodeBuilder from '@/views/barcode-builder/BarcodeBuilder.vue'
import ServerReport from '@/views/server-report/ServerReport.vue'
import DigitalCoupon from '@/views/digital-coupon/Home.vue'
import Transaction from '@/views/digital-coupon/Transaction.vue'
import MyAccount from '@/views/digital-coupon/MyAccount.vue'
import ComCouponTransactionDetail from '@/views/digital-coupon/components/ComCouponTransactionDetail.vue'
import { useAuth } from "@/hooks/useAuth.js";
const {isAuthorize} = useAuth()
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
    meta: { layout: "DigitalCouponLayout",requiresAuth: true }
  },
  {
    path: "/embed/ecoupon/transaction",
    name: "eCouponTransaction",
    component: Transaction,
    meta: { layout: "DigitalCouponLayout",requiresAuth: true }
  },
  {
    path: "/embed/ecoupon/my-account",
    name: "eCouponMyAccopunt",
    component: MyAccount,
    meta: { layout: "DigitalCouponLayout",requiresAuth: true }
  },
  {
    path: "/embed/ecoupon/transaction-detail/:id",
    name: "eCouponTransactionDetail",
    component: ComCouponTransactionDetail,
    meta: { layout: "DigitalCouponLayout",requiresAuth: true }
  }
];

const router = createRouter({
  base: "/embed/",
  history: createWebHistory(),
  routes,
});


router.beforeEach(async (to, from, next) => {
  if(to.meta.requiresAuth){
    if(   !isAuthorize.value){
      window.location = "/login"
    }else {
      next()
    }
  }else {
next();
  }
  
});

export default router;
