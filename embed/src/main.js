import { createApp, reactive } from "vue";
import App from "./App.vue";
import "primeicons/primeicons.css";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import "/node_modules/primeflex/primeflex.css";
import "./assets/main.css";
import DraggableResizableVue from 'draggable-resizable-vue3'
import VueBarcode from '@chenfengyuan/vue-barcode';


const app = createApp(App);

import router from "./router";
app.use(DraggableResizableVue)
// Plugins
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});

app.component(VueBarcode.name, VueBarcode);

 
// Configure route gaurds
router.beforeEach(async (to, from, next) => {
  next();
});

 
app.mount("#app");
