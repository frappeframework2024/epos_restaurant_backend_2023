var fs = require('fs');

var options = {
    key: fs.readFileSync("/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/privkey.pem"),
    cert: fs.readFileSync("/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/cert.pem"),
    ca: fs.readFileSync("/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/chain.pem"),
    rejectUnauthorized: false,
    requestCert: true,
    agent: false
};


var httpsServer = require('https').createServer(options);
var ioServer = require('socket.io');

var io = new ioServer();

io.attach(httpsServer);

httpsServer.listen(3000);

io.sockets.on('connection', function (socket) {
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