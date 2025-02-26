from Circuit import Circuit
import numpy as np
from math import sin, cos

class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.J = {"J1":{}, "J2":{}, "J3":{}, "J4":{}}

    def newton_raph(self):
        iter = 100
        Ymag = np.abs(self.circuit.Ybus)
        theta = np.angle(self.circuit.Ybus)
        x = self.circuit.x
        N = self.circuit.count
        M = N-1

        J1 = self.calc_J1(Ymag, theta, N, x)
        J2 = self.calc_J2(Ymag, theta, N, x)
        J3 = self.calc_J3(Ymag, theta, N, x)
        J4 = self.calc_J4(Ymag, theta, N, x)

        return self.y
    
    def calc_J1(self, Ymag, theta, N, x):
        pass

    def calc_J2(self, Ymag, theta, N, x):
        pass
    
    def calc_J3(self, Ymag, theta, N, x):
        pass
    
    def calc_J4(self, Ymag, theta, N, x):
        pass

    def fast_decoupled(self):
        pass

    def dc_power_flow(self):
        pass
