import { createApp, reactive } from "vue";
import App from "./App.vue";

import router from './router';
 
const app = createApp(App);
 

// Plugins
app.use(router);
 
 

// Configure route gaurds
router.beforeEach(async (to, from, next) => {
	
			next();
		
});

app.mount("#app");
