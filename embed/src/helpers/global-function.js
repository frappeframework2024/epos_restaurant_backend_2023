 

globalThis.app = globalThis.app || {};

globalThis.app.showSuccess = function(message,title="Confirm"){
         window.toast.add({ severity: 'success', summary: window.t("Confirm"), detail: message, life: 3000 })
}