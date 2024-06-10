library(tidyr)
library(purrr)
library(dplyr)

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

write.csv(df,file="df_socdemhpt.csv",row.names = FALSE)
save(df,file="df_socdemhpt.Rdata")

