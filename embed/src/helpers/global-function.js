 

globalThis.app = globalThis.app || {};

globalThis.app.showSuccess = function(message,title="Confirm"){
         window.toast.add({ severity: 'success', summary: title, detail: message, life: 3000 })
}

globalThis.app.showWarning = function(message,title="Warning"){
         window.toast.add({ severity: 'warn', summary: window.t(title), detail: message, life: 3000 })
}

globalThis.app.showError = function(message,title="Warning"){
         window.toast.add({ severity: 'error', summary: window.t(title), detail: message, life: 3000 })
}
