
class Conductor:

  def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
    self.name = name
    self.diam = diam
    self.radius = diam/2
    self.GMR = GMR
    self.resistance = resistance
    self.ampacity = ampacity