#  This class contains various components used in electrical circuits. 
#  Component is a parent class for all the child "component" classes.
import numpy as np
from math import atan, sin, cos

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
   def __init__(self, name: str, bus1: str, bus2: str, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
    
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.power_rating = power_rating
    self.impedance_percent = impedance_percent
    self.x_over_r_ratio = x_over_r_ratio
    self.Zpu = complex
    self.Ypu = complex
    self.yprim = np.array([])


   def calc_impedance(self):
      theta = atan(self.x_over_r_ratio)
      R = self.impedance_percent*cos(theta)/100
      X = self.impedance_percent*sin(theta)/100
      self.Zpu = complex(R, X)
   

   def calc_admittance(self):
      self.Ypu = 1/self.Zpu


   def calc_yprim(self):
      pass

class VoltageSource(Component):
    def __init__(self, name: str, voltage: float, bus1: str):
       self.name = name
       self.voltage = voltage
       self.bus1 = bus1

class CurrentSource(Component):
    pass
