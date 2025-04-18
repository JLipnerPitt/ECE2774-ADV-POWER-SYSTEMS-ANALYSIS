import numpy as np

from Circuit import Circuit, ThreePhaseFault, UnsymmetricalFaults
from Settings import settings
from Tools import read_excel, compare, read_jacobian, display_jacobian
from numpy import round


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

    circ.add_transformer("T1", "D-Y", circ.buses["bus1"], circ.buses["bus2"], 125, 8.5, 10, 0.0018904)
    circ.add_transformer("T2", "Y-D", circ.buses["bus6"], circ.buses["bus7"], 200, 10.5, 12)

    circ.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    circ.add_geometry("Geometry7bus", [0, 19.5, 39], [0, 0, 0])
    circ.add_bundle("Bundle7bus", 2, 1.5, circ.conductors["Partridge"])

    circ.add_tline_from_geometry("L1", circ.buses["bus2"], circ.buses["bus4"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 10)
    circ.add_tline_from_geometry("L2", circ.buses["bus2"], circ.buses["bus3"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 25)
    circ.add_tline_from_geometry("L3", circ.buses["bus3"], circ.buses["bus5"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 20)
    circ.add_tline_from_geometry("L4", circ.buses["bus4"], circ.buses["bus6"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 20)
    circ.add_tline_from_geometry("L5", circ.buses["bus5"], circ.buses["bus6"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 10)
    circ.add_tline_from_geometry("L6", circ.buses["bus4"], circ.buses["bus5"], circ.bundles["Bundle7bus"], circ.geometries["Geometry7bus"], 35)

    circ.add_generator("Gen1", "bus1", 1, 200, 0.12, 0.14, 0.05, 0)
    circ.add_generator("Gen2", "bus7", 1, 200, 0.12, 0.14, 0.05, 0.30864)

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
    YbusValidation(circ, r"Excel_Files\SevenBus\7bus_Ybus_matrix.xlsx")
    NewtonRaphValidation(circ)
    #FastDecoupledValidation(circ)
    #DCPowerFlowValidation(circ)
    #ThreePhaseFaultsValidation(circ, r"Excel_Files\SevenBus\7bus_positive_sequence_Ybus_matrix.xlsx")
    #UnsymmetricalFaultsValidation(circ)
    VARCorrectionValidation(circ)


def ImpedanceValidation(circ: Circuit):
    print("***TRANSMISSION LINE AND TRANSFORMER IMPEDANCE/ADMITTANCE VALIDATION***")
    print()
    for i in range(len(circ.components["Transformers"])):
        print(f"T{i+1} impedance =", round(circ.components["Transformers"][f"T{i+1}"].Zpu, 6))
        print(f"T{i+1} admittance =", round(circ.components["Transformers"][f"T{i+1}"].Ypu, 6))
        print()

    for i in range(len(circ.components["T-lines"])):
        print(f"Line{i+1} impedance =", round(circ.components["T-lines"][f"L{i+1}"].Zseries, 6))
        print(f"Line{i+1} admittance =", round(circ.components["T-lines"][f"L{i+1}"].Yseries, 6))
        print(f"Line{i+1} shunt admittance =", round(circ.components["T-lines"][f"L{i+1}"].Yshunt, 6))
        print()
    
    print()


def YbusValidation(circ: Circuit, path: str):
    print("***YBUS VALIDATIONS***")
    print()
    print("Ybus:")
    Ybus = circ.calc_Ybus()
    circ.print_Ybus()
    print()
    print()
    #pwrworld = read_excel(path)
    #compare(Ybus, pwrworld)
    

def NewtonRaphValidation(circ: Circuit):
    print("***NEWTON-RAPHSON ALGORITHM VALIDATION***")
    print()
    circ.do_newton_raph()
    print("Newton-Raphson algorithm results:")
    circ.print_data()
    print()
    print()


def FastDecoupledValidation(circ: Circuit):
    print("***FAST DECOUPLED ALGORITHM VALIDATION")
    print()
    circ.do_fast_decoupled()
    print("Fast Decoupled results:")
    circ.print_data()
    print()
    print()


def DCPowerFlowValidation(circ: Circuit):
    print("***DC POWER FLOW VALIDATION***")
    print()
    circ.do_dc_power_flow()
    print("DC Power Flow results:")
    circ.print_data(True)
    print()
    print()


def ThreePhaseFaultsValidation(circ: Circuit, path):
    symfault = ThreePhaseFault(circ, 1, 1.0)
    print("***THREE PHASE FAULT VALIDATIONS***")
    print()
    pwrworld = read_excel(path)
    #compare(symfault.faultYbus, pwrworld)
    symfault.calc_fault_values()
    print("ThreePhase Current:")
    symfault.print_current()
    print()
    print("ThreePhase Fault Voltages:")
    symfault.print_voltages()
    print()
    print()


def UnsymmetricalFaultsValidation(circ: Circuit):
    unsym = UnsymmetricalFaults(circ, 1, 1.0)
    SequenceMatricesValidation(unsym)
    SLGValidation(unsym)
    LLValidation(unsym)
    DLGValidation(unsym)


def SequenceMatricesValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***SEQUENCE MATRICES VALIDATION***")
    print()
    print("Zero Sequence Y Matrix")
    usf.print_Y0bus()
    print()

    print("Positive Sequence Y Matrix")
    usf.print_Ypbus()
    print()

    print("Negative Sequence Y Matrix")
    usf.print_Ynbus()
    print()
    print()


def SLGValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***SINGLE LINE TO GROUND FAULT VALIDATION***")
    print()
    usf.SLG_fault_values()
    usf.print_current()
    print()
    print("Single Line to Ground Fault Voltages:")
    usf.print_voltages()
    print()
    print()


def LLValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***LINE TO LINE FAULT VALIDATION***")
    print()
    usf.LL_fault_values()
    usf.print_current()
    print()
    print("Line to Line Fault Voltages:")
    usf.print_voltages()
    print()
    print()


def DLGValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***DOUBLE LINE TO GROUND FAULT VALIDATION***")
    print()
    usf.DLG_fault_values()
    usf.print_current()
    print()
    print("Double Line to Ground Fault Voltages:")
    usf.print_voltages()
    print()
    print()


def VARCorrectionValidation(circ: Circuit):
    print("***VAR COMPENSATION VALIDATION***")
    print()
    print("Bus 2 voltage before compensation:")
    circ.print_data()
    print()
    print("Bus 2 voltage after compensation:")
    circ.add_shunt_capacitor("cap1", 100.0, circ.buses["bus2"])
    circ.calc_Ybus()
    circ.do_newton_raph()
    circ.print_data()
    print()