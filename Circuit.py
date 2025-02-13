"""
Module to implement circuit/system functionality

Filename: Circuit.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-03
"""

import pandas as pd
import Component
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Geometry import Geometry
from Transformer import Transformer
from Conductor import Conductor
from Settings import settings


#  This class "creates" circuits.
class Circuit:
    """
    Circuit class to hold information about system
    """
    def __init__(self, name: str):
        """
        Constructor for the circuit class
        :param name: Name of circuit
        """
        self.name = name
        self.i = float
        self.Ybus = None
        self.powerbase = settings.powerbase

        # Table of all possible components
        self.table = ["Resistors", "Loads", "VSources", "Transformers", "T-Lines"]

        #  Dict that stores all information for each component type
        #  Each component key has a dictionary that stores all components of that type
        self.components = {comp: {} for comp in self.table}

        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometries = {}

    def add_bus(self, name: str, voltage: float):
        """
        Adds bus to circuit object
        :param name: Name of base
        :param voltage: Rated voltage of bus
        :return:
        """
        if name in self.buses:
            print("Bus already exists. No changes to circuit")

        else:
            bus = Bus(name, voltage)
            self.buses.update({name: bus})

    def add_resistor(self, name: str, r: float, bus1="", bus2=""):
        """
        Adds resistor to circuit object
        :param name: Name of resistor
        :param r: Resistance
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :return:
        """
        if name in self.components["Resistors"]:
            print("Resistor already exists. No changes to circuit")

        else:
            resistor = Component.Resistor(name, r, bus1, bus2)
            self.components["Resistors"].update({"R1": resistor})

    def add_load(self, name: str, power: float, voltage: float, bus: str):
        """
        Adds load to circuit object
        :param name: Name of load
        :param power: Rated load power
        :param voltage: Rated load voltage
        :param bus: Bus connection
        :return:
        """
        if name in self.components["Loads"]:
            print("Load already exists. No changes to circuit.")

        else:
            load = Component.Load(name, power, voltage, bus)
            self.components["Loads"].update({name: load})

    def add_voltage_source(self, name: str, v: float, bus: str):
        """
        Adds voltage source to circuit object
        :param name: Name of voltage source
        :param v: Provided voltage
        :param bus: Bus connection
        :return:
        """
        if name in self.components["VSources"]:
            print("Name already exists. No changes to circuit")

        else:
            vsource = Component.VoltageSource(name, v, bus)
            self.components["VSources"].update({name: vsource})
            self.buses[bus].voltage = v  # voltage source overrides bus voltage

    def add_tline(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry,
                  length: float):
        """
        Adds transmission line to circuit object
        :param name: Name of transmission line
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param bundle: Bundle information passed via subclass
        :param geometry: Geometry information passed via subclass
        :param length: Length of transmission line
        :return:
        """
        if name in self.components["T-Lines"]:
            print("Name already exists. No changes to circuit")
        
        else:
            tline = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
            self.components["T-Lines"].update({name: tline})
    
    def add_transformer(self, name: str, bus1: str, bus2: str, power_rating: float,
                        impedance_percent: float, x_over_r_ratio: float):
        """
        Adds transformer to circuit object
        :param name: Name of transformer
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param power_rating: Power rating
        :param impedance_percent: Impedance percent
        :param x_over_r_ratio: X/R Ratio
        :return:
        """
        if name in self.components["Transformers"]:
            print("Name already exists. No changes to circuit")
        
        else:
            transformer = Transformer(name, bus1, bus2, power_rating, impedance_percent,
                                      x_over_r_ratio)
            self.components["Transformers"].update({name: transformer})

    def add_conductor(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        """
        Adds conductor to circuit object for repeated use
        :param name: Name of conductor
        :param diam: Diameter of conductor in inches
        :param GMR: GMR of conductor in feet
        :param resistance: Resistance of conductor at 50°C, 60 Hz
        :param ampacity: Rated ampacity of conductor
        :return:
        """
        if name in self.conductors:
            print("Name already exists. No changes to circuit")

        else:
            conductor = Conductor(name, diam, GMR, resistance, ampacity)
            self.conductors.update({name: conductor})

    def add_bundle(self, name: str, num_conductors: int, spacing: float, conductor: Conductor,
                   v=765.e3):
        """
        Adds bundle to circuit object for repeated use
        :param name: Name of bundle
        :param num_conductors: Number of conductors in bundle
        :param spacing: Equal spacing between conductors
        :param conductor: Conductor subclass
        :param v: Rated voltage of bundle
        :return:
        """
        if name in self.bundles:
            print("Name already exists. No changes to circuit")
        
        else:
            bundle = Bundle(name, num_conductors, spacing, conductor, v)
            self.bundles.update({name: bundle})

    def add_geometry(self, name: str, x: list[float], y: list[float]):
        """
        Adds geometry to circuit object for repeated use
        :param name: Name of geometry
        :param x: List of x coordinates for each phase
        :param y: List of y coordinates for each phase
        :return:
        """
        if name in self.geometries:
            print("Name already exists. No changes to circuit")
    
        else:
            geometry = Geometry(name, x, y)
            self.geometries.update({name: geometry})    

    def calc_Ybus(self):
        pass

    #  checks if buses have the same name and updates the buses list accordingly
    '''
    def check_bus_names(self, index: int, name: str):
      for b in self.buses:
        if self.buses[b].index == index:
          self.buses[b].name = name
          '''


def read_excel():
    dataframe = pd.read_excel(r'C:\Users\iamth\Desktop\Python Programs\ECE2774\Project 2\Excel Files\example6_4.xlsx')
    dataframe = dataframe.fillna(0)  # converts all NaN values to 0
    return dataframe


def compare(Ybus):
    pwrworld = read_excel()
    print(pwrworld)
    

def FivePowerBusSystem():
    settings.set_powerbase(100e6)
    circ = Circuit("Example_6.9")
    conductor1 = Conductor("Drake", 1.106, 0.0375, 0.1288, 900)
    bundle1 = Bundle("Bundle 1", 2, 0.4, conductor1, 250e3)
    geometry1 = Geometry("Geometry 1", [0, 10, 20], [0, 0, 0])

    circ.add_bus("bus1", 15e3)
    circ.add_bus("bus2", 345e3)
    circ.add_bus("bus3", 15e3)
    circ.add_bus("bus4", 345e3)
    circ.add_bus("bus5", 345e3)
    circ.add_transformer("T1", "bus1", "bus5", 400e6, 8.020, 13.333)
    circ.add_transformer("T2", "bus3", "bus4", 800e6, 8.020, 13.333)
    print(circ.components["Transformers"]["T1"].Zpu)
    print(circ.components["Transformers"]["T2"].Zpu)

    circ.add_tline("L3", circ.buses["bus5"], circ.buses["bus4"])
    circ.add_tline("L2", circ.buses["bus5"], circ.buses["bus4"])
    circ.add_tline("L1", circ.buses["bus5"], circ.buses["bus4"])

    return circ


# validation tests
if __name__ == '__main__':
    from Circuit import Circuit
    circuit1 = Circuit("Test Circuit")
    print(circuit1.name)  # Expected output: "Test Circuit"
    print(type(circuit1.name))
    print(circuit1.buses)
    print(type(circuit1.buses))

    circuit1.add_bus("Bus1", 230)
    circuit1.add_bus("Bus1", 230)
    print(type(circuit1.buses["Bus1"]))
    print(circuit1.buses["Bus1"].name, circuit1.buses["Bus1"].base_kv)
    print("Buses in circuit:", list(circuit1.buses.keys()), "\n")

    circuit2 = FivePowerBusSystem()