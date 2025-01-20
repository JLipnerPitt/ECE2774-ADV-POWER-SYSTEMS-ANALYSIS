import Component
import Bus

#  This class "creates" circuits.
class Circuit:

  def __init__(self, name: str):

    self.name = name
    self.i = float

    self.table = ["Resistors", "Loads", "VSources"] #  Table of all possible components

    #  Dict that stores all information for each component type
    #  Each component key has a dictonary that stores all components of that type
    self.components = {comp:{} for comp in self.table}
    
    self.buses = {}


  #  Adds buses to circuit.
  def add_bus(self, name: str, index: int, voltage: float):
    bus = Bus.Bus(name, index, voltage)
    self.buses.update({name:bus})
    self.check_bus_names(index, name)


  def add_resistor(self, name: str, r: float, bus1="", bus2=""):
    
    if name in self.components["Resistors"]:
      print("Resistor already exists. No changes to circuit")

    else:
      resistor = Component.Resistor(name, r, bus1, bus2)
      self.components["Resistors"].update({"R1":resistor})
    
    #self.print_resistors()


  def add_load(self, name: str, power: float, voltage: float, bus: str):

    if name in self.components["Loads"]:
      print("Load already exists. No changes to circuit.")
    
    else:
      load = Component.Load(name, power, voltage, bus)
      self.components["Loads"].update({name:load})
  
    #self.print_loads()


  def add_voltage_source(self, name: str, v: float, bus: str):
    if name in self.components["VSources"]:
      print("Name already exists. No changes to circuit")
    
    else:
      vsource = Component.VoltageSource(name, v, bus)
      self.components["VSources"].update({name:vsource})
      self.buses[bus].voltage = v  #  voltage source overrides bus voltage


  def calc_i(self):

    resistance = 0
    for n in self.components["Resistors"]:
      resistance += self.components["Resistors"][n].value
    
    for n in self.components["Loads"]:
      resistance += self.components["Loads"][n].resistance
    
    self.i = self.buses["bus1"].voltage/resistance
    
    print("Equivalent series resistance =", resistance, "Ω")
    print("Circuit current =", self.i, "A")


  #  checks if buses have the same name and updates the buses list accordingly
  def check_bus_names(self, index: int, name: str):
    for b in self.buses:
      if self.buses[b].index == index:
        self.buses[b].name = name
