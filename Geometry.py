"""
Module to implement geometry functionality

Filename: Geometry.py
Author: Justin Lipner
Date: 2025-01-23
"""

from math import sqrt


class Geometry:
    """
    Subclass geometry for transmission lines
    """
    def __init__(self, name: str, x: list[float], y: list[float]):
        """
        Constructor for Geometry subclass
        :param name: Name of geometry
        :param x: List of x values for each line
        :param y: List of y values for each line
        """
        # pos = [[], []]
        self.name = name
        self.x = x
        self.y = y
        self.Deq = self.calc_Deq()  # in meters

    # Deq = GMD = Dxy
    def calc_Deq(self):
        """
        Calculate Deq from x and y lists
        :return: Deq (float)
        """
        root = len(self.x)
        Dab = sqrt((self.x[1] - self.x[0]) ** 2 + (self.y[1] - self.y[0]) ** 2)
        Dbc = sqrt((self.x[2] - self.x[1]) ** 2 + (self.y[2] - self.y[1]) ** 2)
        Dca = sqrt((self.x[0] - self.x[2]) ** 2 + (self.y[0] - self.y[2]) ** 2)
        self.Deq = (Dab * Dbc * Dca) ** (1 / root)
        return self.Deq


# validation tests
if __name__ == '__main__':
    from Geometry import Geometry
    geometry1 = Geometry("Geometry 1", [0, 10, 20], [0, 0, 0])
    print(geometry1.name, geometry1.x, geometry1.y)
    print("Deq =", geometry1.Deq, "m")
