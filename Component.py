#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
from math import acos
from Settings import settings
import pandas as pd
from Bus import Bus


class Reactor:
    def __init__(self, name: str, mvar: float, bus1: str, bus2: str = None):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus1 if bus2 == None else bus2
        self.mvar = -mvar*1e6
        self.type = "shunt" if bus2 == None else "series"
        self.voltage = bus1.base_kv
        self.Zbase = self.voltage**2/settings.powerbase
        self.Z = 1j*self.voltage**2/self.mvar
        self.Zpu = self.Z/self.Zbase
        self.Y = 1/self.Z
        self.Ypu = 1/self.Zpu
        self.Yprim = self.calc_yprim()


    def calc_yprim(self):

        if self.type == "series":
            from_bus = self.bus1.index
            to_bus = self.bus2.index
            yprim = [[self.Ypu, -self.Ypu], [-self.Ypu, self.Ypu]]
            df = pd.DataFrame(yprim, index=[from_bus, to_bus], columns=[from_bus, to_bus])

        elif self.type == "shunt":
            bus = self.bus1.index
            yprim = [[self.Ypu, 0], [0, 0]]
            df = pd.DataFrame(yprim, index=[bus, bus], columns=[bus, bus])

        return df


class Capacitor:
    def __init__(self, name: str, mvar: float, bus1: str, bus2: str = None):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus1 if bus2 == None else bus2
        self.mvar = mvar*1e6
        self.type = "shunt" if bus2 == None else "series"
        self.voltage = bus1.base_kv
        self.Zbase = self.voltage**2/settings.powerbase
        self.Z = self.voltage**2/(1j*self.mvar)
        self.Zpu = self.Z/self.Zbase
        self.Y = 1/self.Z
        self.Ypu = 1/self.Zpu   
        self.Yprim = self.calc_yprim()
    

    def calc_yprim(self):

        if self.type == "series":
            from_bus = self.bus1.index
            to_bus = self.bus2.index
            yprim = [[self.Ypu, -self.Ypu], [-self.Ypu, self.Ypu]]
            df = pd.DataFrame(yprim, index=[from_bus, to_bus], columns=[from_bus, to_bus])

        elif self.type == "shunt":
            bus = self.bus1.index
            yprim = [[self.Ypu, 0], [0, 0]]
            df = pd.DataFrame(yprim, index=[bus, bus], columns=[bus, bus])
            print(df)

        return df


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
        self.reactive_power = 0.
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


        

