import Circuit
import Solution

circ1 = Circuit.Circuit("MyFirstCircuit")
circ1.add_bus("GND", 0, 0)
circ1.add_bus("bus1", 1, 0)
circ1.add_bus("bus2", 2, 0)
circ1.add_voltage_source("V1", 100,"bus1")
circ1.add_resistor("R1", 5, "bus1", "bus2")
circ1.add_load("load1", 2000, 100, "bus2", "GND")
circ1.print_nodal_voltages()
circ1.calc_i()
circ1.calc_nodal_voltages()
circ1.print_nodal_voltages()




