
//core

//theme
// import "primevue/resources/themes/lara-light-indigo/theme.css";
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import DynamicDialog from 'primevue/dynamicdialog';

//icon 
import 'primeicons/primeicons.css';
// flex css
import '/node_modules/primeflex/primeflex.css'

import { createApp, reactive } from "vue";
import App from "./App.vue";
import PrimeVue from 'primevue/config';

import router from './router';
import { show_alert } from '@/utils/index.js';

import { FrappeApp } from 'frappe-js-sdk';
import DialogService from 'primevue/dialogservice';

//
import Button from 'primevue/button';
import AutoComplete from 'primevue/autocomplete';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';
import ComIsLoadingPanel from '@/components/ComIsLoadingPanel.vue';

const app = createApp(App);

const frappe = new FrappeApp();


// Plugins
app.use(router);
app.use(PrimeVue);
app.use(DialogService);
app.use(ToastService);
// Global Properties,
// components can inject this
app.provide("$frappe", frappe);
window.db = frappe.db()
window.call = frappe.call()
window.auth = frappe.auth()

window.show_alert =show_alert


app.component('DynamicDialog', DynamicDialog);
app.component('Button', Button);
app.component('AutoComplete', AutoComplete)

app.component('ComIsLoadingPanel', ComIsLoadingPanel)

app.component('Toast', Toast);


// Configure route gaurds
router.beforeEach(async (to, from, next) => {
	
	next();		
});

app.mount("#app");
