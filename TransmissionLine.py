import Bundle
import Geometry
import Conductor
import Bus

class TransmissionLine:

  def __init__(self, name:str, bus1: Bus, bus2: Bus, bundle: Bundle, geometry: Geometry, length: float):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.bundle = bundle
    self.geometry = geometry
    self.length = length
    self.zbase = float
    self.ybase = float
  
  def calc_base_values(self):
    pass

  def calc_yprim(self):
    pass
  
def TransmissionLine_Validation():
  conductor1 = Conductor.Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
  bundle1 = Bundle.Bundle("Bundle 1", 2, 1.5, conductor1)
  geometry1 = Geometry.Geometry("Geometry 1", 0, 0, 18.5, 0, 37, 0)
  line1 = TransmissionLine("Line 1", "bus1", "bus2", bundle1, geometry1, 10)

  