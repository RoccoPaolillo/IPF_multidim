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

###### EMPIRICAL AND SYNTHETIC TARGET TO REPRODUCE ######

# emprirical target
total = 6333024
TGT0_30 =  1745215   
TGT30_60 = 2832088
TGT60_100 = 1755721
TGTmale = 3073047   
TGTfemale = 3259977  
TGTHPT = 1193445 # empirical target
TGTNOHPT = 5139579
TGTHF = 93926 # empirical target
TGTNOHF = 6239098
TGT0_30HPT = 3547   # empirical target
TGT30_60HPT = 252543  # empirical target
TGT60_100HPT = 937355  # empirical target
TGT0_30HF = 424  # empirical target
TGT30_60HF = 8459  # empirical target
TGT60_100HF = 85043  # empirical target

#### empirical computed by difference

TGT0_30NOHPT =  1741668
TGT30_60NOHPT =	2579545
TGT60_100NOHPT = 818366
TGT0_30NOHF = 1744791
TGT30_60NOHF = 2823629
TGT60_100NOHF = 1670678

####
TGTmaleHPT = 579109 # synthetic target
TGTfemaleHPT = 614336 # synthetic target
TGTmaleHF = 45577 # synthetic target
TGTfemaleHF = 48349 # synthetic target

# ------- sociodem: 3 categories age gender -------

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

round((TGTmale / total) * TGT0_30)
round((TGTmale / total) * TGT30_60)
round((TGTmale / total) * TGT60_100)
round((TGTfemale / total) * TGT0_30)
round((TGTfemale / total) * TGT30_60)
round((TGTfemale / total) * TGT60_100)

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

round((TGTmale / total) * TGTHPT)
round((TGTmale / total) * TGTNOHPT)
round((TGTfemale / total) * TGTHPT)
round((TGTfemale / total) * TGTNOHPT)


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

round((TGTmale / total) * TGTHF)
round((TGTmale / total) * TGTNOHF)
round((TGTfemale / total) * TGTHF)
round((TGTfemale / total) * TGTNOHF)



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

# test probability form

round( (TGTmaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT0_30HPT)
round( (TGTmaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT30_60HPT)
round( (TGTmaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT60_100HPT)
round( (TGTfemaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT0_30HPT)
round( (TGTfemaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT30_60HPT)
round( (TGTfemaleHPT / (TGTmaleHPT + TGTfemaleHPT)) * TGT60_100HPT)

# conditional probability known joint probability
round((TGT0_30HPT / TGT0_30) * ((TGTmale / total) * TGT0_30)) 
round((TGT30_60HPT / TGT30_60) * ((TGTmale / total) * TGT30_60)) 
round((TGT60_100HPT / TGT60_100) * ((TGTmale / total) * TGT60_100)) 
round((TGT0_30HPT / TGT0_30) * ((TGTfemale / total) * TGT0_30)) 
round((TGT30_60HPT / TGT30_60) * ((TGTfemale / total) * TGT30_60)) 
round((TGT60_100HPT / TGT60_100) * ((TGTfemale / total) * TGT60_100)) 

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

# conditional probability known joint probability

round((TGT0_30HF / TGT0_30) * ((TGTmale / total) * TGT0_30)) 
round((TGT30_60HF / TGT30_60) * ((TGTmale / total) * TGT30_60)) 
round((TGT60_100HF / TGT60_100) * ((TGTmale / total) * TGT60_100)) 
round((TGT0_30HF / TGT0_30) * ((TGTfemale / total) * TGT0_30)) 
round((TGT30_60HF / TGT30_60) * ((TGTfemale / total) * TGT30_60)) 
round((TGT60_100HF / TGT60_100) * ((TGTfemale / total) * TGT60_100)) 


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

# joint probability

round((TGTHPT / total) * TGT0_30) 
round((TGTHPT / total) * TGT30_60) 
round((TGTHPT / total) * TGT60_100) 
round((TGTNOHPT / total) * TGT0_30) 
round((TGTNOHPT / total) * TGT30_60) 
round((TGTNOHPT / total) * TGT60_100) 


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

# test probability
round((TGTHF / total) * TGT0_30) 
round((TGTHF / total) * TGT30_60) 
round((TGTHF / total) * TGT60_100) 
round((TGTNOHF / total) * TGT0_30) 
round((TGTNOHF / total) * TGT30_60) 
round((TGTNOHF / total) * TGT60_100) 


# gender X HPT

TGTmale = 3073047   
TGTfemale = 3259977 
TGTHPT = 1193445 # empirical target
TGTNOHPT = 5139579   


u = np.array([TGTmale, TGTfemale]) # row target (gender)
v = np.array([TGTHPT, TGTNOHPT]) # col target (hpt)

X = np.array([
    [1,1],
    [1,1]
])

Xhptgen = X.copy()
Xhptgen


for _ in range(500):
    Xhptgen, d_u, d_v = ipf_update(Xhptgen, u, v)
    print(f'd_u = {d_u:.5f}, d_v = {d_v:.5f}')
    if d_u <= 0.00001 and d_v <= 0.00001:          # algorithm stops if the distance below threshold
        break

Xhptgen

# test probability
round(( TGTHPT / total) *  TGTmale) 
round((TGTHPT / total) *  TGTfemale) 
round((TGTNOHPT / total) *  TGTmale) 
round((TGTNOHPT / total) *  TGTfemale) 

###### TEST multidimensional probability ######
 

# multiple dimensions probabilities for individual dimension

# first level synthetic, joint 2 genderXage; total,age,gender empirical
male30 = round((TGTmale / total) * TGT0_30)
male60 = round((TGTmale / total) * TGT30_60)
male100 = round((TGTmale / total) * TGT60_100)
female30 = round((TGTfemale / total) * TGT0_30)
female60 =  round((TGTfemale / total) * TGT30_60)
female100 = round((TGTfemale / total) * TGT60_100)
        # first level synthetic, joint genderXhpt
maleHPT = round((TGTmale / total) * TGTHPT)
femaleHPT =  round((TGTfemale / total) * TGTHPT)
maleHF =   round((TGTmale / total) * TGTHF)
femaleHF = round((TGTfemale / total) * TGTHF)
        
        # second level synthetic, joint 3 genderXhptXage -> ageXhpt from empirical data; genderXhpt synthetic
maleHPT30 =  round((maleHPT / TGTHPT) *  TGT0_30HPT)
maleHPT60 = round((maleHPT / TGTHPT) *  TGT30_60HPT)
maleHPT100 =  round((maleHPT / TGTHPT) *  TGT60_100HPT)
femaleHPT30 = round((femaleHPT / (TGTHPT)) *  TGT0_30HPT)
femaleHPT60 =  round((femaleHPT / (TGTHPT)) *  TGT30_60HPT)
femaleHPT100 =   round((femaleHPT / (TGTHPT)) *  TGT60_100HPT)
        
        # second level synthetic, joint 3 genderXhfXage -> ageXhf from empirical data; genderXhf synthetic
maleHF30 =   round((maleHF / TGTHF) * TGT0_30HF) 
maleHF60 =  round((maleHF / TGTHF) * TGT30_60HF)
maleHF100 =    round((maleHF / TGTHF) * TGT60_100HF)
femaleHF30 =   round((femaleHF / (TGTHF)) * TGT0_30HF)
femaleHF60 =  round((femaleHF / (TGTHF)) * TGT30_60HF)
femaleHF100 =  round((femaleHF / (TGTHF)) * TGT60_100HF)

        # third level synthetic, joint 4 genderXhfXageXhpt -> male30 synth I level; maleHPT30 synth II livello; maleHF30 synth II livello
male_HF_HPT_30 = round( total * ((male30 / total) * ((maleHPT30 / male30) * (maleHF30 / male30))) ) # 0
male_HF_HPT_60 = round( total * ((male60 / total) * ((maleHPT60 / male60) * (maleHF60 / male60))) ) # 366
male_HF_HPT_100 = round( total * ((male100 / total) * ((maleHPT100 / male100) * (maleHF100 / male100))) ) # 22032
female_HF_HPT_30 = round( total * ((female30 / total) * ((femaleHPT30 / female30) * (femaleHF30 / female30))) ) # 0 
female_HF_HPT_60 = round( total * ((female60 / total) * ((femaleHPT60 / female60) * (femaleHF60 / female60))) ) # 388
female_HF_HPT_100 = round( total * ((female100 / total) * ((femaleHPT100 / female100) * (femaleHF100 / female100))) ) # 23371
        

# conditional probabilities known joint probabilities

maleHF_HPT_30_2cr = round(((TGTmale / total) * TGT0_30) * ((TGT0_30HPT / TGT0_30) * (TGT0_30HF / TGT0_30)) ) #  0
round(total * ((TGTmale / total) * (TGT0_30 / total) * ((TGT0_30HPT / TGT0_30) * (TGT0_30HF / TGT0_30)) ))
maleHF_HPT_60_2cr = round(((TGTmale / total) * TGT30_60) * ((TGT30_60HPT / TGT30_60) * (TGT30_60HF / TGT30_60)) ) # 366
round(total * ((TGTmale / total) * (TGT30_60 / total) * ((TGT30_60HPT / TGT30_60) * (TGT30_60HF / TGT30_60)) )) # 366
maleHF_HPT_100_2cr = round(((TGTmale / total) * TGT60_100) * ((TGT60_100HPT / TGT60_100) * (TGT60_100HF / TGT60_100))) # 22032
round( total * ((TGTmale / total) * (TGT60_100 / total) * ((TGT60_100HPT / TGT60_100) * (TGT60_100HF / TGT60_100))))
femaleHF_HPT_30_2cr = round(((TGTfemale / total) * TGT0_30) * ((TGT0_30HPT / TGT0_30) * (TGT0_30HF / TGT0_30)) ) #  0
round(total * ((TGTfemale / total) * (TGT0_30 / total) * ((TGT0_30HPT / TGT0_30) * (TGT0_30HF / TGT0_30)) )) #  0
femaleHF_HPT_60_2cr = round(((TGTfemale / total) * TGT30_60) * ((TGT30_60HPT / TGT30_60) * (TGT30_60HF / TGT30_60)) ) # 388
round(total * ((TGTfemale / total) * (TGT30_60 / total) * ((TGT30_60HPT / TGT30_60) * (TGT30_60HF / TGT30_60)) )) # 388
femaleHF_HPT_100_2cr = round(((TGTfemale / total) * TGT60_100) * ((TGT60_100HPT / TGT60_100) * (TGT60_100HF / TGT60_100))) # 23372
round(total * ((TGTfemale / total) * (TGT60_100 / total) * ((TGT60_100HPT / TGT60_100) * (TGT60_100HF / TGT60_100)))) # 23372

maleHF_NHPT_30 = round(((TGTmale / total) * TGT0_30) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30HF / TGT0_30)) ) # 205
round(total * ((TGTmale / total) * (TGT0_30 / total) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30HF / TGT0_30)) )) # 205
maleHF_NHPT_60 = round(((TGTmale / (total) * TGT30_60) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60HF / TGT30_60)) )) # 3739 
round(total * ((TGTmale / total) * (TGT30_60 / total) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60HF / TGT30_60)) )) # 3739
maleHF_NHPT_100 = round(((TGTmale / total) * TGT60_100) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100HF / TGT60_100))) # 19235
round(total * ((TGTmale / total) * (TGT60_100 / total) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100HF / TGT60_100)))) # 19235
femaleHF_NHPT_30 = round(((TGTfemale / total) * TGT0_30) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30HF / TGT0_30)) ) #  218
round(total * ((TGTfemale / total) * (TGT0_30 / total) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30HF / TGT0_30)) )) #  218
femaleHF_NHPT_60 = round(((TGTfemale / total) * TGT30_60) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60HF / TGT30_60)) ) # 3966
round(total * ((TGTfemale / total) * (TGT30_60 / total) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60HF / TGT30_60)) )) # 3966
femaleHF_NHPT_100 = round(((TGTfemale / total) * TGT60_100) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100HF / TGT60_100))) # 20405
round(total * ((TGTfemale / total) * (TGT60_100 / total) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100HF / TGT60_100)))) # 20405

maleNHF_HPT_30 = round(((TGTmale / total) * TGT0_30) * ((TGT0_30HPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) ) #  1721
round(total * ((TGTmale / total) * (TGT0_30 / total) * ((TGT0_30HPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) )) #  1721
maleNHF_HPT_60 = round(((TGTmale / total) * TGT30_60) * ((TGT30_60HPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) ) # 122178
round(total * ((TGTmale / total) * TGT30_60 / total) * ((TGT30_60HPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) ) # 122178
maleNHF_HPT_100 = round(((TGTmale / total) * TGT60_100) * ((TGT60_100HPT / TGT60_100) * (TGT60_100NOHF / TGT60_100))) # 432812
round(total * ((TGTmale / total) * (TGT60_100 / total) * ((TGT60_100HPT / TGT60_100) * (TGT60_100NOHF / TGT60_100)))) # 432812
femaleNHF_HPT_30 = round(((TGTfemale / total) * TGT0_30) * ((TGT0_30HPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) ) # 1825
round(total * ((TGTfemale / total) * (TGT0_30 / total) * ((TGT0_30HPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) )) # 1825
femaleNHF_HPT_60 = round(((TGTfemale / total) * TGT30_60) * ((TGT30_60HPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) ) # 129610
round(total * ((TGTfemale / total) * (TGT30_60 / total) * ((TGT30_60HPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) )) # 129610
femaleNHF_HPT_100 = round(((TGTfemale / total) * TGT60_100) * ((TGT60_100HPT / TGT60_100) * (TGT60_100NOHF / TGT60_100))) # 459140
round(total * ((TGTfemale / total) * (TGT60_100 / total) * ((TGT60_100HPT / TGT60_100) * (TGT60_100NOHF / TGT60_100)))) # 459140

maleNHF_NHPT_30 = round(((TGTmale / total) * TGT0_30) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) ) #  844925
round(total * ((TGTmale / total) * (TGT0_30 / total) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) )) #  844925
maleNHF_NHPT_60 = round(((TGTmale / total) * TGT30_60) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) ) # 1247964
round(total * ((TGTmale / total) * (TGT30_60 / total) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) )) # 1247964
maleNHF_NHPT_100 = round(((TGTmale / total) * TGT60_100) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100NOHF / TGT60_100))) # 377870
round(total * ((TGTmale / total) * (TGT60_100 / total) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100NOHF / TGT60_100)))) # 377870
femaleNHF_NHPT_30 = round(((TGTfemale / total) * TGT0_30) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) ) # 896320
round(total * ((TGTfemale / total) * (TGT0_30 / total) * ((TGT0_30NOHPT / TGT0_30) * (TGT0_30NOHF / TGT0_30)) ) )# 896320
femaleNHF_NHPT_60 = round(((TGTfemale / total) * TGT30_60) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) ) # 1323876
round(total * ((TGTfemale / total) * (TGT30_60 / total) * ((TGT30_60NOHPT / TGT30_60) * (TGT30_60NOHF / TGT30_60)) )) # 1323876
femaleNHF_NHPT_100 = round(((TGTfemale / total) * TGT60_100) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100NOHF / TGT60_100))) # 400856
round(total * ((TGTfemale / total) * (TGT60_100 / total) * ((TGT60_100NOHPT / TGT60_100) * (TGT60_100NOHF / TGT60_100)))) # 400856


# if joint probabilities are not known
maleHF_HPT_30_2 = round(total * ((TGTmale / total) * (TGTHF / total) * (TGTHPT  / total) * (TGT0_30 / total))) # 2367
maleHF_HPT_60_2 = round(total * ((TGTmale / total) * (TGTHF / total) * (TGTHPT  / total) * (TGT30_60 / total))) # 3841
maleHF_HPT_100_2 = round(total * ((TGTmale / total) * (TGTHF / total) * (TGTHPT  / total) * (TGT60_100 / total)))  # 2381
femaleHF_HPT_30_2 = round(total * ((TGTfemale / total) * (TGTHF / total) * (TGTHPT  / total) * (TGT0_30 / total))) # 2367
femaleHF_HPT_60_2 = round(total * ((TGTfemale / total) * (TGTHF / total) * (TGTHPT  / total) * (TGT30_60 / total))) # 3841
femaleHF_HPT_100_2 = round(total * ((TGTfemale / total) * (TGTHF / total) * (TGTHPT  / total) * (TGT60_100 / total)))  # 2381





