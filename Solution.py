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
        y = self.circuit.y
        N = self.circuit.count
        M = N-1

        J1 = self.calc_J1(Ymag, theta, x, N, M)

        return self.J
    
    def calc_J1(self, Ymag, theta, x, N, M):
        for k in range(M):
            J1kk = 0
            for n in range(N):
                Ykn = Ymag[k+1, n]
                Vn = x["V"][f"V{n+1}"]
                dk = x["d"][f"d{k+2}"]
                dn = x["d"][f"d{n+1}"]
                Vk = x["V"][f"V{k+2}"]

                if n == k+1:
                    J1kk += -Ykn*Vn*sin(dk - dn - theta[k+1, n])
                    continue

                self.J["J1"].update({"J1": Vk*Ykn*Vn*sin(dk - dn - theta[k+1, n])})
            print(self.J["J1"])

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
