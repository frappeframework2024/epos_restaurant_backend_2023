export function handleServerMessage(m){
    
    const dictionary = [
        {exception: 'frappe.exceptions.MandatoryError', text: 'Invalid input'},
        {exception: 'frappe.exceptions.TimestampMismatchError', text: 'Please refresh to get the latest document.'},
        {exception: 'frappe.exceptions.LinkExistsError', text: 'Cannot delete because it has relative data.'}
    ]
    const message = JSON.parse(JSON.stringify(m))
    if(message._error_message){
        
        window.postMessage({action:"show_error",message: message._error_message} , '*')
    }

    if(message._server_messages){
 
        const _server_messages = JSON.parse(message._server_messages)
 
		 
			_server_messages.forEach(r => {
                if(JSON.parse(r).message){
                    window.postMessage({action:"show_error",message:JSON.parse(r).message.replace("Error: ","")} , '*')

                    
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

                window.postMessage({action:"show_error",message:arrException[1]} , '*')

                else{
                    const msg = dictionary.find((r)=>r.exception == arrException[0])
                    if(msg.text)
            
                    window.postMessage({action:"show_error",message:msg.text} , '*')
                }
                    
            }
        } 

        
    }else{ 
        window.postMessage({action:"show_error",message:message.httpStatusText} , '*')
    }
}