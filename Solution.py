from Circuit import Circuit
import numpy as np
import pandas as pd
from math import sin, cos

class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.size = 2*(self.circuit.count-1)
        self.J = np.zeros((self.size, self.size))

        self.J1 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J2 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J3 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J4 = np.zeros((self.circuit.count-1, self.circuit.count-1))

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
        print("J1 = \n", self.J1)
        print()

        self.calc_J2_off_diag(Ymag, theta, x, N, M)
        self.calc_J2_on_diag(Ymag, theta, x, N, M)
        print("J2 = \n", self.J2)
        print()


    def calc_J1_off_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            for n in range(M):
                if n == k:
                    continue
                Ykn = Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                self.J1[k, n] = Vk*Ykn*Vn*sin(dk - dn - theta[k, n])
    

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
            J1kk = -Vk*sum
            self.J1[k, k] = J1kk
      

    def calc_J2_off_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            for n in range(M):
                if n == k:
                    continue
                Ykn = Ymag[k, n]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                self.J2[k, n] = Vk*Ykn*cos(dk - dn - theta[k, n])
    

    def calc_J2_on_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            sum = 0
            for n in range(N):
                Ykn = Ymag[k+1, n]
                Vn = x["V"][n]
                dk = x["d"][k+1]
                dn = x["d"][n]
                sum += Ykn*Vn*cos(dk - dn - theta[k+1, n])

            Vk = x["V"][k+1]
            Ykk = Ymag[k+1, k+1]
            J2kk = Vk*Ykk*cos(theta[k+1, k+1])+sum
            self.J2[k, k] = J2kk


    def calc_J3(self, Ymag, theta, N, x):
        pass
    
    def calc_J4(self, Ymag, theta, N, x):
        pass

    def fast_decoupled(self):
        pass

    def dc_power_flow(self, B, P):
        d = np.matmul(-np.linalg.inv(B), P)
        return d
