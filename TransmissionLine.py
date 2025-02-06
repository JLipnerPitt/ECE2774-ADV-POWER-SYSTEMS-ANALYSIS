"""
Module to implement transmission line functionality

Filename: TransmissionLine.py
Author: Justin Lipner
Date: 2025-01-23
"""

from Bundle import Bundle
from Geometry import Geometry
from Conductor import Conductor
from Settings import Settings
import numpy as np

from math import pi, log
from Constants import j, epsilon


class TransmissionLine:
    """
    TransmissionLine class to hold transmission line information
    """

    def __init__(self, name: str, bus1: str, bus2: str, bundle: Bundle, geometry: Geometry,
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
        """
        settings = Settings()  # sets powerbase and frequency of transmission line
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.freq = settings.freq
        self.R = self.calc_R()
        self.X = self.calc_X()
        self.Zseries = self.R + j*self.X
        self.Yseries = 1/self.Zseries
        self.Yshunt = j*self.calc_B()
        self.yprim = self.calc_yprim()

    def calc_R(self):
        """
        Calculate line series resistance from bundle information and length
        :return: Series resistance (float)
        """
        R_c = self.bundle.conductor.resistance
        return R_c*self.length/self.bundle.num_conductors

    def calc_X(self):
        """
        Calculate line series reactance from geometry information
        :return: Series reactance (float)
        """
        L_c = 2*10**-7*log(self.geometry.Deq/self.bundle.DSL)*1609*self.length  # gives Henries
        X_c = 2*pi*self.freq*L_c
        return X_c

    def calc_B(self):
        """
        Calculate line shunt reactance from geometry information
        :return: Shunt reactance (float)
        """
        C_c = 2*pi*epsilon/(log(self.geometry.Deq/self.bundle.DSC))
        C_c = C_c*1609*self.length  # converts F/mi to F
        B = 2*pi*self.freq*C_c 
        return B

    def calc_yprim(self):
        """
        Calculate yprim for admittance matrix
        :return:
        """
        Y = self.Yseries+self.Yshunt
        return np.array([[Y, -Y], [-Y, Y]])


def TransmissionLine_Validation():
    """
    Debugging function to verify TransmissionLine functionality
    :return:
    """
    conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)
    geometry1 = Geometry("Geometry 1", [0, 0, 18.5], [0, 37, 0])
    line1 = TransmissionLine("Line 1", "bus1", "bus2", bundle1, geometry1, 10)
    print(line1.name, line1.bus1, line1.bus2, line1.length)
    print(line1.Zseries, line1.Yseries, line1.Yshunt)
    print(line1.yprim)

TransmissionLine_Validation()
