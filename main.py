import Circuit
import Solution

circ1 = Circuit.Circuit("MyFirstCircuit")
circ1.add_bus("GND", 0, 0)
circ1.add_bus("bus1", 1, 100)
circ1.add_bus("bus2", 2, 0)
circ1.add_voltage_source("V1", 10,"bus1")
circ1.add_resistor("R1", 500, "bus1", "bus2")
circ1.add_load("load1", 10, 1000, "bus2", "GND")

solution1 = Solution.Solution(circ1)
solution1.simple_circuit()





