"""
Module to implement circuit/system functionality
Disclaimer: ChatGPT used for assistance

Filename: Circuit.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-03
"""

from Component import Load, Generator
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


    def change_power_base(self, p: float):
        settings.set_powerbase(p)
        self.powerbase = p*1e6


    def change_frequency(self, f: float):
        settings.set_freq(f)

    
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
            self.bus_order.append(self.count)


    def add_load(self, name: str, bus: str, real: float, reactive: float):
        """
        Adds load to circuit object
        :param name: Name of load
        :param power: Rated load power
        :param voltage: Rated load voltage
        :param bus: Bus connection
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
        
        if name in self.transmission_lines:
            print(f"{name} already exists. No changes to circuit")
            return
        
        tline = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
        self.transmission_lines.update({name: tline})

    
    def add_tline_from_parameters(self, name: str, bus1: Bus, bus2: Bus, R: float, X: float, B: float):
        """
        Adds transmission line to circuit object
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
        
        tline = TransmissionLine.from_parameters(name, bus1, bus2, R, X, B)
        self.transmission_lines.update({name: tline})
    
    
    def add_transformer(self, name: str, type: str, bus1: Bus, bus2: Bus, power_rating: float,
                        impedance_percent: float, x_over_r_ratio: float, gnd_impedance=None):
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
        if name in self.transformers:
            print(f"{name} already exists. No changes to circuit")
            return
        
        transformer = Transformer(name, type, bus1, bus2, power_rating, impedance_percent,
                                      x_over_r_ratio, gnd_impedance)
        self.transformers.update({name: transformer})
    

    def add_generator(self, name: str, bus: str, voltage: float, real_power: float, pos_imp = 0.0, neg_imp = 0.0, zero_imp = 0.0, gnd_imp = 0.0, var_limit = float('inf')):

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

        self.Ybus = y_bus
        return y_bus
    

    def print_Ybus(self):
        self.Ybusdf = pd.DataFrame(data=self.Ybus.round(2), index=self.bus_order, columns=self.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Ybusdf.to_string())


    def change_slack(self, old: str, new: str):
        if self.buses[new].type != "PV":
            print(f"Cannot make '{self.buses[new].name}' a slack bus because it has no generator connection. No changes made to circuit.")
            return
        
        self.buses[old].set_type("PV")
        self.buses[new].set_type("Slack")
        self.slack_bus = new
        self.slack_index = self.buses[new].index
        self.pv_indexes.remove(self.buses[new].index)
        self.pv_indexes.append(self.buses[old].index)


    def calc_indexes(self):
        if len(self.pv_indexes) == 0:
            indexes = self.pq_indexes
        
        else:
            indexes = np.concatenate((self.pq_indexes, self.pv_indexes))

        indexes.sort()
        self.pq_and_pv_indexes = indexes


    def flat_start_y(self, pv_indexes=None, pq_indexes=None):
        if pv_indexes is None:
            pv_indexes = self.pv_indexes
        if pq_indexes is None:
            pq_indexes = self.pq_indexes

        P = []
        Q = []

        for bus in self.buses:

            if self.buses[bus].index in pq_indexes:
              P.append(self.buses[bus].real_power/self.powerbase)
              Q.append(self.buses[bus].reactive_power/self.powerbase)
            
            elif self.buses[bus].index in pv_indexes:
              P.append(self.buses[bus].real_power/self.powerbase)
            
        y = np.concatenate((P, Q))
        indexes = [f"P{i}" for i in self.pq_and_pv_indexes]
        [indexes.append(f"Q{i}") for i in pq_indexes]

        y = pd.DataFrame(y, index=indexes, columns=["y"])
        return y


    def compute_power_injection(self, x, pv_indexes=None, pq_indexes=None):
        if pv_indexes is None:
            pv_indexes = self.pv_indexes
        if pq_indexes is None:
            pq_indexes = self.pq_indexes

        N = self.count
        Ymag = np.abs(self.Ybus)
        theta = np.angle(self.Ybus)
        
        d = x[x.index.str.startswith('d')]
        V = x[x.index.str.startswith('V')]
        P = []
        Q = []
        for k in self.pq_and_pv_indexes:
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


    def do_newton_raph(self):
        from Solution import NewtonRaphson
        solution = NewtonRaphson(self)
        self.x, self.y = solution.newton_raph()
        self.update_voltages_and_angles()
        self.update_generator_power()

    
    def do_fast_decoupled(self):
        from Solution import FastDecoupled
        solution = FastDecoupled(self)
        self.x, self.y = solution.fast_decoupled()
        self.update_voltages_and_angles()
        self.update_generator_power()


    def do_dc_power_flow(self):
        from Solution import DCPowerFlow
        solution = DCPowerFlow(self)
        self.x, self.y = solution.dc_power_flow()
        self.update_voltages_and_angles()
        self.update_generator_power()
    

    def update_voltages_and_angles(self):
        d = self.x[self.x.index.str.startswith("d")]
        V = self.x[self.x.index.str.startswith("V")]

        for bus in self.buses:
            index = self.buses[bus].index-1
            self.buses[bus].set_bus_v(V.iloc[index, 0])
            self.buses[bus].set_angle(d.iloc[index, 0])
    

    def update_generator_power(self):
        P = self.y[self.y.index.str.startswith("P")]
        Q = self.y[self.y.index.str.startswith("Q")]

        for gen in self.generators.values():
            index = self.buses[gen.bus].index-1
            gen.set_power(P.iloc[index, 0]*settings.powerbase/1e6, Q.iloc[index, 0]*settings.powerbase/1e6)
            

    def print_data(self, dcpowerflow=False):
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
            

        voltages = np.array([voltages]).T
        nominal_voltages = np.array([nominal_voltages]).T
        number = np.array([number]).T
        name = np.array([name]).T
        data = np.concatenate((number, name, nominal_voltages, pu_voltages, voltages, angles, load_mw, load_mvar, gen_mw, gen_mvar), axis=1)

        datadf = pd.DataFrame(data=data, index=self.bus_order, columns=["Number", "Name", "Nom kV", "PU Volt", "Volt (kV)", "Angle(Deg)", "Load MW", "Load MVAR", "Gen MW", "Gen MVAR"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(datadf.to_string())
        


class ThreePhaseFault():
    def __init__(self, circuit: Circuit, faultbus: int, faultvoltage: float):
        self.circuit = circuit
        self.faultbus = faultbus
        self.faultvoltage = faultvoltage
        self.faultYbus = self.calc_faultYbus()
        self.faultZbus = np.linalg.inv(self.faultYbus)
        self.Ifn = None
        self.Ipn = None
        self.fault_voltages = None
    

    def calc_faultYbus(self):
        Ybus = self.circuit.Ybus.copy()
        for gen in self.circuit.generators.values():
            index = self.circuit.buses[gen.bus].index-1
            Ybus[index, index] += 1/(gen.sub_transient_reactance)
        
        return Ybus
    

    def calc_fault_values(self):
        from Solution import ThreePhaseFaultParameters
        solution = ThreePhaseFaultParameters(self, self.faultbus, self.faultvoltage)
        self.fault_voltages = solution.calc_fault_voltages()
        self.Ifn = solution.calc_fault_current()
    

    def print_current(self):
        angle = np.rad2deg(np.angle(self.Ifn))
        angles = np.array([angle, angle+240, angle+120])
        magnitude = np.abs(self.Ifn)
        current = np.concatenate(([magnitude], angles)).reshape(1, 4)
        current_df = pd.DataFrame(current, index=[f"Bus{self.faultbus}"], columns=["Magnitude", "Phase A Angle", "Phase B Angle", "Phase C Angle"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(current_df.to_string())


    def print_voltages(self):
        fault_angles = np.rad2deg(np.angle(self.fault_voltages))
        fault_angles = np.array([fault_angles, fault_angles-120, fault_angles+120]).T
        fault_voltages = np.array([np.abs(self.fault_voltages), np.abs(self.fault_voltages), np.abs(self.fault_voltages)]).T
        fault_voltages_df = pd.DataFrame(np.block([fault_voltages, fault_angles]), index=self.circuit.bus_order, columns=["Phase A", "Phase B", "Phase C", "Phase A Angle", "Phase B Angle"
                                                                                                                                                                ,"Phase C Angle"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(fault_voltages_df.to_string())



class UnsymmetricalFaults():
    def __init__(self, circuit: Circuit, faultbus: int, faultvoltage: float):
        self.circuit = circuit
        self.faultbus = faultbus
        self.faultvoltage = faultvoltage
        self.Y0bus = self.calc_zero()
        self.Z0bus = np.linalg.inv(self.Y0bus)
        self.Ypbus = self.calc_positive()
        self.Zpbus = np.linalg.inv(self.Ypbus)
        self.Ynbus = self.calc_negative()
        self.Znbus = np.linalg.inv(self.Ynbus)
        self.Ifn = None
        self.Ipn = None
        self.fault_voltages = None
    

    def calc_zero(self):
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
        Ybus = self.circuit.Ybus.copy()
        for gen in self.circuit.generators.values():
            index = self.circuit.buses[gen.bus].index-1
            Ybus[index, index] += 1/(gen.sub_transient_reactance)
        
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
    

    def calc_negative(self):
        Ynbus = self.circuit.Ybus.copy()
        for gen in self.circuit.generators.values():
            index = self.circuit.buses[gen.bus].index-1
            Ynbus[index, index] += 1/(gen.neg_impedance)
        
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
                Ynbus[index-1, index-1] += 1/Zpu
                
        return Ynbus
    

    def SLG_fault_values(self):
        from Solution import UnsymmetricalFaultParameters
        solution = UnsymmetricalFaultParameters(self, self.faultbus, self.faultvoltage)
        self.fault_voltages, self.Ifn, self.Ipn = solution.SLG_fault_values()
    

    def LL_fault_values(self):
        from Solution import UnsymmetricalFaultParameters
        solution = UnsymmetricalFaultParameters(self, self.faultbus, self.faultvoltage)
        self.fault_voltages, self.Ifn, self.Ipn = solution.LL_fault_values()


    def DLG_fault_values(self):
        from Solution import UnsymmetricalFaultParameters
        solution = UnsymmetricalFaultParameters(self, self.faultbus, self.faultvoltage)
        self.fault_voltages, self.Ifn, self.Ipn = solution.DLG_fault_values()


    def print_Y0bus(self):
        self.Y0df = pd.DataFrame(data=self.Y0bus.round(2), index=self.circuit.bus_order, columns=self.circuit.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Y0df.to_string())

    
    def print_Ypbus(self):
        self.Ypdf = pd.DataFrame(data=self.Ypbus.round(2), index=self.circuit.bus_order, columns=self.circuit.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Ypdf.to_string())


    def print_Ynbus(self):
        self.Yndf = pd.DataFrame(data=self.Ynbus.round(2), index=self.circuit.bus_order, columns=self.circuit.bus_order)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(self.Yndf.to_string())
    

    def print_current(self):
        print(f"Fault current at bus {self.faultbus}: {np.abs(self.Ifn).round(3)} pu")
        print()
        angles = np.rad2deg(np.angle(self.Ipn)).round(2)
        magnitude = np.abs(self.Ipn).round(3)
        data = np.concatenate((magnitude, angles), axis=1)
    
        print("Subtransient Phase Current")
        current_df = pd.DataFrame(data, index=["A", "B", "C"], columns=["Magnitude(pu)", "Angle(deg)"])
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(current_df.to_string())


    def print_voltages(self):
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