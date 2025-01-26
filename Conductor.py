
class Conductor:

  def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
    self.name = name
    self.diam = diam
    self.radius = diam/2
    self.GMR = GMR
    self.resistance = resistance
    self.ampacity = ampacity

def Conductor_Validation():
  conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
  print(f"Name: {conductor1.name}, Diameter = {conductor1.diam}, GMR = {conductor1.GMR}, Resistance = {conductor1.resistance}, Ampacity = {conductor1.ampacity}")

Conductor_Validation()
