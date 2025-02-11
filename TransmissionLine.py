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
import numpy as np

from math import pi, log
from Constants import j, epsilon, mi2m


class TransmissionLine:
    """
    TransmissionLine class to hold transmission line information
    """

    def __init__(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry,
                 length: float):
        """
        Constructor for TransmissionLine object
        :param name: Name of transmission line
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param bundle: Bundle information
        :param geometry: Geometry information
        :param length: Length of line
        :param f: frequency of line
        """  # sets powerbase and frequency of transmission line
        
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.freq = settings.freq
        self.powerbase = settings.powerbase

        self.Zbase = self.bus1.base_kv**2/self.powerbase
        self.R = self.calc_R()
        self.X = self.calc_X()
        self.Zseries = self.R + j*self.X
        self.Yseries = 1/self.Zseries
        self.Yshunt = j*self.calc_B()
        self.yprim = self.calc_yprim()

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
        B_pu = B/self.Zbase
        return B_pu

    def calc_yprim(self):
        """
        Calculate yprim for admittance matrix
        :return:
        """
        Y = self.Yseries+self.Yshunt/2
        return np.array([[Y, -Y], [-Y, Y]])


# validation tests
if __name__ == '__main__':
    from TransmissionLine import TransmissionLine
    bus1 = Bus("bus1", 230)
    bus2 = Bus("bus2", 230)
    conductor1 = Conductor("Drake", 1.106, 0.0375, 0.1288, 900)
    bundle1 = Bundle("Bundle 1", 2, 0.4, conductor1, 250e3)
    geometry1 = Geometry("Geometry 1", [0, 10, 20], [0, 0, 0])
    line1 = TransmissionLine("Line 1", bus1, bus2, bundle1, geometry1, 124.274)
    print(line1.name, line1.bus1.name, line1.bus2.name, line1.length)
    print(line1.Zseries, line1.Yseries, line1.Yshunt)
    print(line1.yprim)
