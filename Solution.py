"""
Solution module for calculating power flow
Disclaimer: ChatGPT used for assistance

Filename: Solution.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-24
"""

from Circuit import Circuit, ThreePhaseFault, UnsymmetricalFaults
import numpy as np
import pandas as pd
from math import sin, cos


class NewtonRaphson:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.pv_indexes = self.circuit.pv_indexes.copy()
        self.pq_indexes = self.circuit.pq_indexes.copy()
        self.var_indexes = []
        self.lim_list = []
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
    
        for i in self.pv_indexes:
            x = x.drop(index=f"V{i}")
        
        return xfull, x


    def y_setup(self, q_limit=False):
        if q_limit is False:
            y = self.circuit.flat_start_y()
        else:
            y = self.circuit.flat_start_y(self.pv_indexes, self.pq_indexes)

        y_indexes = [f"P{i+1}" for i in range(self.circuit.count)]
        [y_indexes.append(f"Q{i+1}") for i in range(self.circuit.count)]
        yfull = pd.DataFrame(np.zeros(self.circuit.count*2), columns=["y"], index=y_indexes)
        yfull.update(y)

        return yfull, y


    def newton_raph(self, q_limit=False):
        self.circuit.calc_indexes() # computes all pq and pv indexes
        iter = 50
        M = self.circuit.count-1
        self.xfull, x = self.x_setup()
        yfull, y = self.y_setup()

        if q_limit:
            for var_ind in self.var_indexes:
                x.loc[f"V{var_ind}"] = 1.0

        for i in range(iter):
          # step 1
          f = self.circuit.compute_power_injection(self.xfull, self.pv_indexes, self.pq_indexes)
          deltay = y - f
          for var_ind in self.var_indexes:
              deltay.iloc[var_ind + len(self.pq_indexes) - 2, 0] = 0
          if np.max(abs(deltay)) < self.tolerance:
              yfull.update(self.calc_y(self.xfull))
              if self.var_limit(yfull):
                  self.xfull, yfull = self.newton_raph(True)
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
        if self.var_limit(yfull):
            self.xfull, yfull = self.newton_raph(True)
        return self.xfull, yfull
        

    def calc_J1_off_diag(self, M):
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        J1 = np.zeros((self.circuit.count, self.circuit.count))
        for k in self.circuit.pq_and_pv_indexes:
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
        for k in self.circuit.pq_and_pv_indexes:
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
        for k in self.circuit.pq_and_pv_indexes:
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
        for k in self.circuit.pq_and_pv_indexes:
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
        for i in self.pv_indexes:
            self.J2 = self.J2.drop(columns=i-1)


    def calc_J3_off_diag(self, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]

        for k in self.pq_indexes:
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
        for k in self.pq_indexes:
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
        for i in self.pv_indexes:
            self.J3 = self.J3.drop(index=i-1)


    def calc_J4_off_diag(self, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        d = self.xfull[self.xfull.index.str.startswith('d')]
        V = self.xfull[self.xfull.index.str.startswith('V')]
        for k in self.pq_indexes:
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
        for k in self.pq_indexes:
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
        for i in self.pv_indexes:
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


    def var_limit(self, y):
        # Relevant information for var limiting as well as initialization
        ind_len = len(self.circuit.buses)
        base = self.circuit.powerbase
        buses = [value for value in self.circuit.buses.values()]
        gens = [value for value in self.circuit.generators.values()]
        loads = [value for value in self.circuit.loads.values()]
        gen_names = []
        load_names = []

        # Data organization, find each generator and bus names (and loads)
        for value in gens:
            gen_names.append((value.name, value.bus))
        for value in loads:
            load_names.append((value.name, value.bus))

        # Iterate through and limit pv buses
        for pv in self.pv_indexes:
            pv_bus = buses[pv - 1].name
            pv_gen = ""
            pv_load = ""

            for current_gen, current_bus in gen_names:
                if current_bus == pv_bus:
                    pv_gen = current_gen

            for current_load, current_bus in load_names:
                if current_bus == pv_bus:
                    pv_load = current_load

            var_lim = self.circuit.generators[pv_gen].var_limit
            if pv_load and pv_load in self.circuit.loads:
                load_q = self.circuit.loads[pv_load].reactive or 0
            else:
                load_q = 0
            self.lim_list.append(var_lim)

            current_power = y.iloc[pv + ind_len - 1, 0] * base + load_q
            if current_power > var_lim:
                y.iloc[pv + ind_len - 1, 0] = var_lim / base
                self.pv_indexes.remove(self.circuit.buses[pv_bus].index)
                self.pq_indexes.append(self.circuit.buses[pv_bus].index)
                self.var_indexes.append(self.circuit.buses[pv_bus].index)
                return True

        num = 0
        for lim in self.var_indexes:
            var_lim = self.lim_list[num]
            y.iloc[lim + ind_len - 1, 0] = var_lim / base
            num += 1
        return False

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
        self.Bfull = self.calc_B()
        self.Pfull = self.calc_P()
        self.xfull = self.x_setup()
        self.yfull = self.y_setup()

    
    def x_setup(self):
        d = np.zeros(self.circuit.count)
        V = np.ones(self.circuit.count)
        x = np.concatenate((d, V))

        x_indexes = [f"d{i+1}" for i in range(self.circuit.count)]
        [x_indexes.append(f"V{i+1}") for i in range(self.circuit.count)]
        x = pd.DataFrame(x, index=x_indexes, columns=["x"])

        return x
    

    def y_setup(self):
        P = []
        Q = np.zeros((self.circuit.count, 1))

        for bus in self.circuit.buses:
            P.append(self.circuit.buses[bus].real_power/self.circuit.powerbase)
        
        y = np.concatenate((np.array([P]).T, Q))
        y_indexes = [f"P{i+1}" for i in range(self.circuit.count)]
        [y_indexes.append(f"Q{i+1}") for i in range(self.circuit.count)]
        y = pd.DataFrame(y, index=y_indexes, columns=["y"])

        return y


    def calc_B(self):
        B = np.imag(self.circuit.Ybus)
        return B


    def calc_P(self):
        P = []

        for bus in self.circuit.buses:
            P.append(self.circuit.buses[bus].real_power/self.circuit.powerbase)
        
        P_indexes = [f"P{i+1}" for i in range(self.circuit.count)]
        P = pd.DataFrame(P, index=P_indexes, columns=["y"])
        return P

    
    def dc_power_flow(self):
        B = np.delete(np.delete(self.Bfull, self.circuit.slack_index-1, axis=0), self.circuit.slack_index-1, axis=1)
        P = self.Pfull.drop(index=f"P{self.circuit.slack_index}")
        d = np.matmul(-np.linalg.inv(B), P.to_numpy())
        
        indexes = [f"d{i}" for i in np.sort(np.concatenate((self.circuit.pq_indexes, self.circuit.pv_indexes)))]
        d = pd.DataFrame(data=d, index=indexes, columns=["x"])
        self.xfull.update(d)

        from_bus = self.circuit.slack_index-1
        temp = pd.DataFrame(data=self.circuit.Ybus[from_bus, :]).drop(index=from_bus)
        to_bus = [i for i in temp != 0][0] + 1 # you ain't ever seen any witch craft like this. no chatgpt either, came straight from the dome.
        Pslack = np.imag(temp.sum())*(0-self.xfull.iloc[to_bus, 0])    

        self.Pfull.iloc[self.circuit.slack_index-1, 0] = Pslack
        self.yfull.update(self.Pfull)

        return self.xfull, self.yfull



class ThreePhaseFaultParameters():
    def __init__(self, symfault: ThreePhaseFault, faultbus: int, faultvoltage: float):
        self.symfault = symfault
        self.fault_bus_index = faultbus
        self.fault_voltage = faultvoltage

    
    def calc_fault_current(self):
        I_fn = self.fault_voltage/self.symfault.faultZbus[self.fault_bus_index-1, self.fault_bus_index-1]
        return I_fn


    def calc_fault_voltages(self):
        Z = self.symfault.faultZbus
        N = self.symfault.circuit.count
        n = self.fault_bus_index-1
        fault_voltages = np.zeros(N, dtype=complex)

        for k in range(N):
            Ek_first = (-Z[k][n]/Z[n][n])*self.fault_voltage
            Ek_second = self.fault_voltage
            fault_voltages[k] = Ek_first + Ek_second
        
        fault_voltages[np.abs(fault_voltages) < 1e-7] = 0

        return fault_voltages



class UnsymmetricalFaultParameters():
    def __init__(self, unsymfault: UnsymmetricalFaults, faultbus: int, faultvoltage: float, Zf=0.0):
        self.unsymfault = unsymfault
        self.faultbus = faultbus
        self.faultvoltage = faultvoltage
        self.Z0 = self.unsymfault.Z0bus
        self.Z1 = self.unsymfault.Zpbus
        self.Z2 = self.unsymfault.Znbus
        self.Zf = Zf
        self.a = -1/2 + 1j*(3**(1/2))/2
        self.A = np.array([[1, 1, 1], [1, self.a**2, self.a], [1, self.a, self.a**2]])
        self.Ainv = np.linalg.inv(self.A)


    def SLG_fault_values(self):
        n = self.faultbus-1
        N = self.unsymfault.circuit.count
        Vf = self.faultvoltage
        fault_voltages = np.zeros((N, 3), dtype=complex)
        fault_current = None
        phase_current = None

        for k in range(N):
            I = Vf/(self.Z0[k,k]+self.Z1[k,k]+self.Z2[k,k]+(3*self.Zf))
            Is = np.array([[I, I, I]], dtype=complex).T
            if k == n:
                fault_current = 3*I
                phase_current = np.matmul(self.A, Is)
                phase_current[np.abs(phase_current) < 1e-6] = 0

            V = np.array([[0, Vf, 0]]).T
            Zsn = np.zeros((3, 3), dtype=complex)
            np.fill_diagonal(Zsn, [self.Z0[k,n], self.Z1[k,n], self.Z2[k,n]])

            Vs = V-np.matmul(Zsn, Is)
            Vp = np.matmul(self.A, Vs)
            Vp[np.abs(Vp) < 1e-5] = 0
            fault_voltages[k, :] = Vp.T

        return fault_voltages, fault_current, phase_current


    def LL_fault_values(self):
        n = self.faultbus-1
        N = self.unsymfault.circuit.count
        Vf = self.faultvoltage
        fault_voltages = np.zeros((N, 3), dtype=complex)
        fault_current = None
        phase_current = None

        for k in range(N):
            I1 = Vf/(self.Z1[k,k]+self.Z2[k,k]+self.Zf)
            I2 = -I1
            Is = np.array([[0, I1, I2]], dtype=complex).T
            if k == n:
                fault_current = (self.a**(2)-self.a)*Vf/(self.Z1[k,k]+self.Z2[k,k]+self.Zf)
                phase_current = np.matmul(self.A, Is)
            
            V = np.array([[0, Vf, 0]]).T
            Zsn = np.zeros((3, 3), dtype=complex)
            np.fill_diagonal(Zsn, [0, self.Z1[k,n], self.Z2[k,n]])

            Vs = V-np.matmul(Zsn, Is)
            Vp = np.matmul(self.A, Vs)
            Vp[np.abs(Vp) < 1e-5] = 0
            fault_voltages[k, :] = Vp.T

        return fault_voltages, fault_current, phase_current



    def DLG_fault_values(self):
        n = self.faultbus-1
        N = self.unsymfault.circuit.count
        Vf = self.faultvoltage
        fault_voltages = np.zeros((N, 3), dtype=complex)
        fault_current = None
        phase_current = None

        for k in range(N):
            a = self.Z2[k,k]*(self.Z0[k,k]+3*self.Zf)
            b = self.Z2[k,k]+self.Z0[k,k]+3*self.Zf
            I1 = Vf/(self.Z1[k,k] + (a/b))
            I2 = -I1*((self.Z0[k,k] + 3*self.Zf)/b)
            I0 = -I1*(self.Z2[k,k]/b)
            Is = np.array([[I0, I1, I2]], dtype=complex).T
            if k == n:
                fault_current = 3*I0
                phase_current = np.matmul(self.A, Is)
                phase_current[np.abs(fault_current) < 1e-5] = 0

            V = np.array([[0, Vf, 0]]).T
            Zsn = np.zeros((3, 3), dtype=complex)
            np.fill_diagonal(Zsn, [self.Z0[k,n], self.Z1[k,n], self.Z2[k,n]])

            Vs = V-np.matmul(Zsn, Is)
            Vp = np.matmul(self.A, Vs)
            Vp[np.abs(Vp) < 1e-5] = 0
            fault_voltages[k, :] = Vp.T

        return fault_voltages, fault_current, phase_current

