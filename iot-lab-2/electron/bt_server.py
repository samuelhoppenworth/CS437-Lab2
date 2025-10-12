import socket
import threading
from time import sleep
from car import Car
import argparse
import bluetooth

parser = argparse.ArgumentParser(description='Start the Picarx server.')
parser.add_argument('--host', type=str, default="10.0.0.218", help='The host IP address to bind to.')
parser.add_argument('--port', type=int, default=65432, help='The port to listen on.')
args = parser.parse_args()

HOST = args.host
PORT = args.port

STATUS_UPDATE_INTERVAL = 0.2
hostMACAddress = "DC:A6:32:80:7D:87" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 0
backlog = 1
size = 1024

def handle_client_commands(client_socket, car, connection_event):
    """
    This function runs in its own thread. It continuously listens for commands
    from the client and controls the car.
    """
    try:
        while connection_event.is_set():
            try:
                data = client_socket.recv(1024)
                if not data:
                    print("Client disconnected gracefully.")
                    break

                message = data.decode().strip()
                print(f"Received command: {message}")

                # Move car based on the message
                if message == '87':
                    car.forward()
                elif message == '83':
                    car.backward()
                elif message == '65':
                    car.lTurn()
                elif message == '68':
                    car.rTurn()
                elif message == 'stop':
                    car.stop()
                
            except (ConnectionResetError, BrokenPipeError):
                print("Client forcibly closed connection.")
                break # Exit loop on connection error
            except Exception as e:
                print(f"Error in command thread: {e}")
                break
    finally:
        print("Command thread stopping.")
        connection_event.clear()
        car.stop()

def broadcast_status(client_socket, car, connection_event):
    """
    This function runs in its own thread. It continuously sends the car's
    status to the client at a regular interval.
    """
    while connection_event.is_set():
        try:
            status_message = car.get_status().encode('utf-8')
            client_socket.sendall(status_message)
            sleep(STATUS_UPDATE_INTERVAL)
        except (ConnectionResetError, BrokenPipeError):
            print("Could not send status, client disconnected.")
            break
        except Exception as e:
            print(f"Error in status thread: {e}")
            break
    
    print("Status broadcast thread stopping.")


def main(): 
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind((hostMACAddress, port))
    s.listen(backlog)
    print("listening on port ", port)
    car = Car()

    try:
        while 1:   
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)

            connection_active = threading.Event()
            connection_active.set() 

            command_thread = threading.Thread(
                    target=handle_client_commands,
                    args=(client, car, connection_active)
                )
            status_thread = threading.Thread(
                    target=broadcast_status,
                    args=(client, car, connection_active)
                )

            command_thread.start()
            status_thread.start()
            
 
    except: 
        print("Closing socket")
        client.close()
        s.close()

