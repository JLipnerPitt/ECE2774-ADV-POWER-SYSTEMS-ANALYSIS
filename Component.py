#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
class Component:

  def __init__(self, name: str, value: float, bus1: str, bus2: str):
    self.name = name
    self.value = value
    self.bus1 = bus1
    self.bus2 = bus2

  '''
  def change_value(self, v):
    self.value = v

  def change_bus1(self, b1):
    self.bus1 = b1

  def change_bus2(self, b2):
    self.bus2 = b2'''

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

class Inductor(Component):
    pass

class Capacitor(Component):
    pass

class Load(Component):
  
  def __init__(self, name: str, power: float, voltage: float, bus1: str, bus2: str):
    self.name = name
    self.power = power
    self.voltage = voltage
    self.bus1 = bus1
    self.bus2 = bus2
    self.resistance = float
    self.g = float
    self.calc_r()
    self.calc_g()

  def calc_r(self):
     self.resistance = self.voltage**2/self.power

  def calc_g(self):
     self.g = 1/self.resistance
    
class VoltageSource(Component):
    def __init__(self, name: str, voltage: float, bus1: str):
       self.name = name
       self.voltage = voltage
       self.bus1 = bus1

class CurrentSource(Component):
    pass
