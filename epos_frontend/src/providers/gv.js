import { authorizeDialog,noteDialog,confirm,i18n,computed } from "@/plugin"
import { createToaster } from "@meforma/vue-toaster";
import moment from '@/utils/moment.js';
import { FrappeApp } from 'frappe-js-sdk';
const frappe = new FrappeApp();
const call = frappe.call();

const { t: $t } = i18n.global; 
 
const toaster = createToaster({ position: "top-right" });
 
export default class Gv {
	constructor() {
		this.setting = {},
		this.customerMeta = null,
		this.saleMeta = null,
		this.countries = [],
		this.promotion = null
		//use this variable to control state of open/close shift in drawer

		this.workingDay = "";
		this.cashierShift= "";
		this.isFullscreen = true;
		this.shortcut_keys = [];
		this.device_setting = null;
		
	}

	
	getPrintReportPath(doctype,name,reportName, isPrint=false){
		let url = "";
		let serverUrl = window.location.protoco
		l + "//" +  window.location.host;
		url  = serverUrl + "/printview?doctype=" + doctype + "&name=" + name + "&format="+ reportName +"&no_letterhead=0&letterhead=Defualt%20Letter%20Head&settings=%7B%7D&_lang=en&d=" + new Date()
		if(isPrint){
			serverUrl = serverUrl + "&trigger_print=" + triggerPrint
		}
	}

	async authorize(settingKey, permissionCode,requiredNoteKey="",categoryNoteName="", product_code = "", inlineNote = false) {

		console.log(settingKey)
		return new Promise(async (resolve,reject) => {
			let is_auth_required  = (this.setting.pos_setting[settingKey] == 1);

			console.log(this.setting.pos_setting[settingKey])
			const device_setting = JSON.parse(localStorage.getItem("device_setting"));		 
			if ( !is_auth_required && device_setting.is_order_station == 1){
				is_auth_required = (this.setting.pos_setting["order_station_open_order_required_password"] == 1)
			} 

			if (is_auth_required) {
				const result = await authorizeDialog({ permissionCode: permissionCode });				
				if (result) {	
				
					
					if(requiredNoteKey && categoryNoteName){						
						//check if require note 
					 

						if(this.setting.pos_setting[requiredNoteKey] == 1){							
							if(inlineNote){	
								resolve({user:result.name,category_note_name: categoryNoteName,discount_codes:result.discount_codes,username:result.username})
							}else{
								const resultNote = await noteDialog({name:categoryNoteName,data:{product_code:product_code}}) ;
								if(resultNote){
									resolve({user:result.name, discount_codes:result.discount_codes,note:resultNote,username:result.username});
								}else{
									resolve(false);
								}
							}							
						}
						else{
							resolve({user:result.name, discount_codes:result.discount_codes,note:"",username:result.username});	
						}
					}
					else{
						resolve({user:result.name, discount_codes:result.discount_codes,note:"",username:result.username});
					}					
				} 
				else {
					resolve(false);
				}
			}
			else {		

			 	const currentUser = JSON.parse(localStorage.getItem("current_user"));	
			 	if (JSON.parse(localStorage.getItem("current_user")).permission[permissionCode] == 1) {		
					
					if(requiredNoteKey && categoryNoteName){						
						//check if require note 
						
						if(this.setting.pos_setting[requiredNoteKey] == 1){ 
							
							if(inlineNote){ 
								resolve({user:currentUser.full_name, discount_codes:currentUser.permission.discount_codes,note:'',username:currentUser.name,category_note_name: categoryNoteName})
							}else{
								const resultNote = await noteDialog({name:categoryNoteName,data:{product_code:""}}) ;
								if(resultNote){
									resolve({user:currentUser.full_name, discount_codes:currentUser.permission.discount_codes,note:resultNote,username:currentUser.name});
								}else{ 
									resolve(false);
								}
							}
						}
						else{
							resolve({user:currentUser.full_name, discount_codes:currentUser.permission.discount_codes,note:"",show_confirm:1,username:currentUser.name});
						}
					}
					else{						
						resolve({user:currentUser.full_name, discount_codes:currentUser.permission.discount_codes,note:"",username:currentUser.name});
					}				
					
				} else {
					 
					toaster.warning($t("msg.You do not have permission to perform this action"))
					resolve(false);
				}
			}
		})

	}

	async confirm_close_working_day(working_day){		 
		const current_user =     localStorage.getItem('current_user');
		if(current_user==null || current_user == undefined){
			// Home Logout 
		}
		else{
			let check_date = "";
			if(this.setting.close_business_day_on=="Current Day"){
				check_date =  moment(working_day).format('yyyy-MM-DD') + " " + this.setting.alert_close_working_day_after;
			}else{ 
				check_date = moment(working_day).add(1, 'days').format('yyyy-MM-DD') + " " + this.setting.alert_close_working_day_after;
			}
	
			if(new Date() > new Date(check_date)){
				await confirm({title:`${$t('Current Working Day')} (${moment(working_day).format('DD-MM-yyyy')})`, text:$t('msg.Your working day is to long please close your working day'),hide_cancel:true});		
				
			}
		}
	}

	getCurrentUser(){
		if(this.checkCookie('system_user') == 'yes'){
			return this.checkCookie('user_id')
		}
		return ''
	}

	getPromotionByCustomerGroup(customer_group){
		let promotions = []

		if(this.promotion && this.promotion.length > 0){
			
			this.promotion.forEach(r => {
				if(r.customer_groups.length > 0){
					r.customer_groups.forEach(g=>{
						if(g.customer_group_name_en == customer_group){
							promotions.push(r)
						}
					})
				}else{
					promotions.push(r)
				}
				
			});
			
			return promotions
		}
	
		
		return promotions
	}

	getPromotionByCustomerGroupSingleRecod(customer_group){
		const data = this.getPromotionByCustomerGroup(customer_group)
		return data[0]
	}

	checkCookie(name) {
		var nameEQ = name + "=";
		var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++) {
		  var c = ca[i];
		  while (c.charAt(0)==' ') c = c.substring(1,c.length);
		  if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
		}
		return null;
	}

	 getCurrnecyFormat = computed(()=> {
		let format = '#,###,##0.00##';
		const curr = this.setting?.currencies.find(r => r.name == this.setting?.default_currency);
		if(curr)
		{
			format = curr.pos_currency_format;
		}
		return format;
	})

	showServerMessage(message_data){
		const dictionary = [
			{exception: 'frappe.exceptions.MandatoryError', text: 'Invalid input'},
			{exception: 'frappe.exceptions.TimestampMismatchError', text: 'Please refresh to get the latest document.'},
			{exception: 'frappe.exceptions.LinkExistsError', text: 'Cannot delete because it has relative data.'}
		]
		const message = JSON.parse(JSON.stringify(message_data))
		if(message._error_message){
			toaster.warning($t(message._error_message))

		}
	
		if(message._server_messages){
	 
			const _server_messages = JSON.parse(message._server_messages)
	 
			 
				_server_messages.forEach(r => {
					if(JSON.parse(r).message){
						toaster.warning($t(JSON.parse(r).message.replace("Error: ","")))
						
					}
					 
					
				});
				
			}
				
			else  if(message.httpStatus == 417){
			var arrException = []
			if(message.exception){
				if(Array.isArray(message.exception)){
					arrException = message.exception
				}
				else if(message.exception){
					arrException = message.exception.split(':')
				  
				}
				if(arrException[0]){
					if(arrException[0] == 'frappe.exceptions.ValidationError')
						toaster.warning($t(arrException[1]))
						
	
					else{
						const msg = dictionary.find((r)=>r.exception == arrException[0])
						if(msg.text)
							toaster.warning($t(msg.text))
					}
						
				}
			} 

		}else{ 
		 
			toaster.warning($t(message?.exception || message.httpStatusText))
			 
		}
	}
	onPrintWorkingDayAndCashierShift(name,pos_profile,doctype) {
		let body = {
            data:{
                pos_profile: pos_profile == ""? localStorage.getItem("pos_profile") : pos_profile,
            }
        }
        call.post("epos_restaurant_2023.api.api.get_sale_list_table_badge",body)
		if(doctype == "Cashier Shift"){
			call.get('epos_restaurant_2023.api.desktop_api.cashier_shift_info',{"name":name,"pos_profile":pos_profile})
            .then((data) => {
				let resp = data.message
				const send_data = {
					action: "print_close_cashier_shift",
					setting: this.setting?.pos_setting,
					cashier_shift: resp.cashier_shift,
					station_device_printing:(this.setting?.device_setting?.station_device_printing)||"",
				}
				window.chrome.webview.postMessage(JSON.stringify(send_data));
            }).catch((res)=>{
                console.log(res)
            })
		}
		else{
			call.get('epos_restaurant_2023.api.desktop_api.get_working_day_info',{"name":name,"pos_profile":pos_profile})
            .then((data) => {
				let resp = data.message
				const send_data = {
					action: "print_close_working_day",
					setting: this.setting?.pos_setting,
					working_day: resp.working_day,
					station_device_printing:(this.setting?.device_setting?.station_device_printing)||"",
				}
				window.chrome.webview.postMessage(JSON.stringify(send_data));
            }).catch((res)=>{
                console.log(res)
            })
		}
    }
}

 