import numpy as np

from Circuit import Circuit, ThreePhaseFault, UnsymmetricalFaults
from Settings import settings
from Tools import read_excel, compare, read_jacobian, display_jacobian
from numpy import round


def CreateSevenPowerBusSystem():
    circ = Circuit("Example_7bus")

    circ.add_bus("bus1", 20)
    circ.add_bus("bus2", 230)
    circ.add_bus("bus3", 230)
    circ.add_bus("bus4", 230)
    circ.add_bus("bus5", 230)
    circ.add_bus("bus6", 230)
    circ.add_bus("bus7", 18)

    circ.add_transformer("T1", "D-Y", "bus1", "bus2", 125, 8.5, 10, 0.0018904)
    circ.add_transformer("T2", "Y-D", "bus6", "bus7", 200, 10.5, 12)

    circ.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    circ.add_geometry("Geometry7bus", [0, 19.5, 39], [0, 0, 0])
    circ.add_bundle("Bundle7bus", 2, 1.5, "Partridge")

    circ.add_tline_from_geometry("L1", "bus2", "bus4", "Bundle7bus", "Geometry7bus", 10)
    circ.add_tline_from_geometry("L2", "bus2", "bus3", "Bundle7bus", "Geometry7bus", 25)
    circ.add_tline_from_geometry("L3", "bus3", "bus5", "Bundle7bus", "Geometry7bus", 20)
    circ.add_tline_from_geometry("L4", "bus4", "bus6", "Bundle7bus", "Geometry7bus", 20)
    circ.add_tline_from_geometry("L5", "bus5", "bus6", "Bundle7bus", "Geometry7bus", 10)
    circ.add_tline_from_geometry("L6", "bus4", "bus5", "Bundle7bus", "Geometry7bus", 35)

    circ.add_generator("Gen1", "bus1", 1, 125, 0.12, 0.14, 0.05, 0)
    circ.add_generator("Gen2", "bus7", 1, 200, 0.12, 0.14, 0.05, 0.30864)

    circ.add_load("Load1", "bus3", 110, 50)
    circ.add_load("Load2", "bus4", 100, 70)
    circ.add_load("Load3", "bus5", 100, 65)

    return circ


def SevenPowerBusSystemValidation():
    circ = CreateSevenPowerBusSystem()
    #circ.change_slack("bus1", "bus7")
    ImpedanceValidation(circ)
    YbusValidation(circ, r"Excel_Files\SevenBus\7bus_Ybus_matrix.xlsx")
    DCPowerFlowValidation(circ)
    FastDecoupledValidation(circ)
    NewtonRaphValidation(circ)
    VARLimitValidation()
    ThreePhaseFaultsValidation(circ, r"Excel_Files\SevenBus\7bus_positive_sequence_Ybus_matrix.xlsx")
    UnsymmetricalFaultsValidation(circ)
    CapacitorCorrectionValidation(circ)


def ImpedanceValidation(circ: Circuit):
    print("***TRANSMISSION LINE AND TRANSFORMER IMPEDANCE/ADMITTANCE VALIDATION***")
    print()
    for i in range(len(circ.transformers)):
        print(f"T{i+1} impedance =", round(circ.transformers[f"T{i+1}"].Zpu, 6))
        print(f"T{i+1} admittance =", round(circ.transformers[f"T{i+1}"].Ypu, 6))
        print()

    for i in range(len(circ.transmission_lines)):
        print(f"Line{i+1} impedance =", round(circ.transmission_lines[f"L{i+1}"].Zseries, 6))
        print(f"Line{i+1} admittance =", round(circ.transmission_lines[f"L{i+1}"].Yseries, 6))
        print(f"Line{i+1} shunt admittance =", round(circ.transmission_lines[f"L{i+1}"].Yshunt, 6))
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
    print("Newton-Raphson algorithm results:")
    circ.do_newton_raph()
    circ.do_newton_raph()
    print()
    print()


def VARLimitValidation(var_test=40*1e6):
    print("***VAR LIMIT VALIDATION***")
    print()
    circ = CreateSevenPowerBusSystem()
    circ.generators["Gen2"].var_limit = var_test
    circ.do_newton_raph()
    print(f"VAR Limiting results for {var_test/1e6} MVAR at Gen2:")
    circ.generators["Gen2"].var_limit = 40e6
    circ.do_newton_raph(True)
    print()
    print()


def FastDecoupledValidation(circ: Circuit):
    print("***FAST DECOUPLED ALGORITHM VALIDATION")
    print()
    print("Fast Decoupled results:")
    circ.do_fast_decoupled()
    circ.do_fast_decoupled()
    print()
    print()


def DCPowerFlowValidation(circ: Circuit):
    print("***DC POWER FLOW VALIDATION***")
    print()
    print("DC Power Flow results:")
    circ.do_dc_power_flow()
    circ.do_dc_power_flow()
    print()
    print()


def ThreePhaseFaultsValidation(circ: Circuit, path):
    symfault = ThreePhaseFault(circ, 1)
    print("***THREE PHASE FAULT VALIDATIONS***")
    print()
    #pwrworld = read_excel(path)
    #compare(symfault.faultYbus, pwrworld)
    symfault.calc_fault_values()
    print()


def UnsymmetricalFaultsValidation(circ: Circuit):
    unsym = UnsymmetricalFaults(circ, 1)
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
    usf.SLG_fault_values()


def LLValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***LINE TO LINE FAULT VALIDATION***")
    usf.LL_fault_values()


def DLGValidation(unsymfault: UnsymmetricalFaults):
    usf = unsymfault
    print("***DOUBLE LINE TO GROUND FAULT VALIDATION***")
    usf.DLG_fault_values()
    usf.print_current()
    print()
    print("Double Line to Ground Fault Voltages:")
    usf.print_voltages()
    print()
    print()


def CapacitorCorrectionValidation(circ: Circuit):
    print("***CAPACITOR CORRECTION VALIDATION***")
    print()
    print("System before compensation:")
    circ.print_data()
    print()

    print("System after compensation:")
    circ.add_shunt_capacitor("cap1", 100.0, "bus2")
    circ.add_shunt_capacitor("cap2", 100.0, "bus3")
    circ.do_newton_raph()
    print()


def ReactorCorrectionValidation():
    print()
    print("***REACTOR CORRECTION VALIDATION***")
    print()
    circ2 = Circuit("ReactorValidation")
    circ2.add_bus("bus1", 230)
    circ2.add_bus("bus2", 230)

    circ2.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
    circ2.add_geometry("Geometry7bus", [0, 19.5, 39], [0, 0, 0])
    circ2.add_bundle("Bundle7bus", 2, 1.5, "Partridge")
    circ2.add_tline_from_geometry("L1", "bus1", "bus2", "Bundle7bus", "Geometry7bus", 75)

    circ2.add_generator("Gen1", "bus1", 1, 200, 0.12, 0.14, 0.05, 0)
    circ2.add_load("Load1", "bus2", 100, -100)

    print("Before Correction:")
    circ2.do_newton_raph()
    print()

    print("After Correction:")
    circ2.add_shunt_reactor("reactor1", -80, "bus2")
    circ2.do_newton_raph()