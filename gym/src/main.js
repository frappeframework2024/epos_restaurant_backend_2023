import { createApp, reactive } from "vue";
import App from "./App.vue";

import router from './router';
import resourceManager from "../../../doppio/libs/resourceManager";
import call from "../../../doppio/libs/controllers/call";
import socket from "../../../doppio/libs/controllers/socket";
import Auth from "../../../doppio/libs/controllers/auth";
import { FrappeApp } from 'frappe-js-sdk';

const app = createApp(App);
const auth = reactive(new Auth());
const frappe = new FrappeApp();

// Plugins
app.use(router);
app.use(resourceManager);

// Global Properties,
// components can inject this
app.provide("$auth", auth);
app.provide("$call", call);
app.provide("$socket", socket);
app.provide("$frappe", frappe);


// Configure route gaurds
router.beforeEach(async (to, from, next) => {
	next({ name: 'Home' });		
});

app.mount("#app");
