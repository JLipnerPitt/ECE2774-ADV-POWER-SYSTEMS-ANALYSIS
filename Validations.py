import numpy as np

from Circuit import Circuit, ThreePhaseFaults, UnsymmetricalFaults
from Settings import settings
from Tools import read_excel, compare, read_jacobian, display_jacobian


def CreateFivePowerBusSystem():
    circ = Circuit("Example_6.9")

    circ.add_bus("bus1", 15)
    circ.add_bus("bus2", 345)
    circ.add_bus("bus3", 15)
    circ.add_bus("bus4", 345)
    circ.add_bus("bus5", 345)

    circ.add_transformer("T1", circ.buses["bus1"], circ.buses["bus5"], 400, 8.024, 13.33333333)
    circ.add_transformer("T2", circ.buses["bus3"], circ.buses["bus4"], 800, 8.024, 13.33333333)

    circ.add_tline_from_parameters("L1", circ.buses["bus2"], circ.buses["bus4"], R=0.009, X=0.100, B=1.72)
    circ.add_tline_from_parameters("L2", circ.buses["bus2"], circ.buses["bus5"], R=0.0045, X=0.05, B=0.88)
    circ.add_tline_from_parameters("L3", circ.buses["bus5"], circ.buses["bus4"], R=0.00225, X=0.025, B=0.44)

    circ.add_generator("Gen1", "bus1", 1, 400, 0.045)
    circ.add_generator("Gen2", "bus3", 1, 520, 0.0225)

    circ.add_load("Load1", "bus2", 800, 280)
    circ.add_load("Load2", "bus3", 80, 40)
    return circ


def CreateSevenPowerBusSystem():
    circ = Circuit("Example_7bus")

    circ.add_bus("bus1", 20)
    circ.add_bus("bus2", 230)
    circ.add_bus("bus3", 230)
    circ.add_bus("bus4", 230)
    circ.add_bus("bus5", 230)
    circ.add_bus("bus6", 230)
    circ.add_bus("bus7", 18)

    circ.add_transformer("T1", circ.buses["bus1"], circ.buses["bus2"], 125, 8.5, 10)
    circ.add_transformer("T2", circ.buses["bus6"], circ.buses["bus7"], 200, 10.5, 12)

    circ.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    circ.add_geometry("Geometry7bus", [0, 19.5, 39], [0, 0, 0])
    circ.add_bundle("Bundle7bus", 2, 1.5, circ.conductors["Partridge"])

    circ.add_tline_from_geometry("L1", circ.buses["bus2"], circ.buses["bus4"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 10)
    circ.add_tline_from_geometry("L2", circ.buses["bus2"], circ.buses["bus3"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 25)
    circ.add_tline_from_geometry("L3", circ.buses["bus3"], circ.buses["bus5"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 20)
    circ.add_tline_from_geometry("L4", circ.buses["bus4"], circ.buses["bus6"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 20)
    circ.add_tline_from_geometry("L5", circ.buses["bus5"], circ.buses["bus6"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 10)
    circ.add_tline_from_geometry("L6", circ.buses["bus4"], circ.buses["bus5"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 35)

    circ.add_generator("Gen1", "bus1", 1, 200, 0.12, 0.14, 0.05)
    circ.add_generator("Gen2", "bus7", 1, 200, 0.12, 0.14, 0.05)

    circ.add_load("Load1", "bus3", 110, 50)
    circ.add_load("Load2", "bus4", 100, 70)
    circ.add_load("Load3", "bus5", 100, 65)

    return circ


def FivePowerBusSystemValidation():
    circ = CreateFivePowerBusSystem()
    #circ.change_slack("bus1", "bus3")
    ImpedanceValidation(circ)
    YbusValidation(circ, r"Excel_Files\example6_9.xlsx")
    NewtonRaphValidation(circ)
    FastDecoupledValidation(circ)
    DCPowerFlowValidation(circ)
    ThreePhaseFaultsValidation(circ, r"Excel_Files\5bus_positive_sequence_Ybus_matrix.xlsx")


def SevenPowerBusSystemValidation():
    circ = CreateSevenPowerBusSystem()
    #circ.change_slack("bus1", "bus7")
    ImpedanceValidation(circ)
    YbusValidation(circ, r"Excel_Files\sevenpowerbus_system.xlsx")
    NewtonRaphValidation(circ)
    FastDecoupledValidation(circ)
    DCPowerFlowValidation(circ)
    ThreePhaseFaultsValidation(circ, r"Excel_Files\7bus_positive_sequence_Ybus_matrix.xlsx")
    UnsymmetricalFaultsValidation(circ)


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


def YbusValidation(circ: Circuit, path: str):
    Ybus = circ.calc_Ybus()
    pwrworld = read_excel(path)
    compare(Ybus, pwrworld)
    

def NewtonRaphValidation(circ: Circuit):
    x, y = circ.do_newton_raph()
    print("Newton-Raphson algorithm converged results:")
    print(x.T)
    print()
    print(y.T)
    print()
    print()


def FastDecoupledValidation(circ: Circuit):
    x, y = circ.do_fast_decoupled()
    print("Fast decoupled algorithm converged results:")
    print(x.T)
    print()
    print(y.T)
    print()
    print()


def DCPowerFlowValidation(circ: Circuit):
    circ.flat_start_y()
    d = np.degrees(circ.do_dc_power_flow())
    print("DC Power Flow (angles in degrees):")
    print(d.T)
    print()
    print()


def ThreePhaseFaultsValidation(circ: Circuit, path):
    faults = ThreePhaseFaults(circ)
    print("***ThreePhase Fault Validations***")
    pwrworld = read_excel(path)
    compare(faults.faultYbus, pwrworld)
    fault_voltages = faults.calc_fault_voltages(1, 1.0)
    print()
    print("fault current =", np.abs(faults.I_fn))
    print("fault voltages:")
    print(fault_voltages)
    print()


def UnsymmetricalFaultsValidation(circ: Circuit):
    unsym = UnsymmetricalFaults(circ)
    SequenceMatricesValidation(unsym)

def SequenceMatricesValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***SequenceMatricesValidation***")
    print("Zero Sequence Matrix =")
    print(usf.zero_Ybus)
    print()

    print("Positive Sequence Matrix =")
    print(usf.positive_Ybus)
    print()

    print("Negative Sequence Matrix =")
    print(usf.negative_Ybus)
    print()