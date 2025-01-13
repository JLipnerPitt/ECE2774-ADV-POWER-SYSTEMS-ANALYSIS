import Component
import Bus

#  This class "creates" circuits.
class Circuit:

  def __init__(self, name):

    self.name = name

    self.table = ["Resistors", "Capacitors", "Inductors"] #  Table of all possible components

    #  Dict that stores all information for each component type
    #  Each component key has a dictonary that stores all components of that type
    self.components = {comp:{} for comp in self.table}
    
    self.bus_count = 0
    self.resistor_count = 0
    self.capacitor_count = 0
    self.inductor_count = 0
    self.load_count = 0
    self.voltage_source_count = 0
    self.current_source_count = 0

    self.bus_order = []
    self.buses = []
    self.resistors = []
    self.capacitors = []
    self.inductors = []
    self.voltage_sources = []
    self.current_sources = []

  #  Adds buses to circuit.
  def add_bus(self, number, name, voltage, angle):  
    self.bus_count += 1
    bus = Bus.Bus(number, name, voltage, angle)
    self.buses.append(bus)
    self.check_bus_names(number, name)

  #  Changes the buses a component is connected to
  def change_resistor_connection(self, component_name, bus1, bus2):
    if component_name in self.components["Resistors"]:
      self.components["Resistors"][component_name][1] = bus1
      self.components["Resistors"][component_name][2] = bus2

    else:
      print("Resistor does not exist. No changes to circuit.")
    
    self.print_resistors()

  def add_resistor(self, r, bus1=None, bus2=None):
    
    #  No resistors have been created 
    if self.resistor_count == 0:
      info = []
      resistor = Component.Resistor("R1", r)
      self.resistor_count += 1
      self.resistors.append(resistor)
      self.bus1 = bus1
      self.bus2 = bus2

      #  The following 4 lines of code append the information associated with a resistor to the info list
      #  and updates the resistor with the chosen name in the components dictionary
      info.append(r)
      info.append(bus1)
      info.append(bus2)
      self.components["Resistors"].update({"R1":info})
    
    #  Resistor list has resistors in it
    else:
      info = []
      self.resistor_count += 1
      resistor = Component.Resistor(f"R{self.resistor_count}", r)
      self.resistors.append(resistor)
      self.bus1 = bus1
      self.bus2 = bus2
      info.append(r)
      info.append(bus1)
      info.append(bus2)
      self.components["Resistors"].update({f"R{self.resistor_count}":info})
    
    self.print_resistors()

  def get_resistor(self):
    pass

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

  def add_load(self, ld):
    pass

  def add_voltage_source(self, v):
    #  No voltage sources have been created 
    if self.voltage_source_count == 0:
      vsource = Component.VoltageSource("V1", v)
      self.voltage_source_count += 1
      self.voltage_sources.append(vsource)
    
    #  Voltage source list has sources in it
    else:
      self.voltage_source_count += 1
      vsource = Component.VoltageSource(f"V{self.voltage_source_count}", v)
      self.voltage_sources.append(vsource)

  def add_current_source(self, a):
    #  No voltage sources have been created 
    if self.current_source_count == 0:
      csource = Component.VoltageSource("I1", a)
      self.current_source_count += 1
      self.current_sources.append(csource)
    
    #  Voltage source list has sources in it
    else:
      self.current_source_count += 1
      csource = Component.CurrentSource(f"I{self.current_source_count}", a)
      self.voltage_sources.append(csource)

  def print_resistors(self):
    print(self.components["Resistors"], '\n')
  
  def print_buses(self):
    for i in self.buses:
      print(f"Bus #: {i.number}, Bus Name: {i.name}", '\n')

  #  checks if buses have the same name and updates the buses list accordingly
  def check_bus_names(self, number, name):
    for b in self.buses:
      if b.number == number:
        b.name = name
