document.onkeydown = updateKey;
document.onkeyup = resetKey;

var server_port;
var server_addr;

/**
 * This function runs when the window is loaded.
 * It uses SweetAlert to create a popup and ask for connection details.
 */
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
        buttons: {
            confirm: {
                text: "Save",
                value: true,
                visible: true,
                className: "",
                closeModal: true
            }
        }
    }).then((value) => {
        if (value) {
            // Retrieve the values from the popup inputs
            server_addr = document.getElementById("swal-input-ip").value;
            server_port = parseInt(document.getElementById("swal-input-port").value, 10);

            // Basic validation
            if (!server_addr || !server_port) {
                swal("Error", "IP address and port are required.", "error");
            } else {
                swal("Saved!", `The application will now connect to ${server_addr}:${server_port}`, "success");
            }
        } else {
             swal("Cancelled", "Connection details not provided.", "warning");
        }
    });
};


function client(){
    if (!server_addr || !server_port) {
        console.error("Server address or port not set.");
        return;
    }
    
    const net = require('net');
    var input = document.getElementById("message").value;

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        console.log('connected to server!');
        client.write(`${input}\r\n`);
    });
    
    // get the data from the server
    client.on('data', (data) => {
        document.getElementById("bluetooth").innerHTML = data;
        console.log(data.toString());
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });

    client.on('error', (err) => {
        console.error(`Connection error: ${err.message}`);
        swal("Connection Failed", `Could not connect to ${server_addr}:${server_port}. Please check the details and restart.`, "error");
    });
}

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;
    let key = e.keyCode.toString();

    if (key === '87') { // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_data(key);
    }
    else if (key === '83') { // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_data(key);
    }
    else if (key === '65') { // left (a)
        document.getElementById("leftArrow").style.color = "green";
        send_data(key);
    }
    else if (key === '68') { // right (d)
        document.getElementById("rightArrow").style.color = "green";
        send_data(key);
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
}


function send_data(message) {
    if (!server_addr || !server_port) {
        console.error("Server address or port not set.");
        return;
    }
    
    const net = require('net');
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        client.write(`${message}\r\n`);
    });

    client.on('data', (data) => {
        document.getElementById("bluetooth").innerHTML = data;
        console.log(data.toString());
        client.end();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });

    client.on('error', (err) => {
        console.error(`Connection error: ${err.message}`);
    });
}


// update data for every 50ms
function update_data(){
    setInterval(function(){
        // get image from python server
        client();
    }, 50);
}