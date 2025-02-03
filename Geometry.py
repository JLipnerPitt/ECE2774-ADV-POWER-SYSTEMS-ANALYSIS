from math import sqrt

class Geometry:

  def __init__(self, name: str, x: list[float], y: list[float]):
    # pos = [[], []]
    self.name = name
    self.x = x
    self.y = y
    self.Deq = self.calc_Deq()

  # Deq = GMD = Dxy
  def calc_Deq(self):
    root = len(self.x)
    Dab = sqrt((self.x[1]-self.x[0])**2 + (self.y[1]-self.y[0])**2)
    Dbc = sqrt((self.x[2]-self.x[1])**2 + (self.y[2]-self.y[1])**2)
    Dca = sqrt((self.x[0]-self.x[2])**2 + (self.y[0]-self.y[2])**2)
    self.Deq = (Dab*Dbc*Dca)**(1/root)
    return self.Deq
  
def Geometry_Validation():
  geometry1 = Geometry("Geometry 1", [0, 10, 20], [0, 0, 0])
  print(geometry1.name, geometry1.x, geometry1.y)
  print("Deq =", geometry1.Deq)

Geometry_Validation()