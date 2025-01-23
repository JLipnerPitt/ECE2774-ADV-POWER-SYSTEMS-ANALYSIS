#  This class creates buses (nodes). Each bus has a name, voltage level, and angle.
#  If no voltage or angle is provided, they are assumed to be zero.
class Bus:

  def __init__(self, name: str, index: int):
    self.index = index
    self.name = name
    self.voltage = float
    self.angle = float

  def set_voltage(self, v: float):
    self.voltage = v
