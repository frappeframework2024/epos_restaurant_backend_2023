const http = require('http');
const socketio = require('socket.io');

const server = http.createServer();
 
const io = require('socket.io')(server, {
  path: '/socketserver/socket.io',
  cors: {
    origin: '*',
  }
});

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


  socket.on("ReservationDetail",(reservation)=>{
    io.emit("ReservationDetail",reservation)
  })

  socket.on("UpdateCashierShift",(arg)=>{
    io.emit("UpdateCashierShift",arg)
  })

  socket.on("RefreshData",(arg)=>{
    io.emit("RefreshData",arg)
  })

  socket.on("Housekeeping",(arg)=>{
    io.emit("Housekeeping",arg)
  })
  
  socket.on("ComHousekeepingStatistic",(arg)=>{
    io.emit("ComHousekeepingStatistic",arg)
  })
  
  socket.on("ComHousekeepingStatus",(arg)=>{
    io.emit("ComHousekeepingStatus",arg)
  })

  socket.on("Frontdesk",(arg)=>{
    io.emit("Frontdesk",arg)
  })

  socket.on("ComIframeModal",(arg)=>{
    io.emit("ComIframeModal",arg)
  })

  socket.on("ComGuestLedger",(arg)=>{
    io.emit("ComGuestLedger",arg)
  })
  
  socket.on("Dashboard",(arg)=>{
    io.emit("Dashboard",arg)
  })


  socket.on("CityLedgerAccount",(arg)=>{
    io.emit("CityLedgerAccount",arg)
  })


  socket.on("RoomInventory",(arg)=>{
    io.emit("RoomInventory",arg)
  })


  socket.on("GuestLedgerTransaction",(arg)=>{
    io.emit("GuestLedgerTransaction",arg)
  })


  socket.on("RunNightAudit",(arg)=>{
    io.emit("RunNightAudit",arg)
  })


  socket.on("GuestDetail",(arg)=>{
    io.emit("GuestDetail",arg)
  })


  socket.on("ReservationList",(arg)=>{
    io.emit("ReservationList",arg)
  })


  socket.on("ReservationStayDetail",(arg)=>{
    io.emit("ReservationStayDetail",arg)
  })

  socket.on("ReservationStayList",(arg)=>{
    io.emit("ReservationStayList",arg)
  })

  socket.on("ChartDoughnut",(arg)=>{
    io.emit("ChartDoughnut",arg)
  })


  socket.on("TodaySummary",(arg)=>{
    io.emit("TodaySummary",arg)
  })


  socket.on("GuestList",(arg)=>{
    io.emit("GuestList",arg)
  })


  socket.on("GuestType",(arg)=>{
    io.emit("GuestType",arg)
  })


  socket.on("FolioTransactionDetail",(arg)=>{
    io.emit("FolioTransactionDetail",arg)
  })


  socket.on("FolioTransactionList",(arg)=>{
    io.emit("FolioTransactionList",arg)
  })

  socket.on("ComCityLedgerDetail",(arg)=>{
    io.emit("ComCityLedgerDetail",arg)
  })

  socket.on("ComBusinessSource",(arg)=>{
    io.emit("ComBusinessSource",arg)
  })

  socket.on("Reports",(arg)=>{
    io.emit("Reports",arg)
  })
  

  
});

server.listen(3000, () => {
  console.log('Server started on port 3000');
});