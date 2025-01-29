import Circuit
import Solution

#  Validation Case
circ1 = Circuit.Circuit("MyFirstCircuit")
circ1.add_bus("bus1")
circ1.add_bus("bus2")
circ1.add_voltage_source("V1", 100,"bus1")
circ1.add_resistor("R1", 5, "bus1", "bus2")
circ1.add_load("load1", 2000, 100, "bus2")
circ1.calc_i()
solution1 = Solution.Solution(circ1)
solution1.do_power_flow()
circ1.print_nodal_voltages()


#  Example Case
circ2 = Circuit.Circuit("MyFirstCircuit")
circ2.add_bus("bus1")
circ2.add_bus("bus2")
circ2.add_voltage_source("V1", 200,"bus1")
circ2.add_resistor("R1", 10, "bus1", "bus2")
circ2.add_load("load1", 5000, 125, "bus2")
circ2.calc_i()
solution2 = Solution.Solution(circ2)
solution2.do_power_flow()
circ1.print_nodal_voltages()




