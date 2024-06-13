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
df$totage <- df$fem + df$man  # tot age ASL>age
manASL <- df %>% group_by(DENOMINAZI) %>% summarize(manASL = sum(man))
femASL <- df %>% group_by(DENOMINAZI) %>% summarize(femASL = sum(fem))
dftotgentomerge <- merge(femASL,manASL, by = c("DENOMINAZI"))
df <- merge(df,dftotgentomerge,by = c("DENOMINAZI"))
df$sumgenASL <- df$femASL + df$manASL

dftoteta <- df %>% group_by(DENOMINAZI) %>% summarize(sumageASL = sum(totage))
df <- merge(df,dftoteta,by = c("DENOMINAZI"))

# hypertension

# sociodemographics

setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/hypertension/")
dfhp <- read.csv("df_hypertension.csv",sep=";")
dfhp[dfhp$DENOMINAZI == "ASL Roma 1",]$DENOMINAZI <- "ROMA 1"
dfhp[dfhp$DENOMINAZI == "ASL Roma 2",]$DENOMINAZI <- "ROMA 2"
dfhp[dfhp$DENOMINAZI == "ASL Roma 3",]$DENOMINAZI <- "ROMA 3"
dfhp[dfhp$DENOMINAZI == "ASL Roma 4",]$DENOMINAZI <- "ROMA 4"
dfhp[dfhp$DENOMINAZI == "ASL Roma 5",]$DENOMINAZI <- "ROMA 5"
dfhp[dfhp$DENOMINAZI == "ASL Roma 6",]$DENOMINAZI <- "ROMA 6"
dfhp[dfhp$DENOMINAZI == "ASL Frosinone",]$DENOMINAZI <- "FROSINONE"
dfhp[dfhp$DENOMINAZI == "ASL Latina",]$DENOMINAZI <- "LATINA"
dfhp[dfhp$DENOMINAZI == "ASL Rieti",]$DENOMINAZI <- "RIETI"
dfhp[dfhp$DENOMINAZI == "ASL Viterbo",]$DENOMINAZI <- "VITERBO"
dfhp[dfhp$fem_cases == "(*)",]$fem_cases <- 0
dfhp[dfhp$male_cases == "(*)",]$male_cases <- 0
names(dfhp)[2] <- "hpt_fem"
names(dfhp)[3] <- "hpt_male"

# merge datasets
df <- merge(df,dfhp,by=c("DENOMINAZI","classi_eta"))
df$hpt_fem <- as.numeric(df$hpt_fem)
df$hpt_male <- as.numeric(df$hpt_male)
df$hpt <- df$hpt_fem + df$hpt_male
df$nohpt <- df$totage - df$hpt

dftothpt <- df %>% group_by(DENOMINAZI) %>% summarize(hptASL = sum(hpt))
df <- merge(df,dftothpt,by="DENOMINAZI")
dftotnohpt <- df %>% group_by(DENOMINAZI) %>% summarize(nohptASL = sum(nohpt))
df <- merge(df,dftotnohpt,by="DENOMINAZI")
df$sumhptASL <- df$hptASL + df$nohptASL

# write.csv(df,file="df_socdemhpt.csv",row.names = FALSE)
# save(df,file="df_socdemhpt.Rdata")








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
}

disease_df("hearth_failure","hf")

# merging health failure
setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")

df <- read.csv("df_socdemhpt.csv",sep=",")
df$classi_eta <- str_replace_all(df$classi_eta,"-","_")
hf <- read.csv("hf.csv",sep=",")
hf$classi_eta <- paste0("\"",hf$classi_eta,"\"")

df <- merge(df,hf,by =c("DENOMINAZI","classi_eta"))

df$hf <- df$hf_fem + df$hf_male
df$nohf <- df$totage - df$hf

dftothf <- df %>% group_by(DENOMINAZI) %>% summarize(hfASL = sum(hf))
df <- merge(df,dftothf,by="DENOMINAZI")
dftotnohf <- df %>% group_by(DENOMINAZI) %>% summarize(nohfASL = sum(nohf))
df <- merge(df,dftotnohf,by="DENOMINAZI")
df$sumhfASL <- df$hfASL + df$nohfASL

df$classi_eta <- str_replace_all(df$classi_eta,"\"","")
write.csv(df, file ="ASL_hpt_hf.csv",row.names = F)

### algorithm
setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/")
df <- read.csv( file ="ASL_hpt_hf.csv", sep = ",")

df$eta_range <- "00_00"
df[df$classi_eta %in% c("00_04","05_09","10_14","15_19","20_24","25_29"),]$eta_range <- "00_29"
df[df$classi_eta %in% c("30_34","35_39","40_44","45_49","50_54","55_59"),]$eta_range <- "30_59"
df[df$classi_eta %in% c("60_64","65_69","70_74","75_79","80_84","85_100"),]$eta_range <- "60_100"

df_agem_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(agem_range = sum(man))
df_agef_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(agef_range = sum(fem))
df_hpt_fem_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hpt_fem_range = sum(hpt_fem))
df_hpt_male_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hpt_male_range = sum(hpt_male))
df_hf_fem_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hf_fem_range = sum(hf_fem))
df_hf_male_range <- df %>% group_by(DENOMINAZI,eta_range) %>% summarize(hf_male_range = sum(hf_male))

df_list <- list(df_agem_range, df_agef_range, df_hpt_fem_range, df_hpt_male_range, df_hf_fem_range, df_hf_male_range) 
df_range <- reduce(df_list, full_join, by= c('DENOMINAZI',"eta_range"))

df_range$totage_range <- df_range$agem_range + df_range$agef_range
df_range$tothpt_range <- df_range$hpt_fem_range + df_range$hpt_male_range
df_range$tothf_range <- df_range$hf_fem_range + df_range$hf_male_range

sumage_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(age_ASL = sum(totage_range))
sumhpt_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(hpt_ASL = sum(tothpt_range))
sumhf_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(hf_ASL = sum(tothf_range))
summale_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(male_ASL = sum(agem_range))
sumfem_ASL <- df_range %>% group_by(DENOMINAZI) %>% summarize(fem_ASL = sum(agef_range))

list_ASL <- list(df_range, sumage_ASL, sumhpt_ASL, sumhf_ASL, summale_ASL, sumfem_ASL)
df_range <- reduce(list_ASL, full_join, by= c('DENOMINAZI'))

df_range$nohptASL <- df_range$age_ASL - df_range$hpt_ASL
df_range$sumhptASL <- df_range$hpt_ASL + df_range$nohptASL

df_range$nohfASL <- df_range$age_ASL - df_range$hf_ASL
df_range$sumhfASL <- df_range$hf_ASL + df_range$nohfASL

df_range$genASL <- df_range$male_ASL + df_range$fem_ASL
write.csv(df_range, file="df_range.csv",row.names = F)


