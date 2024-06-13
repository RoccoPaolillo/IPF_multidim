library(tidyr)
library(purrr)
library(dplyr)
library(stringr)

# sociodemographics

setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/sociodem_asl")
file.list = list.files( pattern = "*.csv")

theData_list<-lapply(file.list, read.csv2)
df <-bind_rows(theData_list)
names(df) <- c("classi_eta","ita_f","ita_m","stran_f","stran_m","DENOMINAZI")
df$fem <- df$ita_f + df$stran_f # tot fem ASL>age
df$man <- df$ita_m + df$stran_m # tot men ASL>age
df$mar_ageASL <- df$fem + df$man  # tot age ASL>age
mar_manASL <- df %>% group_by(DENOMINAZI) %>% summarize(mar_manASL = sum(man))
mar_femASL <- df %>% group_by(DENOMINAZI) %>% summarize(mar_femASL = sum(fem))
dftotgentomerge <- merge(mar_femASL,mar_manASL, by = c("DENOMINAZI"))
df <- merge(df,dftotgentomerge,by = c("DENOMINAZI"))
df$tot_genASL <- df$mar_femASL + df$mar_manASL

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
# merging health failure
setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")

df <- read.csv("df_socdem.csv",sep=",")
df$classi_eta <- str_replace_all(df$classi_eta,"-","_")
df$classi_eta <- str_replace_all(df$classi_eta,"\"","")
hf <- read.csv("hf.csv",sep=",")
hpt <- read.csv("hpt.csv",sep=",")
# hf$classi_eta <- paste0("\"",hf$classi_eta,"\"")

df <- reduce(list(df,hf,hpt), full_join, by= c('DENOMINAZI',"classi_eta"))

df$tot_hpt <- df$hpt_fem + df$hpt_male
df$tot_nohpt <- df$mar_ageASL - df$tot_hpt
df$male_nohpt <- df$man - df$hpt_male
df$fem_nohpt <- df$fem - df$hpt_fem

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

# Age ranges



df <- read.csv("soc_hpt_hf.csv",sep =",")



#####

df$hf <- df$hf_fem + df$hf_male
df$nohf <- df$mar_ageASL - df$hf

dftot_hf <- df %>% group_by(DENOMINAZI) %>% summarize(mar_hfASL = sum(hf))
df <- merge(df,dftot_hf,by="DENOMINAZI")
dftot_nohf <- df %>% group_by(DENOMINAZI) %>% summarize(mar_nohfASL = sum(nohf))
df <- merge(df,dftot_nohf,by="DENOMINAZI")
df$tot_hfASL <- df$mar_hfASL + df$mar_nohfASL

df$classi_eta <- str_replace_all(df$classi_eta,"\"","")
write.csv(df, file ="ASL_hpt_hf.csv",row.names = F)

### ranges
setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")
df <- read.csv( file ="ASL_hpt_hf.csv", sep = ",")

df$eta_range <- "00_00"
df[df$classi_eta %in% c("00_04","05_09","10_14","15_19","20_24","25_29"),]$eta_range <- "00_29"
df[df$classi_eta %in% c("30_34","35_39","40_44","45_49","50_54","55_59"),]$eta_range <- "30_59"
df[df$classi_eta %in% c("60_64","65_69","70_74","75_79","80_84","85_100"),]$eta_range <- "60_100"

df10 <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(man = sum(man),
                                                            fem = sum(fem),
                                                            mar_ageASL = man + fem,
                                                            hpt_fem = sum(hpt_fem),
                                                            hpt_male = sum(hpt_male),
                                                            hf_fem = sum(hf_fem),
                                                            hf_male = sum(hf_male)
)

df10tot <- df %>% group_by(DENOMINAZI) %>% summarize(tot_ageASL = sum(mar_ageASL),
                                                     mar_manASL = sum(man),
                                                     mar_femASL = sum(fem),
                                                     tot_genASL = mar_manASL + mar_femASL,
                                                     mar_hptASL = sum(hpt_fem) + sum(hpt_male),
                                                     mar_nohptASL = sum(nohpt_fem) + sum(nohpt_male),
                                                     tot_hptASL = mar_hptASL + mar_nohptASL,
                                                     mar_hf_fem = sum(hf_fem),
                                                     mar_hf_male = sum(hf_male)
                                                     )



#

# df_agem_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(agem_range = sum(man))
# df_agef_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(agef_range = sum(fem))
# df_hpt_fem_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hpt_fem_range = sum(hpt_fem))
# df_hpt_male_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hpt_male_range = sum(hpt_male))
# df_hf_fem_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hf_fem_range = sum(hf_fem))
# df_hf_male_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hf_male_range = sum(hf_male))

df_list <- list(df_agem_range, df_agef_range, df_hpt_fem_range, df_hpt_male_range, df_hf_fem_range, df_hf_male_range) 
df_range <- reduce(df_list, full_join, by= c('DENOMINAZI',"eta_range"))

df_range$mar_age_range <- df_range$agem_range + df_range$agef_range
df_range$tot_hpt_range <- df_range$hpt_fem_range + df_range$hpt_male_range
df_range$tot_hf_range <- df_range$hf_fem_range + df_range$hf_male_range

mar_age_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(age_ASL = sum(mar_age_range))
tot_hpt_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(hpt_ASL = sum(tot_hpt_range))
tot_hf_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(hf_ASL = sum(tot_hf_range))
tot_male_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(male_ASL = sum(agem_range))
tot_fem_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(fem_ASL = sum(agef_range))

list_ASL <- list(df_range, mar_age_ASL, tot_hpt_ASL, tot_hf_ASL, tot_male_ASL, tot_fem_ASL)
df_range <- reduce(list_ASL, full_join, by= c('DENOMINAZI'))

df_range$nohptASL <- df_range$age_ASL - df_range$hpt_ASL
df_range$tot_hptASL <- df_range$hpt_ASL + df_range$nohptASL

df_range$nohfASL <- df_range$age_ASL - df_range$hf_ASL
df_range$tot_hfASL <- df_range$hf_ASL + df_range$nohfASL

df_range$genASL <- df_range$male_ASL + df_range$fem_ASL
write.csv(df_range, file="df_range.csv",row.names = F)


