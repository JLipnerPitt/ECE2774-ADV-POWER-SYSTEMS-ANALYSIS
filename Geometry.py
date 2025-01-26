import Bundle

class Geometry:

  def __init__(self, name: str, xa: float, ya: float, xb: float, yb: float, xc: float, yc: float):
    self.name = name
    self.xa = xa
    self.ya = ya
    self.xb = xb
    self.yb = yb
    self.xc = xc
    self.yc = yc
    self.Deq = float
    self.calc_DEQ()

  # Deq = GMD = Dxy
  def calc_Deq(self):
    self.Deq = (self.xa*self.ya*self.xb*self.yb*self.xc*self.yc)**(1/9)