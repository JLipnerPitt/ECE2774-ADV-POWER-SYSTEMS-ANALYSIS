"""
Module to implement transformer functionality

Filename: Transformer.py
Author: Justin Lipner
Date: 2025-02-03
"""

import numpy as np
from math import atan, sin, cos
from Settings import settings


class Transformer:
    """
    Transformer class to hold transformer information
    """

    def __init__(self, name: str, bus1: str, bus2: str, power_rating: float,
                 impedance_percent: float, x_over_r_ratio: float):
        """
        Constructor for Transformer objects
        :param name: Name of transformer
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param power_rating: Power rating
        :param impedance_percent: Impedance percent
        :param x_over_r_ratio: X/R Ratio
        """
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.Zpu = self.calc_impedance()
        self.Ypu = self.calc_admittance()
        self.yprim = self.calc_yprim()

    def calc_impedance(self):
        """
        Given X/R ratio and impedance percent, calculate per unit impedance
        :return: Per-unit impedance (complex)
        """
        theta = atan(self.x_over_r_ratio)
        R = self.impedance_percent * cos(theta) / 100
        R = R*settings.powerbase/self.power_rating  # updating pu to system power base

        X = self.impedance_percent * sin(theta) / 100
        X = X*settings.powerbase/self.power_rating  # updating pu to system power base
        Zpu = complex(R, X)
        return Zpu

    def calc_admittance(self):
        """
        Calculate admittance defined as reciprocal of impedance
        :return: Per-unit admittance (complex)
        """
        return 1 / self.Zpu

    def calc_yprim(self):
        """
        Establish yprim matrix to be used in system admittance matrix
        :return: Admittance matrix (np.array(list[list[]])
        """
        return np.array([[self.Ypu, -self.Ypu], [-self.Ypu, self.Ypu]])

# validation tests 
if __name__ == '__main__':
    from Transformer import Transformer
    transformer1 = Transformer("main", "bus1", "bus2", 125e6, 8.5, 10)
    print(transformer1.name, transformer1.bus1, transformer1.bus2, transformer1.power_rating)
    print(transformer1.Zpu, transformer1.Ypu)
    print(transformer1.yprim)
