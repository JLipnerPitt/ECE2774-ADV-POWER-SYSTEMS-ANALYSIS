#  This class creates buses (nodes). Each bus has a name, voltage level, and index.

class Bus:

  def __init__(self, name: str):
    self.name = name
    self.voltage = float
    

  def set_voltage(self, v: float):
    self.voltage = v