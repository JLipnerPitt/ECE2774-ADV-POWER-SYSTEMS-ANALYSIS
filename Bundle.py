"""
Module to implement bundle functionality

Filename: Bundle.py
Author: Justin Lipner
Date: 2025-01-23
"""

import Conductor
from math import sqrt


class Bundle:
    """
    Subclass Bundle for transmission line
    """
    def __init__(self, name: str, num_conductors: int, spacing: float, conductor: Conductor):
        """
        Constructor for Bundle subclass
        :param name: Name of bundle
        :param num_conductors: Number of conductors in bundle
        :param spacing: Equal spacing between conductors
        :param conductor: Conductor for this bundle
        """
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor
        self.DSC = self.calc_DSC()
        self.DSL = self.calc_DSL()

    # modify edge cases to be more verbose (warning)
    def calc_DSC(self):
        """
        Calculate Dsc from conductor and spacing information
        :return: Dsc (float)
        """
        n = self.num_conductors
        d = self.spacing
        r = self.conductor.radius
        DSC = float

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
        DSL = float

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


def Bundle_Validation():
    """
    Debugging function for verifying Bundle functionality
    :return:
    """
    conductor1 = Conductor.Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)
    print(
        f"Bundle name: {bundle1.name}, # of conductors = {bundle1.num_conductors}, "
        f"spacing = {bundle1.spacing}, Conductor name: {bundle1.conductor.name}")
    print(f"DSC = {bundle1.DSC}, DSL = {bundle1.DSL}")


Bundle_Validation()
