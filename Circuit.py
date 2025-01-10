import Bus
import Component

#  This class "creates" circuits.
class Circuit:

  def __init__(self, name, buses, resistors):
    self.name = name
    self.buses = buses
    self.resistors = resistors

  def print_resistors(self):
    for i in self.resistors:
      print(i.name, "=", i.resistance, "Ω")
  
  def print_buses(self):
    for i in self.buses:
      print(i.name)