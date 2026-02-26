export function handleServerMessage(m){
    
    const dictionary = [
        {exception: 'frappe.exceptions.MandatoryError', text: 'Invalid input'},
        {exception: 'frappe.exceptions.TimestampMismatchError', text: 'Please refresh to get the latest document.'},
        {exception: 'frappe.exceptions.LinkExistsError', text: 'Cannot delete because it has relative data.'}
    ]
    const message = JSON.parse(JSON.stringify(m))
    if(message._error_message){
     
         app.showError(message._error_message)
    }

    if(message._server_messages){
 
       
        const _server_messages = JSON.parse(message._server_messages)
 
		 
			_server_messages.forEach(r => {
                if(JSON.parse(r).message){
                    
                     app.showError(JSON.parse(r).message.replace("Error: ",""))
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

                
                    app.showError(arrException[1])

                else{
                    const msg = dictionary.find((r)=>r.exception == arrException[0])
                    if(msg.text)
                        app.showError(msg.text)
                }
                    
            }
        } 

        
    }else{ 
        
        app.showError(message.httpStatusText)

    }
}