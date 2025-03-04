"""
Solution module for calculating power flow

Filename: Solution.py
Author: Justin Lipner, Bailey Stout
Date: 2025-02-24
"""

from Circuit import Circuit
import numpy as np
import pandas as pd
from math import sin, cos


class Solution:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.size = 2*(self.circuit.count-1)
        self.J = np.zeros((self.size, self.size))
        self.Ymag = np.abs(self.circuit.Ybus)
        self.theta = np.angle(self.circuit.Ybus)

        self.J1 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J2 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J3 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J4 = np.zeros((self.circuit.count-1, self.circuit.count-1))


    def newton_raph(self):
        iter = 100
        x = self.circuit.x
        y = self.circuit.y
        M = self.circuit.count-1
        i = self.circuit.buses[self.circuit.slack].index-1

        self.Ymag = np.delete(np.delete(self.Ymag, i, axis=0), i, axis=1)
        self.theta = np.delete(np.delete(self.theta, i, axis=0), i, axis=1)

        self.calc_J1_off_diag(x, M)
        self.calc_J1_on_diag(x, M)
        print("J1 = \n", self.J1)
        print()

        self.calc_J2_off_diag(Ymag, theta, x, M)
        self.calc_J2_on_diag(Ymag, theta, x, M)
        print("J2 = \n", self.J2)
        print()

        self.calc_J3_off_diag(Ymag, theta, x, N, M)
        self.calc_J3_on_diag(Ymag, theta, x, N, M)
        print("J3 = \n", self.J3)
        print()

        self.calc_J4_off_diag(Ymag, theta, x, N, M)
        self.calc_J4_on_diag(Ymag, theta, x, N, M)
        print("J4 = \n", self.J4)
        print()


    def calc_J1_off_diag(self, x, M):
        Ymag = self.Ymag
        theta = self.theta
        print(Ymag)
        print(theta)
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


    def calc_J1_on_diag(self, x, M):
        Ymag = self.Ymag
        theta = self.theta
        for k in range(M):
            sum = 0
            for n in range(M):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                sum += Ykn*Vn*sin(dk - dn - self.theta[k, n])

            Vk = x["V"][k+1]
            J1kk = -Vk*sum
            self.J1[k, k] = J1kk


    def calc_J2_off_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            for n in range(M):
                if n == k:
                    continue
                Ykn = Ymag[k+1, n+1]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                self.J2[k, n] = Vk*Ykn*cos(dk - dn - theta[k+1, n+1])


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


    def calc_J3_off_diag(self, Ymag, theta, x, N, M):
        for k in self.circuit.pq_indexes:
            for n in range(M):
                if k-2 == n:
                    continue
                Ykn = Ymag[k-1, n+1]
                Vn = x["V"][n]
                dk = x["d"][k-2]
                dn = x["d"][n]
                Vk = x["V"][k-2]
                self.J3[k-2, n] = -Vk*Ykn*Vn*cos(dk - dn - theta[k-1, n+1])


    def calc_J3_on_diag(self, Ymag, theta, x, N, M):
        for k in self.circuit.pq_indexes:
            sum = 0
            for n in range(N):
                if n == k-1:
                    continue
                Ykn = Ymag[k-1, n]
                Vn = x["V"][n]
                dk = x["d"][k-1]
                dn = x["d"][n]
                sum += Ykn*Vn*cos(dk - dn - theta[k-1, n])

            Vk = x["V"][k-1]
            J3kk = Vk*sum
            self.J3[k-2, k-2] = J3kk


    def calc_J4_off_diag(self, Ymag, theta, x, N, M):
        for k in self.circuit.pq_indexes:
            for n in range(M):
                if n == k-2:
                    continue
                Ykn = Ymag[k-1, n+1]
                dk = x["d"][k-2]
                dn = x["d"][n]
                Vk = x["V"][k-2]
                self.J4[k-2, n] = Vk * Ykn * sin(dk - dn - theta[k-1, n+1])


    def calc_J4_on_diag(self, Ymag, theta, x, N, M):
        for k in self.circuit.pq_indexes:
            sum = 0
            for n in range(N):
                Ykn = Ymag[k-1, n]
                Vn = x["V"][n]
                dk = x["d"][k-1]
                dn = x["d"][n]
                sum += Ykn * Vn * sin(dk - dn - theta[k-1, n])

            Vk = x["V"][k-1]
            Ykk = Ymag[k-1, k-1]
            J4kk = -1 * Vk * Ykk * sin(theta[k-1, k-1]) + sum
            self.J4[k-2, k-2] = J4kk
        
        for k in self.circuit.pv_indexes:
            self.J4[k-2, k-2] = 1


    def fast_decoupled(self):
        pass


    def dc_power_flow(self, B, P):
        d = np.matmul(-np.linalg.inv(B), P)
        return d
