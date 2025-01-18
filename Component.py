#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
class Component:


  def __init__(self, name: str, value: float, bus1: str, bus2: str):
    self.name = name
    self.value = value
    self.bus1 = bus1
    self.bus2 = bus2


class Resistor(Component):
    
    
    def __init__(self, name: str, value: float, bus1: str, bus2: str):
      self.name = name
      self.value = value
      self.bus1 = bus1
      self.bus2 = bus2
      self.g = float
      self.calc_g()

       
    def calc_g(self):
       self.g = 1/self.value


class Load(Component):
  

  def __init__(self, name: str, power: float, voltage: float, bus: str):
    self.name = name
    self.power = power
    self.voltage = voltage
    self.bus1 = bus
    self.resistance = float
    self.g = float
    self.calc_r()
    self.calc_g()


  def calc_r(self):
     self.resistance = self.voltage**2/self.power


  def calc_g(self):
     self.g = 1/self.resistance
    

class VoltageSource(Component):
    def __init__(self, name: str, voltage: float, bus: str):
       self.name = name
       self.voltage = voltage
       self.bus = bus
