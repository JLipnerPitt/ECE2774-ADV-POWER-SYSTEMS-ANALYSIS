"""
Module to implement transformer functionality

Filename: Transformer.py
Author: Justin Lipner
Date: 2025-02-03
"""

import pandas as pd
from Bus import Bus
from math import atan, sin, cos
from Settings import settings
from Tools import custom_round_complex


class Transformer:
    """
    Transformer class to hold transformer information
    """

    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float,
                 impedance_percent: float, x_over_r_ratio: float, ground_imp = 0.0):
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
        self.power_rating = power_rating*1e6
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.ground_imp = ground_imp
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
        Zpu = R+1j*X
        return Zpu

    def calc_admittance(self):
        """
        Calculate admittance defined as reciprocal of impedance
        :return: Per-unit admittance (complex)
        """
        Ypu = 1/self.Zpu
        return Ypu

    def calc_yprim(self):
        """
        Establish yprim matrix to be used in system admittance matrix
        :return: Admittance matrix (np.array(list[list[]])
        """
        yprim = [[self.Ypu, -self.Ypu], [-self.Ypu, self.Ypu]]
        bus1 = self.bus1.index
        bus2 = self.bus2.index
        df = pd.DataFrame(yprim, index=[bus1, bus2], columns=[bus1, bus2])
        return df

# validation tests 
if __name__ == '__main__':
    from Transformer import Transformer
    from Bus import Bus
    from Settings import settings

    settings.set_powerbase(100e6)
    bus1 = Bus("bus1", 15e3, 1)
    bus2 = Bus("bus2", 30e3, 2)
    power_rating = 125e6
    impedance_percent = 8.5
    x_over_r_ratio = 10
    transformer1 = Transformer("T1", bus1, bus2, power_rating, impedance_percent, x_over_r_ratio)

    print(f"Name: {transformer1.name}, from {transformer1.bus1.name} to {transformer1.bus2.name},", 
          f"Rating = {transformer1.power_rating/1e6} MVA")
    print(f"Z = {transformer1.Zpu}, Y = {transformer1.Ypu}")
    print(f"Yprim = {transformer1.yprim}")
