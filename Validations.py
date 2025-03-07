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

    circ.add_transformer("T1", circ.buses["bus1"], circ.buses["bus5"], 400e6, 8.020, 13.333)
    circ.add_transformer("T2", circ.buses["bus3"], circ.buses["bus4"], 800e6, 8.020, 13.333)

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
    ImpedanceValidation(circ)
    YbusValidation(circ)
    FlatStartValidation(circ)
    NewtonRaphValidation(circ)
    DCPowerFlowValidation(circ)

    #circ.compute_power_injection()
    #print(circ.y, '\n')


def SevenPowerBusSystemValidation():
    circ = CreateSevenPowerBusSystem()
    ImpedanceValidation(circ)
    YbusValidation(circ)
    FlatStartValidation(circ)
    NewtonRaphValidation(circ)
    DCPowerFlowValidation(circ)
    
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
    circ.flat_start()
    print("Flat start values:")
    print("d =", circ.x["d"])
    print("V =", circ.x["V"])
    print("P =", circ.y["P"])
    print("Q =", circ.y["Q"])
    print()


def NewtonRaphValidation(circ: Circuit):
    calculated_jacobian = circ.do_newton_raph()
    powerworld_jacobian = read_jacobian(circ.count - 1)

    # print("Powerworld Jacobian values:\n")
    # display_jacobian(powerworld_jacobian)

    print("Calculated Jacobian values:\n")
    count = 1
    for j in calculated_jacobian:
        jacobian_difference = j - powerworld_jacobian[count - 1]
        # print(f"J{count} =\n", j)
        print(f"J{count} Difference = \n", np.round(jacobian_difference, 6))
        print()
        count += 1



def DCPowerFlowValidation(circ: Circuit):
    d = circ.do_dc_power_flow()
    print("DC Power Flow: d = ", d)

