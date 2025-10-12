// --- Global State Variables ---
var server_port;
var server_addr;
var socketClient = null; // This will hold our single, persistent socket connection
var isKeyDown = false;   // Prevents message flooding from holding a key down

// --- Event Listeners ---
document.onkeydown = updateKey;
document.onkeyup = resetKey;

// Runs when the app loads
window.onload = function() {
    swal({
        title: "Enter Raspberry Pi Details",
        content: {
            element: "div",
            attributes: {
                innerHTML: `
                    <p>Enter the IP address or hostname of your Raspberry Pi:</p>
                    <input id="swal-input-ip" class="swal-content__input" placeholder="IP Address / Hostname" value="10.0.0.218">
                    <p>Enter the port number:</p>
                    <input id="swal-input-port" class="swal-content__input" type="number" placeholder="Port" value="65432">
                `
            }
        },
        buttons: { confirm: { text: "Save and Connect", value: true } }
    }).then((value) => {
        if (value) {
            server_addr = document.getElementById("swal-input-ip").value;
            server_port = parseInt(document.getElementById("swal-input-port").value, 10);
            if (!server_addr || !server_port) {
                swal("Error", "IP address and port are required.", "error");
            } else {
                swal("Saved!", `Attempting to connect to ${server_addr}:${server_port}`, "info");
                connectToServer(); // Automatically connect after getting details
            }
        } else {
             swal("Cancelled", "Connection details not provided.", "warning");
        }
    });
};

/**
 * Creates and manages the single, persistent connection to the server.
 */
function connectToServer() {
    // If we are already connected or connecting, do nothing.
    if (socketClient) {
        console.log("Already connected or attempting to connect.");
        return;
    }

    const net = require('net');
    socketClient = new net.Socket();
    
    // --- Setup Event Listeners ONCE for the persistent socket ---

    // This event fires when the connection is successfully established.
    socketClient.on('connect', () => {
        console.log('Connection established with server!');
    });

    // This event fires whenever data is received from the server.
    socketClient.on('data', (data) => {
        const message = data.toString().trim();
        console.log("Received from server:", message);

        const status = parseServerStatus(message);
        if (status) {
            // Update the UI with the parsed data
            document.getElementById("voltage").innerText = status.batteryVoltage.toFixed(2);
            document.getElementById("direction").innerText = status.direction;
            document.getElementById("turning").innerText = status.turning;
        }
    });

    // This event fires when the server closes the connection.
    socketClient.on('close', () => {
        console.log('Connection closed by server.');
        document.getElementById("connection_status").innerText = "Disconnected";
        document.getElementById("connection_status_dot").style.color = "red";
        document.getElementById("connectButton").disabled = false;
        socketClient = null; // Clear the socket object
    });

    // This event fires when a connection error occurs.
    socketClient.on('error', (err) => {
        console.error(`Connection error: ${err.message}`);
        swal("Connection Failed", `Could not connect. Check the server and your connection.`, "error");
        socketClient.destroy(); // Ensure the socket is destroyed on error
        document.getElementById("connection_status").innerText = "Error";
        document.getElementById("connection_status_dot").style.color = "red";
        document.getElementById("connectButton").disabled = false;
        socketClient = null; // Clear the socket object
    });

    // Initiate the connection
    socketClient.connect(server_port, server_addr);
}

/**
 * Parses the status message from the server.
 */
function parseServerStatus(message) {
    if (typeof message !== 'string' || !message.startsWith('sts ')) {
        return null;
    }
    const parts = message.split(' ');
    if (parts.length !== 4) return null;

    try {
        return {
            batteryVoltage: parseFloat(parts[1]),
            direction: (['stopped', 'forward', 'backward', 'left', 'right'][parseInt(parts[2], 10)] || 'unknown'),
            turning: (parts[3].toLowerCase() === 'true').toString()
        };
    } catch (e) {
        return null;
    }
}

/**
 * Sends a message over the persistent socket connection.
 */
function sendMessageToServer(message) {
    // Only send if the socket exists and is writable
    if (socketClient && socketClient.writable) {
        console.log('Sending message:', message);
        socketClient.write(`${message}\r\n`);
    } else {
        console.error('Not connected. Cannot send message.');
    }
}

// Handles keyboard presses to control the car.
function updateKey(e) {
    // If a key is already being held down, do nothing.
    if (isKeyDown) return; 
    isKeyDown = true;

    e = e || window.event;
    let key = e.keyCode.toString();

    if (['87', '83', '65', '68'].includes(key)) { // W, S, A, D
        if (key === '87') document.getElementById("upArrow").style.color = "green";
        if (key === '83') document.getElementById("downArrow").style.color = "green";
        if (key === '65') document.getElementById("leftArrow").style.color = "green";
        if (key === '68') document.getElementById("rightArrow").style.color = "green";
        sendMessageToServer(key);
    }
}

// Handles key releases to stop the car.
function resetKey(e) {
    isKeyDown = false;
    e = e || window.event;
    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";

    sendMessageToServer("stop"); 
}