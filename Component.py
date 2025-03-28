#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
from math import acos
from Settings import settings

class Resistor:
    
    def __init__(self, name: str, value: float, bus1: str, bus2: str):
        self.name = name
        self.value = value
        self.bus1 = bus1
        self.bus2 = bus2
        self.g = float
        self.calc_g()


    def calc_g(self):
        self.g = 1 / self.value


class Inductor:
    pass


class Capacitor:
    pass


class Load:

    def __init__(self, name: str, bus: str, real_power: float, reactive_power: float):
        self.name = name
        self.power = real_power*1e6
        self.reactive = reactive_power*1e6
        self.bus = bus
        self.Smag = (self.power**2 + self.reactive**2)**(1/2)
        self.angle = acos(self.power/self.Smag)


class Generator:

    def __init__(self, name: str, bus: str, voltage: float, real_power: float, pos_impedance: float):
        self.name = name
        self.bus = bus
        self.voltage = voltage
        self.real_power = real_power*1e6
        self.pos_seq_impedance = pos_impedance*settings.powerbase/self.real_power  # updating pu impedance to system power base

        

