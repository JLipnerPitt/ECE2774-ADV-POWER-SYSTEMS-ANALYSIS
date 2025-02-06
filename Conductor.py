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
        :param diam: Diameter of conductor
        :param GMR: GMR of conductor
        :param resistance: Resistance of conductor at 50 C, 60 Hz
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
    conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    print(
        f"Name: {conductor1.name}, Diameter = {conductor1.diam}, GMR = {conductor1.GMR}, "
        f"Radius = {conductor1.radius}, Resistance = {conductor1.resistance}, "
        f"Ampacity = {conductor1.ampacity}")
