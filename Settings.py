"""
Module for settings throughout power system calculations

Filename: Settings.py
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
        self.powerbase = powerbase*1e6


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
        self.powerbase = p*1e6


settings = Settings()
