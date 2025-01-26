import Conductor
from math import sqrt

class Bundle:

  def __init__(self, name: str, num_conductors: int, spacing: float, conductor: Conductor):
    self.name = name
    self.num_conductors = num_conductors
    self.spacing = spacing
    self.conductor = conductor
    self.DSC = float
    self.DSL = float
    self.calc_DSC()
    self.calc_DSL()

  def calc_DSC(self):
    n = self.num_conductors
    d = self.spacing
    r = self.conductor.diam/2

    match n:
      case 1:
        self.DSC = r
      case 2:
        self.DSC = sqrt(d*r)
      case 3:
        self.DSC = (d**(n-1)*r)**(1/n)
      case 4:
        self.DSC = 1.091*(d**(n-1)*r)**(1/n)


  def calc_DSL(self):
    n = self.num_conductors
    GMR = self.conductor.GMR
    d = self.spacing

    match n:
      case 1:
        self.DSL = GMR
      case 2:
        self.DSL = sqrt(d*GMR)
      case 3:
        self.DSL = (d**(n-1)*GMR)**(1/n)
      case 4:
        self.DSL = 1.091*(d**(n-1)*GMR)**(1/n)
      case _:
        self.DSL = 0

def Bundle_Validation():
  conductor1 = Conductor.Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
  bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)
  print(f"Bundle name: {bundle1.name}, # of conductors = {bundle1.num_conductors}, spacing = {bundle1.spacing}, Conductor name: {bundle1.conductor.name}")
  print(f"DSC = {bundle1.DSC}, DSL = {bundle1.DSL}")

Bundle_Validation()

