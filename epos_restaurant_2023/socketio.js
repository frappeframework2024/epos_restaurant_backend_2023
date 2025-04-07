const io = require("socket.io")();
const redis = require("redis");
const redisAdapter = require("socket.io-redis");

const redisClient = redis.createClient({ host: "localhost", port: 13003 });
io.adapter(redisAdapter({ pubClient: redisClient, subClient: redisClient.duplicate() }));

io.on("connection", (socket) => {
    console.log("Client connected:", socket.id);

    // Listen for messages from clients
    socket.on("client_message", (data) => {
        console.log("Received from client:", data);
        // Broadcast to all other clients
        io.emit("new_message", { text: data.text });
    });

    socket.on("disconnect", () => {
        console.log("Client disconnected:", socket.id);
    });
});

io.listen(9000); // Match Frappe's socket port