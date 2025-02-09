"""
Module to implement bundle functionality
Disclaimer: ChatGPT used for assistance

Filename: Bundle.py
Author: Justin Lipner, Bailey Stout
Date: 2025-01-23
"""

from Conductor import Conductor
from math import sqrt
from warnings import warn


class Bundle:
    """
    Subclass Bundle for transmission line
    """
    def __init__(self, name: str, num_conductors: int, spacing: float, conductor: Conductor,
                 v=765.e3):
        """
        Constructor for Bundle subclass
        :param name: Name of bundle
        :param num_conductors: Number of conductors in bundle
        :param spacing: Equal spacing between conductors
        :param conductor: Conductor for this bundle
        :param v: Line voltage
        """
        self.name = name
        self.v = v
        self.num_conductors = num_conductors
        self.verify_num()
        self.spacing = spacing
        self.conductor = conductor
        self.DSC = self.calc_DSC()
        self.DSL = self.calc_DSL()

    def verify_num(self):
        """
        Verify that the num_conductors is correct - if not, reassign based on voltage
        :return:
        """
        # Reference voltages for low, medium, and high
        lv = 230e3
        mv = 300e3
        hv = 400e3

        # Reassign num_conductors if invalid input
        if self.num_conductors not in {1, 2, 3, 4}:
            if self.v < lv:
                self.num_conductors = 1
            elif lv <= self.v < mv:
                self.num_conductors = 2
            elif mv <= self.v < hv:
                self.num_conductors = 3
            else:
                self.num_conductors = 4
            warn(f"Invalid conductor count. Must be 1 - 4. "
                          f"Defaulting to {self.num_conductors} conductors for {self.v / 1e3} kV.")

    def calc_DSC(self):
        """
        Calculate Dsc from conductor and spacing information
        :return: Dsc (float)
        """
        n = self.num_conductors
        d = self.spacing
        r = self.conductor.radius

        match n:
            case 1:
                DSC = r
            case 2:
                DSC = sqrt(d * r)
            case 3:
                DSC = (d ** (n - 1) * r) ** (1 / n)
            case 4:
                DSC = 1.091 * (d ** (n - 1) * r) ** (1 / n)
            case _:
                DSC = 0

        return DSC

    # modify edge cases to be more verbose (warning)
    def calc_DSL(self):
        """
        Calculate Dsl from conductor and spacing information
        :return: Dsl (float)
        """
        n = self.num_conductors
        GMR = self.conductor.GMR
        d = self.spacing

        match n:
            case 1:
                DSL = GMR
            case 2:
                DSL = sqrt(d * GMR)
            case 3:
                DSL = (d ** (n - 1) * GMR) ** (1 / n)
            case 4:
                DSL = 1.091 * (d ** (n - 1) * GMR) ** (1 / n)
            case _:
                DSL = 0

        return DSL


# validation tests
if __name__ == '__main__':
    from Bundle import Bundle
    conductor1 = Conductor.Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    bundle1 = Bundle("Bundle 1", 5, 1.5, conductor1, 250e3)
    print(
        f"Bundle name: {bundle1.name}, # of conductors = {bundle1.num_conductors}, "
        f"spacing = {bundle1.spacing}, Conductor name: {bundle1.conductor.name}")
    print(f"DSC = {bundle1.DSC}, DSL = {bundle1.DSL}")
