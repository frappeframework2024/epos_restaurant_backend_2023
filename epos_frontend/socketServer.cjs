const http = require('http');
const socketio = require('socket.io');

const server = http.createServer();
 
const io = require('socket.io')(server, {
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


});




server.listen(3000, () => {
  console.log('Server started on port 3000');
});