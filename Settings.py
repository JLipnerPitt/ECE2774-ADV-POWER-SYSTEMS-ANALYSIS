"""
Module for constants throughout power system calculations

Filename: Constants.py
Author: Justin Lipner
Date: 2025-02-06
"""


class Settings:
    """
    Settings class for user to adjust system parameters
    """
    def __init__(self, powerbase=100, freq=60):
        """
        Constructor for Settings object
        :param powerbase: MVA Base
        :param freq: Frequency Hz
        """
        self.freq = freq
        self.powerbase = powerbase

    def set_freq(self, f):
        """
        Set function for frequency
        :param f: Frequency Hz
        :return:
        """
        self.freq = f

    def set_powerbase(self, p):
        """
        Set function for base power
        :param p: MVA Base
        :return:
        """
        self.powerbase = p


settings = Settings()
