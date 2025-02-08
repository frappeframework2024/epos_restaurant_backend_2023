import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import BarcodeBuilder from '@/views/barcode-builder/BarcodeBuilder.vue'
import ServerReport from '@/views/server-report/ServerReport.vue'

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
  },
  {
    path: "/embed/server-report",
    name: "ServerReport",
    component: ServerReport,
  }
];

const router = createRouter({
  base: "/embed/",
  history: createWebHistory(),
  routes,
});

export default router;
