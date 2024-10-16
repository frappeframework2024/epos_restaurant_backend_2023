import { createRouter, createWebHistory } from "vue-router";
import CheckIn from "@/views/CheckIn.vue";
import CheckInUI from "@/views/CheckInUI.vue";
import SaleCoupon from "@/views/SaleCoupon.vue";
import Home from "@/views/home.vue";


const routes = [
  { path: "/", redirect: '/gym/check-in' },
  { path: "/gym/check-in",name: "CheckIn",component: CheckIn,},
  { path: "/gym/sale-coupon",name: "SaleCoupon",component: SaleCoupon,},
  { path: "/gym/home",name: "Home",component: Home,},
  { path: "/gym/check-in-ui",name: "CheckInUI",component: CheckInUI,}
];

const router = createRouter({
  base: "/gym/",
  history: createWebHistory(),
  routes,
});

export default router;
