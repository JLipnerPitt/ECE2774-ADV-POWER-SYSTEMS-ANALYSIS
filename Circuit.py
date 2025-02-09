from Component import Component
from Bus import Bus
from TransmissionLine import TransmissionLine
from Bundle import Bundle
from Geometry import Geometry
from Transformer import Transformer
from Conductor import Conductor

#  This class "creates" circuits.
class Circuit:

    def __init__(self, name: str):

        self.name = name
        self.i = float

        self.table = ["Resistors", "Loads", "VSources", "Transformers", "T-Lines"]  # Table of all possible components

        #  Dict that stores all information for each component type
        #  Each component key has a dictonary that stores all components of that type
        self.components = {comp: {} for comp in self.table}

        self.buses = {}
        self.conductors = {}
        self.bundles = {}
        self.geometries = {}


    #  Adds buses to circuit.
    def add_bus(self, name: str, voltage: float):
      bus = Bus(name, voltage)
      self.buses.update({name:bus})
      #self.check_bus_names(name)


    def add_resistor(self, name: str, r: float, bus1="", bus2=""):

        if name in self.components["Resistors"]:
            print("Resistor already exists. No changes to circuit")

        else:
            resistor = Component.Resistor(name, r, bus1, bus2)
            self.components["Resistors"].update({"R1": resistor})

        # self.print_resistors()


    def add_load(self, name: str, power: float, voltage: float, bus: str):

        if name in self.components["Loads"]:
            print("Load already exists. No changes to circuit.")

        else:
            load = Component.Load(name, power, voltage, bus)
            self.components["Loads"].update({name: load})


    def add_voltage_source(self, name: str, v: float, bus: str):
        if name in self.components["VSources"]:
            print("Name already exists. No changes to circuit")

        else:
            vsource = Component.VoltageSource(name, v, bus)
            self.components["VSources"].update({name: vsource})
            self.buses[bus].voltage = v  # voltage source overrides bus voltage
    

    def add_tline(self, name: str, bus1: str, bus2: str, bundle: Bundle, geometry: Geometry, length: float):
        tline = TransmissionLine(name, bus1, bus2, bundle, geometry, length)
        self.components["T-Lines"].update({name: tline})

    
    def add_transformer(self, name: str, bus1: str, bus2: str, power_rating: float,
                 impedance_percent: float, x_over_r_ratio: float):
        transformer = Transformer(name, bus1, bus2, power_rating, impedance_percent, x_over_r_ratio)
        self.components["Transformers"].update({name: transformer})
    

    def add_conductor(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        conductor = Conductor(name, diam, GMR, resistance, ampacity)
        self.conductors.update({name: conductor})


    def add_bundle(self, name: str, num_conductors: int, spacing: float, conductor: Conductor,
                 v=765.e3):
        bundle = Bundle(name, num_conductors, spacing, conductor)
        self.bundles.update({name: bundle})

    
    def add_geometry(self, name: str, x: list[float], y: list[float]):
      geometry = Geometry(name, x, y)
      self.geometries.update({name: geometry})    


    #  checks if buses have the same name and updates the buses list accordingly
    '''
    def check_bus_names(self, index: int, name: str):
      for b in self.buses:
        if self.buses[b].index == index:
          self.buses[b].name = name
          '''

# validation tests
if __name__ == '__main__':
  from Circuit import Circuit
  circuit1 = Circuit("Test Circuit")
  print(circuit1.name) # Expected output: "Test Circuit"
  print(type(circuit1.name))
  print(circuit1.buses)
  print(type(circuit1.buses)) 

  circuit1.add_bus("Bus1", 230)
  print(type(circuit1.buses["Bus1"]))
  print(circuit1.buses["Bus1"].name, circuit1.buses["Bus1"].base_kv)
  print("Buses in circuit:", list(circuit1.buses.keys()))

def SevenPowerBusSystem():
  circuit1 = Circuit("Seven Power Bus System")