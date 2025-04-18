#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
from math import acos
from Settings import settings
import pandas as pd
from Bus import Bus


class Load:

    def __init__(self, name: str, bus: str, real_power: float, reactive_power: float):
        self.name = name
        self.bus = bus
        self.real_power = real_power*1e6
        self.reactive_power = reactive_power*1e6
        self.Smag = (self.real_power**2 + self.reactive_power**2)**(1/2)
        self.S = self.real_power + 1j*self.reactive_power
        self.pf = self.real_power/self.Smag
        self.angle = acos(self.pf)


class Generator:

    def __init__(self, name: str, bus: str, voltage: float, real_power: float, sub_transient_reactance = 0.0, neg_impedance = 0.0, zero_impedance = 0.0, gnd_impedance = None, var_limit = float('inf')):
        self.name = name
        self.bus = bus
        self.voltage = voltage
        self.real_power = real_power*1e6
        self.reactive_power = 0
        self.sub_transient_reactance = 1j*sub_transient_reactance*settings.powerbase/self.real_power  # updating pu impedance to system power base
        self.neg_impedance = 1j*neg_impedance*settings.powerbase/self.real_power
        self.zero_impedance = 1j*zero_impedance*settings.powerbase/self.real_power
        self.Zn = gnd_impedance
        self.Y0prim = self.calc_Y0prim()
        self.var_limit = var_limit
    

    def set_power(self, real: float, reactive: float):
        self.real_power = real*1e6
        self.reactive_power = reactive*1e6

        
    def calc_Y0prim(self):
        if self.Zn == None:
            Y0prim = 0
        elif self.Zn >= 0:
            Y0prim = 1/(3*self.Zn+self.zero_impedance)
        
        return Y0prim


        

