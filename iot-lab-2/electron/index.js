document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port;
var server_addr;

// This function runs when the window loads to get the server details.
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
        buttons: { confirm: { text: "Save", value: true } }
    }).then((value) => {
        if (value) {
            server_addr = document.getElementById("swal-input-ip").value;
            server_port = parseInt(document.getElementById("swal-input-port").value, 10);
            if (!server_addr || !server_port) {
                swal("Error", "IP address and port are required.", "error");
            } else {
                swal("Saved!", `The application will connect to ${server_addr}:${server_port}`, "success");
            }
        } else {
             swal("Cancelled", "Connection details not provided.", "warning");
        }
    });
};


function parseServerStatus(message) {
  if (typeof message !== 'string' || !message.startsWith('sts ')) {
    return null;
  }

  const parts = message.split(' ');
  if (parts.length !== 4) {
    console.error("Malformed status message received:", message);
    return null;
  }

  try {
    const status = {
      batteryVoltage: parseFloat(parts[1]),
      direction: parseInt(parts[2], 10),
      turning: parts[3].toLowerCase() === 'true'
    };

    // Final check to ensure the numbers were parsed correctly
    if (isNaN(status.batteryVoltage) || isNaN(status.direction)) {
      console.error("Failed to parse numeric values from status:", message);
      return null;
    }
    return status;
  } catch (error) {
    console.error("Error parsing server status:", error);
    return null;
  }
}

function sendMessageToServer(message) {
    if (!server_addr || !server_port) {
        console.error("Server address or port not set.");
        return;
    }
    
    const net = require('net');
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        console.log('Connected. Sending message:', message);
        client.write(`${message}\r\n`);
    });
    
    client.on('data', (data) => {
        const message = data.toString().trim();
        console.log("Received from server:", message);

        const status = parseServerStatus(message);

        if (status) {
            document.getElementById("temperature").innerText = status.batteryVoltage.toFixed(2) + ' V';
            document.getElementById("direction").innerText = `Direction Code: ${status.direction}`;
            document.getElementById("speed").innerText = `Is Turning: ${status.turning}`;

        }
        client.end();
    });

    client.on('end', () => console.log('Disconnected from server.'));

    client.on('error', (err) => {
        console.error(`Connection error: ${err.message}`);
        swal("Connection Failed", `Could not connect. Check the server and your connection.`, "error");
    });
}

// Handles keyboard presses to control the car.
function updateKey(e) {
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

function resetKey(e) {
    e = e || window.event;
    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";

    sendMessageToServer("stop"); 
}