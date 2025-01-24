import Conductor

class Bundle:

  def __init__(self, name: str, num_conductors: int, spacing: float, conductor: Conductor):
    self.name = name
    self.num_conductors = num_conductors
    self.spacing = spacing
    self.conductor = conductor