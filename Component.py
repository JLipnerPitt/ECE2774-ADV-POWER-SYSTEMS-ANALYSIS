#  This class contains various components used in electrical circuits. 
#  Component is a generic parent class for all the child "component" classes.
class Component:
  pass

class Resistor(Component):
    
  def __init__(self, name, resistance):
    self.name = name
    self.resistance = resistance

class Inductor(Component):
    
  def __init__(self, name, inductance):
    self.name = name
    self.inductance = inductance

class Capacitor(Component):
    
  def __init__(self, name, capacitance):
    self.name = name
    self.capacitance = capacitance

class Load(Component):

  def __init__(self, name, p, pf):
    self.name = name
    self.p = p
    self.pf = pf
  
class VoltageSource(Component):
  
  def __init__(self, name, voltage):
    self.name = name
    self.voltage = voltage

class CurrentSource(Component):
    
  def __init__(self, name, current):
    self.name = name
    self.current = current
