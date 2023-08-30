const http = require('http');
const socketio = require('socket.io');




const express = require('express');
const app = express();
const http = require('http');
const fs = require('fs');
var options = {
    key: fs.readFileSync('/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/privkey.pem'),
    cert: fs.readFileSync('/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/cert.pem')
};
var port = process.env.PORT || 3000;

http.createServer(function (req, res) {
    res.writeHead(301, { "Location": "https://" + req.headers['host'] + req.url});
    res.end();
})
var server = http.createServer(options, app);

const io = require('socket.io')(httpsServer);

io.on('connection', (socket) => {

  
  socket.on("UpdateTable",(arg)=>{
    io.emit("UpdateData",arg)
  })

  //Print Receipt
  socket.on("PrintReceipt",(arg)=>{
    io.emit("PrintReceipt",arg)
  })

  socket.on("RefreshTable",()=>{
    io.emit("RefreshTable")
  })


  socket.on("ShowOrderInCustomerDisplay",(arg,show_thank_you = "")=>{
    io.emit("ShowOrderInCustomerDisplay",arg, show_thank_you)
  })


  //edoor raise event
  socket.on("RefresheDoorDashboard",(arg)=>{
    io.emit("RefresheDoorDashboard",arg)
  })
  socket.on("RefreshNightAuditStep",(arg)=>{
    io.emit("RefreshNightAuditStep",arg)
  })

  socket.on("RefreshReservationDetail",(reservation)=>{
 
    io.emit("RefreshReservationDetail",reservation)
  })

  socket.on("UpdateCashierShift",(arg)=>{
    io.emit("UpdateCashierShift",arg)
  })

  socket.on("RefreshData",(arg)=>{
    //arg data sould be json format {property:"Property name","action":"refersh_city_ledger"}
    io.emit("RefreshData",arg)
  })

});

httpsServer.listen(port, () => {
  console.log('Server started on port 3000');
});
