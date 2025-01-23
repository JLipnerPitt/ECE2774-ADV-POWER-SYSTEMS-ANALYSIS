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

class Inductor(Component):
    pass

class Capacitor(Component):
    pass

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

class Transformer(Component):
   def __init__(self, name: str, power: float, prim_voltage: float, sec_voltage: float, 
                                      Zbasepu: float, turns_ratio: float, bus1: str, bus2: str):
    
    self.name = name
    self.power = power
    self.prim_voltage = prim_voltage
    self.sec_voltage = sec_voltage
    self.turns_ratio = turns_ratio
    self.bus1 = bus1
    self.bus2 = bus2
    self.Zbasepu = Zbasepu
    self.impedance = calc_impedance(self.Zbasepu, self.prim_voltage, self.power)
    self.admittance = calc_admit(self.impedance)

    def calc_impedance(Zbasepu, Vbase, Pbase):
       Zbase = Vbase**2/Pbase
       Z = Zbase*Zbasepu
       return Z
    
    def calc_admit(Z):
       Y = 1/Z
       return Y 

class VoltageSource(Component):
    def __init__(self, name: str, voltage: float, bus1: str):
       self.name = name
       self.voltage = voltage
       self.bus1 = bus1

class CurrentSource(Component):
    pass
