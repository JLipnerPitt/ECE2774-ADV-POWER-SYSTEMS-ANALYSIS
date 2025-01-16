import Component
import Bus

#  This class "creates" circuits.
class Circuit:

  def __init__(self, name: str):

    self.name = name
    self.i = 0

    self.table = ["Resistors", "Loads", "VSources"] #  Table of all possible components

    #  Dict that stores all information for each component type
    #  Each component key has a dictonary that stores all components of that type
    self.components = {comp:{} for comp in self.table}
    
    self.buses = {}
    
    self.bus_count = 0
    self.resistor_count = 0
    self.capacitor_count = 0
    self.inductor_count = 0
    self.load_count = 0
    self.voltage_source_count = 0
    self.current_source_count = 0

    self.bus_order = []

  #  Adds buses to circuit.
  def add_bus(self, name: str, number: int, voltage: float, angle=0.0):
    self.bus_count += 1
    bus = Bus.Bus(number, name, voltage, angle)
    self.buses.update({name:bus})
    self.check_bus_names(number, name)

  def add_resistor(self, name: str, r: float, bus1="", bus2=""):
    
    if name in self.components["Resistors"]:
      print("Resistor already exists. No changes to circuit")

    else:
      resistor = Component.Resistor(name, r, bus1, bus2)
      self.resistor_count += 1
      self.components["Resistors"].update({"R1":resistor})
    
    #self.print_resistors()

    #  Changes the buses a resistor component is connected to
  def change_resistor_connection(self, component_name, b1, b2):
    if component_name in self.components["Resistors"]:
      resistor = self.components["Resistors"][component_name]
      resistor.bus1 = b1
      resistor.bus2 = b2
    
    else:
      print("Resistor does not exist. No changes to circuit.")
    
    #self.print_resistors()

  def add_load(self, name: str, power: float, voltage: float, bus1: str, bus2: str):

    if name in self.components["Loads"]:
      print("Load already exists. No changes to circuit.")
    
    else:
      load = Component.Load(name, power, voltage, bus1, bus2)
      self.load_count += 1
      self.components["Loads"].update({name:load})
  
    #self.print_loads()

  def add_voltage_source(self, name: str, v: float, bus: str):
    if name in self.components["VSources"]:
      print("Name already exists. No changes to circuit")
    
    else:
      self.voltage_source_count += 1
      vsource = Component.VoltageSource(name, v, bus)
      self.components["VSources"].update({name:vsource})
      self.buses[bus].voltage = v  #  voltage source overrides bus voltage

  def calc_i(self):

    resistance = 0
    for i in self.components["Resistors"]:
      resistance += self.components["Resistors"][i].value
    
    for i in self.components["Loads"]:
      resistance += self.components["Loads"][i].resistance
    
    self.i = self.buses["bus1"].voltage/resistance
    
    print("Equivalent series resistance =", resistance, "Ω")
    print("Circuit current =", self.i, "A")
  
  def calc_nodal_voltages(self):
    self.buses["bus2"].voltage = self.i*self.components["Resistors"]["R1"].value
    
  def print_resistors(self):
    print(self.components["Resistors"], '\n')

  def print_loads(self):
    print(self.components["Loads"], '\n')

  def print_nodal_voltages(self):
    for i in self.buses:
      print(f"Bus #{self.buses[i].name}, {self.buses[i].voltage} V")
    print()

  #  checks if buses have the same name and updates the buses list accordingly
  def check_bus_names(self, number: int, name: str):
    for b in self.buses:
      if self.buses[b].number == number:
        self.buses[b].name = name
