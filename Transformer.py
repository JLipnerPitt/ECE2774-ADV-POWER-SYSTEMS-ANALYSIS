import numpy as np
from math import atan, sin, cos

class Transformer():
   def __init__(self, name: str, bus1: str, bus2: str, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
    
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.power_rating = power_rating
    self.impedance_percent = impedance_percent
    self.x_over_r_ratio = x_over_r_ratio
    self.Zpu = self.calc_impedance()
    self.Ypu = self.calc_admittance()
    self.yprim = self.calc_yprim()

    self.calc_impedance()
    self.calc_admittance()
    self.calc_yprim()


   def calc_impedance(self):
      theta = atan(self.x_over_r_ratio)
      R = self.impedance_percent*cos(theta)/100
      X = self.impedance_percent*sin(theta)/100
      Zpu = complex(R, X)
      return Zpu
   

   def calc_admittance(self):
      return 1/self.Zpu


   def calc_yprim(self):
      return np.array([self.Ypu, -self.Ypu], [-self.Ypu, self.Ypu])