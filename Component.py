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
        self.S = self.power + 1j*self.reactive
        self.pf = self.power/self.Smag
        self.angle = acos(self.pf)


class Generator:

    def __init__(self, name: str, bus: str, voltage: float, real_power: float, sub_transient_reactance = 0.0, neg_impedance = 0.0, zero_impedance = 0.0, gnd_impedance = None):
        self.name = name
        self.bus = bus
        self.voltage = voltage
        self.real_power = real_power*1e6
        self.sub_transient_reactance = 1j*sub_transient_reactance*settings.powerbase/self.real_power  # updating pu impedance to system power base
        self.neg_impedance = 1j*neg_impedance*settings.powerbase/self.real_power
        self.zero_impedance = 1j*zero_impedance*settings.powerbase/self.real_power
        self.Zn = gnd_impedance
        self.Y0prim = self.calc_Y0prim()
    

    def calc_Y0prim(self):
        if self.Zn == None:
            Y0prim = 0
        elif self.Zn >= 0:
            Y0prim = 1/(3*self.Zn+self.zero_impedance)
        
        return Y0prim


        

