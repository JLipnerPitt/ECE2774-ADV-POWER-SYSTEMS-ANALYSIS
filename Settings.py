
class Settings:

  def __init__(self, powerbase=100, freq=60):
    self.freq = freq
    self.powerbase = powerbase
  
  def set_freq(self, f):
    self.freq = f
  
  def set_powerbase(self, p):
    self.powerbase = p