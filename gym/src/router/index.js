import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";

const routes = [
  { path: "/", redirect: '/gym' },
  { path: "/gym",name: "Home",component: Home,}
];

const router = createRouter({
  base: "/gym/",
  history: createWebHistory(),
  routes,
});

export default router;
