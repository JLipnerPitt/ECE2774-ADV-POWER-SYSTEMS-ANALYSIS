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
        self.tolerance = 0.001
        self.xfull = None
        self.J1 = None
        self.J2 = None
        self.J3 = None
        self.J4 = None


    def set_tolerance(self, tol: float):
        self.tolerance = tol


    def x_setup(self):
        d = np.zeros(self.circuit.count)
        V = np.ones(self.circuit.count)
        xfull = np.concatenate((d, V))

        x_indexes = [f"d{i+1}" for i in range(self.circuit.count)]
        [x_indexes.append(f"V{i+1}") for i in range(self.circuit.count)]
        xfull = pd.DataFrame(xfull, index=x_indexes, columns=["x"])

        x = xfull.drop(index=f"d{self.slack_index+1}").drop(
                       index=f"V{self.slack_index+1}")
    
        for i in self.circuit.pv_indexes:
            x = x.drop(index=f"V{i}")
        
        return xfull, x


    def y_setup(self):
        y = self.circuit.flat_start_y()

        y_indexes = [f"P{i+1}" for i in range(self.circuit.count)]
        [y_indexes.append(f"Q{i+1}") for i in range(self.circuit.count)]
        yfull = pd.DataFrame(np.zeros(self.circuit.count*2), columns=["y"], index=y_indexes)
        yfull.update(y)

        return yfull, y


    def newton_raph(self):
        self.circuit.calc_indexes() # computes all pq and pv indexes
        iter = 50
        M = self.circuit.count-1
        self.xfull, x = self.x_setup()
        yfull, y = self.y_setup()

        for i in range(iter):
          # step 1
          f = self.circuit.compute_power_injection(self.xfull)
          deltay = y - f
          if np.max(abs(deltay)) < self.tolerance:
              yfull.update(self.calc_y(self.xfull))
              return self.xfull, yfull

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
          J = np.block([[self.J1.to_numpy(), self.J2.to_numpy()], [self.J3.to_numpy(), self.J4.to_numpy()]])
          deltax = np.linalg.solve(J, deltay.to_numpy())

          #step 4
          x = x + deltax
          self.xfull.update(x)
        
        yfull.update(self.calc_y(self.xfull))
        return self.xfull, yfull
        

    def calc_J1_off_diag(self, M):
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        J1 = np.zeros((self.circuit.count, self.circuit.count))
        for k in self.circuit.indexes:
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k-1, 0])
                J1[k-1, n] = Vk*Ykn*Vn*sin(dk - dn - self.theta[k-1, n])
        
        J1 = pd.DataFrame(J1)
        self.J1 = J1


    def calc_J1_on_diag(self, M):
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.circuit.indexes:
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
            self.J1.iloc[k-1, k-1] = J1kk
        
        self.J1 = self.J1.drop(index=self.slack_index).drop(columns=self.slack_index)
        

    def calc_J2_off_diag(self, M):
        J2 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.circuit.indexes:
            for n in range(M+1):
                if n+1 == k:
                    continue
                Ykn = self.Ymag[k-1, n]
                dk = float(d.iloc[k-1, 0])
                dn = float(d.iloc[n, 0])
                Vk = float(V.iloc[k-1, 0])
                J2[k-1, n] = Vk*Ykn*cos(dk - dn - self.theta[k-1, n])
        
        J2 = pd.DataFrame(J2)
        self.J2 = J2
        

    def calc_J2_on_diag(self, M):
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.circuit.indexes:
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
            self.J2.iloc[k-1, k-1] = J2kk
        
        self.J2 = self.J2.drop(index=self.slack_index).drop(columns=self.slack_index)
        for i in self.circuit.pv_indexes:
            self.J2 = self.J2.drop(columns=i-1)


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

        J3 = pd.DataFrame(J3)
        self.J3 = J3

            
    def calc_J3_on_diag(self, M):
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
            self.J3.iloc[k-1, k-1] = J3kk
        
        self.J3 = self.J3.drop(index=self.slack_index).drop(columns=self.slack_index)
        for i in self.circuit.pv_indexes:
            self.J3 = self.J3.drop(index=i-1)


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
        
        J4 = pd.DataFrame(J4)
        self.J4 = J4


    def calc_J4_on_diag(self, M):
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
            self.J4.iloc[k-1, k-1] = J4kk
        
        self.J4 = self.J4.drop(index=self.slack_index).drop(columns=self.slack_index)
        for i in self.circuit.pv_indexes:
            self.J4 = self.J4.drop(index=i-1).drop(columns=i-1)


    def calc_y(self, xfull):
        N = self.circuit.count
        d = xfull[xfull.index.str.startswith('d')]
        V = xfull[xfull.index.str.startswith('V')]
        y = np.zeros(N*2)
        indexes = np.zeros(N*2, dtype=object)
        for k in range(N):
            sum1 = 0
            sum2 = 0
            indexes[k] = f"P{k+1}"
            indexes[k+N] = f"Q{k+1}"
            for n in range(N):
                Ykn = self.Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                sum1 += Ykn*Vn*cos(dk - dn - self.theta[k, n])
                sum2 += Ykn*Vn*sin(dk - dn - self.theta[k, n])
            
            Vk = float(V.iloc[k, 0])
            Pk = Vk*sum1
            y[k] = Pk
            Qk = Vk*sum2
            y[k+N] = Qk

        y[np.abs(y) < 1e-3] = 0
        y = pd.DataFrame(y, index=indexes, columns=["y"])
        return y


class FastDecoupled():
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.slack_index = self.circuit.slack_index-1
        self.B = pd.DataFrame(np.imag(self.circuit.Ybus))
        self.tolerance = 0.001
        self.xfull = None
        self.yfull = None
        self.J1 = None
        self.J4 = None


    def set_tolerance(self, tol: float):
        self.tolerance = tol


    def setup(self):
        Vfull_indexes = [f"V{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        V_indexes = [f"V{i}" for i in self.circuit.pq_indexes]
        d_indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]

        Vfull = pd.DataFrame(np.ones(self.circuit.count-1), columns=["x"], index=Vfull_indexes)
        V = pd.DataFrame(np.ones(self.circuit.count-1-len(self.circuit.pv_indexes)), columns=["x"], index=V_indexes)
        d = pd.DataFrame(np.zeros(self.circuit.count-1), columns=["x"], index=d_indexes)
        
        y_indexes = [f"P{i+1}" for i in range(self.circuit.count)]
        [y_indexes.append(f"Q{i+1}") for i in range(self.circuit.count)]
        y = pd.DataFrame(np.zeros(self.circuit.count*2), columns=["y"], index=y_indexes)

        x_indexes = [f"d{i+1}" for i in range(self.circuit.count)]
        [x_indexes.append(f"V{i+1}") for i in range(self.circuit.count)]
        xfull = np.concatenate((np.zeros(self.circuit.count), 
                                np.ones(self.circuit.count)))
        xfull = pd.DataFrame(xfull, index=x_indexes, columns=["x"])

        return Vfull, V, d, y, xfull


    def fast_decoupled(self):
        iter = 75
        Vfull, V, d, self.yfull, self.xfull = self.setup()
        y = self.circuit.flat_start_y()
        self.calc_J1(Vfull)
        self.calc_J4(V)

        for i in range(iter):
          # step 1
          f = self.circuit.compute_power_injection(self.xfull)
          deltay = y - f
          if np.max(np.abs(deltay)) < self.tolerance:
              self.yfull.update(self.calc_y(self.xfull))
              return self.xfull, self.yfull
          
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
        
        self.yfull.update(self.calc_y(self.xfull))
        return self.xfull, self.yfull
    

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

        
    def calc_y(self, xfull):
        N = self.circuit.count
        d = xfull[xfull.index.str.startswith('d')]
        V = xfull[xfull.index.str.startswith('V')]
        y = np.zeros(N*2)
        indexes = np.zeros(N*2, dtype=object)
        Ymag = np.abs(self.circuit.Ybus)
        theta = np.angle(self.circuit.Ybus)
        for k in range(N):
            sum1 = 0
            sum2 = 0
            indexes[k] = f"P{k+1}"
            indexes[k+N] = f"Q{k+1}"
            for n in range(N):
                Ykn = Ymag[k, n]
                Vn = float(V.iloc[n, 0])
                dk = float(d.iloc[k, 0])
                dn = float(d.iloc[n, 0])
                sum1 += Ykn*Vn*cos(dk - dn - theta[k, n])
                sum2 += Ykn*Vn*sin(dk - dn - theta[k, n])
            
            Vk = float(V.iloc[k, 0])
            Pk = Vk*sum1
            y[k] = Pk
            Qk = Vk*sum2
            y[k+N] = Qk

        y[np.abs(y) < 1e-3] = 0
        y = pd.DataFrame(y, index=indexes, columns=["y"])
        return y
    

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

