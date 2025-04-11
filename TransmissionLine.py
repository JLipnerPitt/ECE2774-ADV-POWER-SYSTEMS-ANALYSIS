"""
Module to implement transmission line functionality

Filename: TransmissionLine.py
Author: Justin Lipner
Date: 2025-01-23
"""

from Bundle import Bundle
from Geometry import Geometry
from Conductor import Conductor
from Settings import settings
from Bus import Bus
import pandas as pd
from math import pi, log
from Constants import j, epsilon, mi2m
from Tools import custom_round_complex, custom_round


class TransmissionLine:
    """
    TransmissionLine class to hold transmission line information
    """

    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle = None, geometry: Geometry = None,
                 length: float = None, flag: bool = True):
        """
        Constructor for TransmissionLine object
        :param name: Name of transmission line
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param bundle: Bundle information
        :param geometry: Geometry information
        :param length: Length of line
        :param f: frequency of line
        """ 
        
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.freq = settings.freq
        self.powerbase = settings.powerbase
        self.Zbase = self.bus1.base_kv**2/self.powerbase

        if flag:
            self.R = self.calc_R()
            self.X = self.calc_X()
            self.Zseries = self.R + j*self.X
            self.Z0series = 2.5*(self.R + j*self.X)
            self.Yseries = 1/self.Zseries
            self.Y0series = 1/self.Z0series
            self.Yshunt = j*self.calc_B()
            self.yprim = self.calc_yprim()
            self.yprim0 = self.calc_yprim0()

        else:
            # "Bypass" path: skip these calculations if flag is false
            self.R = None
            self.X = None
            self.Zseries = None
            self.Yseries = None
            self.Yshunt = None
            self.yprim = None

    
    @classmethod
    def from_parameters(cls, name: str, bus1: Bus, bus2: Bus, R: float, X: float, B: float) -> "TransmissionLine":
        line = cls(name, bus1, bus2, flag=False)
        line.R = R
        line.X = X 
        line.Zseries = R + j*X
        line.Yseries = custom_round_complex(1/line.Zseries, 2)
        line.Yshunt = j*custom_round(B, 2)
        line.yprim = line.calc_yprim()
        return line


    def calc_R(self):
        """
        Calculate line series resistance from bundle information and length
        :return: Series resistance in pu (float)
        """
        #  n = num_conductors
        R_c = self.bundle.conductor.resistance  # gives Ω*n/mi
        R_c = R_c*self.length/self.bundle.num_conductors  # converts Ω*n/mi to Ω
        R_cpu = R_c/self.Zbase
        return R_cpu


    def calc_X(self):
        """
        Calculate line series reactance from geometry information
        :return: Series reactance in pu (float)
        """
        L_c = 2*10**-7*log(self.geometry.Deq/self.bundle.DSL)  # gives H/m
        L_c = L_c*mi2m*self.length  # converts H/m to H
        X_c = 2*pi*self.freq*L_c
        X_cpu = X_c/self.Zbase
        return X_cpu


    def calc_B(self):
        """
        Calculate line shunt susceptance from geometry information
        :return: Shunt susceptance in pu (float)
        """
        C_c = 2*pi*epsilon/(log(self.geometry.Deq/self.bundle.DSC))  # gives F/m
        C_c = C_c*mi2m*self.length  # converts F/m to F
        B = 2*pi*self.freq*C_c
        B_pu = B*self.Zbase
        return B_pu


    def calc_yprim(self):
        """
        Calculate yprim for admittance matrix
        :return:
        """
        Y = self.Yseries + self.Yshunt/2
        bus1 = self.bus1.index
        bus2 = self.bus2.index
        yprim = [[Y, -Y+self.Yshunt/2], [-Y+self.Yshunt/2, Y]]

        df = pd.DataFrame(yprim, index=[bus1, bus2], columns=[bus1, bus2])
        return df
    

    def calc_yprim0(self):
        """
        Calculate yprim for admittance matrix
        :return:
        """
        Y0 = self.Y0series + self.Yshunt/2
        bus1 = self.bus1.index
        bus2 = self.bus2.index
        yprim = [[Y0, -Y0+self.Yshunt/2], [-Y0+self.Yshunt/2, Y0]]

        df = pd.DataFrame(yprim, index=[bus1, bus2], columns=[bus1, bus2])
        return df


# validation tests
def validation1():
    from TransmissionLine import TransmissionLine
    bus1 = Bus("bus1", 230, 1)
    bus2 = Bus("bus2", 230, 2)
    conductor1 = Conductor("Drake", 1.106, 0.0375, 0.1288, 900)
    bundle1 = Bundle("Bundle 1", 2, 0.4, conductor1, 250e3)
    geometry1 = Geometry("Geometry 1", [0, 10, 20], [0, 0, 0])
    line1 = TransmissionLine("Line 1", bus1, bus2, bundle1, geometry1, 124.274)
    print(f"Line: {line1.name}, from {line1.bus1.name} to {line1.bus2.name}, length: {line1.length} miles")
    print(f"Z = {line1.Zseries}, Y_series = {line1.Yseries}, Y_shunt = {line1.Yshunt}")
    print(f"Yprim = {line1.yprim}")
    print()

def validation2():
    from TransmissionLine import TransmissionLine
    bus1 = Bus("bus1", 230, 1)
    bus2 = Bus("bus2", 230, 2)
    line1 = TransmissionLine.from_parameters("Line 1", bus1, bus2, R=0.009, X=0.100, B=1.72)
    print(f"Line: {line1.name}, from {line1.bus1.name} to {line1.bus2.name}")
    print(f"Z = {line1.Zseries}, Y_series = {line1.Yseries}, Y_shunt = {line1.Yshunt}")
    print(f"Yprim = {line1.yprim}")


# validation tests
if __name__ == '__main__':
    validation1()
    validation2()
