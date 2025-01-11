import Component
import Bus

#  This class "creates" circuits.
class Circuit:

  def __init__(self, name):
    self.name = name

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

  def add_resistor(self, r):
    
    #  No resistors have been created 
    if self.resistor_count == 0:
      resistor = Component.Resistor("R1", r)
      self.resistor_count += 1
      self.resistors.append(resistor)
    
    #  Resistor list has resistors in it
    else:
      self.resistor_count += 1
      resistor = Component.Resistor(f"R{self.resistor_count}", r)
      self.resistors.append(resistor)

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
    for i in self.resistors:
      print(i.name, "=", i.resistance, "Ω")
  
  def print_buses(self):
    for i in self.buses:
      print(f"Bus #: {i.number}, Bus Name: {i.name}")
    print()

  #  checks if buses have the same name and updates the buses list accordingly
  def check_bus_names(self, number, name):
    for b in self.buses:
      if b.number == number:
        b.name = name
