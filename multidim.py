# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 09:43:48 2023

@author: rocpa
"""

import numpy as np
import pandas as pd
import matplotlib
import csv
import os

# algorithm

def ipf_update(M, u, v):
    r_sums = M.sum(axis=1) # axis 1 and shape 1 = columns. Sum on axis 1 is equal to sum of elements of the row
    N = np.array([[ M[r,c] * u[r] / r_sums[r] for c in range(M.shape[1])]
                  for r in range(M.shape[0])])

    c_sums = N.sum(axis=0) # axis 0 and shape 0 = row. Sum on axis 0 is equal to sum of elements of the columns
    O = np.array([[ N[r, c] * v[c] / c_sums[c] for c in range(N.shape[1])]
                  for r in range(N.shape[0])])

    d_u = np.linalg.norm(u - O.sum(axis=1), 2)   # l2-norm as validation measure (vectorial difference between target and fitter values)
    d_v = np.linalg.norm(v - O.sum(axis=0), 2)

    return np.round(O), d_u, d_v


# ------- 3 categories age -------

TGT0_30 =  1745215 #  array_m[51:81,2].sum() + array_f[51:81,2].sum()
TGT30_60 = 2832088
TGT60_100 = 1755721
TGTmale = 3073047 #  array_m[0:51,2].sum() + array_m[51:81,2].sum() + array_m[81:101,2].sum()
TGTfemale = 3259977 #  array_f[0:51,2].sum() + array_f[51:81,2].sum() + array_f[81:101,2].sum()


u = np.array([TGT0_30, TGT30_60,TGT60_100]) # row target (age)
v = np.array([TGTmale, TGTfemale]) # col target (gender)

X = np.array([
    [1,1],
    [1,1],
    [1,1]
])

Xdem = X.copy()
Xdem


for _ in range(500):
    Xdem, d_u, d_v = ipf_update(Xdem, u, v)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xdem

# gender HPT

TGTHPT = 1193445
TGTNOHPT = 5139579

Xgenhpt = np.array([[1,1],
                 [1,1]])

u_gen = np.array([TGTmale, TGTfemale]) # row target (gender)
v_hpt = np.array([TGTHPT, TGTNOHPT]) # col target (hpt)

for _ in range(500):
    Xgenhpt, d_u, d_v = ipf_update(Xgenhpt, u_gen, v_hpt)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xgenhpt



# gender HF

TGTHF = 93926
TGTNOHF = 6239098

Xgenhf = np.array([[1,1],
                 [1,1]])

u_gen = np.array([TGTmale, TGTfemale]) # row target (gender)
v_hf = np.array([TGTHF, TGTNOHF]) # col target (hpt)

for _ in range(500):
    Xgenhf, d_u, d_v = ipf_update(Xgenhf, u_gen, v_hf)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xgenhf


# gen age HPT
TGT0_30HPT = 3547
TGT30_60HPT = 252543
TGT60_100HPT = 937355
TGTmaleHPT = 579109
TGTfemaleHPT = 614336

u_hpt =  np.array([TGT0_30HPT,TGT30_60HPT,TGT60_100HPT]) # row hpt <=30, hpt 30-60, hpt > 60
v_hpt = np.array([TGTmaleHPT,TGTfemaleHPT]) # man wiyh hpt, fem with hpt

Xhpt = Xdem.copy()
Xhpt

for _ in range(20):
    Xhpt, d_u, d_v = ipf_update(Xhpt, u_hpt, v_hpt)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xhpt

# gen age HF
TGT0_30HF = 424
TGT30_60HF = 8459
TGT60_100HF = 85043
TGTmaleHF = 45577
TGTfemaleHF = 48349

u_hf =  np.array([TGT0_30HF,TGT30_60HF,TGT60_100HF]) # row hpt <=30, hpt 30-60, hpt > 60
v_hf = np.array([TGTmaleHF,TGTfemaleHF]) # man wiyh hpt, fem with hpt

Xhf = Xdem.copy()
Xhf

for _ in range(20):
    Xhf, d_u, d_v = ipf_update(Xhf, u_hf, v_hf)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xhf



# compute percentages

def percsample(T):
    P = np.array([[T[r,c]  / T.sum() for c in range(T.shape[1])]
                  for r in range(T.shape[0])])
    return  P

# percentage fitted
Xdemper = percsample(Xdem) 
