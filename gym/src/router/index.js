import { createRouter, createWebHistory } from "vue-router";
import CheckIn from "@/views/CheckIn.vue";

const routes = [
  { path: "/", redirect: '/gym/check-in' },
  { path: "/gym/check-in",name: "CheckIn",component: CheckIn,}
];

const router = createRouter({
  base: "/gym/",
  history: createWebHistory(),
  routes,
});

export default router;
