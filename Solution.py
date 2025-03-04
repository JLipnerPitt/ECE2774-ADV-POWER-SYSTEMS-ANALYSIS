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

        self.calc_J3_off_diag(Ymag, theta, x, N, M)
        self.calc_J3_on_diag(Ymag, theta, x, N, M)
        print("J3 = \n", self.J3)
        print()

        self.calc_J4_off_diag(Ymag, theta, x, N, M)
        self.calc_J4_on_diag(Ymag, theta, x, N, M)
        print("J4 = \n", self.J4)
        print()


    def calc_J1_off_diag(self, Ymag, theta, x, N, M):
        for k in range(M):
            for n in range(M):
                if k == n:
                    continue
                Ykn = Ymag[k+1, n+1]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                self.J1[k, n] = Vk*Ykn*Vn*sin(dk - dn - theta[k+1, n+1])


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

    def read_jacobian(self):
        M = self.circuit.count - 1
        jacobian = []

        csv_J1 = np.zeros((M, M), dtype=float)
        csv_J2 = np.zeros((M, M), dtype=float)
        csv_J3 = np.zeros((M, M), dtype=float)
        csv_J4 = np.zeros((M, M), dtype=float)

        main_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(main_dir, r"Excel_Files\fivepowerbusystem_flatstart_jacobian_matrix.csv")

        df = pd.read_csv(file_path, header=None, skiprows=3, dtype=str)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        start_row = 0
        start_col = 4
        shift = M + 1

        for idx, (i, j) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
            row_idx = start_row + i * shift
            col_idx = start_col + j * shift
            matrix = df.iloc[row_idx:row_idx + M, col_idx:col_idx + M].to_numpy(dtype=float)

            if idx == 0:
                csv_J1 = matrix
            elif idx == 1:
                csv_J2 = matrix
            elif idx == 2:
                csv_J3 = matrix
            else:
                csv_J4 = matrix

            jacobian.append(matrix)

        # For debugging purposes
        display_jacobian(jacobian)

        return jacobian, csv_J1, csv_J2, csv_J3, csv_J4


def display_jacobian(jacobian):
    for i, j in enumerate(jacobian, 1):
        print(f"csv_J{i} =\n", j, "\n")

