import Circuit

circ1 = Circuit.Circuit("MyFirstCircuit")
circ1.add_resistor(10)
#circ1.add_resistor(25)
#circ1.print_resistors()
circ1.change_resistor_connection("R1", "bus1", "bus2")
circ1.change_resistor_connection("R2", "bus1", "bus2")

"""circ1.add_bus(1,1,100,0)
circ1.add_bus(1,2,100,0)
circ1.print_buses()

circ1.add_bus(1,3,100,0)
circ1.add_bus(2,1,100,0)
print(circ1.resistors)"""

