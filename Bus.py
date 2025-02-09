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
    index = 0

    def __init__(self, name: str, base_kv: float):
        """
        Bus object constructor
        :param name: Name of bus
        :param base_kv: Rated bus voltage
        """
        self.name = name
        self.base_kv = base_kv

        # Unique bus index for each created object
        Bus.index += 1
        self.index = Bus.index
    
    def set_bus_v(self, v: float):
        self.base_kv = v


# validation tests
if __name__ == '__main__':
    from Bus import Bus
    bus1 = Bus("Bus 1", 20)
    bus2 = Bus("Bus 2", 230)
    print(bus1.name, bus1.base_kv, bus1.index)
    print(bus2.name, bus2.base_kv, bus2.index)
    print("Bus count =", Bus.index)

    bus1.set_bus_v(500)
    print(bus1.base_kv)
