#  This class creates buses (nodes). Each bus has a name, voltage level, and angle.
#  If no voltage or angle is provided, they are assumed to be zero.
class Bus:


  def __init__(self, name, index, voltage=float):
    self.index = index
    self.name = name
    self.voltage = voltage
    

  def set_voltage(self, v: float):
    self.voltage = v