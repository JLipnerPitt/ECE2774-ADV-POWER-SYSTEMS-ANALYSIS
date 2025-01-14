#  This class creates buses (nodes). Each bus has a name, voltage level, and angle.
#  If no voltage or angle is provided, they are assumed to be zero.
class Bus:

  def __init__(self, number, name, voltage=138000.0000, angle=0):
    self.number = number
    self.name = name
    self.voltage = voltage
    self.angle = angle

  def set_bus_voltage(self, v):
    self.voltage = v
