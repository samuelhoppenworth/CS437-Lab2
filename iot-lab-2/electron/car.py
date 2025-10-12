from picarx import Picarx
from robot_hat.utils import get_battery_voltage

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

