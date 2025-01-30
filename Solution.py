import Circuit

class Solution:
    
    def __init__(self, circuit: Circuit):
      self.circuit = circuit

    def do_power_flow(self):
      v = self.circuit.i*self.circuit.components["Resistors"]["R1"].resistance
      self.circuit.buses["bus2"].set_voltage(v)