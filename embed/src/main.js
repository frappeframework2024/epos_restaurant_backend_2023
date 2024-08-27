import { createApp, reactive } from "vue";
import App from "./App.vue";
import "primeicons/primeicons.css";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import "/node_modules/primeflex/primeflex.css";
import "./assets/main.css";




const app = createApp(App);

import router from "./router";

// Plugins
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});

 
 
// Configure route gaurds
router.beforeEach(async (to, from, next) => {
  next();
});

 
app.mount("#app");
