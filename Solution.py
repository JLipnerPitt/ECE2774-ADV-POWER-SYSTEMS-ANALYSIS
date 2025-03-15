"""
Solution module for calculating power flow
Disclaimer: ChatGPT used for assistance

Filename: Solution.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-24
"""

from Circuit import Circuit
import numpy as np
import pandas as pd
from math import sin, cos


class NewtonRaphson:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.slack_index = self.circuit.slack_index-1
        self.Ymag = np.abs(self.circuit.Ybus)
        self.theta = np.angle(self.circuit.Ybus)
        self.xfull = self.circuit.flat_start_x()

        self.J1 = None
        self.J2 = None
        self.J3 = None
        self.J4 = None


    def x_setup(self):
        d = np.zeros(self.circuit.count-1)
        V = np.ones(self.circuit.count-1-len(self.circuit.pv_indexes))
        x = np.concatenate((d, V))

        x_indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        [x_indexes.append(f"V{i}") for i in self.circuit.pq_indexes]
        x = pd.DataFrame(x, columns=["x"], index=x_indexes)
        return x
    

    def newton_raph(self):
        iter = 50
        x = self.x_setup()
        y = self.circuit.flat_start_y()
        M = self.circuit.count-1

        for i in range(iter):
          # step 1
          f = self.circuit.compute_power_injection(self.xfull)
          deltay = y - f

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
          deltax = np.linalg.solve(J, deltay.to_numpy())

          #step 4
          x = x + deltax
          self.xfull.update(x)
        
        return self.xfull


    def calc_J1_off_diag(self, M):
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        J1 = np.zeros((self.circuit.count, self.circuit.count))
        indexes = np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes))
        for k in indexes:
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k-1, 0])
                J1[k-1, n] = Vk*Ykn*Vn*sin(dk - dn - self.theta[k-1, n])
        
        J1 = np.delete(np.delete(J1, self.slack_index, axis=0), self.slack_index, axis=1)
        self.J1 = J1


    def calc_J1_on_diag(self, M):
        J1 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        indexes = np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes))
        for k in indexes:
            sum = 0
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*sin(dk - dn - self.theta[k-1, n])

            Vk = float(V.iloc[k-1, 0])
            J1kk = -Vk*sum
            J1[k-1, k-1] = J1kk
        
        J1 = np.delete(np.delete(J1, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J1, np.diag(J1))
        

    def calc_J2_off_diag(self, M):
        J2 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        indexes = np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes))
        for k in indexes:
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k-1, 0])
                J2[k-1, n] = Vk*Ykn*cos(dk - dn - self.theta[k-1, n])
        
        J2 = np.delete(np.delete(J2, self.slack_index, axis=0), self.slack_index, axis=1)
        self.J2 = J2
        

    def calc_J2_on_diag(self, M):
        J2 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        indexes = np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes))
        for k in indexes:
            sum = 0
            for n in range(M+1):
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*cos(dk - dn - self.theta[k-1, n])

            Vk = float(V.iloc[k-1, 0])
            Ykk = self.Ymag[k-1, k-1]
            J2kk = Vk*Ykk*cos(self.theta[k-1, k-1])+sum
            J2[k-1, k-1] = J2kk
        
        J2 = np.delete(np.delete(J2, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J2, np.diag(J2))
        offset = 1
        for i in self.circuit.pv_indexes:
          self.J2 = np.delete(self.J2, i-offset-1, axis=1)
          offset += 1


    def calc_J3_off_diag(self, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]

        for k in self.circuit.pq_indexes:
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k-1, 0])
                J3[k-1, n] = -Vk*Ykn*Vn*cos(dk - dn - self.theta[k-1, n])

        self.J3 = np.delete(np.delete(J3, self.slack_index, axis=0), self.slack_index, axis=1)

            
    def calc_J3_on_diag(self, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.circuit.pq_indexes:
            sum = 0
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*cos(dk - dn - self.theta[k-1, n])

            Vk = float(V.iloc[k-1, 0])
            J3kk = Vk*sum
            J3[k-1, k-1] = J3kk
        
        J3 = np.delete(np.delete(J3, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J3, np.diag(J3))
        offset = 1
        for i in self.circuit.pv_indexes:
          self.J3 = np.delete(self.J3, i-offset-1, axis=0)
          offset += 1


    def calc_J4_off_diag(self, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.circuit.pq_indexes:
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k-1, 0])
                J4[k-1, n] = Vk*Ykn*sin(dk - dn - self.theta[k-1, n])
        
        self.J4 = np.delete(np.delete(J4, self.slack_index, axis=0), self.slack_index, axis=1)


    def calc_J4_on_diag(self, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.circuit.pq_indexes:
            sum = 0
            for n in range(M+1):
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                sum += Ykn*Vn*sin(dk - dn - self.theta[k-1, n])

            Vk = float(V.iloc[k-1, 0])
            Ykk = self.Ymag[k-1, k-1]
            J4kk = -Vk*Ykk*sin(self.theta[k-1, k-1])+sum
            J4[k-1, k-1] = J4kk
        
        J4 = np.delete(np.delete(J4, self.slack_index, axis=0), self.slack_index, axis=1)
        np.fill_diagonal(self.J4, np.diag(J4))
        offset = 1
        for i in self.circuit.pv_indexes:
          self.J4 = np.delete(np.delete(self.J4, i-offset-1, axis=0), i-offset-1, axis=1)
          offset += 1


class FastDecoupled():
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.slack_index = self.circuit.slack_index-1
        self.xfull = self.circuit.flat_start_x()
        self.B = pd.DataFrame(np.imag(self.circuit.Ybus))
        self.J1 = None
        self.J4 = None


    def setup(self):
        Vfull_indexes = [f"V{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        V_indexes = [f"V{i}" for i in self.circuit.pq_indexes]
        d_indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]

        Vfull = pd.DataFrame(np.ones(self.circuit.count-1), columns=["x"], index=Vfull_indexes)
        V = pd.DataFrame(np.ones(self.circuit.count-1-len(self.circuit.pv_indexes)), columns=["x"], index=V_indexes)
        d = pd.DataFrame(np.zeros(self.circuit.count-1), columns=["x"], index=d_indexes)
        return Vfull, V, d
    

    def calc_J1(self, V):
        V = np.diag(V.to_numpy().flatten())
        B = self.B.drop(index=self.slack_index).drop(columns=self.slack_index)
        J1 = -np.matmul(V, B.to_numpy())
        self.J1 = J1
    
    
    def calc_J4(self, V):
        B = self.B.drop(index=self.slack_index).drop(columns=self.slack_index)

        for k in self.circuit.pv_indexes:
            B = B.drop(index=k-1).drop(columns=k-1)

        V = np.diag(V.to_numpy().flatten())
        self.J4 = -np.matmul(np.abs(V), B.to_numpy())


    def fast_decoupled(self):
        iter = 75
        Vfull, V, d = self.setup()
        y = self.circuit.flat_start_y()
        self.calc_J1(Vfull)
        self.calc_J4(V)
    
        for i in range(iter):
          # step 1
          f = self.circuit.compute_power_injection(self.xfull)
          deltay = y - f
          P = deltay[deltay.index.str.startswith('P')]
          Q = deltay[deltay.index.str.startswith('Q')]

          # step 2
          deltad = np.linalg.solve(self.J1, P.to_numpy())
          deltaV = np.linalg.solve(self.J4, Q.to_numpy())

          #step 3
          d = d + deltad
          V = V + deltaV
          self.xfull.update(d)
          self.xfull.update(V)
        
        return self.xfull


class DCPowerFlow():
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.B = self.calc_B()
        self.P = self.calc_P()
    

    def calc_B(self):
        B = np.imag(self.circuit.Ybus)
        B = np.delete(np.delete(B, self.circuit.slack_index-1, axis=0), self.circuit.slack_index-1, axis=1)
        B = np.round(B, -1)
        return B


    def calc_P(self):
        P = []

        for bus in self.circuit.buses:
            P.append(self.circuit.buses[bus].real_power/self.circuit.powerbase)
        
        P = np.delete(P, self.circuit.slack_index-1, axis=0)
        P_indexes = [f"P{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        
        P = pd.DataFrame(P, index=P_indexes, columns=["P"])

        return P

    
    def dc_power_flow(self):
        d = np.matmul(-np.linalg.inv(self.B), self.P)
        indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        d.index = indexes
        d.columns = ["d"]
        return d

