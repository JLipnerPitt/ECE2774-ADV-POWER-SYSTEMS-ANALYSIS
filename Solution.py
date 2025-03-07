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

        self.J1 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J2 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J3 = np.zeros((self.circuit.count-1, self.circuit.count-1))
        self.J4 = np.zeros((self.circuit.count-1, self.circuit.count-1))


    def newton_raph(self):
        iter = 100
        x = self.circuit.x
        y = self.circuit.y
        M = self.circuit.count-1

        self.calc_J1_off_diag(x, M)
        self.calc_J1_on_diag(x, M)

        self.calc_J2_off_diag(x, M)
        self.calc_J2_on_diag(x, M)

        self.calc_J3_off_diag(x, M)
        self.calc_J3_on_diag(x, M)

        self.calc_J4_off_diag(x, M)
        self.calc_J4_on_diag(x, M)

        return self.J1, self.J2, self.J3, self.J4


    def calc_J1_off_diag(self, x, M):
        Ymag = np.delete(np.delete(self.Ymag, self.slack_index, axis=0), self.slack_index, axis=1)
        theta = np.delete(np.delete(self.theta, self.slack_index, axis=0), self.slack_index, axis=1)
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
        J1 = np.zeros((self.circuit.count, self.circuit.count))
        for k in range(M+1):
            sum = 0
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                sum += Ykn*Vn*sin(dk - dn - self.theta[k, n])

            Vk = x["V"][k]
            J1kk = -Vk*sum
            J1[k, k] = J1kk
        
        J1 = np.delete(np.delete(J1, self.slack_index, axis=0), self.slack_index, axis=1)
        self.J1 = self.J1 + J1
        

    def calc_J2_off_diag(self, x, M):
        Ymag = np.delete(np.delete(self.Ymag, self.slack_index, axis=0), self.slack_index, axis=1)
        theta = np.delete(np.delete(self.theta, self.slack_index, axis=0), self.slack_index, axis=1)
        for k in range(M):
            for n in range(M):
                if n == k:
                    continue
                Ykn = Ymag[k, n]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                self.J2[k, n] = Vk*Ykn*cos(dk - dn - theta[k, n])


    def calc_J2_on_diag(self, x, M):
        J2 = np.zeros((self.circuit.count, self.circuit.count))
        for k in range(M+1):
            sum = 0
            for n in range(M+1):
                Ykn = self.Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                sum += Ykn*Vn*cos(dk - dn - self.theta[k, n])

            Vk = x["V"][k]
            Ykk = self.Ymag[k, k]
            J2kk = Vk*Ykk*cos(self.theta[k, k])+sum
            J2[k, k] = J2kk
        
        J2 = np.delete(np.delete(J2, self.slack_index, axis=0), self.slack_index, axis=1)
        self.J2 = self.J2 + J2


    def calc_J3_off_diag(self, x, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J3[k, :] = 0
                continue
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                J3[k, n] = -Vk*Ykn*Vn*cos(dk - dn - self.theta[k, n])

        self.J3 = np.delete(np.delete(J3, self.slack_index, axis=0), self.slack_index, axis=1)

            
    def calc_J3_on_diag(self, x, M):
        J3 = np.zeros((self.circuit.count, self.circuit.count))
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J3[k, k] = 0
                continue
            sum = 0
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                sum += Ykn*Vn*cos(dk - dn - self.theta[k, n])

            Vk = x["V"][k]
            J3kk = Vk*sum
            J3[k, k] = J3kk
        
        J3 = np.delete(np.delete(J3, self.slack_index, axis=0), self.slack_index, axis=1)
        self.J3 = self.J3 + J3


    def calc_J4_off_diag(self, x, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J4[k, :] = 0
                continue
            for n in range(M+1):
                if n == k:
                    continue
                Ykn = self.Ymag[k, n]
                dk = x["d"][k]
                dn = x["d"][n]
                Vk = x["V"][k]
                J4[k, n] = Vk*Ykn*sin(dk - dn - self.theta[k, n])
        
        self.J4 = np.delete(np.delete(J4, self.slack_index, axis=0), self.slack_index, axis=1)


    def calc_J4_on_diag(self, x, M):
        J4 = np.zeros((self.circuit.count, self.circuit.count))
        for k in range(M+1):
            if k+1 in self.circuit.pv_indexes:
                J4[k, k] = 1
                continue
            sum = 0
            for n in range(M+1):
                Ykn = self.Ymag[k, n]
                Vn = x["V"][n]
                dk = x["d"][k]
                dn = x["d"][n]
                sum += Ykn*Vn*sin(dk - dn - self.theta[k, n])

            Vk = x["V"][k]
            Ykk = self.Ymag[k, k]
            J4kk = -Vk*Ykk*sin(self.theta[k, k])+sum
            J4[k, k] = J4kk
        
        J4 = np.delete(np.delete(J4, self.slack_index, axis=0), self.slack_index, axis=1)
        self.J4 = self.J4 + J4


    def fast_decoupled(self):
        pass


    def dc_power_flow(self, B, P):
        d = np.matmul(-np.linalg.inv(B), P)
        return d

