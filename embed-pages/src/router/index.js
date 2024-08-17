import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import BarcodeBuilder from "@/views/barcode_builder/BarcodeBuilder.vue";

const routes = [
  { path: "/", redirect: '/embed-pages' },
  { path: "/embed-pages", name: "Home", component: Home },
  { path: "/embed-pages/barcode-builder", name: "BarcodeBuilder", component: BarcodeBuilder },
];

const router = createRouter({
  base: "/embed-pages/",
  history: createWebHistory(),
  routes,
});

export default router;
