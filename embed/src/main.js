import { createApp, reactive } from "vue";
import App from "./App.vue";
import "primeicons/primeicons.css";
import "primeflex/primeflex.css";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";

//Import PrimeVue Components
import Button from "primevue/button";
import Checkbox from "primevue/checkbox";
import FloatLabel from "primevue/floatlabel";
import InputText from "primevue/inputtext";
import Fieldset from "primevue/fieldset";
import Slider from "primevue/slider";

const app = createApp(App);

import router from "./router";

// Plugins
app.use(router);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});

// PrimeVue Components

app.component("Button", Button);
app.component("Checkbox", Checkbox);
app.component("FloatLabel", FloatLabel);
app.component("InputText", InputText);
app.component("Fieldset", Fieldset);
app.component("Slider", Slider);

// Configure route gaurds
router.beforeEach(async (to, from, next) => {
  next();
});

app.mount("#app");
