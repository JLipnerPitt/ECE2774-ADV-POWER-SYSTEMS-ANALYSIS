import Circuit

class Solution:
    
    def __init__(self, circuit: Circuit):
      self.circuit = circuit

    def do_power_flow(self):
      v = self.circuit.i*self.circuit.components["Resistors"]["R1"].value
      self.circuit.buses["bus2"].set_voltage(v)
      self.print_nodal_voltages()

    def print_nodal_voltages(self):
      for n in self.circuit.buses:
        print(f"Bus #{self.circuit.buses[n].index}, {self.circuit.buses[n].voltage} V")
      print()