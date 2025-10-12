import socket
from time import sleep
from car import Car
import argparse

parser = argparse.ArgumentParser(description='Start the Picarx server.')
parser.add_argument('--host', type=str, default="10.0.0.218", help='The host IP address to bind to.')
parser.add_argument('--port', type=int, default=65432, help='The port to listen on.')
args = parser.parse_args()

HOST = args.host
PORT = args.port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    car = Car()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client, clientInfo = s.accept()
            print("Client connected:", clientInfo)

            with client:
                while True:
                    try:
                        data = client.recv(1024)
                        if not data:
                            print("Client disconnected")
                            car.stop()
                            break
                        
                        message = data.decode().strip()
                        print("Received:", message)

                        # Call the correct car function based on the message
                        if message == '87':       # W key for Forward
                            car.forward()
                        elif message == '83':     # S key for Backward
                            car.backward()
                        elif message == '65':     # A key for Left Turn
                            car.lTurn()
                        elif message == '68':     # D key for Right Turn
                            car.rTurn()
                        elif message == 'stop':   # Sent when a key is released
                            car.stop()

                        car_status = car.get_status().encode('utf-8')
                        print("Sending:", car_status)
                        client.sendall(car_status)

                    except (ConnectionResetError, BrokenPipeError):
                        print("Client forcibly closed connection.")
                        car.stop()
                        break
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        car.stop()
                        break

    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        car.stop()
        s.close()
