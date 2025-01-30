import Bundle
from math import prod

class Geometry:

  def __init__(self, name: str, x: list[float], y: list[float]):
    self.name = name
    self.x = x
    self.y = y
    self.Deq = float
    self.calc_Deq()

  # Deq = GMD = Dxy
  def calc_Deq(self):
    temp = []
    n = len(self.x)
    m = len(self.y)
    root = n*m
    for i in range(n):
      for k in range(m):
        temp.append((self.x[i]+self.y[k]))
        print((self.x[i]+self.y[k]))
    self.Deq = (prod(temp))**(1/root)
  
def Geometry_Validation():
  geometry1 = Geometry("Geometry 1", [0, 0.5, 2], [4, 4.3])
  print(geometry1.name, geometry1.x, geometry1.y)
  print("Deq =", geometry1.Deq)

Geometry_Validation()