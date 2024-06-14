# IPF_multidim
Multidimensionality of IPF, project FOSSR
Data from [opensalutelazio](https://www.opensalutelazio.it/salute/stato_salute.php?stato_salute) Data concern the resident population and the cases of illness out of the residential population. So the resident population is the reference for the synthetic population
Goal: synthetic data for intersectionality disease and sociodemographic.

Variables the testing is based on:
* Socio-demographics:
   + Gender (M,F)
   + Age (00-29,30-59,85-100): here they are clustered in this ranges, the original dataset is from 00-04 to 85-100 in steps of 5
Incidence disease:
  * Hypertension (HPT, NOHPT): cases of no hypertension are computed taking the reference level (total cases, male population, female population and substracting the case of hypertension)
  * Heath failure (HF, NOHF): cases of no hearth failure are computed taking the reference level (total cases, male population, female population and substracting the case of hearth failure)

* Crossed categories available in the empirical observations
