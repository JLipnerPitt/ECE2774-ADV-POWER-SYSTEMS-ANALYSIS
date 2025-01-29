#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
class Component:
    pass

class Resistor(Component):
    
    def __init__(self, name: str, resistance: float, bus1: str, bus2: str):
      self.name = name
      self.resistance = resistance
      self.bus1 = bus1
      self.bus2 = bus2
      self.g = float
      self.calc_g()

       
    def calc_g(self):
       self.g = 1/self.resistance


class Load(Component):
  
  def __init__(self, name: str, power: float, voltage: float, bus: str):
    self.name = name
    self.power = power
    self.voltage = voltage
    self.bus = bus
    self.resistance = float
    self.g = float
    self.calc_r()
    self.calc_g()


  def calc_r(self):
     self.resistance = self.voltage**2/self.power


  def calc_g(self):
     self.g = self.power/self.voltage**2
    

class VoltageSource(Component):
    
    def __init__(self, name: str, voltage: float, bus: str):
       self.name = name
       self.voltage = voltage
       self.bus = bus
