from Circuit import Circuit
import numpy as np
from math import sin, cos

class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit

    def newton_raph(self):
        iter = 100
        N = self.circuit.count-1
        x = self.circuit.x
        Y = np.abs(self.circuit.Ybus)
        theta = np.angle(self.circuit.Ybus)
        
        print(f"Ymag = {Y}")
        print(f"theta = {theta}")
        y = {"P":{}, "Q":{}}
        P = []
        Q = []
    
        for n in range(N+1):
            for k in range(N):
                Vk = x["V"][f"V{k+2}"]
                Ykn = np.sum(Y[n, :], axis=0)
                print(Ykn)
                Vn = x["V"][f"V{n+1}"]
                dk = x["d"][f"d{k+2}"]
                dn = x["d"][f"d{n+1}"]

                Pk = Vk*Ykn*Vn*cos(dk - dn - theta[k][n])
                Qk = Vk*Ykn*Vn*sin(dk - dn - theta[k][n])
                y["P"].update({f"P{k+2}": Pk})
                y["Q"].update({f"Q{k+2}": Qk})
        
        print(y)
        return y


    def fast_decoupled(self):
        pass

    def dc_power_flow(self):
        pass
