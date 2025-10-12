import time
from picarx import Picarx
from robot_hat.utils import get_battery_voltage

class Car:
    def __init__(self):
        self.px = Picarx()
        self.speed = 0
        self.turning = False
        self.direction = 1  # 1=forward, 2=backward, 3=left, 4=right
        self.battery_voltage = None

    def update_speed(self, value):
        self.speed = value

    def update_turning(self, turning_status):
        self.turning = turning_status

    def update_battery_voltage(self):
        self.battery_voltage = get_battery_voltage()

    def get_status(self):
        self.update_battery_voltage()
        return f"sts {self.battery_voltage:.2f} {self.direction} {self.turning}"

    def forward(self, amount=1):
        self.px.set_dir_servo_angle(0)
        for _ in range(amount):
            self.px.forward(50)
            time.sleep(0.192)
        self.px.forward(0)
        self.direction = 1 # forward

    def backward(self, amount=1):
        self.px.set_dir_servo_angle(0)
        self.px.backward(50)
        time.sleep(0.385 * amount)
        self.px.backward(0)
        self.direction = 2 # backward

    def rTurn(self, fixpos=True):
        self.turning = True
        if fixpos:
            for _ in range(4):
                self.px.set_dir_servo_angle(45)
                self.px.forward(30)
                time.sleep(0.285)
                self.px.set_dir_servo_angle(-45)
                self.px.backward(30)
                time.sleep(0.290)
                self.px.backward(0)
                self.px.set_dir_servo_angle(0)
        else:
            self.px.set_dir_servo_angle(45)
            self.px.forward(30)
            time.sleep(1.5)
            self.px.forward(0)

        self.direction = 4  # right
        self.turning = False

    def lTurn(self, fixpos=True):
        self.turning = True
        if fixpos:
            for _ in range(4):
                self.px.set_dir_servo_angle(-45)
                self.px.forward(30)
                time.sleep(0.27)
                self.px.set_dir_servo_angle(45)
                self.px.backward(30)
                time.sleep(0.285)
                self.px.backward(0)
                self.px.set_dir_servo_angle(0)
        else:
            self.px.set_dir_servo_angle(-45)
            self.px.forward(30)
            time.sleep(1.5)
            self.px.forward(0)

        self.direction = 3  # left
        self.turning = False
