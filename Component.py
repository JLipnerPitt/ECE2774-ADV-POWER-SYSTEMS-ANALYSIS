#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
from math import acos
from Settings import settings


class Load:

    def __init__(self, name: str, bus: str, real_power: float, reactive_power: float):
        """
        Constructor for Load class
        :param name: Name of load
        :param bus: Bus connection
        :param real_power: Real power load is using
        :param reactive_power: Reactive power load is using
        """
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
        self.X0 = self.calc_X0(zero_impedance)
        self.X1 = self.calc_X1(sub_transient_reactance)
        self.X2 = self.calc_X2(neg_impedance)
        self.Zn = gnd_impedance
        self.Y0prim = self.calc_Y0prim()
        self.var_limit = var_limit
    

    def calc_X0(self, X0):
        X0 = 1j*X0*settings.powerbase/self.real_power
        return X0


    def calc_X1(self, X1):
        X1 = 1j*X1*settings.powerbase/self.real_power
        return X1


    def calc_X2(self, X2):
        X2 = 1j*X2*settings.powerbase/self.real_power
        return X2


    def set_power(self, real: float, reactive: float):
        self.real_power = real*1e6
        self.reactive_power = reactive*1e6

        
    def calc_Y0prim(self):
        if self.Zn == None:
            Y0prim = 0
        elif self.Zn >= 0:
            Y0prim = 1/(3*self.Zn+self.X0)
        
        return Y0prim


        

