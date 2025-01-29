import Bundle
from math import prod

class Geometry:

  def __init__(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
    self.name = name
    self.x = [xa, xb, xc]
    self.y = [ya, yb, yc]
    self.Deq = float
    self.calc_Deq()

  # Deq = GMD = Dxy
  def calc_Deq(self):
    temp = []
    for i in range(3):
      for k in range(3):
        temp.append((self.x[i]+self.y[k]))
    self.Deq = (prod(temp))**(1/9)
  
def Geometry_Validation():
  geometry1 = Geometry("Geometry 1", 0, 0, 18.5, 0, 37, 0)
  print(geometry1.name, geometry1.x, geometry1.y)
  print("Deq =", geometry1.Deq)

Geometry_Validation()