#  This class creates buses (nodes). Each bus has a name, voltage level, and index.

class Bus:
  index = 0
  def __init__(self, name: str, base_kv: float):
    self.name = name
    self.base_kv = base_kv
    Bus.index += 1
    self.index = Bus.index
