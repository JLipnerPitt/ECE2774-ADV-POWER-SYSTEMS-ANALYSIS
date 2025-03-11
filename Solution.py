"""
Solution module for calculating power flow
Disclaimer: ChatGPT used for assistance

Filename: Solution.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-24
"""

from Circuit import Circuit
import os
import numpy as np
import pandas as pd
from math import sin, cos


class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.size = 2*(self.circuit.count-1)
        self.slack_index = self.circuit.slack_index-1
        self.J = np.zeros((self.size, self.size))
        self.Ymag = np.abs(self.circuit.Ybus)
        self.theta = np.angle(self.circuit.Ybus)
        self.xfull = self.circuit.x

        self.J1 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J2 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J3 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J4 = np.zeros((self.circuit.count-1, self.circuit.count-1))


    def x_setup(self):
        d = np.zeros(self.circuit.count-1)
        V = np.ones(self.circuit.count-1-len(self.circuit.pv_indexes))
        x = np.concatenate((d, V))

        indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        [indexes.append(f"V{i}") for i in self.circuit.pq_indexes]
        x = pd.DataFrame(x, columns=["x"], index=indexes)
        return x
    

    def newton_raph(self):
        iter = 5
        x = self.x_setup()
        y = self.circuit.compute_power_mismatch(self.xfull)
        M = self.circuit.count-1

        for i in range(iter):
          # step 1
          f = self.circuit.compute_power_injection(self.xfull)
          deltay = y - f
          print("Step1: y - deltay =")
          print(deltay.T)
          print()

          #step 2
          self.calc_J1_off_diag(M)
          self.calc_J1_on_diag(M)

          self.calc_J2_off_diag(M)
          self.calc_J2_on_diag(M)

          self.calc_J3_off_diag(M)
          self.calc_J3_on_diag(M)

          self.calc_J4_off_diag(M)
          self.calc_J4_on_diag(M)

          # step 3
          J = np.block([[self.J1, self.J2], [self.J3, self.J4]])
          for n in self.circuit.pv_indexes:
              J = np.delete(J, self.size-n, axis=1)
              J = np.delete(J, self.size-n, axis=0)
          print(f"J{i} =\n", J, '\n')
          indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
          [indexes.append(f"V{i}") for i in self.circuit.pq_indexes]
          deltax = np.matmul(np.linalg.inv(J), deltay)
          deltax.index = indexes
          deltax.columns = ["x"]

          #step 4
          print(f"x({i}) =")
          x = x + deltax
          print(x.T)
          self.xfull.update(x)
          
        return J, x


    def calc_J1_off_diag(self, M):
        Ymag = np.delete(np.delete(self.Ymag, self.slack_index, axis=0), self.slack_index, axis=1)
        theta = np.delete(np.delete(self.theta, self.slack_index, axis=0), self.slack_index, axis=1)
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]

        for k in range(M):
            for n in range(M):
                if n == k:
                    continue
                Ykn = Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k, 0])
                self.J1[k, n] = Vk*Ykn*Vn*sin(dk - dn - theta[k, n])


    def calc_J1_on_diag(self, M):
        J1 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M+1):
            sum = 0
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*sin(dk - dn - self.theta[k, n])

            Vk = float(V.iloc[k, 0])
            J1kk = -Vk*sum
            J1[k, k] = J1kk
        
        J1 = np.delete(np.delete(J1, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J1, np.diag(J1))
        

    def calc_J2_off_diag(self, M):
        Ymag = np.delete(np.delete(self.Ymag, self.slack_index, axis=0), self.slack_index, axis=1)
        theta = np.delete(np.delete(self.theta, self.slack_index, axis=0), self.slack_index, axis=1)
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M):
            for n in range(M):
                if n == k:
                    continue
                Ykn = Ymag[k, n]
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k, 0])
                self.J2[k, n] = Vk*Ykn*cos(dk - dn - theta[k, n])


    def calc_J2_on_diag(self, M):
        J2 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M+1):
            sum = 0
            for n in range(M+1):
                Ykn = self.Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*cos(dk - dn - self.theta[k, n])

            Vk = float(V.iloc[k, 0])
            Ykk = self.Ymag[k, k]
            J2kk = Vk*Ykk*cos(self.theta[k, k])+sum
            J2[k, k] = J2kk
        
        J2 = np.delete(np.delete(J2, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J2, np.diag(J2))


    def calc_J3_off_diag(self, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J3[k, :] = 0
                continue
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k, 0])
                J3[k, n] = -Vk*Ykn*Vn*cos(dk - dn - self.theta[k, n])

        self.J3 = np.delete(np.delete(J3, self.slack_index, axis=0), self.slack_index, axis=1)

            
    def calc_J3_on_diag(self, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J3[k, k] = 0
                continue
            sum = 0
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*cos(dk - dn - self.theta[k, n])

            Vk = float(V.iloc[k, 0])
            J3kk = Vk*sum
            J3[k, k] = J3kk
        
        J3 = np.delete(np.delete(J3, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J3, np.diag(J3))


    def calc_J4_off_diag(self, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J4[k, :] = 0
                continue
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k, 0])
                J4[k, n] = Vk*Ykn*sin(dk - dn - self.theta[k, n])
        
        self.J4 = np.delete(np.delete(J4, self.slack_index, axis=0), self.slack_index, axis=1)


    def calc_J4_on_diag(self, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J4[k, k] = 1
                continue
            sum = 0
            for n in range(M+1):
                Ykn = self.Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*sin(dk - dn - self.theta[k, n])

            Vk = float(V.iloc[k, 0])
            Ykk = self.Ymag[k, k]
            J4kk = -Vk*Ykk*sin(self.theta[k, k])+sum
            J4[k, k] = J4kk
        
        J4 = np.delete(np.delete(J4, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J4, np.diag(J4))


    def fast_decoupled(self):
        pass


    def dc_power_flow(self, B, P):
        d = np.matmul(-np.linalg.inv(B), P)
        return 

