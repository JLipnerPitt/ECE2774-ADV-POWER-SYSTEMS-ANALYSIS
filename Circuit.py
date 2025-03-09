"""
Module to implement circuit/system functionality
Disclaimer: ChatGPT used for assistance

Filename: Circuit.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-03
"""

from Component import Resistor, Load, VoltageSource, Generator
import numpy as np
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Geometry import Geometry
from Transformer import Transformer
from Conductor import Conductor
from Settings import settings
from Constants import j
from math import sin, cos
import Tools

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
        self.i = {}
        self.Ybus = None
        self.powerbase = settings.powerbase

        # Table of all possible components
        self.table = ["Resistors", "Loads", "VSources", "Generators", "Transformers", "T-lines"]

        #  Dict that stores all information for each component type
        #  Each component key has a dictionary that stores all components of that type
        self.components = {comp: {} for comp in self.table}

        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometries = {}
        self.x = None
        self.y = None
        self.count = 0
        self.slack = str
        self.slack_index = int
        self.pq_indexes = []
        self.pv_indexes = []


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
            self.count += 1
            bus = Bus(name, voltage, self.count)
            self.buses.update({name: bus})
            self.pq_indexes.append(self.count)


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
            resistor = Resistor(name, r, bus1, bus2)
            self.components["Resistors"].update({"R1": resistor})


    def add_load(self, name: str, bus: str, power: float, reactive: float):
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
            load = Load(name, bus, power, reactive)
            self.components["Loads"].update({name: load})
            self.buses[bus].real_power = self.buses[bus].real_power + (-power)
            self.buses[bus].reactive_power = self.buses[bus].reactive_power + (-reactive)


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
            vsource = VoltageSource(name, v, bus)
            self.components["VSources"].update({name: vsource})
            self.buses[bus].voltage = v  # voltage source overrides bus voltage


    def add_tline_from_geometry(self, name: str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry,
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

    
    def add_tline_from_parameters(self, name: str, bus1: Bus, bus2: Bus, R: float, X: float, B: float):
        
        if name in self.components["T-lines"]:
            print(f"{name} already exists. No changes to circuit")
        
        else:
          tline = TransmissionLine.from_parameters(name, bus1, bus2, R, X, B)
          self.components["T-lines"].update({name: tline})
    
    
    def add_transformer(self, name: str, bus1: Bus, bus2: Bus, power_rating: float,
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
    

    def add_generator(self, name: str, bus: str, voltage: float, real_power: float):

        if name in self.components["Generators"]:
            print(f"{name} already exists. No changes to circuit")
        
        else:
            if len(self.components["Generators"]) == 0:
                gen = Generator(name, bus, voltage, real_power)
                self.components["Generators"].update({name: gen})
                self.buses[bus].type = "Slack"
                self.slack = bus
                self.slack_index = self.buses[bus].index
                self.pq_indexes.remove(self.buses[bus].index)
                self.buses[bus].real_power = real_power
            
            else:
                gen = Generator(name, bus, voltage, real_power)
                self.components["Generators"].update({name: gen})
                self.buses[bus].type = "PV"
                self.pq_indexes.remove(self.buses[bus].index)
                self.pv_indexes.append(self.buses[bus].index)
                self.buses[bus].real_power = real_power + self.buses[bus].real_power


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
        for line in self.components["T-lines"]:
            yprim = self.components["T-lines"][line].yprim
            from_bus = yprim.index[0]
            to_bus = yprim.index[1]
            i, j = from_bus-1, to_bus-1
            y_bus[i, i] += yprim.iloc[0, 0]
            y_bus[j, j] += yprim.iloc[1, 1]
            y_bus[i, j] += yprim.iloc[0, 1]
            y_bus[j, i] += yprim.iloc[1, 0]
            
        # Iterate through XFMR impedance
        for xfmr in self.components["Transformers"]:
            yprim = self.components["Transformers"][xfmr].yprim
            from_bus = yprim.index[0]
            to_bus = yprim.index[1]
            i, j = from_bus-1, to_bus-1
            y_bus[i, i] += yprim.iloc[0, 0]
            y_bus[j, j] += yprim.iloc[1, 1]
            y_bus[i, j] += yprim.iloc[0, 1]
            y_bus[j, i] += yprim.iloc[1, 0]

        self.Ybus = y_bus
        return y_bus


    def change_slack(self, old: str, new: str):
        self.buses[old].set_type("PV")
        self.buses[new].set_type("Slack")
        self.slack = new
        self.slack_index = self.buses[new].index
        self.pv_indexes.remove(self.buses[new].index)
        self.pv_indexes.append(self.buses[old].index)
        self.pv_indexes.sort()


    def flat_start(self):
        d = np.zeros(self.count)
        V = np.ones(self.count)
        self.x = {"d": d, "V": V}

        P = []
        Q = []
        
        for bus in self.buses:
            P.append(self.buses[bus].real_power/self.powerbase)
            Q.append(self.buses[bus].reactive_power/self.powerbase)

        P = np.delete(P, self.slack_index-1)
        Q = np.delete(Q, self.slack_index-1)
        self.y = {"P": P, "Q": Q}


    def compute_power_injection(self, x):
        M = self.count-1
        N = self.count
        Ymag = np.abs(self.Ybus)
        theta = np.angle(self.Ybus)
        P = np.zeros(M+1)
        Q = np.zeros(M+1)
        indexes = np.concatenate((self.pq_indexes, self.pv_indexes))
        for k in indexes:
            sum1 = 0
            sum2 = 0
            for n in range(N):
                Ykn = Ymag[k-1, n]
                Vn = x["V"][n]
                dk = x["d"][k-1]
                dn = x["d"][n]
                sum1 += Ykn*Vn*cos(dk - dn - theta[k-1, n])
                sum2 += Ykn*Vn*sin(dk - dn - theta[k-1, n])
            
            Vk = x["V"][k-1]
            Pk = Vk*sum1
            Qk = Vk*sum2
            P[k-1] = Pk
            Q[k-1] = Qk
        
        P = np.delete(P, self.slack_index-1, axis=0)
        Q = np.delete(Q, self.slack_index-1, axis=0)
        return P, Q


    def do_newton_raph(self):
        from Solution import Solution
        solution = Solution(self)
        data = solution.newton_raph()
        return data

    
    def do_fast_decoupled(self):
        pass


    def do_dc_power_flow(self):
        from Solution import Solution
        solution = Solution(self)
        B = np.imag(self.Ybus)
        B = np.delete(np.delete(B, self.slack_index-1, axis=0), self.slack_index-1, axis=1)
        d = solution.dc_power_flow(B, self.y["P"])
        return d




# validation tests
if __name__ == '__main__':
    import Validations
    Validations.FivePowerBusSystemValidation()

