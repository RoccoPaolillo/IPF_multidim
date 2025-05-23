library(tidyr)
library(purrr)
library(dplyr)
library(stringr)

# data preparation ###########

setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/sociodem_asl")
file.list = list.files( pattern = "*.csv")

theData_list<-lapply(file.list, read.csv2)
df <-bind_rows(theData_list)
names(df) <- c("classi_eta","ita_f","ita_m","stran_f","stran_m","DENOMINAZI")
df$fem <- df$ita_f + df$stran_f 
df$man <- df$ita_m + df$stran_m 
df$mar_ageASL <- df$fem + df$man  # marginal of age for that ASL, since each row is a age class per ASL(DENOMINAZI)
mar_manASL <- df %>% group_by(DENOMINAZI) %>% summarize(mar_manASL = sum(man)) # marginal male population per ASL
mar_femASL <- df %>% group_by(DENOMINAZI) %>% summarize(mar_femASL = sum(fem)) # marginal female population per ASL
dftotgentomerge <- merge(mar_femASL,mar_manASL, by = c("DENOMINAZI")) # total population
df <- merge(df,dftotgentomerge,by = c("DENOMINAZI")) # adds the marginal total population to the sociodemographic df per ASL
df$tot_genASL <- df$mar_femASL + df$mar_manASL # reports the marginal total gender (total population) per ASL

dftot_age <- df %>% group_by(DENOMINAZI) %>% summarize(tot_ageASL = sum(mar_ageASL))
df <- merge(df,dftot_age,by = c("DENOMINAZI"))

write.csv(df,file="C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/df_socdem.csv",row.names = FALSE)



setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")


disease_df <- function(folder,disease){

file.list = list.files(paste0(folder,"/"),  pattern = "*.csv")

results = list()
for (i in file.list) {
 df <- read.csv(paste0(folder,"/",i),sep=";",skip = 9)[1:10,]
 df[df == "(*)"] <- 0
 df$gender <- paste0(disease,"_",unlist(strsplit(i,"-"))[1])
 df$classi_eta <- unlist(strsplit(i,"-"))[2]
 names(df)[1] = "DENOMINAZI"
 names(df)[2] = disease
 results[[i]] = df
}
df <- bind_rows(results)


#d[d$disease == "(*)",]$disease <- 0
# df[df == "(*)"] <- 0
df <- tidyr::spread(df, key = gender, value = disease)
df[,3] <- as.numeric(df[,3])
df[,4] <- as.numeric(df[,4])
df[df$DENOMINAZI == "ASL Roma 1",]$DENOMINAZI <- "ROMA 1"
df[df$DENOMINAZI == "ASL Roma 2",]$DENOMINAZI <- "ROMA 2"
df[df$DENOMINAZI == "ASL Roma 3",]$DENOMINAZI <- "ROMA 3"
df[df$DENOMINAZI == "ASL Roma 4",]$DENOMINAZI <- "ROMA 4"
df[df$DENOMINAZI == "ASL Roma 5",]$DENOMINAZI <- "ROMA 5"
df[df$DENOMINAZI == "ASL Roma 6",]$DENOMINAZI <- "ROMA 6"
df[df$DENOMINAZI == "ASL Frosinone",]$DENOMINAZI <- "FROSINONE"
df[df$DENOMINAZI == "ASL Latina",]$DENOMINAZI <- "LATINA"
df[df$DENOMINAZI == "ASL Rieti",]$DENOMINAZI <- "RIETI"
df[df$DENOMINAZI == "ASL Viterbo",]$DENOMINAZI <- "VITERBO"

write.csv(df,file=paste0(disease,".csv"),row.names = F)
df
}

df <- disease_df("hearth_failure","hf")

# merging datasets 

setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")

df <- read.csv("df_socdem.csv",sep=",")
df$classi_eta <- str_replace_all(df$classi_eta,"-","_")
df$classi_eta <- str_replace_all(df$classi_eta,"\"","")
hf <- read.csv("hf.csv",sep=",") # hf heart failure
hpt <- read.csv("hpt.csv",sep=",") # hpt hypertension
# hf$classi_eta <- paste0("\"",hf$classi_eta,"\"")

df <- reduce(list(df,hf,hpt), full_join, by= c('DENOMINAZI',"classi_eta"))

df$tot_hpt <- df$hpt_fem + df$hpt_male  # total population hpt
df$tot_nohpt <- df$mar_ageASL - df$tot_hpt # compute who has not hpt at marginal level: population for ageXASL minus marginal population with hpt
df$male_nohpt <- df$man - df$hpt_male # compute male without hpt: male population ageXASL minus males with hpt for ageXASL
df$fem_nohpt <- df$fem - df$hpt_fem # compute female without hpt: male population ageXASL minus females with hpt for ageXASL

# idem for heart failure
df$tot_hf <- df$hf_fem + df$hf_male 
df$tot_nohf <- df$mar_ageASL - df$tot_hf 
df$male_nohf <- df$man - df$hf_male
df$fem_nohf <-  df$fem - df$hf_fem

df_marg <- df %>% group_by(DENOMINAZI) %>% summarize(mar_hptASL = sum(tot_hpt),
                                                     mar_nohptASL = sum(tot_nohpt),
                                                     mar_hfASL = sum(tot_hf),
                                                     mar_nohfASL = sum(tot_nohf),
                                                     mar_hptmanASL = sum(hpt_male),
                                                     mar_nohptmanASL = sum(male_nohpt),
                                                     mar_hptfemASL = sum(hpt_fem),
                                                     mar_nohptfemASL = sum(fem_nohpt),
                                                     
                                                     mar_hfmanASL = sum(hf_male),
                                                     mar_nohfmanASL = sum(male_nohf),
                                                     mar_hffemASL = sum(hf_fem),
                                                     mar_nohffemASL = sum(fem_nohf),
                                                     )

df <- merge(df,df_marg, by= c('DENOMINAZI'))

write.csv(df,file= "C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/soc_hpt_hf.csv",row.names = F)

# marginals for the population #######

setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")
df <- read.csv("soc_hpt_hf.csv",sep =",")

df$eta_range <- "00_00"
df[df$classi_eta %in% c("00_04","05_09","10_14","15_19","20_24","25_29"),]$eta_range <- "00_29"
df[df$classi_eta %in% c("30_34","35_39","40_44","45_49","50_54","55_59"),]$eta_range <- "30_59"
df[df$classi_eta %in% c("60_64","65_69","70_74","75_79","80_84","85_100"),]$eta_range <- "60_100"

# population aggregation
df_range <- df %>% group_by(eta_range) %>% summarize(man_r = sum(man),
                                                                fem_r = sum(fem),
                                                                hpt_man_r = sum(hpt_male),
                                                                male_nohpt_r =  sum(male_nohpt),
                                                                hpt_fem_r =  sum(hpt_fem),
                                                                fem_nohpt_r =  sum(fem_nohpt),
                                                                hf_male_r =  sum(hf_male),
                                                                male_nohf_r =  sum(male_nohf),
                                                                hf_fem_r =  sum(hf_fem),
                                                                fem_nohf_r =  sum(fem_nohf),
                                                                mar_ageASL_r = sum(mar_ageASL)
  
) 


mar_male_pop <- sum(df_range$man_r)
mar_fem_pop <- sum(df_range$fem_r)
mar_hpt_pop <- sum(df_range$hpt_fem_r) + sum(df_range$hpt_man_r)
mar_nohpt_pop <- sum(df_range$fem_nohpt_r) + sum(df_range$male_nohpt_r)
mar_hf_pop <- sum(df_range$hf_fem_r) + sum(df_range$hf_male_r)
mar_nohf_pop <-  sum(df_range$fem_nohf_r) + sum(df_range$male_nohf_r)
mar_00_29 <- df_range[df_range$eta_range == "00_29",]$mar_ageASL_r
mar_30_59 <- df_range[df_range$eta_range == "30_59",]$mar_ageASL_r
mar_60_100 <- df_range[df_range$eta_range == "60_100",]$mar_ageASL_r

write.csv(df_range,file= "C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/df_range.csv",row.names = F)


# Algorithm #####

cells = c("M_A1_HT_HF", "M_A1_HT_NHF", "M_A1_NHT_HF", "M_A1_NHT_NHF" ,
"M_A2_HT_HF", "M_A2_HT_NHF", "M_A2_NHT_HF", "M_A2_NHT_NHF",
"M_A3_HT_HF" , "M_A3_HT_NHF", "M_A3_NHT_HF", "M_A3_NHT_NHF",

"F_A1_HT_HF", "F_A1_HT_NHF", "F_A1_NHT_HF", "F_A1_NHT_NHF" ,
"F_A2_HT_HF", "F_A2_HT_NHF", "F_A2_NHT_HF", "F_A2_NHT_NHF",
"F_A3_HT_HF", "F_A3_HT_NHF", "F_A3_NHT_HF", "F_A3_NHT_NHF")

value = c(rep(1,length(cells)))

ipf <- data.frame(cells, value)

fitted_M <- ipf %>% filter(unlist(strsplit(cells,"_"))[1] == "M" )
  
  sum(ipf[unlist(strsplit(ipf$cells,"_"))[1] == "M" ,]$value)


  fitted_M <- ipf %>% filter(unlist(strsplit(cells,"_"))[1] == "M" )



ipf %>% filter(unlist(strsplit(cells,"_"))[1] == "M" ) %>% su

for (i in ipf$cells) {
 if(unlist(strsplit(i,"_"))[1] == "M"){print(sum(df[df$i]))}

}

print(unlist(strsplit("M_A2_NHT_HF","_"))[1])


