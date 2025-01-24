import Bundle
import Geometry

class TransmissionLine:

  def __init__(self, name:str, bus1: str, bus2: str, bundle: Bundle, geometry: Geometry, length: float):
    self.name = name
    self.bus1 = bus1
    self.bus2 = bus2
    self.bundle = bundle
    self.geometry = geometry
    self.length = length

  