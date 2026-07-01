<template>
	<div>
		<SplashScreen v-if="state.isLoading" />
		
		<v-sheet v-else id="app-container" v-resize="onResize">
			<div >
				<v-progress-linear class="progress_bar" v-if="isLoading" indeterminate color="teal"></v-progress-linear>
				<MainLayout v-if="layout=='main_layout'" />
				<SaleLayout v-else-if="layout=='sale_layout'" />
				<KitchenOrderDisplayLayout v-else-if="layout=='kitchen_order_display_layout'" />
				<BlankLayout v-else />
				<PromiseDialogsWrapper />
			</div>
		</v-sheet>
		<DynamicDialog />
	</div>
</template>
<script setup>
import { useRouter, useRoute, routeLocationKey} from 'vue-router'
import MainLayout from './components/layout/MainLayout.vue';
import BlankLayout from './components/layout/BlankLayout.vue';
import KitchenOrderDisplayLayout from '@/components/layout/KitchenOrderDisplayLayout.vue';
import SplashScreen from './components/SplashScreen.vue';
import SaleLayout from './components/layout/SaleLayout.vue';
import { PromiseDialogsWrapper } from 'vue-promise-dialogs';
import { createResource } from '@/resource.js'
import {provide, reactive, computed, onMounted, inject, i18n,onUnmounted,postApi,payWaySuccessDialog } from '@/plugin'
import { useStore } from 'vuex'
import { createToaster } from '@meforma/vue-toaster';
import { FrappeApp } from 'frappe-js-sdk';
import { useDisplay } from 'vuetify'; 
import DynamicDialog from 'primevue/dynamicdialog';
import WebSocketPrinter from "@/utils/websocket-printer.js"
import { ref } from 'vue';

import createPaywaySocket from './utils/paywaysocketio';


import Sale from "./providers/sale"; 

const router = useRouter()
const route = useRoute()
 
const provideSale = reactive(new Sale(router));
provide("$sale", provideSale);
const sale = provideSale;




const layout = computed(() => {
	return route.meta.layout  || "blank_layout"
})

const frappe = inject('$frappe');
const call = frappe.call();
const { t: $t } = i18n.global; 

const toast = createToaster({position:'top-right'});
const gv = inject("$gv"); 


const pos_license = inject("$pos_license");
const product = inject("$product");
const tableLayout = inject("$tableLayout");
const socket = inject("$socket");
const auth = inject("$auth");
const store = useStore();
const screen = inject('$screen');
let state = reactive({
	isLoading: false
}); 

const { mobile } = useDisplay();
const licenseToaster = createToaster({ position: "top", duration: 1000*60*60, type: "error" });

socket.on("PrintReceipt", (arg) => {	
	let isWindows = localStorage.getItem("is_window")=="1";
	let isElectron= localStorage.getItem("electronWrapper") == "1";
	if( isWindows || isElectron){
		const device_setting = JSON.parse(localStorage.getItem("device_setting"));
		const station_device_printing = device_setting?.station_device_printing||"";
		const data = JSON.parse(arg) ;	 
		//data.sale.pos_profile == localStorage.getItem("pos_profile")
		if( station_device_printing == data.station_device_printing){
			if(isWindows){
				window.chrome.webview.postMessage(arg);
			}
			else if(isElectron){ 
				console.info("electron message action => ",data.action)
				window.electronAPI.send('vue-message', arg);
			}
		}
	} 
});

socket.on("ABAPayWaySuccess", async (arg,key) => {		
		const device_setting = JSON.parse(localStorage.getItem("device_setting"));
		const device_id = device_setting?.device_id||"";
		const pos_profile = localStorage.getItem("pos_profile");
		const business_branch = decodeURIComponent(gv.setting?.business_branch);
		const _key = `${business_branch}_${pos_profile}_${device_id}`;
		const endpoint = window.location.pathname.replace(/^\/+/, '');
		if(key == _key && endpoint != "epos_frontend/customer-display"){ 
			await payWaySuccessDialog();
		}
	 
});

// print from emenu order
socket.on("OnPrintReport", async (arg) => { 
	if(printService){	
		if(arg.order_number!==""){		
			await postApi("printing.get_mobile_order_to_kitchen_pdf", {
				pdf: 0,
				doc_name: arg.order_number
			}).then(result=>{
				result.message.forEach(x => {
					printService.submit({
						'type': x[0],//printer name
						'url': 'file.pdf',
						'file_content': x[1] //base 64 pdf
					});
				});
			});			
		}
	}
});




let printService  = null;
const isLoading = computed(() => {
	const value = store.state.isLoading;
	if(!value){
		

		 if(gv.device_setting?.web_socket_print_url){
			printService = new WebSocketPrinter(null, gv.setting.device_setting.web_socket_print_url);
		 }
	}
	return value;
});

const is_window = localStorage.getItem("is_window");
const is_apk_ipa = localStorage.getItem("apkipa");
pos_license.web_platform  = false;
if((is_window||0) == 0 && (is_apk_ipa||0)==0){ 
	pos_license.web_platform  = true;
	const _webuid = localStorage.getItem("_webuid");
	if((_webuid||0)==0){
		localStorage.removeItem("device_name");
	}else{ 		
		pos_license.onPOSLicenseCheck(_webuid).then((_res)=>{
			if(_res.status == false){
				onLogout();			
				localStorage.clear();
				router.reload();
			}else if(_res.status == true && _res.expired == true){
				onLogout();		  	
			}
		}); 
	};
}


const _device = localStorage.getItem("device_name");
if(_device == null || _device == undefined){
	localStorage.removeItem("pos_profile");
}

if (!localStorage.getItem("pos_profile")) {
	state.isLoading = false;
	if((_device||"") !=""){
		localStorage.removeItem("device_name");
	}	
	router.push({ name: 'StartupConfig' });

} else {

	const pos_profile = localStorage.getItem("pos_profile");
	localStorage.removeItem("__startup_device");
	state.isLoading = true;
	let get_system_settings = call.post("epos_restaurant_2023.api.api.get_system_settings",
		{
			pos_profile: pos_profile,
			device_name: localStorage.getItem("device_name")
		}
	);

	get_system_settings.then((_doc)=>{
		let doc = _doc.message;

		//connect estc-socket-server
		if((doc.estc_payway_socket_server_url ||"") != ""){
			onPayWaySocketSetup(doc);
		}	
		const customer_display_key = `${doc.business_branch}_${pos_profile}_${doc.device_setting.device_id}`;
		state.isLoading = false;
		localStorage.setItem("setting", JSON.stringify(doc)); 
		gv.setting = doc;
		gv.device_setting = doc.device_setting;
		gv.customer_display_key = customer_display_key;
		sale.customer_display_key = customer_display_key;
		sale.setting = doc;
		product.setting = doc;
		tableLayout.setting = doc;
		tableLayout.table_groups = doc.table_groups || '';
		localStorage.setItem("device_setting",JSON.stringify(doc.device_setting))
		localStorage.setItem("table_groups", JSON.stringify(doc.table_groups || null))			
		checkPromotionDay(gv.setting.business_branch);	
		
		let current_user = localStorage.getItem("current_user");
		if (current_user) {

			//init menu product 
			product.onInit();				
			createResource({
				url: "epos_restaurant_2023.api.api.get_current_shift_information",
				params: {
					business_branch: gv.setting?.business_branch,
					pos_profile: pos_profile
				},
				onSuccess(data) {
					gv.workingDay = data.wroking_day;
					gv.cashierShift = data.cashier_shift;
				},
				auto: true,
			})
		} 

		// set print socket url			
		if(gv.device_setting?.web_socket_print_url){			
			window.printService = new WebSocketPrinter(null, gv.setting.device_setting.web_socket_print_url);
		}
		

	}).catch((x) => {
		if (x.error_text == undefined) {
				//localStorage.removeItem("pos_profile")
		} else {
			if (x.error_text[0] === 'Invalid POS Profile name') {
				localStorage.removeItem("pos_profile")
			}
			else if(x.error_text[0] === 'Internal Server Error'){	
				//router.push({ name: 'ServerError' })
			}
			else{
				toast.error(JSON.stringify(x))
			}
		}

	}).finally(() => {
		state.isLoading = false;
	});  
}

async function onPayWaySocketSetup(doc) {	
	// console.log({"estc socket":doc.estc_payway_socket_server_url}) 
	const payway_socket = createPaywaySocket(doc.estc_payway_socket_server_url);
	// ABA Socket Client Join Room
	const myRoom = doc.property_code; // unique per client
	
	// Listen to connection and disconnection explicitly
    payway_socket.on('connect', () => {
		gv.estc_socket_connected = true;        
    });

    payway_socket.on('disconnect', (reason) => {
		gv.estc_socket_connected = false;
        
    }); 

	// payway_socket.emit('joinRoom', myRoom);
	await payway_socket.joinRoom(myRoom);
	// ABA PayWay Listening payment callback 
	await payway_socket.on("ABAPayCallback", async (arg) => { 
		sale.handlePayWayPaymentCallback(payway_socket, arg);
	});

}


//get user info 
let current_user = localStorage.getItem('current_user')
if(current_user!=null){
	const frappe = new FrappeApp();
	const auth = frappe.auth();
	auth.getLoggedInUser().then((user) => {
		current_user = current_user ? JSON.parse(current_user) : null
		if (!current_user) {	 
			createResource({
				url: 'epos_restaurant_2023.api.api.get_user_info',
				params: {
					name: current_user?.name
				},
				cache: "get_current_login_user",
				auto: true,
				onSuccess(doc) {  
					current_user = doc
					localStorage.setItem("current_user", JSON.stringify(current_user));
				}
			})
		}
	}).catch((error) => console.error(error));	
}

function checkPromotionDay(business_branch){
	if(auth.isLoggedIn){  
		const resp = call.post("epos_restaurant_2023.api.promotion.check_promotion",{
			business_branch: business_branch
		});
		resp.then((_doc)=>{ 
			let doc = _doc.message;
			
			gv.promotion = doc;
			sale.promotion = doc;
		}) ;
	}
}

function onResize() {
	screen.onResizeHandle()
}


function onLogout() {
    auth.logout().then((r) => {
        router.push({ name: 'Login' });
    });
}
 

const actionListeningHandler = async function (e) {
	if (e.isTrusted && e.data.action) {
		if(e.data.action=="show_error"){
			toast.error(e.data.message)
		}
	}
}

onMounted(async () => {
	window.mobile = mobile.value
	window.addEventListener('message', actionListeningHandler, false);
	setTimeout(()=>{
		if (pos_license.license != null){
			if (pos_license.license.show_license_msg){
				licenseToaster.warning($t(pos_license.license.message))
			}
		}   
	}, 5000)
	//check if NN user 
	const current_user =  localStorage.getItem('current_user');
	
    if(current_user==null || current_user == undefined){
        onLogout();
    }else{
		const pos_user =JSON.parse(current_user)
		if(auth.cookie.user_id != pos_user.name){
			onLogout();
		}		 
	}

	gv.device_setting  = JSON.parse(localStorage.getItem("device_setting"));	
	
	// get pos local setting and set global
	if (!localStorage.getItem("item_menu_setting")){
		localStorage.setItem("item_menu_setting", JSON.stringify( gv.itemMenuSetting) )
	}

	
	onResize()

})



onUnmounted(()=>{
	window.removeEventListener('message', actionListeningHandler, false);
})
</script>
<style>
.progress_bar {
	position: absolute !important;
	z-index: 9999 !important;
}

/* width */
::-webkit-scrollbar {
	width: 5px;
	height: 5px;
}

/* Track */
::-webkit-scrollbar-track {
	box-shadow: inset 0 0 5px rgb(206, 206, 206);
	border-radius: 10px;
}

/* Handle */
::-webkit-scrollbar-thumb {
	background: rgb(165, 165, 165);
	border-radius: 10px;
}

button {
  text-transform: none !important;
}
</style>