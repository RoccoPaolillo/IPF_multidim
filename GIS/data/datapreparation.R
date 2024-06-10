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
df$age <- df$fem + df$man  # tot age ASL>age
manASL <- df %>% group_by(DENOMINAZI) %>% summarize(manASL = sum(man))
femASL <- df %>% group_by(DENOMINAZI) %>% summarize(femASL = sum(fem))
dftotgentomerge <- merge(femASL,manASL, by = c("DENOMINAZI"))
df <- merge(df,dftotgentomerge,by = c("DENOMINAZI"))
df$sumgenASL <- df$femASL + df$manASL

dftoteta <- df %>% group_by(DENOMINAZI) %>% summarize(sumageASL = sum(age))
df <- merge(df,dftoteta,by = c("DENOMINAZI"))

# hypertension

# sociodemographics

setwd("C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/hypertension/")
dfhp <- read.csv("F0_4.csv",sep =";",skip = 9)
dfhp2 <- read.csv("M40_44.csv",sep =";",skip = 9) 
dfhp3 <- read.csv2("M80_84.csv",sep =";",skip = 9) 
dfhp4 <- read.csv2("F80_84.csv",sep =";",skip = 1) 
dfhp5 <- read.csv("F5_9.csv",sep =";",skip = 4)


library(stringr)

file.list = list.files( pattern = "*.csv")
theData_list<-lapply(file.list, read.csv)
dfh <-bind_rows(theData_list)






