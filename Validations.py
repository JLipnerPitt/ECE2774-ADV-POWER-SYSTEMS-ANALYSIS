import numpy as np

from Circuit import Circuit
from Settings import settings
from Tools import read_excel, compare, read_jacobian, display_jacobian


def CreateFivePowerBusSystem():
    settings.set_powerbase(100e6)
    circ = Circuit("Example_6.9")

    circ.add_bus("bus1", 15e3)
    circ.add_bus("bus2", 345e3)
    circ.add_bus("bus3", 15e3)
    circ.add_bus("bus4", 345e3)
    circ.add_bus("bus5", 345e3)

    circ.add_transformer("T1", circ.buses["bus1"], circ.buses["bus5"], 400e6, 8.024, 13.33333333)
    circ.add_transformer("T2", circ.buses["bus3"], circ.buses["bus4"], 800e6, 8.024, 13.33333333)

    circ.add_tline_from_parameters("L1", circ.buses["bus2"], circ.buses["bus4"], R=0.009, X=0.100, B=1.72)
    circ.add_tline_from_parameters("L2", circ.buses["bus2"], circ.buses["bus5"], R=0.0045, X=0.05, B=0.88)
    circ.add_tline_from_parameters("L3", circ.buses["bus5"], circ.buses["bus4"], R=0.00225, X=0.025, B=0.44)

    circ.add_generator("Gen1", "bus1", 1, 0)
    circ.add_generator("Gen2", "bus3", 1, 520e6)

    circ.add_load("Load1", "bus2", 800e6, 280e6)
    circ.add_load("Load2", "bus3", 80e6, 40e6)
    return circ

def CreateSevenPowerBusSystem():
    settings.set_powerbase(100e6)
    circ = Circuit("Example_7bus")

    circ.add_bus("bus1", 20e3)
    circ.add_bus("bus2", 230e3)
    circ.add_bus("bus3", 230e3)
    circ.add_bus("bus4", 230e3)
    circ.add_bus("bus5", 230e3)
    circ.add_bus("bus6", 230e3)
    circ.add_bus("bus7", 18e3)

    circ.add_transformer("T1", circ.buses["bus1"], circ.buses["bus2"], 125e6, 10.5, 10)
    circ.add_transformer("T2", circ.buses["bus6"], circ.buses["bus7"], 200e6, 8.5, 12)

    circ.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    circ.add_geometry("Geometry7bus", [0, 19.5, 39], [0, 0, 0])
    circ.add_bundle("Bundle7bus", 2, 1.5, circ.conductors["Partridge"])

    circ.add_tline_from_geometry("L1", circ.buses["bus2"], circ.buses["bus4"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 10)
    circ.add_tline_from_geometry("L2", circ.buses["bus2"], circ.buses["bus3"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 25)
    circ.add_tline_from_geometry("L3", circ.buses["bus3"], circ.buses["bus5"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 20)
    circ.add_tline_from_geometry("L4", circ.buses["bus4"], circ.buses["bus6"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 20)
    circ.add_tline_from_geometry("L5", circ.buses["bus5"], circ.buses["bus6"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 10)
    circ.add_tline_from_geometry("L6", circ.buses["bus4"], circ.buses["bus5"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 35)

    return circ


def FivePowerBusSystemValidation():
    circ = CreateFivePowerBusSystem()
    #circ.change_slack("bus1", "bus3")
    ImpedanceValidation(circ)
    YbusValidation(circ)
    FlatStartValidation(circ)
    NewtonRaphValidation(circ)
    DCPowerFlowValidation(circ)


def SevenPowerBusSystemValidation():
    circ = CreateSevenPowerBusSystem()
    ImpedanceValidation(circ)
    YbusValidation(circ)
    FlatStartValidation(circ)
    #PowerInjectionValidation(circ)
    NewtonRaphValidation(circ)
    #DCPowerFlowValidation(circ)
    
    #circ.compute_power_injection()
    #print(circ.y, '\n')


def ImpedanceValidation(circ: Circuit):
    for i in range(len(circ.components["Transformers"])):
        print(f"T{i+1} impedance =", circ.components["Transformers"][f"T{i+1}"].Zpu)
        print(f"T{i+1} admittance =", circ.components["Transformers"][f"T{i+1}"].Ypu)
        print()

    for i in range(len(circ.components["T-lines"])):
        print(f"Line{i+1} impedance =", circ.components["T-lines"][f"L{i+1}"].Zseries)
        print(f"Line{i+1} admittance =", circ.components["T-lines"][f"L{i+1}"].Yseries)
        print(f"Line{i+1} shunt admittance =", circ.components["T-lines"][f"L{i+1}"].Yshunt)
        print()


def YbusValidation(circ: Circuit):
    Ybus = circ.calc_Ybus()
    pwrworld = read_excel()
    compare(Ybus, pwrworld)


def FlatStartValidation(circ: Circuit):
    x = circ.flat_start_x()
    print("Flat start values:")
    print(x.T)


def PowerInjectionValidation(circ: Circuit):
    import pandas as pd
    d = [-0.4277802, -0.002617994, -0.04590216, -0.08063421]
    V = [0.77687, 0.97368, 0.94599]
    x = np.concatenate((d, V))
    x = pd.DataFrame(x, columns=["x"], index=["d2", "d3", "d4", "d5", "V2", "V4", "V5"])

    P, Q = circ.compute_power_injection(x)
    print(f"P = {P}")
    print(f"Q = {Q}")
    

def NewtonRaphValidation(circ: Circuit):
    J, x = circ.do_newton_raph()


def DCPowerFlowValidation(circ: Circuit):
    x = circ.flat_start_x()
    y = circ.flat_start_y(x)
    d = circ.do_dc_power_flow(y)
    print("DC Power Flow: d = ", d)

