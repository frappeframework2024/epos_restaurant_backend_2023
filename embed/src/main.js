import { createApp, reactive } from "vue";
import App from "./App.vue";
import "@/helpers/global-function.js"

import "primeicons/primeicons.css";
import PrimeVue from "primevue/config";
import Aura from "@primevue/themes/aura";
import "/node_modules/primeflex/primeflex.css";
import "./assets/main.css";
import DraggableResizableVue from 'draggable-resizable-vue3'
import VueBarcode from '@chenfengyuan/vue-barcode';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import DynamicDialog from 'primevue/dynamicdialog';
import DialogService from 'primevue/dialogservice';
import socket from './utils/socketio';




// custom component
import currencyFormat from '@/components/currencyFormat.vue'
import ComIcon from '@/components/ComIcon.vue'
import ComDialogContent from '@/components/ComDialogContent.vue'
import EmptyTemplate from '@/components/EmptyTemplate.vue'
import router from "./router";
import { useAuth } from "./hooks/useAuth";

import i18n from './i18n'


async function initApp() {
const app = createApp(App);
app.use(i18n)
// Make `t` globally accessible
app.config.globalProperties.t = i18n.global.t;  
window.t = i18n.global.t;

app.provide("$socket", socket)


app.use(DraggableResizableVue)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    dark:false
  },
});

app.use(ConfirmationService);
app.use(DialogService);
 
app.use(ToastService);
app.component(VueBarcode.name, VueBarcode);
app.component('DynamicDialog', DynamicDialog);

// use custom components //
app.component('currencyFormat', currencyFormat)
app.component('ComIcon', ComIcon)
app.component('ComDialogContent', ComDialogContent)
app.component('EmptyTemplate', EmptyTemplate)


// Configure route gaurds


 

  const { checkUserLogin } = useAuth()
  await checkUserLogin()   // wait here before app renders

  app.use(router)
  app.mount('#app')
}



 
 
initApp()