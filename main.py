from Circuit import Circuit

circ = Circuit("Example_7bus")

circ.change_power_base(100)

circ.add_bus("bus1", 20)
circ.add_bus("bus2", 230)
circ.add_bus("bus3", 230)
circ.add_bus("bus4", 230)
circ.add_bus("bus5", 230)
circ.add_bus("bus6", 230)
circ.add_bus("bus7", 18)

circ.add_transformer("T1", "D-Y", "bus1", "bus2", 125, 8.5, 10, 0.0018904)
circ.add_transformer("T2", "Y-D", "bus6", "bus7", 200, 10.5, 12)

circ.add_conductor("Partridge", 0.642, 0.0217, 0.385, 460)
circ.add_geometry("Geometry7bus", [0, 19.5, 39], [0, 0, 0])
circ.add_bundle("Bundle7bus", 2, 1.5, "Partridge")

circ.add_tline_from_geometry("L1", "bus2", "bus4", "Bundle7bus", "Geometry7bus", 10)
circ.add_tline_from_geometry("L2", "bus2", "bus3", "Bundle7bus", "Geometry7bus", 25)
circ.add_tline_from_geometry("L3", "bus3", "bus5", "Bundle7bus", "Geometry7bus", 20)
circ.add_tline_from_geometry("L4", "bus4", "bus6", "Bundle7bus", "Geometry7bus", 20)
circ.add_tline_from_geometry("L5", "bus5", "bus6", "Bundle7bus", "Geometry7bus", 10)
circ.add_tline_from_geometry("L6", "bus4", "bus5", "Bundle7bus", "Geometry7bus", 35)

circ.add_generator("Gen1", "bus1", 1, 0, 0.12, 0.14, 0.05, 0)
circ.add_generator("Gen2", "bus7", 1, 200, 0.12, 0.14, 0.05, 0.30864)

circ.add_load("Load1", "bus3", 110, 50)
circ.add_load("Load2", "bus4", 100, 70)
circ.add_load("Load3", "bus5", 100, 65)



