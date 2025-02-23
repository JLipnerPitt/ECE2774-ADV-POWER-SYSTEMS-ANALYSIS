"""
Module to implement circuit/system functionality
Disclaimer: ChatGPT used for assistance

Filename: Circuit.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-03
"""

import pandas as pd
import numpy as np
import os

import Component
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Geometry import Geometry
from Transformer import Transformer
from Conductor import Conductor
from Settings import settings
from Constants import j

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
        self.table = ["Resistors", "Loads", "VSources", "Transformers", "T-lines"]

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
            print(f"{name} already exists. No changes to circuit")

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
            print(f"{name} already exists. No changes to circuit")

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
            print(f"{name} already exists. No changes to circuit")

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
            print(f"{name} already exists. No changes to circuit")

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
        if name in self.components["T-lines"]:
            print(f"{name} already exists. No changes to circuit")
        
        else:
            tline = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
            self.components["T-lines"].update({name: tline})
    
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
            print(f"{name} already exists. No changes to circuit")
        
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
            print(f"{name} already exists. No changes to circuit")

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
            print(f"{name} already exists. No changes to circuit")
        
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
        """
        Calculate admittance matrix of system and export to CSV
        :return: Admittance matrix (list[list[complex double]])
        """
        num_buses = len(self.buses)
        y_bus = np.zeros((num_buses, num_buses), dtype=complex)

        # Iterate through line impedance
        for line_name, line in self.components["T-Lines"].items():
            y_prim = line.calc_yprim()
            from_bus = line.bus1
            to_bus = line.bus2
            i, j = from_bus.index - 1, to_bus.index - 1
            y_bus[i, i] += y_prim[0, 0]
            y_bus[j, j] += y_prim[1, 1]
            y_bus[i, j] -= y_prim[0, 1]
            y_bus[j, i] -= y_prim[1, 0]

        # Iterate through XFMR impedance
        for xfmr_name, xfmr in self.components["Transformers"].items():
            y_prim = xfmr.calc_yprim()
            from_bus_name = xfmr.bus1
            to_bus_name = xfmr.bus2
            from_bus = self.buses[from_bus_name]
            to_bus = self.buses[to_bus_name]
            i, j = from_bus.index - 1, to_bus.index - 1
            y_bus[i, i] += y_prim[0, 0]
            y_bus[j, j] += y_prim[1, 1]
            y_bus[i, j] -= y_prim[0, 1]
            y_bus[j, i] -= y_prim[1, 0]

        # Save y_bus in csv for debugging and return
        y_bus_str = np.array(
            [[f"{val.real:.6f} + {val.imag:.6f}j" for val in row] for row in y_bus])
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Ybus_Matrix.csv")
        np.savetxt(desktop_path, y_bus_str, delimiter=",", fmt="%s")

        return y_bus

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
    #conductor1 = Conductor("Drake", 1.106, 0.0375, 0.1288, 900)
    #bundle1 = Bundle("Bundle 1", 2, 0.4, conductor1, 250e3)
    #geometry1 = Geometry("Geometry 1", [0, 10, 20], [0, 0, 0])
    #circ.add_tline("L3", circ.buses["bus5"], circ.buses["bus4"], bundle1, geometry1, 50)
    #circ.add_tline("L2", circ.buses["bus5"], circ.buses["bus4"], bundle1, geometry1, 100)
    #circ.add_tline("L1", circ.buses["bus5"], circ.buses["bus4"], bundle1, geometry1, 200)
    #circ.components["T-lines"]["L1"].Zseries = 0.0090 + j*0.100
    #circ.components["T-lines"]["L2"].Zseries = 0.0045 + j*0.050
    #circ.components["T-lines"]["L3"].Zseries = 0.00225 + j*0.025

    circ.add_bus("bus1", 15e3)
    circ.add_bus("bus2", 345e3)
    circ.add_bus("bus3", 15e3)
    circ.add_bus("bus4", 345e3)
    circ.add_bus("bus5", 345e3)
    circ.add_transformer("T1", "bus1", "bus5", 400e6, 8.020, 13.333)
    circ.add_transformer("T2", "bus3", "bus4", 800e6, 8.020, 13.333)

    print(circ.components["Transformers"]["T1"].Zpu)
    print(circ.components["Transformers"]["T2"].Zpu)
    print()

    line1 = TransmissionLine.from_parameters("L1", circ.buses["bus2"], circ.buses["bus4"], R=0.009, X=0.100, B=1.72)
    line2 = TransmissionLine.from_parameters("L2", circ.buses["bus2"], circ.buses["bus5"], R=0.0045, X=0.05, B=0.88)
    line3 = TransmissionLine.from_parameters("L3", circ.buses["bus5"], circ.buses["bus4"], R=0.00225, X=0.025, B=0.44)

    circ.components["T-lines"].update({"L1": line1})
    circ.components["T-lines"].update({"L2": line2})
    circ.components["T-lines"].update({"L3": line3})

    print(circ.components["T-lines"]["L1"].Zseries)
    print(circ.components["T-lines"]["L2"].Zseries)
    print(circ.components["T-lines"]["L3"].Zseries)
    print()

    print(circ.components["T-lines"]["L1"].Yshunt)
    print(circ.components["T-lines"]["L2"].Yshunt)
    print(circ.components["T-lines"]["L3"].Yshunt)
    print()

    print(circ.components["T-lines"]["L1"].yprim)
    print(circ.components["T-lines"]["L2"].yprim)
    print(circ.components["T-lines"]["L3"].yprim)
    print()
    
    return circ


# validation tests
if __name__ == '__main__':
    """
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
    """
    circuit2 = FivePowerBusSystem()
    circuit2.calc_Ybus()