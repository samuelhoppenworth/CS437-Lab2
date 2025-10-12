import socket
from time import sleep
from picarx import Picarx
from robot_hat.utils import get_battery_voltage
import argparse

parser = argparse.ArgumentParser(description='Start the Picarx server.')
parser.add_argument('--host', type=str, default="10.0.0.218", help='The host IP address to bind to.')
parser.add_argument('--port', type=int, default=65432, help='The port to listen on.')
args = parser.parse_args()

HOST = args.host
PORT = args.port

class Car:
    def __init__(self):
        self.px = Picarx()
        self.speed = 0
        self.turning = False
        self.direction = 1
        self.battery_voltage = None

    def update_speed(self, value):
        self.speed = value

    def update_turning(self, turning_status):
        self.turning = turning_status
    
    def update_battery_voltage(self):
        self.battery_voltage = get_battery_voltage()
                
    def get_status(self):
        self.update_battery_voltage()
        return f"sts {self.battery_voltage} {self.direction} {self.turning}"


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
                        # check if client still connected
                        client.settimeout(0.5)
                        data = client.recv(1024)
                        if data == b'':
                            print("Client disconnected")
                            break
                        elif data:
                            print("Received:", data.decode())
                        
                        # send status
                        car_status = car.get_status().encode('utf-8')
                        print("Sending:", car_status)
                        client.sendall(car_status)
                        sleep(0.5)

                    except socket.timeout:
                        car_status = car.get_status().encode('utf-8')
                        client.sendall(car_status)
                        sleep(0.5)
                    except (ConnectionResetError, BrokenPipeError):
                        print("Client forcibly closed connection.")
                        break

    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        car.px.stop()
        s.close()