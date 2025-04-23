"""
Module to implement bus functionality

Filename: Bus.py
Author: Justin Lipner
Date: 2025-01-23
"""


class Bus:

    def __init__(self, name: str, base_kv: float, index: int):
        self.name = name
        self.base_kv = base_kv*1e3
        self.index = index
        self.Vpu = 1 # per unit voltage
        self.V = base_kv # actual voltage.
        self.angle = 0.0
        self.real_power = 0.0
        self.reactive_power = 0.0
        self.type = "PQ" # bus type
    

    def set_bus_v(self, v: float):
        self.Vpu = v
        self.V = self.base_kv*v
    

    def set_angle(self, a: float):
        self.angle = a


    def set_type(self, t: str):
        self.type = t
    

    def update_power(self, real: float, reactive: float):
        self.real_power += real
        self.reactive_power += reactive


# validation tests
if __name__ == '__main__':
    from Bus import Bus
    bus1 = Bus("Bus 1", 20, 1)
    bus2 = Bus("Bus 2", 230, 2)
    print(bus1.name, bus1.base_kv, bus1.index)
    print(bus2.name, bus2.base_kv, bus2.index)

    bus1.set_bus_v(500)
    print(bus1.base_kv)
