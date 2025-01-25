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
