"""
Module to implement circuit/system functionality
Disclaimer: ChatGPT used for assistance

Filename: Circuit.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-03
"""

from Component import Load, Generator, Reactor, Capacitor
import numpy as np
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Geometry import Geometry
from Transformer import Transformer
from Conductor import Conductor
from Settings import settings
from math import sin, cos
import pandas as pd

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
        self.powerbase = settings.powerbase

        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometries = {}
        self.transmission_lines = {}
        self.transformers = {}
        self.loads = {}
        self.generators = {}
        self.reactors = {}
        self.capacitors = {}

        self.count = 0
        self.slack_bus = str
        self.slack_index = int
        self.pq_indexes = []
        self.pv_indexes = []
        self.pq_and_pv_indexes = []
        self.bus_order = []

        self.Ybus = None # system admittance matrix
        self.x = None # stores bus voltages and angles after power flow is ran
        self.y = None # stores bus power injections after power flow is ran
        self.voltages = None
        
        self.changed = False


    def change_power_base(self, p: float):
        """
        Changes the systems base power.
        :param p: New base power.
        :return:
        """
        settings.set_powerbase(p)
        self.powerbase = p*1e6


    def change_frequency(self, f: float):
        """
        Changes the systems base frequency.
        :param f: New system frequency.
        :return:
        """
        settings.set_freq(f)

    
    def add_bus(self, name: str, voltage: float):
        """
        Adds a bus to the system.
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
            self.bus_order.append(self.count)


    def add_load(self, name: str, bus: str, real: float, reactive: float):
        """
        Adds a load to system.
        :param name: Name of load
        :param bus: Bus connection
        :param real: Load's real power usage
        :param reactive: Load's reactive power usage
        :return:
        """
        if name in self.loads:
            print(f"{name} already exists. No changes to circuit.")
            return
        
        if bus not in self.buses:
            print(f"{bus} does not exist. No changes to circuit.")
            return

        load = Load(name, bus, real, reactive)
        self.loads.update({name: load})
        self.buses[bus].set_power(-real*1e6, -reactive*1e6)


    def add_tline_from_geometry(self, name: str, bus1: str, bus2: str, bundle: str, geometry: str,
                  length: float):
        """
        Adds a transmission line to system.
        :param name: Name of transmission line
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param bundle: Bundle information passed via subclass
        :param geometry: Geometry information passed via subclass
        :param length: Length of transmission line
        :return:
        """
        
        if name in self.transmission_lines:
            print(f"{name} already exists. No changes to circuit")
            return
        
        tline = TransmissionLine(name, self.get_bus(bus1), self.get_bus(bus2), self.get_bundle(bundle), self.get_geometry(geometry), length)
        self.transmission_lines.update({name: tline})
        self.changed = True

    
    def add_tline_from_parameters(self, name: str, bus1: str, bus2: str, R: float, X: float, B: float):
        """
        Adds a transmission line to system.
        :param name: Name of transmission line
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param R: per unit resistance
        :param X: per unit reactance
        :param B: per unit shunt admittance
        :return:
        """
        
        if name in self.transmission_lines:
            print(f"{name} already exists. No changes to circuit")
            return
        
        tline = TransmissionLine.from_parameters(name, self.get_bus(bus1), self.get_bus(bus2), R, X, B)
        self.transmission_lines.update({name: tline})
        self.changed = True
    
    
    def add_transformer(self, name: str, type: str, bus1: str, bus2: str, power_rating: float,
                        impedance_percent: float, x_over_r_ratio: float, gnd_impedance=None):
        """
        Adds a transformer to system.
        :param name: Name of transformer
        :param bus1: First bus connection
        :param bus2: Second bus connection
        :param power_rating: Power rating
        :param impedance_percent: Impedance percent
        :param x_over_r_ratio: X/R Ratio
        :return:
        """
        if name in self.transformers:
            print(f"{name} already exists. No changes to circuit")
            return
        
        transformer = Transformer(name, type, self.get_bus(bus1), self.get_bus(bus2), power_rating, impedance_percent,
                                      x_over_r_ratio, gnd_impedance)
        self.transformers.update({name: transformer})
        self.changed = True
    

    def add_generator(self, name: str, bus: str, voltage: float, real_power: float, pos_imp = 0.0, neg_imp = 0.0, zero_imp = 0.0, gnd_imp = 0.0, var_limit = float('inf')):
        """
        Adds a generator to system.
        :param name: Name of transformer
        :param bus: Bus connection
        :param voltage: Operating voltage in pu
        :param real_power: Power rating
        :param pos_imp: Positive sequence impedance
        :param neg_imp: Negative sequence impedance
        :param zero_imp: Zero sequence impedance
        :param gnd_imp: Ground sequence impedance
        :param var_limit: Maximum VARs the generator can safely output
        :return:
        """
        if name in self.generators:
            print(f"{name} already exists. No changes to circuit")
            return
        
        if bus not in self.buses:
            print(f"{bus} does not exist. No changes to circuit")
            return
    
        if len(self.generators) == 0:
            gen = Generator(name, bus, voltage, real_power, pos_imp, neg_imp, zero_imp, gnd_imp, var_limit)
            self.generators.update({name: gen})
            self.buses[bus].type = "Slack"
            self.slack_bus = bus
            self.slack_index = self.buses[bus].index
            self.pq_indexes.remove(self.buses[bus].index)
            self.buses[bus].set_power(real_power*1e6, 0)
        
        else:
            gen = Generator(name, bus, voltage, real_power, pos_imp, neg_imp, zero_imp, gnd_imp, var_limit)
            self.generators.update({name: gen})
            self.buses[bus].type = "PV"
            self.pq_indexes.remove(self.buses[bus].index)
            self.pv_indexes.append(self.buses[bus].index)
            self.buses[bus].set_power(real_power*1e6, 0)


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


    def add_bundle(self, name: str, num_conductors: int, spacing: float, conductor: Conductor):
        """
        Adds bundle to circuit object for repeated use
        :param name: Name of bundle
        :param num_conductors: Number of conductors in bundle
        :param spacing: Equal spacing between conductors
        :param conductor: Conductor subclass
        :return:
        """
        if name in self.bundles:
            print(f"{name} already exists. No changes to circuit")
        
        else:
            bundle = Bundle(name, num_conductors, spacing, self.get_conductor(conductor))
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

    """
    def add_series_reactor(self, name: str, mvar: float, bus1: str, bus2: str):

        if name in self.reactors:
            print("Name already exists. No changes to circuit")
        
        else:
            reactor = Reactor(name, mvar, self.get_bus(bus1), self.get_bus(bus2))
            self.reactors.update({name: reactor})
            self.changed = True
    """

    def add_shunt_reactor(self, name: str, mvar: float, bus: str):

        if name in self.reactors:
            print("Name already exists. No changes to circuit")
        
        else:
            reactor = Reactor(name, mvar, self.get_bus(bus))
            self.reactors.update({name: reactor})
            self.changed = True

    """
    def add_series_capacitor(self, name: str, mvar: float, bus1: str, bus2: str):

        if name in self.capacitors:
            print("Name already exists. No changes to circuit")
        
        else:
            capacitor = Capacitor(name, mvar, self.get_bus(bus1), self.get_bus(bus2))
            self.capacitors.update({name: capacitor})
            self.changed = True
    """

    def add_shunt_capacitor(self, name: str, mvar: float, bus: str):

        if name in self.capacitors:
            print("Name already exists. No changes to circuit")
        
        else:
            capacitor = Capacitor(name, mvar, self.get_bus(bus))
            self.capacitors.update({name: capacitor})
            self.changed = True


    def get_conductor(self, name: str):
        """
        Retrieves the name of the specified conductor.
        :param name: Conductor name
        :return:
        """
        return self.conductors[name]
    

    def get_bus(self, name: str):
        """
        Retrieves the name of the specified bus.
        :param name: Bus name
        :return:
        """
        return self.buses[name]
    

    def get_bundle(self, name: str):
        """
        Retrieves the name of the specified bundle.
        :param name: Bundle name
        :return:
        """
        return self.bundles[name]
    

    def get_geometry(self, name: str):
        """
        Retrieves the name of the specified geometry.
        :param name: Geometry name
        :return:
        """
        return self.geometries[name]


    def calc_Ybus(self):
        """
        Calculates systems admittance matrix.
        :return: Admittance matrix (list[list[complex double]])
        """
        num_buses = len(self.buses)
        y_bus = np.zeros((num_buses, num_buses), dtype=complex)

        # Iterate through line impedance
        for line in self.transmission_lines.values():
            from_bus = line.bus1.index-1
            to_bus = line.bus2.index-1
            y_bus[from_bus, from_bus] += line.yprim.iloc[0, 0]
            y_bus[from_bus, to_bus] += line.yprim.iloc[0, 1]
            y_bus[to_bus, from_bus] += line.yprim.iloc[1, 0]
            y_bus[to_bus, to_bus] += line.yprim.iloc[1, 1]

        # Iterate through XFMR impedance
        for xfmr in self.transformers.values():
            from_bus = xfmr.bus1.index-1
            to_bus = xfmr.bus2.index-1
            y_bus[from_bus, from_bus] += xfmr.yprim.iloc[0, 0]
            y_bus[from_bus, to_bus] += xfmr.yprim.iloc[0, 1]
            y_bus[to_bus, from_bus] += xfmr.yprim.iloc[1, 0]
            y_bus[to_bus, to_bus] += xfmr.yprim.iloc[1, 1]

        # Iterate through reactor dictionary
        for reactor in self.reactors.values():
            from_bus = reactor.bus1.index-1
            to_bus = reactor.bus2.index-1
            y_bus[from_bus, from_bus] += reactor.Yprim.iloc[0, 0]
            y_bus[from_bus, to_bus] += reactor.Yprim.iloc[0, 1]
            y_bus[to_bus, from_bus] += reactor.Yprim.iloc[1, 0]
            y_bus[to_bus, to_bus] += reactor.Yprim.iloc[1, 1]
        
        # Iterate through capacitor dictionary
        for capacitor in self.capacitors.values():
            from_bus = capacitor.bus1.index-1
            to_bus = capacitor.bus2.index-1
            y_bus[from_bus, from_bus] += capacitor.Yprim.iloc[0, 0]
            y_bus[from_bus, to_bus] += capacitor.Yprim.iloc[0, 1]
            y_bus[to_bus, from_bus] += capacitor.Yprim.iloc[1, 0]
            y_bus[to_bus, to_bus] += capacitor.Yprim.iloc[1, 1]

        self.Ybus = y_bus
        return y_bus
    

    def print_Ybus(self):
        """
        Prints power the system's Ybus matrix.
        :return:
        """
        self.Ybusdf = pd.DataFrame(data=self.Ybus.round(2), index=self.bus_order, columns=self.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Ybusdf.to_string())


    def change_slack(self, old: str, new: str):
        """
        Changes the system's slack bus.
        :param old: Old slack bus.
        :param new: New slack bus.
        :return:
        """
        if self.buses[new].type != "PV":
            print(f"Cannot make '{self.buses[new].name}' a slack bus because it has no generator connection. No changes made to circuit.")
            return
        
        self.buses[old].set_type("PV")
        self.buses[new].set_type("Slack")
        self.slack_bus = new
        self.slack_index = self.buses[new].index
        self.pv_indexes.remove(self.buses[new].index)
        self.pv_indexes.append(self.buses[old].index)


    def compute_power_injection(self, x, pq_and_pv_indexes, pv_indexes, pq_indexes):
        """
        Calculates the power injection at each bus.
        :param x: Dataframe that holds bus voltages and angles
        :param pq_and_pv_indexes: List containing each PQ and PV bus index
        :param pv_indexes: List containing each PV bus index
        :param pq_indexes: List containing each PQ bus index
        :return:
        """
        N = self.count
        Ymag = np.abs(self.Ybus)
        theta = np.angle(self.Ybus)
        
        d = x[x.index.str.startswith('d')]
        V = x[x.index.str.startswith('V')]
        P = []
        Q = []
        for k in pq_and_pv_indexes:
            sum1 = 0
            sum2 = 0
            for n in range(N):
                Ykn = Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                sum1 += Ykn*Vn*cos(dk - dn - theta[k-1, n])
                sum2 += Ykn*Vn*sin(dk - dn - theta[k-1, n])
            
            Vk = float(V.iloc[k-1, 0])
            Pk = Vk*sum1
            P.append(Pk)
            if k in pv_indexes:
              continue
            Qk = Vk*sum2
            Q.append(Qk)
            
        P = np.array(P)
        Q = np.array(Q)
        y = np.concatenate((P, Q))
        indexes = [f"P{int(i)}" for i in np.sort(np.concatenate((pq_indexes, pv_indexes)))]
        [indexes.append(f"Q{int(i)}") for i in pq_indexes]
        y = pd.DataFrame(y, index=indexes, columns=["y"])
        return y


    def do_newton_raph(self, var_limit=False):
        """
        Uses the Newton-Raphson algorithm to solve for the system's bus voltages and angles.
        :return:
        """
        from Solution import NewtonRaphson
        if self.changed == True:
            self.calc_Ybus()
            self.changed = False
        solution = NewtonRaphson(self, var_limit)
        self.x, self.y = solution.newton_raph()
        self.voltages = self.to_rectangular()
        self.update_voltages_and_angles()
        self.update_generator_power()
        self.update_reactor_power()
        self.update_capacitor_power()
        self.print_data()
        print()

    
    def do_fast_decoupled(self, var_limit=False):
        """
        Uses the Fast Decoupled algorithm to solve for the system's bus voltages and angles.
        :return:
        """
        from Solution import FastDecoupled
        if self.changed == True:
            self.calc_Ybus()
            self.changed = False
        solution = FastDecoupled(self, var_limit)
        self.x, self.y = solution.fast_decoupled()
        self.voltages = self.to_rectangular()
        self.update_voltages_and_angles()
        self.update_generator_power()
        self.update_reactor_power()
        self.update_capacitor_power()
        self.print_data()
        print()

    
    def do_dc_power_flow(self):
        """
        Uses the DC Power Flow algorithm to solve for the system's bus voltages and angles.
        :return:
        """
        from Solution import DCPowerFlow
        if self.changed == True:
            self.calc_Ybus()
            self.changed = False
        solution = DCPowerFlow(self)
        self.x, self.y = solution.dc_power_flow()
        self.update_voltages_and_angles()
        self.update_generator_power()
        self.print_data(True)
        print()
    

    def to_rectangular(self):
        """Converts the magnitude and angle values of the bus voltages into rectangular complex voltages
        :return:
        """
        mag = self.x[self.x.index.str.startswith("V")].to_numpy()
        angles = self.x[self.x.index.str.startswith("d")].to_numpy()
        N = len(mag)
        V = np.zeros(N, dtype=complex)
        for i in range(N):
            V[i] = mag[i]*(cos(angles[i])+1j*sin(angles[i]))
        return V
    

    def update_voltages_and_angles(self):
        """
        Updates the voltages and angles at each bus with the values calculated in the power flow results.
        :return:
        """
        d = self.x[self.x.index.str.startswith("d")]
        V = self.x[self.x.index.str.startswith("V")]

        for bus in self.buses:
            index = self.buses[bus].index-1
            self.buses[bus].set_bus_v(V.iloc[index, 0])
            self.buses[bus].set_angle(d.iloc[index, 0])
    

    def update_generator_power(self):
        """
        Updates the power delivered by each generator using the results from the most recent power flow calculation.
        :return:
        """
        P = self.y[self.y.index.str.startswith("P")]
        Q = self.y[self.y.index.str.startswith("Q")]

        for gen in self.generators.values():
            index = self.buses[gen.bus].index-1
            gen.set_power(P.iloc[index, 0]*settings.powerbase/1e6, Q.iloc[index, 0]*settings.powerbase/1e6)
    

    def update_reactor_power(self):
        """
        Updates the power absored by each reactor using the results from the most recent power flow calculation.
        :return:
        """
        for reactor in self.reactors.values():
            index = self.buses[reactor.bus1.name].index-1
            V_reactor = self.voltages[index]  # actual bus voltage found after power flow
            reactor.update_power(V_reactor)


    def update_capacitor_power(self):
        """
        Updates the power delivered by each capacitor using the results from the most recent power flow calculation.
        :return:
        """
        for capacitor in self.capacitors.values():
            index = self.buses[capacitor.bus1.name].index-1
            V_capacitor = self.voltages[index]  # actual bus voltage found after power flow
            capacitor.update_power(V_capacitor)


    def print_data(self, dcpowerflow=False):
        """
        Prints necessary information from system.
        :return:
        """
        x = self.x.to_numpy()
        angles = np.rad2deg(x[0:self.count]).round(3)
        pu_voltages = x[self.count:].round(5)
        voltages = []
        nominal_voltages = []
        number = []
        name = []

        load_mw = np.zeros((self.count, 1))
        load_mvar = np.zeros((self.count, 1))
        gen_mw = np.zeros((self.count, 1))
        gen_mvar = np.zeros((self.count, 1))
        shunt_mvar = np.zeros((self.count, 1))

        for bus in self.buses.values():
            nominal_voltages.append(bus.base_kv/1e3)
            voltages.append((bus.V/1e3).round(3))
            number.append(bus.index)
            name.append(bus.name)
        
        if dcpowerflow==False:
            for load in self.loads.values():
                index = self.buses[load.bus].index-1
                load_mw[index, 0] = load.real_power/1e6
                load_mvar[index, 0] = load.reactive_power/1e6
        else:
            for load in self.loads.values():
                index = self.buses[load.bus].index-1
                load_mw[index, 0] = load.real_power/1e6
        
        for gen in self.generators.values():
            index = self.buses[gen.bus].index-1
            gen_mw[index, 0] = round(gen.real_power/1e6, 2)
            gen_mvar[index, 0] = round(gen.reactive_power/1e6, 2)
        
        for reactor in self.reactors.values():
            index = self.buses[reactor.bus1.name].index-1
            shunt_mvar[index, 0] = round(reactor.Q/1e6, 2)
        
        for capacitor in self.capacitors.values():
            index = self.buses[capacitor.bus1.name].index-1
            shunt_mvar[index, 0] = round(capacitor.Q/1e6, 2)
            
        voltages = np.array([voltages]).T
        nominal_voltages = np.array([nominal_voltages]).T
        number = np.array([number]).T
        name = np.array([name]).T
        data = np.concatenate((number, name, nominal_voltages, pu_voltages, voltages, angles, load_mw, load_mvar, gen_mw, gen_mvar, shunt_mvar), axis=1)

        datadf = pd.DataFrame(data=data, index=self.bus_order, columns=["Number", "Name", "Nom kV", "PU Volt", "Volt (kV)", "Angle(Deg)", "Load MW", "Load MVAR", "Gen MW", "Gen MVAR", "Shunt MVAR"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(datadf.to_string())
        


# This class does symmetrical/three phase fault analysis.
class ThreePhaseFault():
    def __init__(self, circuit: Circuit, faultbus: int):
        """
        Constructor for the ThreePhaseFault class.
        :param circuit: Circuit object
        :param faultbus: Bus index to run fault analysis on
        """
        self.circuit = circuit
        self.faultbus = faultbus
        self.faultYbus = self.calc_faultYbus()
        self.faultZbus = np.linalg.inv(self.faultYbus)
        self.Ifn = float  # fault current
        self.Ipn = None  # phase current, will become an np.ndarray
        self.fault_voltages = None  # will become an np.ndarray
    

    def calc_faultYbus(self):
        """
        Calculate system's fault admittance matrix.
        :return: Admittance matrix (list[list[complex double]])
        """
        Ybus = self.circuit.Ybus.copy()
        for gen in self.circuit.generators.values():
            index = self.circuit.buses[gen.bus].index-1
            Ybus[index, index] += 1/(gen.X1)
        
        # calculates impedance for each load in the system
        if len(self.circuit.loads) != 0:
            for load in self.circuit.loads.values():
                bus = load.bus # bus name as a string
                Vbase = self.circuit.buses[bus].base_kv
                V = self.circuit.buses[bus].V
                index = self.circuit.buses[bus].index
                I = np.conjugate(load.S/V)
                Zbase = Vbase**2/self.circuit.powerbase
                Z = V/I
                Zpu = Z/Zbase
                Ybus[index-1, index-1] += 1/Zpu
                
        return Ybus
    

    def calc_fault_values(self):
        """
        Setups the solution process for finding the Three Phase fault values.
        :return:
        """
        from Solution import ThreePhaseFaultParameters
        solution = ThreePhaseFaultParameters(self, self.faultbus)
        self.fault_voltages, self.Ifn = solution.ThreePhase_fault_values()
        print(f"Three Phase Fault at bus {self.faultbus}:")
        print()
        self.print_current()
        print()
        self.print_voltages()
        print()
        print()
    

    def print_current(self):
        """
        Prints the system's fault current at the chosen bus, along with its sub-transient phase currents.
        :return:
        """
        print("Fault current:")
        angle = np.rad2deg(np.angle(self.Ifn))
        angles = np.round(np.array([angle, angle+240, angle+120]), 2)
        magnitude = np.round(np.abs(self.Ifn), 3)
        current = np.concatenate(([magnitude], angles)).reshape(1, 4)
        current_df = pd.DataFrame(current, index=[f"Bus{self.faultbus}"], columns=["Magnitude", "Phase A Angle", "Phase B Angle", "Phase C Angle"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(current_df.to_string())


    def print_voltages(self):
        """
        Prints the systems fault voltages for the chosen fault.
        :return:
        """
        print("Fault Voltages:")
        fault_angles = np.rad2deg(np.angle(self.fault_voltages))
        fault_angles = np.round(np.array([fault_angles, fault_angles-120, fault_angles+120]).T, 2)
        fault_voltages = np.round(np.array([np.abs(self.fault_voltages), np.abs(self.fault_voltages), np.abs(self.fault_voltages)]).T, 5)
        fault_voltages_df = pd.DataFrame(np.block([fault_voltages, fault_angles]), index=self.circuit.bus_order, columns=["Phase A", "Phase B", "Phase C", "Phase A Angle", "Phase B Angle"
                                                                                                                                                                ,"Phase C Angle"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(fault_voltages_df.to_string())



# This class does unsymmetrical fault analysis.
class UnsymmetricalFaults():
    def __init__(self, circuit: Circuit, faultbus: int):
        """
        Constructor for the UnsymmetricalFaults class.
        :param circuit: Circuit object
        :param faultbus: Bus index to run fault analysis on
        """
        self.circuit = circuit
        self.faultbus = faultbus
        self.voltages = self.circuit.voltages
        self.Y0bus = self.calc_zero()
        self.Z0bus = np.linalg.inv(self.Y0bus)
        self.Ypbus = self.calc_positive()
        self.Zpbus = np.linalg.inv(self.Ypbus)
        self.Ynbus = self.calc_negative()
        self.Znbus = np.linalg.inv(self.Ynbus)
        self.Ifn = float
        self.Ipn = None
        self.fault_voltages = None
    

    def calc_zero(self):
        """
        Calculates the system's zero sequence admittance matrix.
        :return: np.ndarray
        """
        N = self.circuit.count
        Ybus0 = np.zeros((N, N), dtype=complex)

        for gen in self.circuit.generators.values():
            bus = self.circuit.buses[gen.bus]
            index = bus.index-1
            Ybus0[index, index] += gen.Y0prim
        
        for line in self.circuit.transmission_lines.values():
            i = line.bus1.index-1
            j = line.bus2.index-1
            Ybus0[i, i] += line.yprim0.iloc[0, 0]
            Ybus0[i, j] += line.yprim0.iloc[0, 1]
            Ybus0[j, i] += line.yprim0.iloc[1, 0]
            Ybus0[j, j] += line.yprim0.iloc[1, 1]
        
        for xfmr in self.circuit.transformers.values():
            i = xfmr.bus1.index-1
            j = xfmr.bus2.index-1
            Ybus0[i, i] += xfmr.yprim0.iloc[0, 0]
            Ybus0[i, j] += xfmr.yprim0.iloc[0, 1]
            Ybus0[j, i] += xfmr.yprim0.iloc[1, 0]
            Ybus0[j, j] += xfmr.yprim0.iloc[1, 1]

        return Ybus0


    def calc_positive(self):
        """
        Calculates system's positive sequence admittance matrix.
        :return: np.ndarray
        """
        Ybus = self.circuit.Ybus.copy()

        for gen in self.circuit.generators.values():
            index = self.circuit.buses[gen.bus].index-1
            Ybus[index, index] += 1/(gen.X1)
        
        # calculates impedance for each load in the system
        if len(self.circuit.loads) != 0:
            for load in self.circuit.loads.values():
                bus = load.bus  # bus name as a string
                Vbase = self.circuit.buses[bus].base_kv
                V = self.circuit.buses[bus].V
                index = self.circuit.buses[bus].index
                I = np.conjugate(load.S/V)
                Zbase = Vbase**2/self.circuit.powerbase
                Z = V/I
                Zpu = Z/Zbase
                Ybus[index-1, index-1] += 1/Zpu

        return Ybus
    

    def calc_negative(self):
        """
        Calculates system's zero sequence admittance matrix.
        :return: np.ndarray
        """
        Ynbus = self.circuit.Ybus.copy()

        for gen in self.circuit.generators.values():
            index = self.circuit.buses[gen.bus].index-1
            Ynbus[index, index] += 1/(gen.X2)
        
        if len(self.circuit.loads) != 0:
            for load in self.circuit.loads.values():
                bus = load.bus  # bus name as a string
                Vbase = self.circuit.buses[bus].base_kv
                V = self.circuit.buses[bus].V
                index = self.circuit.buses[bus].index
                I = np.conjugate(load.S/V)
                Zbase = Vbase**2/self.circuit.powerbase
                Z = V/I
                Zpu = Z/Zbase
                Ynbus[index-1, index-1] += 1/Zpu
                
        return Ynbus
    

    def SLG_fault_values(self):
        """
        Setups the solution process for finding the Single Line to Ground fault values.
        :return:
        """
        from Solution import UnsymmetricalFaultParameters
        solution = UnsymmetricalFaultParameters(self, self.faultbus)
        self.fault_voltages, self.Ifn, self.Ipn = solution.SLG_fault_values()
        print(f"Single Line to Ground Fault at bus {self.faultbus}:")
        print()
        self.print_current()
        self.print_voltages()
        print()
        print()
    

    def LL_fault_values(self):
        """
        Setups the solution process for finding the Line to Line fault values.
        :return:
        """
        from Solution import UnsymmetricalFaultParameters
        solution = UnsymmetricalFaultParameters(self, self.faultbus)
        self.fault_voltages, self.Ifn, self.Ipn = solution.LL_fault_values()
        print(f"Line to Line Fault at bus {self.faultbus}:")
        print()
        self.print_current()
        self.print_voltages()
        print()
        print()


    def DLG_fault_values(self):
        """
        Setups the solution process for finding the Double Line to Ground fault values.
        :return:
        """
        from Solution import UnsymmetricalFaultParameters
        solution = UnsymmetricalFaultParameters(self, self.faultbus)
        self.fault_voltages, self.Ifn, self.Ipn = solution.DLG_fault_values()
        print(f"Double Line to Ground Fault at bus {self.faultbus}:")
        print()
        self.print_current()
        self.print_voltages()
        print()
        print()


    def print_Y0bus(self):
        """
        Prints the system's zero sequence admittance matrix.
        :return:
        """
        self.Y0df = pd.DataFrame(data=self.Y0bus.round(2), index=self.circuit.bus_order, columns=self.circuit.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Y0df.to_string())

    
    def print_Ypbus(self):
        """
        Prints the system's positive sequence admittance matrix.
        :return:
        """
        self.Ypdf = pd.DataFrame(data=self.Ypbus.round(2), index=self.circuit.bus_order, columns=self.circuit.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Ypdf.to_string())


    def print_Ynbus(self):
        """
        Prints the system's negative sequence admittance matrix.
        :return:
        """
        self.Yndf = pd.DataFrame(data=self.Ynbus.round(2), index=self.circuit.bus_order, columns=self.circuit.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Yndf.to_string())
    

    def print_current(self):
        """
        Prints the system's fault current at the chosen bus, along with its sub-transient phase currents.
        :return:
        """
        print(f"Fault current: {np.abs(self.Ifn).round(3)} pu")
        angles = np.rad2deg(np.angle(self.Ipn)).round(2)
        magnitude = np.abs(self.Ipn).round(3)
        data = np.concatenate((magnitude, angles), axis=1)
    
        print("Subtransient Phase Current")
        current_df = pd.DataFrame(data, index=["A", "B", "C"], columns=["Magnitude(pu)", "Angle(deg)"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(current_df.to_string())
        print()


    def print_voltages(self):
        """
        Prints the systems fault voltages for the chosen fault.
        :return:
        """
        fault_angles = np.rad2deg(np.angle(self.fault_voltages)).round(2)
        fault_voltages_df = pd.DataFrame(np.block([np.abs(self.fault_voltages).round(5), fault_angles]), index=self.circuit.bus_order, columns=["Phase A", "Phase B", "Phase C", 
                                                                                                                               "Phase A Angle", "Phase B Angle","Phase C Angle"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(fault_voltages_df.to_string())
    

# validation tests
if __name__ == '__main__':
    
    import Validations
    Validations.SevenPowerBusSystemValidation()
    Validations.ReactorCorrectionValidation()