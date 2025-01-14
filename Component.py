#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
class Component:

  def __init__(self, name, value, bus1, bus2):
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
    
    def __init__(self, name, value, bus1, bus2):
      self.name = name
      self.value = value
      self.bus1 = bus1
      self.bus2 = bus2
      self.g = None
      self.calc_g()
       
    def calc_g(self):
       self.g = 1/self.value

class Inductor(Component):
    pass

class Capacitor(Component):
    pass

class Load(Component):
    
  def __init__(self, name, voltage, power, resistance, bus1):
    self.name = name
    self.voltage = voltage
    self.power = power
    self.resistance = resistance
    self.bus1 = bus1
    self.g = None
    self.calc_g()
       
  def calc_g(self):
     self.g = 1/self.resistance
    
class VoltageSource(Component):
    def __init__(self, name, voltage, bus):
       self.name = name
       self.voltage = voltage
       self.bus = bus

class CurrentSource(Component):
    pass
