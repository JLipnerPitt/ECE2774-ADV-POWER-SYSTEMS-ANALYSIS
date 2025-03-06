"""
Module to implement bus functionality

Filename: Bus.py
Author: Justin Lipner
Date: 2025-01-23
"""


class Bus:
    """
    Bus class to hold bus information
    """

    def __init__(self, name: str, base_kv: float, index: int):
        """
        Bus object constructor
        :param name: Name of bus
        :param base_kv: Rated bus voltage
        """
        self.name = name
        self.base_kv = base_kv
        self.index = index
        self.v = 1
        self.angle = 0
        self.real_power = 0
        self.reactive_power = 0
        self.type = "PQ"
    

    def set_bus_v(self, v: float):
        self.v = v
    

    def set_angle(self, d: float):
        self.angle = d


    def set_type(self, type: str):
        self.type = type


# validation tests
if __name__ == '__main__':
    from Bus import Bus
    bus1 = Bus("Bus 1", 20, 1)
    bus2 = Bus("Bus 2", 230, 2)
    print(bus1.name, bus1.base_kv, bus1.index)
    print(bus2.name, bus2.base_kv, bus2.index)

    bus1.set_bus_v(500)
    print(bus1.base_kv)
