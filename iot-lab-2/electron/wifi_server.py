import socket
from time import sleep
from picarx import Picarx
from robot_hat.utils import get_battery_voltage

HOST = "10.0.0.218"     # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

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
    try:
        while 1:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            with client:
                # Get binary data from client
                # data = client.recv(1024)      
                # if data != b"":
                    # print(data)     
                    # client.sendall(data)
                    
                # Send car status to client
                car_status = car.get_status().encode('utf-8')
                client.sendall(car_status)
                sleep(0.5)
    except: 
        print("\nClosing socket")
        client.close()
        s.close()
    finally:
        car.px.stop()
        