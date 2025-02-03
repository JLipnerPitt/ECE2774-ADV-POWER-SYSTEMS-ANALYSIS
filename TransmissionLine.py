import Bundle
import Geometry
import Conductor
from math import pi, log

class TransmissionLine():

  def __init__(self, name: str, bus1: str, bus2: str, bundle: Bundle, geometry: Geometry, length: float):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.bundle = bundle
    self.geometry = geometry
    self.length = length
    self.R = self.calc_R()
    self.X = self.calc_X()
    self.B = self.calc_B()
    self.yprim = self.calc_yprim()

  def calc_R(self):
    R_c = self.bundle.conductor.resistance
    return R_c*1609*self.length/self.bundle.num_conductors 

  def calc_X(self):
    L_c = 2*10^-7*log(self.geometry.Deq/self.geometry.DSL)*1000*200  # gives Henries
    X_c = 2*pi*60*L_c
    return X_c

  def calc_B(self):
    epsilon = 8.854*10^-12
    C_c = 2*pi*epsilon/(log(self.geometry.Deq/self.bundle.DSC))
    C_c = C_c*1609*self.length  # converts F/m to F using length (in miles)
    return C_c

  def calc_yprim(self):
    pass
  
def TransmissionLine_Validation():
  conductor1 = Conductor.Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
  bundle1 = Bundle.Bundle("Bundle 1", 2, 1.5, conductor1)
  geometry1 = Geometry.Geometry("Geometry 1", 0, 0, 18.5, 0, 37, 0)
  line1 = TransmissionLine("Line 1", "bus1", "bus2", bundle1, geometry1, 10)
  

  