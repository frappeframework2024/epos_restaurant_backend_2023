const { readFileSync } = require("fs");
const { createServer } = require("https");
const { Server } = require("socket.io");

const httpsServer = createServer({
  key: readFileSync("/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/privkey.pem"),
  cert: readFileSync("/etc/letsencrypt/live/www.ebad.ewebcloudserver.com/cert.pem")
});

const io = new Server(httpsServer, { /* options */ });

io.on("connection", (socket) => {
 
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

httpsServer.listen(3000, () => {
  console.log('Server started on port 3000');
});