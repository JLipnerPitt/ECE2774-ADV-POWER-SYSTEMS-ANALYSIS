#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
from math import acos
from Settings import settings


class Component:

    def __init__(self, name: str, value: float, bus1: str, bus2: str):
        self.name = name
        self.value = value
        self.bus1 = bus1
        self.bus2 = bus2


class Resistor(Component):

    def __init__(self, name: str, value: float, bus1: str, bus2: str):
        self.name = name
        self.value = value
        self.bus1 = bus1
        self.bus2 = bus2
        self.g = float
        self.calc_g()


    def calc_g(self):
        self.g = 1 / self.value


class Inductor(Component):
    pass


class Capacitor(Component):
    pass


class Load(Component):

    def __init__(self, name: str, real_power: float, reactive_power: float, voltage: float, bus: str):
        self.name = name
        self.power = real_power
        self.reactive = reactive_power
        self.voltage = voltage
        self.bus = bus
        self.R = self.calc_R()
        self.X = self.calc_X()
        self.Z = self.R + self.X*1j
        self.g = self.calc_G()


    def calc_R(self):
        return self.voltage**2 / self.power
    

    def calc_X(self):
        return self.voltage**2 / self.reactive


    def calc_G(self):
        return 1/self.resistance
    

    def calc_angle(self):
        S = (self.power**2 + self.reactive**2)**1/2
        return acos(self.power/S)


class VoltageSource(Component):

    def __init__(self, name: str, voltage: float, bus1: str):
        self.name = name
        self.voltage = voltage
        self.bus1 = bus1


class CurrentSource(Component):
    pass
