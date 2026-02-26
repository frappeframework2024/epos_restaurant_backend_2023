import { ref } from "vue"
import { FrappeApp } from 'frappe-js-sdk';
const isAuthorize = ref(false)
const currentLoginUsername = ref()


export function useAuth() {
    async function checkUserLogin(){
        const frappe = new FrappeApp();
       const auth = frappe.auth()
       
        await auth
            .getLoggedInUser()
            .then((user) =>{
                 console.log(user)
                 currentLoginUsername.value = user;
               
                 isAuthorize.value = true
            })
            .catch((error) => {
                if(error.httpStatus == 403){
                    isAuthorize.value = false;
                }
                
            });

      
    }
    return {
        isAuthorize,
        currentLoginUsername,
        checkUserLogin
    }
}