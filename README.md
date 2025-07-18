# IPF_multidim
Multidimensionality of IPF, project FOSSR

Data from [opensalutelazio](https://www.opensalutelazio.it/salute/stato_salute.php?stato_salute) Data concern the resident population and the cases of illness out of the residential population. So the resident population is the reference for the synthetic population

Goal: synthetic data for intersectionality disease and sociodemographic.

Algorithm in ```multidim.py``` to implement multiple iterative proportional fitting

* Socio-demographics:
   + Gender, 2 categories (M,F)
   + Age, 3 categories (A1: 00-29, A2: 30-59, A3: 60-100): here they are clustered in these ranges, the original dataset is from 00-04 to 85-100 in steps of 5
     
* Incidence disease (chosen because of different distribution):
   + Hypertension, 2 categories (HPT, NHT): cases of no hypertension are computed taking the reference level (total cases, male population, female population and substracting the case of hypertension)
   + Heath failure, 2 categories (HF, NHF): cases of no hearth failure are computed taking the reference level (total cases, male population, female population and substracting the case of hearth failure)

Reproducing joint categories age (age30,age3060,age60100) * gender (male, female) * hpt (hptyes, hptno) * hf (hfyes, hfno)
