import './index.css';
import { createApp, reactive } from "vue";

import App from "./App.vue";

import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

import '@mdi/font/css/materialdesignicons.css'
import { vue3Debounce } from 'vue-debounce'
//import VueNumberFormat from 'vue-number-format'
import NumberFormat from 'number-format.js'
import CurrencyFormat from './components/CurrencyFormat.vue';
import ComPlaceholder from './components/layout/components/ComPlaceholder.vue'
import ComAutoComplete from './components/form/ComAutoComplete.vue'
import ComTableView from './components/table/table_view/ComTableView.vue'
import ComTdImage from './components/table/table_view/ComTdImage.vue'
import ComInput from './components/form/ComInput.vue'
import ComPrintPreview from './components/ComPrintPreview.vue'
import ComChip from './components/ComChip.vue'
import ComModal from './components/ComModal.vue'
import Avatar from "vue3-avatar";
import socket from './utils/socketio';
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';

 


import DialogService from 'primevue/dialogservice';
import Vue3DraggableResizable from 'vue3-draggable-resizable'
//default styles
import 'vue3-draggable-resizable/dist/Vue3DraggableResizable.css'



import router from './router';
import call from "./utils/call";

import Auth from "./utils/auth";
import Sale from "./providers/sale";
import KOD from "./providers/kod";
import POSLicense from "./providers/pos_license";
import TableLayout from "./providers/table_layout";
import Gv from "./providers/gv";
import Product from "./providers/product";
import Screen from "./providers/screen";
import moment from "./utils/moment";
import KeyStroke from './plugin/key_stroke';
import store from "./store";
import Toaster from "@meforma/vue-toaster";
import { resourcesPlugin } from "./resources"
import { FrappeApp } from 'frappe-js-sdk';
import { setConfig, frappeRequest } from './resource';
import MasonryWall from '@yeger/vue-masonry-wall'
setConfig('resourceFetcher', frappeRequest)



import { createBottomSheet } from 'bottom-sheet-vue3'
import 'bottom-sheet-vue3/style.css'
// i18n
import { i18n } from "./i18n";
import { mainTheme, secondaryTheme } from '@/utils/theme.js';
const app = createApp(App);

const frappe = new FrappeApp();
const auth = reactive(new Auth());
const gv = reactive(new Gv());
const sale = reactive(new Sale());
const kod = reactive(new KOD());
const pos_license = reactive(new POSLicense());
const tableLayout = reactive(new TableLayout());
const product = reactive(new Product());
const screen = reactive(new Screen());



const vuetify = createVuetify({
	components,
	directives,
	icons: {
		defaultSet: 'mdi',
	},
	display: {
		mobileBreakpoint: 'md',
	},
	 theme: {
	 	defaultTheme: 'mainTheme',
		themes: {
			mainTheme,
	 	},
	   },
	// theme: {
	// 	defaultTheme: 'secondaryTheme',
	// 	themes: {
	// 		secondaryTheme,
	// 	},
	// },

});



//load langauge
var lang = localStorage.getItem('lang');
if ((lang || "") == "") {
	localStorage.setItem('lang', 'en');
	lang = "en";
}
app.use(i18n);



app.use(router);
app.use(resourcesPlugin);
app.use(vuetify);
app.use(store);
app.use(Vue3DraggableResizable)
app.use(createBottomSheet())
app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
});
app.use(DialogService);
app.use(Toaster, {
	position: "top",
})
app.use(MasonryWall)

// Global Properties,
// components can inject this
app.provide("$gv", gv);
app.provide("$pos_license", pos_license);
app.provide("$sale", sale);
app.provide("$kod", kod);
app.provide("$tableLayout", tableLayout);
app.provide("$product", product);
app.provide("$numberFormat", NumberFormat)
app.provide("$socket", socket)

app.provide("$screen", screen);
app.provide("$auth", auth);
app.provide("$call", call);
app.provide("$frappe", frappe);


app.provide("$moment", moment)
app.config.globalProperties.$filter = {
	isEmpty(str) {
		return (!str || str.trim().length === 0);
	}
}


//app.use(VueNumberFormat, {prefix: '$ ', decimal: '.', thousand: ',',precision:2})


app.directive('debounce', vue3Debounce({ lock: true }))

// Configure route gaurds

router.beforeEach(async (to, from, next) => {

	 
		if (!localStorage.getItem("pos_profile")) {
			if (to.matched.some((record) => !record.meta.isStartupConfig)) {

				next({ name: "StartupConfig", query: { route: to.path } })
			} else {
				next()
			}
		}
		else {

			if (to.matched.some((record) => !record.meta.isLoginPage)) {
				// this route requires auth, check if logged in
				// if not, redirect to login page.
				if (!auth.isLoggedIn) {

					next({ name: 'Login', query: { route: to.path } });
				} else {
					next();
				}

			} else {
				if (auth.isLoggedIn) {
					next({ name: 'Home' });
				} else {
					next();
				}
			}
	} 
});

 
	app.component('CurrencyFormat', CurrencyFormat);
	app.component('ComPlaceholder', ComPlaceholder);
	app.component('ComAutoComplete', ComAutoComplete);
	app.component('ComPrintPreview', ComPrintPreview);
	app.component("avatar", Avatar);
	app.component('ComChip', ComChip)
	app.component('ComInput', ComInput)
	app.component('ComTableView', ComTableView)
	app.component('ComTdImage', ComTdImage)
	app.component('ComModal', ComModal)
	
	KeyStroke(app)
	
	
	app.mount("#app");




