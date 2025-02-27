from Circuit import Circuit
import numpy as np
import pandas as pd
from math import sin, cos

class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.size = 2*(self.circuit.count-1)
        self.J = np.zeros((self.size, self.size))

    def newton_raph(self):
        iter = 100
        Ymag = np.abs(self.circuit.Ybus)
        theta = np.angle(self.circuit.Ybus)
        
        x = self.circuit.x
        y = self.circuit.y
        N = self.circuit.count
        M = N-1

        self.calc_J1_off_diag(Ymag, theta, x, N, M)
        self.calc_J1_on_diag(Ymag, theta, x, N, M)
    
    def calc_J1_off_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            for n in range(N):
                if n == k+1:
                    continue
                Ykn = Ymag[k+1, n]
                Vn = x["V"][n]
                dk = x["d"][k+1]
                dn = x["d"][n]
                Vk = x["V"][k+1]
                self.J[k+1, n] = Vk*Ykn*Vn*sin(dk - dn - theta[k+1, n])
                print(self.J, '\n')
        print(self.J, '\n')
    
    def calc_J1_on_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            sum = 0
            for n in range(N):
                if n == k+1:
                    continue
                Ykn = Ymag[k+1, n]
                Vn = x["V"][n]
                dk = x["d"][k+1]
                dn = x["d"][n]
                sum += Ykn*Vn*sin(dk - dn - theta[k+1, n])
            Vk = x["V"][k+1]
            Jkk = -Vk*sum
            self.J[k+1, k+1] = Jkk
        print(self.J, '\n')
      

    def calc_J2(self, Ymag, theta, x, N, M):
        for k in range(M):
            J2kk = 0
            for n in range(N):
                Ykn = Ymag[k+1, n]
                dk = x["d"][k+1]
                dn = x["d"][n]
                Vk = x["V"][k+1]

                if n == k+1:
                    Vn = x["V"][n+1]
                    J2kk += -Ykn*Vn*sin(dk - dn - theta[k+1, n])
                    continue

                self.J["J2"].update({"J2": Vk*Ykn*cos(dk - dn - theta[k+1, n])})
            print(self.J["J2"])
    
    def calc_J3(self, Ymag, theta, N, x):
        pass
    
    def calc_J4(self, Ymag, theta, N, x):
        pass

    def fast_decoupled(self):
        pass

    def dc_power_flow(self):
        pass
