import Component
import Bus

#  This class "creates" circuits.
class Circuit:

  def __init__(self, name):

    self.name = name

    self.table = ["Resistors", "Capacitors", "Inductors", "Loads", "VSources", "CSources"] #  Table of all possible components

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
  def add_bus(self, name, number, voltage, angle=0):
    self.bus_count += 1
    bus = Bus.Bus(number, name, voltage, angle)
    self.buses.update({name:bus})
    self.check_bus_names(number, name)

  def add_resistor(self, name, r, bus1=None, bus2=None):
    
    if name in self.components["Resistors"]:
      print("Resistor already exists. No changes to circuit")

    else:
      resistor = Component.Resistor(name, r, bus1, bus2)
      self.resistor_count += 1
      self.components["Resistors"].update({"R1":resistor})
    
    self.print_resistors()

    #  Changes the buses a resistor component is connected to
  def change_resistor_connection(self, component_name, b1, b2):
    if component_name in self.components["Resistors"]:
      resistor = self.components["Resistors"][component_name]
      resistor.bus1 = b1
      resistor.bus2 = b2
    
    else:
      print("Resistor does not exist. No changes to circuit.")
    
    self.print_resistors()

  def add_capacitor(self, c):

    #  No capacitors have been created 
    if self.capacitor_count == 0:
      capacitor = Component.Capacitor("C1", c)
      self.capacitor_count += 1
      self.capacitors.append(capacitor)
    
    #  Capacitor list has capacitors in it
    else:
      self.capacitor_count += 1
      capacitor = Component.Capacitor(f"C{self.capacitor_count}", c)
      self.capacitors.append(capacitor)

  def add_inductor(self, l):

    #  No inductors have been created 
    if self.inductor_count == 0:
      inductor = Component.Capacitor("L1", l)
      self.inductor_count += 1
      self.inductors.append(inductor)
    
    #  Inductor list has inductors in it
    else:
      self.inductor_count += 1
      inductor = Component.Inductor(f"L{self.inductor_count}", l)
      self.inductors.append(inductor)

  def add_load(self, name, power, resistance, bus1, bus2):

    if name in self.components["Loads"]:
      print("Load already exists. No changes to circuit.")
    
    else:
      load = Component.Load(name, power, resistance, bus1, bus2)
      self.load_count += 1
      self.components["Loads"].update({name:load})
  
    self.print_loads()
    

  def add_voltage_source(self, name, v, bus):
    if name in self.components["VSources"]:
      print("Name already exists. No changes to circuit")
    
    else:
      self.voltage_source_count += 1
      vsource = Component.VoltageSource(name, v, bus)
      self.components["VSources"].update({name:vsource})
      self.buses[bus].voltage = v  #  voltage source overrides bus voltage
      

  def add_current_source(self, a):
    #  No voltage sources have been created 
    if self.current_source_count == 0:
      csource = Component.VoltageSource("I1", a)
      self.current_source_count += 1
      self.components["CSources"].update({"I1":csource})
    
    #  Voltage source list has sources in it
    else:
      self.current_source_count += 1
      csource = Component.CurrentSource(f"I{self.current_source_count}", a)
      self.components["CSources"].update({f"I{self.current_source_count}":csource})

  def print_resistors(self):
    print(self.components["Resistors"], '\n')

  def print_loads(self):
    print(self.components["Loads"], '\n')

  def print_buses(self):
    for i in self.buses:
      print(f"Bus #: {self.buses[i].number}, Bus Name: {self.buses[i].name}", '\n')

  #  checks if buses have the same name and updates the buses list accordingly
  def check_bus_names(self, number, name):
    for b in self.buses:
      if self.buses[b].number == number:
        self.buses[b].name = name
