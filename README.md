# IPF_multidim
Multidimensionality of IPF, project FOSSR

Data from [opensalutelazio](https://www.opensalutelazio.it/salute/stato_salute.php?stato_salute) Data concern the resident population and the cases of illness out of the residential population. So the resident population is the reference for the synthetic population

Goal: synthetic data for intersectionality disease and sociodemographic.

Algorithm in ```multidimensional_ipf.nlogo```: IPF for each dimension. For each cross-category, it reports the number of cases estimated for that category. 

Variables the testing is based on (TGT in the interface, which represent the marginals):

* Socio-demographics:
   + Gender, 2 categories (M,F)
   + Age, 3 categories (A1: 00-29, A2: 30-59, A3: 60-100): here they are clustered in these ranges, the original dataset is from 00-04 to 85-100 in steps of 5
     
* Incidence disease (chosen because of different distribution):
   + Hypertension, 2 categories (HPT, NHT): cases of no hypertension are computed taking the reference level (total cases, male population, female population and substracting the case of hypertension)
   + Heath failure, 2 categories (HF, NHF): cases of no hearth failure are computed taking the reference level (total cases, male population, female population and substracting the case of hearth failure)

* Crossed categories available in the empirical observations:
  + Hypertension * gender;  Hypertension * age; the cases no hpt are compued as above
  + Hearth failure * gender;  Hypertension * age; the cases  no hf are computed as above

Data used in TGT in the interface multidimensional_ipf.nlogo are aggregated for the entire population Lazio at the year 2022. Il dataframe ```soc_hpt_hf.csv``` in GIS/data/lazio_ASL_istat integrates the row data extracting the ASL level (DENOMINAZI), but raw data in the folder in GIS/data/lazio_ASL_istat report an individual sheet for age * gender downloaded from opensalutelazio. Function ```disease_df``` in GIS/data/datapreparation.R is to compose them.

* Objective:
  
The synthetic data elaborated concern sociodemographics (gender(2)*age(3)) that are actually in the empirical data, and the intersection of incidence disease HPT(2) and HF(2) in each intersection of socio-demographics, for which there is no empirical information that justifies the synthetic reconstruction. For instance, for the category man (M) in the first range (A1):
* M_A1_HPT_HF (with hypertension and with heart failure)
* M_A1_NHT_HF (without hypertension and with heart failure)
* M_A1_NHT_NHF (without hypertension and without heart failure)
* M_A1_HPT_NHF (with hypertension and without heart failure)
  
In the long  term, with more diseases and function run for each category, here to test
