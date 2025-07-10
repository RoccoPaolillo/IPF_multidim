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


# ------- sociodem: 3 categories age gender -------

# emprirical target
TGT0_30 =  1745215   
TGT30_60 = 2832088
TGT60_100 = 1755721
TGTmale = 3073047   
TGTfemale = 3259977  


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

# test joint probability

round((TGTmale / (TGTmale + TGTfemale)) * TGT0_30)
round((TGTmale / (TGTmale + TGTfemale)) * TGT30_60)
round((TGTmale / (TGTmale + TGTfemale)) * TGT60_100)
round((TGTfemale / (TGTmale + TGTfemale)) * TGT0_30)
round((TGTfemale / (TGTmale + TGTfemale)) * TGT30_60)
round((TGTfemale / (TGTmale + TGTfemale)) * TGT60_100)

# ---- disease incidence ----
# gender HPT

TGTHPT = 1193445 # empirical target
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

# test joint probability

round((TGTmale / (TGTmale + TGTfemale)) * TGTHPT)
round((TGTmale / (TGTmale + TGTfemale)) * TGTNOHPT)
round((TGTfemale / (TGTmale + TGTfemale)) * TGTHPT)
round((TGTfemale / (TGTmale + TGTfemale)) * TGTNOHPT)


# gender HF

TGTHF = 93926 # empirical target
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

# test joint probability

round((TGTmale / (TGTmale + TGTfemale)) * TGTHF)
round((TGTmale / (TGTmale + TGTfemale)) * TGTNOHF)
round((TGTfemale / (TGTmale + TGTfemale)) * TGTHF)
round((TGTfemale / (TGTmale + TGTfemale)) * TGTNOHF)



# gen age HPT 
TGT0_30HPT = 3547   # empirical target
TGT30_60HPT = 252543  # empirical target
TGT60_100HPT = 937355  # empirical target
TGTmaleHPT = 579109 # synthetic target
TGTfemaleHPT = 614336 # synthetic target

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

# test joint probability

round( (TGTmaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT0_30HPT)
round( (TGTmaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT30_60HPT)
round( (TGTmaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT60_100HPT)
round( (TGTfemaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT0_30HPT)
round( (TGTfemaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT30_60HPT)
round( (TGTfemaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT60_100HPT)


# gen age HF
TGT0_30HF = 424  # empirical target
TGT30_60HF = 8459  # empirical target
TGT60_100HF = 85043  # empirical target
TGTmaleHF = 45577 # synthetic target
TGTfemaleHF = 48349 # synthetic target

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

round( (TGTmaleHF / (TGTmaleHF + TGTfemaleHF)) * TGT0_30HF)
round( (TGTmaleHF / (TGTmaleHF + TGTfemaleHF)) * TGT30_60HF)
round( (TGTmaleHF / (TGTmaleHF + TGTfemaleHF)) * TGT60_100HF)
round( (TGTfemaleHF / (TGTmaleHF + TGTfemaleHF)) * TGT0_30HF)
round( (TGTfemaleHF / (TGTmaleHF + TGTfemaleHF)) * TGT30_60HF)
round( (TGTfemaleHF / (TGTmaleHF + TGTfemaleHF)) * TGT60_100HF)

# age X HPT

TGT0_30 =  1745215   
TGT30_60 = 2832088
TGT60_100 = 1755721
TGTHPT = 1193445 # empirical target
TGTNOHPT = 5139579

u_age =  np.array([TGT0_30,TGT30_60,TGT60_100]) # row hpt <=30, hpt 30-60, hpt > 60
v_hpt = np.array([TGTHPT,TGTNOHPT]) # column hpt, no hpt

X = np.array([
    [1,1],
    [1,1],
    [1,1]
])

Xhptage = X.copy()
Xhptage

for _ in range(20):
    Xhptage, d_u, d_v = ipf_update(Xhptage, u_age, v_hpt)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xhptage

# age X HF


TGT0_30 =  1745215   
TGT30_60 = 2832088
TGT60_100 = 1755721
TGTHF = 93926 # empirical target
TGTNOHF = 6239098

u_age =  np.array([TGT0_30,TGT30_60,TGT60_100]) # row hpt <=30, hpt 30-60, hpt > 60
v_hf = np.array([TGTHF,TGTNOHF]) # # column hf, no hf

X = np.array([
    [1,1],
    [1,1],
    [1,1]
])

Xhfage = X.copy()
Xhfage

for _ in range(20):
    Xhfage, d_u, d_v = ipf_update(Xhfage, u_age, v_hf)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xhfage


# compute percentages

def percsample(T):
    P = np.array([[T[r,c]  / T.sum() for c in range(T.shape[1])]
                  for r in range(T.shape[0])])
    return  P

# percentage fitted
Xdemper = percsample(Xdem) 


