#  This class contains various components used in electrical circuits. 
#  Component is a generic parent class for all the child "component" classes.
class Component:
  pass

class Resistor(Component):
    
    def __init__(self, name, bus1, bus2, resistance):
      self.name = name
      self.bus1 = bus1
      self.bus2 = bus2
      self.resistance = resistance

class Inductor(Component):
    
  def __init__(self, name, bus1, bus2, inductance):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.inductance = inductance

class Capacitor(Component):
    
  def __init__(self, name, bus1, bus2, capacitance):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.capacitance = capacitance

class Load(Component):

  def __init__(self, name, bus1, bus2, pf):
      self.name = name
      self.bus1 = bus1
      self.bus2 = bus2
      self.pf = pf
  
class VoltageSource(Component):
  
  def __init__(self, name, bus1, bus2, voltage):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.voltage = voltage

class CurrentSource(Component):
    
  def __init__(self, name, bus1, bus2, current):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.current = current
