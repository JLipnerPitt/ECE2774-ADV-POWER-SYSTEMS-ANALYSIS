import Component
import Bus
import Circuit

r1 = Component.Resistor("r1", "A", "B", 10)
r2 = Component.Resistor("r2", "A", "B", 10)
resistors = [r1,r2]

Gnd = Bus.Bus("GND")
bus1 = Bus.Bus("b1")

buses = [Gnd,bus1]

circ1 = Circuit.Circuit("MyFirstCircuit", buses, resistors)
circ1.print_resistors()
