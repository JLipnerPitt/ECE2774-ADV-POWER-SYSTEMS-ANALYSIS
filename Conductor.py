"""
Module to implement conductor functionality

Filename: Conductor.py
Author: Justin Lipner
Date: 2025-01-23
"""


class Conductor:
    """
    Subclass Conductor for transmission line
    """
    def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        """
        Constructor for conductor subclass
        :param name: Name of conductor
        :param diam: Diameter of conductor in inches
        :param GMR: GMR of conductor in feet
        :param resistance: Resistance of conductor at 50°C, 60 Hz
        :param ampacity: Rated ampacity of conductor
        """
        self.name = name
        self.diam = diam  # in inches
        self.radius = diam / 24  # in feet
        self.GMR = GMR  # in feet
        self.resistance = resistance
        self.ampacity = ampacity


# validation tests
if __name__ == '__main__':
    from Conductor import Conductor
    #conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    #conductor1 = Conductor("Falcon", 1.545, 0.0520, 0.0646, 1380)
    conductor1 = Conductor("Drake", 1.106, 0.0375, 0.1288, 900)
    print(
        f"Name: {conductor1.name}, Diameter = {conductor1.diam} in, GMR = {conductor1.GMR} ft, "
        f"Radius = {conductor1.radius} ft, Resistance = {conductor1.resistance} Ω, "
        f"Ampacity = {conductor1.ampacity} A")
