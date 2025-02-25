from Circuit import Circuit
import numpy as np
from math import sin, cos

class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.y = {"P":{}, "Q":{}}
        self.J = {"J1":{}, "J2":{}, "J3":{}, "J4":{}}

    def newton_raph(self):
        iter = 100
        N = self.circuit.count-1
        x = self.circuit.x
        Ymag = np.abs(self.circuit.Ybus)
        theta = np.angle(self.circuit.Ybus)
        
        print("Ymag = ")
        print(Ymag)
        print("theta = ")
        print(theta)
        print()
    
        for n in range(N+1):
            for k in range(N):
                Vk = x["V"][f"V{k+2}"]
                Ykn = np.sum(Ymag[n, :], axis=0)
                Vn = x["V"][f"V{n+1}"]
                dk = x["d"][f"d{k+2}"]
                dn = x["d"][f"d{n+1}"]

                Pk = Vk*Ykn*Vn*cos(dk - dn - theta[k][n])
                Qk = Vk*Ykn*Vn*sin(dk - dn - theta[k][n])
                self.y["P"].update({f"P{k+2}": Pk})
                self.y["Q"].update({f"Q{k+2}": Qk})
        
        print("y = ")
        print(self.y)

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
