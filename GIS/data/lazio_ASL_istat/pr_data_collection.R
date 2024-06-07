library(rvest)
library(tidyverse)
library(tibble)
library(dplyr)
library(stringi)
library(stringr)
library(readtext)
library(gdata)
library(lubridate)
# Sys.setlocale("LC_MESSAGES", 'en_GB.UTF-8')
# url_tr = "https://raw.githack.com/ccs-amsterdam/r-course-material/master/miscellaneous/simple_html.html"

setwd("C:/Users/rocpa/OneDrive/Desktop/ROME_CNR/WP5/datalazio")

url = "https://www.opensalutelazio.it/salute/stato_salute.php" 

https://www.metabolomicsworkbench.org/data/mb_structure_ajax.php
pg <- html_session(url)

data <- 
  purrr::map_dfr(
    1:4, # you might wanna change it to a small number to try first or scrape multiple times and combine data frames later, in case something happens in the middle
    function(i) {
      pg <- rvest:::request_POST(pg,
                                 url,
                                 body = list(
                                   page = i
                                 ))
      read_html(pg) %>%
        html_node("table") %>%
        html_table() 
    }
  )

url <- "https://www.metabolomicsworkbench.org/data/mb_structure_tableonly.php"
pg <- html_session(url)
data <- 
  purrr::map_dfr(
    1:30, # you might wanna change it to a small number to try first or scrape multiple times and combine data frames later, in case something happens in the middle
    function(i) {
      pg <- rvest:::html_form_submit(pg,
                                 url)
      read_html(pg) %>%
        html_node("table") %>%
        html_table() 
    }
  )


# delete #########
# del <- read.csv("delete_text.csv",sep=";",fileEncoding="UTF-8-BOM")[,1]
# CNT ####
# BVMW #### ok ####
df <- data[data$actor == "BVMW",]
del_t <- paste0(del[del$text == "BVMW",]$delete,collapse="|")
# functions
title <- function(i){read_html(i) %>% html_element("div.col-sm-12") %>% 
    html_element("h1") %>% html_text2()}
subtitle <- function(i){read_html(i) %>% html_element("div.col-sm-12") %>% 
    html_element("p.teaser") %>%
    html_text2()}
text <- function(i){read_html(i) %>% html_element(".text-left") %>% 
    html_text2()}


# BITKOM #### ok ####
i = "https://www.bitkom.org/Presse/Presseinformation/Jedes-dritte-Startup-hat-Corona-Hilfen-erhalten"
df <- data[data$actor == "BITKOM",]
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
subtitle <- "xxxxx"
text <- function(i){read_html(i) %>% html_element("div.wysiwyg__body") %>% html_text2()}

# VDA ok ####
df <- df %>% filter(
  link != "https://www.vda.de/vda/de/presse/Pressemeldungen/210528_Fit-for-55_Wir-setzen-auf-Innovationen--Investitionen--Infrastruktur" &
    link != "https://www.vda.de/vda/de/presse/Pressemeldungen/210714_Fit-for-55_Ambitionierte-Ziele-brauchen-Technologieoffenheit-und-die-richtigen-Rahmenbedingungen" &
    link !=   "https://www.vda.de/vda/de/presse/Pressemeldungen/211206_Studie_Reiner-Elektrofahrzeug-Ansatz-w-rde-zu-Verlust-einer-halben-Million-Arbeitspl-tze-in-der-EU-f-hren")

i = "https://www.vda.de/vda/de/presse/Pressemeldungen/200604-Statement-von-VDA-Praesidentin-Hildegard-Mueller-zum-Koalitionsausschuss"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
subtitle <- "xxx" # no subtitle because not always available on online texts
text <- function(i){read_html(i) %>% html_element("div.RichText_RichText__vPwAm") %>% html_text2()}



# HDE ok ####
i <- "https://einzelhandel.de/index.php?option=com_content&view=article&id=12762"
title <- function(i){read_html(i) %>% html_element("h1") %>% html_text2}
text <- function(i){read_html(i) %>% html_element("article.item-page") %>% html_elements("p") %>% html_text2() %>% paste(sep ="",collapse = " ")}
subtitle <- "xxxxx"


# ZDH ok ####
i <- "https://www.zdh.de/presse/veroeffentlichungen/pressemitteilungen/konjunkturpaket-jetzt-schnell-und-buerokratiearm-umsetzen/"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_element("div.co__rteContent.rteContent") %>% html_text2()}
subtitle <- function(i){read_html(i) %>% html_element("div.contentHeaderHeader__text") %>% html_text2()}



# VCI # ok ####

i <-"https://www.vci.de/presse/pressemitteilungen/ueberwindung-der-corona-folgen-braucht-zeit.jsp"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_element("div.component.c-text-image") %>% html_text2()}
subtitle <- "xxxxx"



# VBI # ok ####
i <- "https://bdi.eu/presse/pressemitteilungen/?tx_solr%5Bpage%5D=11"
title <- function(i){read_html(i) %>% html_element("head") %>% html_element("title") %>% html_text2()}
subtitle <- function(i){read_html(i) %>% html_element("div.custom_intro.mb-3")  %>% 
    html_element("span.intro.w-100.unit.text-dark.fw-medium.fs-125.mb-3") %>% html_text2()}
subtitle <- function(i){read_html(i) %>% html_element("div.single__content.w-100.no-gutters") %>% 
    html_element("p") %>% html_text2()}






# BdB # ok 2 to add ####
i <- "https://bankenverband.de/newsroom/presse-infos/kreditwirtschaft-hilft-grosstes-staatliches-kreditprogramm-umzusetzen/"
title <- function(i){read_html(i) %>% html_element("h1") %>% html_text2()}
subtitle <-  "xxxxx"
text <- function(i){read_html(i) %>% html_element("div.row.content.article-content.bv__presstemplate") %>%
    html_elements("p") %>% html_text2() %>% paste(collapse="")}



# BIO-Deutschland # ok taken manually 1 link ####
i <- "https://www.biodeutschland.org/de/pressemitteilungen/massnahmen-der-bundesregierung-erreichen-den-forschenden-mittelstand-nicht.html"
read_html(i) %>% html_element("div.newsletter") %>% html_element("h1") %>% html_text2()
"xxxxx"
read_html(i) %>% html_element("div.newsletter") %>% html_elements("p") %>%
  html_text2() # %>% paste(,collapse="")


# ZVEI # ok composed handy some ####
i <- "https://www.zvei.org/presse-medien/pressebereich/klimabericht-zeigt-gebaeudesektor-muss-endlich-energiewendefaehig-werden"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
subtitle <- "xxxxx"
text <- function(i){read_html(i) %>% html_element("p.MsoBodyText") %>% html_text2()}



# BDE # ok ####
i <- "https://www.bde.de/presse/mitgliedschaft-unternehmensgruen/"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
subtitle <- function(i){read_html(i) %>% html_nodes("[name = 'description']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_element("div.rich-text") %>% html_text2()}




# ZIA # ok hand corrected ####
i <- "https://zia-deutschland.de/pressrelease/eu-kommission-macht-weg-fuer-hoehere-hilfen-frei-hilfsprogramme-muessen-nun-zuegig-angepasst-werden/"
title <- function(i){read_html(i) %>% html_element("h2.hl1") %>% html_text2()}
subtitle <- "xxxxx"
text <- function(i){read_html(i) %>% html_element("div.text") %>% html_text2()}


# BDG # out of context (russia) ####
i <- "https://www.guss.de/organisation/presseinformation/auswirkungen-der-russlandsanktionen"


# vDMA # ok hand uploaded ####
i <- "https://www.vdma.org/viewer/-/v2article/render/56889858"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
subtitle <- function(i){read_html(i) %>% html_nodes("[property = 'og:description']") %>% html_attr("content")}
# read_html(i) %>% html_elements("div.article__text p") %>% html_text2()

dfa <- data.frame(actor = "VDMA", policy = "eu-aufbauplan", link = "chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.vdma.org/c/document_library/get_file?uuid=61f42bc9-e5a0-d40d-2c25-366e4b9d9558&groupId=34570",
                  type = "positionpaper",date = "06/08/2020",
                  title = "Eckpunkte, Bewertung, Nachbesserungsempfehlungen zu den Beschlüssen des EU Gipfels im Juli 2020")




# TUV # ok ####
i <- "https://www.tuev-verband.de/pressemitteilungen/stellungnahme-konjunkturpaket-1"

title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_element("div.news-text-wrap") %>% html_text2()}
subtitle <- function(i){read_html(i) %>% html_element("div.teaser-text") %>% html_text2()}


# BDS # ok hand compiled ####
# GDV # ok hand compiled ####

gdv <- readtext("gdv_04.05.2020.docx",sep = "_",
                       encoding = "UTF-8")[,2]






# VDV # ok hand compiled ####
i <- "https://www.vdv.de/presse.aspx?mode=detail&id=d9375875-79ed-415c-bad4-fc38aa0b4d0c"
read_html(i) %>% html_element("div.headline") %>% html_text2()
read_html(i) %>%  html_element("div.press-release-detail.entry") %>% html_text2()
read_html(i) %>%  html_elements("div.press-release-detail.entry div") %>% html_text2()  #[2]
read_html(i) %>% html_elements("div.press-release-detail.entry") %>% html_text2()

title <- function(i){read_html(i) %>% html_element("div.headline") %>% html_text2()}
text <- function(i){read_html(i) %>%  html_elements("div.press-release-detail.entry div") %>% html_text2()}

for (i in 1:9) {
  df[i,]$text <- df[i,]$text[[1]][2]
  
}


# TXM # ok hand compiled ####

i <- "https://textil-mode.de/de/newsroom/pressemitteilungen/corona-steuerhilfegesetz-muss-fuer-effektive-und-effiziente-unterstuet/"
title <- function(i){read_html(i) %>% html_element("h1") %>% html_text2()}
text <- function(i){read_html(i) %>% html_element("div.ce_text.block") %>% html_text2()}




# BBS # ok hand compiled

# DGB ok ####

i <- "https://www.dgb.de/uber-uns/dgb-heute/internationale-und-europaeische-gewerkschaftspolitik/++co++9a16d8c0-7930-11ec-844c-001a4a160123"

title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_elements("span.usercontent") %>% html_text2() %>% paste0(collapse = " ")}
subtitle <- "xxxxx"

# DIHK ok ####

i <- "https://www.dihk.de/de/themen-und-positionen/wirtschaftlicher-neustart-nach-der-corona-krise-in-der-eu-51196"

title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_elements("div.rte__content") %>% html_text2()  %>% paste0(collapse = " ")}
subtitle <- function(i){read_html(i) %>% html_elements("div.header-article__content p") %>% html_text2()}



# upload data ####
data <- read.csv("deu_compiled/EUKEY.csv",sep=";",fileEncoding="UTF-8-BOM")
data[is.na(data)] = 0
df <- data[data$actor == "VDMA",]
# del <- read.csv("delete_text.csv",sep=";",fileEncoding = "UTF-8-BOM")
# "%nin%" <- Negate("%in%")
# a <- df[!duplicated(df$link),]
df <- df %>% filter(check_run != 1)

# short survey 
# read_html(i) %>% html_element("ul.is-style-custom-ul-chevrons.is-style-iconPrimary") %>%
#   html_text2()

# dataset composition ####
# df$title <- lapply(df$link,title)
# df$title <- unlist(df$title)
# df$text <- lapply(df$link,text)
# df$text <-  unlist(df$text)
# df$subtitle <- lapply(df$link,subtitle)
# df$subtitle <- unlist(df$subtitle)

df <- df[df$type == "PS",]

df <- df[,c(1:5,7:9)]
df$check_run <- 1
df <- df[,c(1,2,3,4,5,9,6,7,8)]

df <- df[!duplicated(df$link),]

df <- df[2:3,]

str_match(df$text,del_t)
df$text <- str_replace_all(df$text,del_t,"")
df <- apply(df,2,as.character)

write.csv2(df,"deu_compiled/vdma_eu.csv",row.names = F) # other 2 articles to add

# test df
# rm(df)
df <- read.csv("compiled/bds.csv",sep=";")
str_match(df$text,del_t)

data[1,]
dff <- data[1,]
d <- paste0(p,collapse="|")



# TEST CODE
i = "https://bdi.eu/artikel/news/verhandlungen-nicht-mit-politischen-zielen-ueberfrachten/"
title <- read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")
subtitle <- "xxxxx"
text <- read_html(i) %>% html_element("div.wysiwyg__body") %>% html_text2()
#



# Data check #####

# one
i <- "https://www.bauindustrie.de/pm/koalition-legt-mit-konjunkturpaket-guten-start-hin"
read_html(i) %>% html_element("div.news-text-wrap") %>% html_text2()


# run-all
for (i in df$text) {
  message('row: ', i)
  t <- read_html(i) %>% html_element("article.item-page") %>% html_elements("p") %>% html_text2()
  print(df$link)
  print(t)
}



# VATM # ####
i <- "https://www.vatm.de/vatm-statement-mehrwertsteuersenkung-wird-kundenfreundlich-und-unbuerokratisch-umgesetzt/"
read_html(i) %>% html_element("h1") %>% html_text2()
read_html(i) %>% html_element("body")


# GDV #### itemlist not working ####
i <- "https://www.gdv.de/de/themen/politische-positionen/stellungnahmen/steuerliche-corona-hilfsmassnahmen-weiter-verbessern-84842"
read_html(i) %>% 
  html_element("h1.title.title--mlarge.color--bordeaux") %>% html_text2()
read_html(i) %>% html_nodes("[property = 'og:description']") %>% html_attr("content")
read_html(i) %>% html_element("div.article_text_description") %>% html_text2()

# TXM # textil-mode to add!!
# https://textil-mode.de/de/search/?q=konjunkturpaket
  
# TUV # to add!!
# https://www.tuev-verband.de/pressemitteilungen/stellungnahme-konjunkturpaket-1
  

# DGB ####

i <- "https://www.dgb.de/einblick/ausgaben-archiv/2020"

# read_html(i) %>% html_nodes("div.ul.li a") %>% html_attr("href")

ls <- read_html(i) %>% html_nodes("div.row h4 a") %>% html_attr("href")

title <- function(i){t <- read_html(i) %>% html_elements("div.box h3") %>% html_text2()
t <- t[1]
t
}

text <- function(i){read_html(i) %>% html_elements("span.usercontent p") %>% html_text2() %>% paste0(collapse = " ")}

date <- function(i){read_html(i) %>% html_nodes("div.date") %>% html_text2() %>% paste0(collapse = " ")}
df$date <- substr(df$date,10,19)


# VERDI pressemitteilung ####

# i <- "https://www.verdi.de/presse/pressemitteilungen/landespressemitteilung"

i <- "https://www.verdi.de/presse/pressemitteilungen?page=86#zentralsearch"

lss <- list()
for (i in 1:89) {
  
  # i <- paste0("https://bdi.eu/presse/pressemitteilungen/?tx_solr%5Bpage%5D=",i)
  l <- paste0("https://www.verdi.de/presse/pressemitteilungen?page=",i,"#zentralsearch")
  ls <- read_html(l) %>% html_nodes("h3.title.x-big a") %>% html_attr("href") # https://www.dbb.de/
  
  lss[[i]] <- ls
  
}
lss

ls <- read_html(i) %>% html_nodes("h3.title.x-big a") %>% html_attr("href") #1-89; # landespressemitteilung 3:38

title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){
  t <- read_html(i) %>% html_elements("div.content-text.wysiwyg") %>% html_text2() %>% unlist()
t <- t[1]
t
}

date <- function(i){read_html(i) %>% html_elements("span.date") %>% html_text2()}

# IG METALL ####

i <- "https://www.igmetall.de//presse/pressemitteilungen/textile-dienste-tarifverhandlungen-ergebnislos-beendet"

ls <- paste0("https://www.igmetall.de/",
       read_html(i) %>% html_nodes("div.col-lg-12.col-sm-12.teaserGrid-list__Among--above.column-count--one a") %>% html_attr("href"))

title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}

text <- function(i){read_html(i) %>% html_elements("div.col-sm-10.offset-sm-1.col-md-10.offset-md-1.col-lg-8.offset-lg-2 p") %>% html_text2() %>% 
    paste0(collapse = " ")
}

subtitle <- function(i){read_html(i) %>% html_elements("h2.p") %>% html_text2()}

date <- function(i){read_html(i) %>% html_elements("b.d-none.d-md-inline") %>% html_text2() %>% paste0(collapse = " ")}

# BVMW ####

df <- read.xls("datasets_draft/bvmw.xls",sheet = "mgz_service") 

i <- "https://www.bvmw.de/themen/coronavirus/news/5802/schrittweise-schuloeffnung-und-beibehalten-der-pruefungen-ist-vernuenftig/"

read_html(i) %>% html_nodes("div.row.sameheight a") %>% html_attr("href")

title <- function(i){read_html(i) %>% html_elements("div.col-sm-12 h1") %>% html_text2()}
 text <- function(i){read_html(i) %>% html_elements("div.paragraph.text-left") %>% html_text2() %>% paste0(collapse = " ")}
# text <- function(i){read_html(i) %>% html_elements("div.paragraph") %>% html_text2() %>% paste0(collapse = " ")}
subtitle <- function(i){read_html(i) %>% html_nodes("[property = 'og:description']") %>% html_attr("content")}
 
date <- function(i){read_html(i) %>% html_elements("span.timestamp") %>% html_text2() %>% paste0(collapse = " ")}
df$date <- substr(df$date,13,22)






# BDI # ok ####

i = "https://bdi.eu/themenfelder/alle-dossiers-a-z/"
# title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>%  html_attr("content")}
# read_html(i) %>% html_element("div.teaser") %>% html_text2()

# ls <- read_html(i) %>% html_nodes("h3.results-topic a")  %>% html_attr("href") #"https://bdi.eu/"
ls <- read_html(i) %>% html_nodes("div.bdi-teaser__content-wrap a") %>% html_attr("href")

title <- function(i){read_html(i) %>% html_elements("div.bdi-content.bdi-ctype__text h1") %>% html_text2()}
text <- function(i){read_html(i) %>% html_elements("div.bdi-content.bdi-ctype__text") %>% html_elements("p") %>% html_text2() %>% paste(sep ="",collapse = " ")}
subtitle <- "xxxxx"
date <- function(i){read_html(i) %>% html_elements("time") %>% html_text2() %>% paste(sep ="",collapse = " ")}


df <- df[!(df$link %in% 
             c("https://bdi.eu//artikel/news/appell-der-deutschen-gewerblichen-wirtschaft-unternehmensteuern-modernisieren/",
               "https://bdi.eu//artikel/news/appell-der-deutschen-gewerblichen-wirtschaft-unternehmensteuern-modernisieren/")
           ),]

i <-  "https://bdi.eu//themenfelder/aussenwirtschaft/china/" 
 read_html(i) %>% html_nodes("h3.results-topic a")  %>% html_attr("href") 



 
# BAU ok ####
 
i <- "https://www.bauindustrie.de/pm/bauministerkonferenz-muss-bezahlbarkeit-von-wohnraum-in-den-blick-nehmen"

 df <- data[data$actor == "BAUINDUSTRIE",]
 del_t <- paste0(del[del$text == "BAUINDUSTRIE",]$delete,collapse="|")
 
 title <- function(i){read_html(i) %>% 
     html_nodes("[property = 'og:title']") %>% html_attr("content")}
 text <- function(i){read_html(i) %>% html_element("div.news-text-wrap") %>% html_text2()}
subtitle <- function(i){read_html(i) %>% html_nodes("[property = 'og:description']") %>% html_attr("content") %>% paste(collapse = " ")}
date <- function(i){read_html(i) %>% html_elements("span.list-date") %>% html_text2()}  


link <- paste0("https://www.bauindustrie.de",read_html(i) %>% html_nodes("a.card-body-link") %>%
          html_attr("href"))

df <- data.frame(link)

# DBB TU

monate <-  c("Januar","Februar","Maerz","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember")
i <- "https://www.dbb.de/archiv/archivliste/2020/Mai.html"

 paste0("https://www.dbb.de/",read_html(i) %>% html_nodes("h2 a") %>% html_attr("href")) # https://www.dbb.de/
 
 df <- rbind(df2020,df2021)

i <- "https://www.dbb.de/artikel/pflege-geht-die-ganze-gesellschaft-an.html"

 
 
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
text <- function(i){read_html(i) %>% html_elements("article.content p") %>% html_text2() %>% paste0(collapse = " ")}

df$link <- str_replace(df$link,"https://www.dbb.de/https://","https://")
subtitle <- "xxxxx"
date <- function(i){read_html(i) %>% html_elements("time") %>% html_text2()}

df$date <- str_replace(df$date," Januar ","01.")
df$date <- str_replace(df$date," Februar ","02.")
df$date <- str_replace(df$date," März ","03.")
df$date <- str_replace(df$date," April ","04.")
df$date <- str_replace(df$date," Mai ","05.")
df$date <- str_replace(df$date," Juni ","06.")
df$date <- str_replace(df$date," Juli ","07.")
df$date <- str_replace(df$date," August ","08.")
df$date <- str_replace(df$date," September ","09.")
df$date <- str_replace(df$date," Oktober ","10.")
df$date <- str_replace(df$date," November ","11.")
df$date <- str_replace(df$date," Dezember ","12.")

# VDMA 

df <- read.xls("datasets_draft/vdma2.xls")

i <- "https://www.vdma.org/viewer/-/v2article/render/4034004"

title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")}
read_html(i) %>% html_elements("div.article-viewer-page__content__components.ue-dynamic-content-wrapper p") 


# data downloading ####
# multiple links ####


lss <- list()
for (i in monate) {
  
 # i <- paste0("https://bdi.eu/presse/pressemitteilungen/?tx_solr%5Bpage%5D=",i)
 l <- paste0("https://www.dbb.de/archiv/archivliste/2021/",i,".html")
 ls <- paste0("https://www.dbb.de/",read_html(l) %>% html_nodes("h2 a") %>% html_attr("href")) # https://www.dbb.de/

  lss[[i]] <- ls
  
}
lss


for (i in df$link) {
  message('Scraping URL: ', i)
 p <- title(i)
 p
  
}

df <- plyr::ldply (lss, data.frame)
df <- rename(df, page_orig = .id)
df <- rename(df, link = X..i..)

# df <- read.csv("bvmw.csv",sep = ";",fileEncoding = "UTF-8-BOM") 

# compose df ####
df$title <- lapply(df$link,title) 
df$title <- unlist(df$title)

df$text <- lapply(df$link,text)
df$text <- unlist(df$text)

df$subtitle <- lapply(df$link, subtitle)
df$subtitle <- unlist(df$subtitle)

df$date <- lapply(df$link,date)
df$date <- unlist(df$date)  
# df$date <- substr(df$date,1,10)

df$content <- paste(df$title,df$subtitle,df$text)
df$actor <- "BVMW"
df$source <- "mgz_service"
df$organization <- "TA"
df$selected <- 1
df$note <- NA
df$ID <- paste0(df$actor,"_",df$source,"_",df$date,"_",rownames(df))


# df$date <- as.Date(df$date,format = "%d.%m.%Y")

df <- df[,c(12,7,9,8,1,2,3,4,6,5,10,11)]

write.csv(df,"deu_compiled/final/bkp/bvmw_mgz_service.csv",row.names = FALSE)
df <- read.csv("deu_compiled/final/bkp/bvmw_mgz_service.csv",sep = ",")




# ITALY #####
# read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content")
# read_html ####
i <- "https://www.confindustria.it/home/media/comunicati-stampa"
read_html(i) %>% html_element("accordion_toggle.truncate")

library(quanteda)
library(tm)
library(tm.plugin.factiva)
library(RNewsflow)
library(quanteda.textstats)
library(data.table)
library(dplyr)
library(lubridate)
library(stringi)
library(stringr)
library(readtext)

setwd("C:/Users/rocpa/OneDrive/Desktop/CNT/press_release/CONFINDUSTRIA")

filenames <- list.files("CI_1.html", full.names=TRUE)

# source read by Factiva for each document. It creates a nested list
source_list <- lapply(filenames,FactivaSource)

# last Factiva passage for each document
raw_list <- lapply(source_list,Corpus,list(language = NA))

n <- length(raw_list) 

a <- readtext("CI_1.html",encoding = "UTF-8")


# FIOM ok ####
 
df <- read_html("https://www.fiom-cgil.it/net/index.php/cerca?searchword=react&ordering=newest&searchphrase=exact&limit=300") %>%
   html_elements('dl.search-results dt.result-title a') %>% 
   html_attr('href')
 
 df <- paste0("https://www.fiom-cgil.it",df)
 
 df <- "https://www.fiom-cgil.it/net/index.php/home-formazione/8019-fondo-nuove-competenze-emanato-il-decreto-attuativo-per-favorire-la-ripresa-delle-attivita-produttive"
 
i <- "https://www.fiom-cgil.it/net/index.php/comunicazione/stampa-e-relazioni-esterne/7361-fca-siglata-intesa-quadro-per-l-utilizzo-della-cassa-per-far-fronte-all-emergenza-covid-19"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content") %>% unique()} #  %>% paste0(collapse = " ")}
#title <- function(i){read_html(i) %>% html_nodes("title") %>% html_text2()}
text <- function(i){read_html(i) %>% html_elements("p") %>% html_text2() %>% paste0(collapse = " ")}
date <- function(i){read_html(i) %>% html_elements("time") %>% html_text2()}
# read_html(i) %>% html_nodes("[itemprop = 'articleBody']") %>% html_attr("text") 


df <- data.frame(df)
df <- rename(df, link = df)

df$actor <- "fiom"
df$check_run <- 1
df$type <- "NA"

df$policy <- "esf"
df$title <- lapply(df$link, title)
 df$title <- unlist(df$title)
df$text <- lapply(df$link,text)
df$text <- unlist(df$text)
df$date <- lapply(df$link,date)
df$date <- unlist(df$date)
df$subtitle <- "xxxxx"



df <- df[,c(2,5,1,4,8,3,6,7,9)]

write.csv2(df,"ita_compiled/fiom/fiom_esf.csv",row.names = F) # other 2 articles to add






# webb = list()       # multiple pages extraction
# for (i in 1:6) {
#   wb <- "https://www.fiom-cgil.it/net/index.php/cerca?searchword=cura%20italia&ordering=newest&searchphrase=exact"
#   ls <- read_html(wb) %>%
#     html_elements("dt.result-title a") %>%
#     html_attr("href")
#   webb[[i]] = ls
# }
# webb
# 
# df <- plyr::ldply (webb, data.frame)
# df2 <- rename(df2, link = X..i..)


ls <- read_html(wb) %>% html_elements("dt.result-title a") %>%  html_attr("href")




# add before: https://www.fiom-cgil.it/

# FIM ok ####
 
ls <- read_html("https://www.fim-cisl.it/page/2/?s=%22recovery+plan%22") %>%
   html_elements("ul.search-results-page__list a")%>% 
   html_attr('href')

# ls2 <- read_html("https://www.fim-cisl.it/page/2/?s=%22cura+italia%22") %>%
#   html_elements("ul.search-results-page__list a")%>% 
#   html_attr('href')

ls <- c("https://www.fim-cisl.it/2020/10/16/europa-il-sindacato-e-la-contrattazione-una-risorsa-fondamentale-usare-le-risorse-per-modernizzazione-dellindustria-e-competenze-dei-lavoratori/",
        "https://www.fim-cisl.it/2020/09/23/dossier-ilva-e-giunta-lora-di-giocare-allo-scoperto/")



i <- "https://www.fim-cisl.it/2020/03/19/marelli-aperta-cassa-per-covid-19/"
title <- function(i){read_html(i) %>% html_nodes("[property = 'og:title']") %>% html_attr("content") %>% paste0(collapse = " ")}
text <- function(i){read_html(i) %>% html_elements("div.post__content > p") %>% html_text2() %>% paste0(collapse = " ")}
date <- function(i){read_html(i) %>% html_element("span.post__meta-item.post__meta-item--date") %>% html_text2()}



# Confesercenti ok ####

webb = list()       # multiple pages extraction
for (i in 1:6) {
  wb <- paste0("https://www.confesercenti.it/page/",i,"/?s=%22fse%22")# 3
  ls <- read_html(wb) %>%
    html_elements("div.elementor-widget-container h3 a") %>%
    html_attr("href")
  webb[[i]] = ls
}
webb

df2 <- plyr::ldply (webb, data.frame)
df2 <- rename(df2, link = X..i..)


ls2 <- read_html("https://www.confesercenti.it/?s=%22nextgeneration%22") %>%  # individual page extraction
  html_elements("div.elementor-widget-container h3 a") %>%
  html_attr("href")
ls2

i <- "https://www.confesercenti.it/blog/confesercenti-torino-fiarc-il-sistema-di-calcolo-ci-penalizza/"

read_html(i) %>%
  html_nodes("[property = 'og:description']") %>%
  html_attr("content")

 read_html(i) %>% html_element("div.elementor-widget-container h4") %>% html_text2()

# title <-  function(i){read_html(i) %>%
#   html_element("div.elementor-widget-container h4") %>%
#   html_text2()}

df <- c(ls1,ls2)
df <- unique(df)

df <- data.frame(df)
df <- rename(df, link = df)

df <- rbind(df1,df2)


# title <- function(i){read_html(i) %>%
#     html_element("title") %>%
#     html_text2()}

title <- function(i){read_html(i) %>%
    html_element("h1.elementor-heading-title.elementor-size-default") %>%
    html_text2()}
text <-   function(i){read_html(i) %>%
  html_elements("div.elementor-widget-container p") %>%
  html_text2() %>% paste0(collapse = " ")}

date <- function(i){read_html(i) %>%
    html_element("span.elementor-icon-list-text.elementor-post-info__item.elementor-post-info__item--type-date") %>%
    html_text2()}


subtitle <- function(i){read_html(i) %>% html_element("div.elementor-widget-container h4") %>% html_text2()}



# Confapi ok ####


i <- "https://www.confapi.org/it/media-confapi/comunicati/2061-comunicato-congiunto-su-superbonus.html"

text <- function(i){read_html(i) %>% html_nodes("div.page-header") %>% html_text2()}
title <- function(i){read_html(i) %>% html_nodes("[itemprop = 'articleBody']") %>% html_text2()}
date <- function(i){read_html(i) %>% html_elements("time") %>% html_text2()}


# FLCGIL ####
 
 read_html("https://www.flcgil.it/search/query/%22piano+nazionale+di+ripresa+e+resilienza%22/channel/comunicati-stampa/method/260")  %>%
   html_elements("ol.bs_search_results h3 a") %>%
   html_attr("href")
 
 read_html("https://www.flcgil.it/search/query/%22piano+nazionale+di+ripresa+e+resilienza%22/channel/comunicati-stampa/method/260")  %>% #multiple links
   html_elements("ul.bs_search_pager a") %>%
   html_attr("href")

# https://www.flcgil.it/

 
# Federmeccanica ####
 
 read_html("https://www.federmeccanica.it/area-stampa/comunicati-stampa/itemlist/filter.html?ftext=pnrr&restcata=24&moduleId=209&Itemid=403&876548d641a632fdab10a27c66c85f28=1") %>%
   html_elements("div#itemListLeading h2.media-h2 a") %>%
   html_attr("href")
 
 # https://www.federmeccanica.it/
 
# Confartigianato
 
 # multiple links
 read_html("https://www.confartigianato.it/?s=%22cura+italia%22&paged=1") %>%
   html_elements("a.page-numbers") %>%
   html_attr("href")
 
 # individual
 title <- read_html("https://www.confartigianato.it/2021/05/credito-appello-di-banche-e-imprese-alle-istituzioni-italiane-continuare-a-garantire-liquidita/") %>%
   html_elements("h1.headInModule.single_post") %>%
   html_text2()
 
 
title <- read_html("https://www.confartigianato.it/2021/05/credito-appello-di-banche-e-imprese-alle-istituzioni-italiane-continuare-a-garantire-liquidita/") %>%
   html_elements("div.pf-content p") %>%
   html_text2() %>% paste0(collapse  = " ")
 
 

# CONFCOMMERCIO ####


i <- "https://www.confcommercio.it/search?q=%22decreto%20rilancio%22&category=2481502&category=39352&category=39912&category=2499453"

df <- read_html(i) %>% html_elements("h4 a") %>%  html_attr("href")

title <- function(i){read_html(i) %>% html_elements("title") %>% html_text2()}
# title <- function(i){read_html(i) %>% html_elements("h1.confcommercio-dettaglio-news--title") %>% html_text2()}
text <- function(i){read_html(i) %>% html_elements("div.confcommercio-dettaglio-news--text") %>% html_text2() %>% paste0(collapse = " ")}
subtitle <- "xxxxx"
date <- function(i){read_html(i) %>% html_elements("span.publish-date") %>% html_text2()}


# df <- plyr::ldply (df, data.frame)
# df <- rename(df, link = X..i..)

# FISAC ####

read_html("https://www.fisac-cgil.it/?s=%22cura+italia%22") %>%
  html_elements("h2.post-title a") %>%
  html_attr("href")


title <- read_html("https://www.fisac-cgil.it/122156/cgil-cisl-uil-su-mancato-riconoscimento-dello-stato-di-malattia-per-i-lavoratori-malati-di-covid-19-asintomatici") %>%
  html_elements("title") %>%
  html_text2()


text <- read_html("https://www.fisac-cgil.it/122156/cgil-cisl-uil-su-mancato-riconoscimento-dello-stato-di-malattia-per-i-lavoratori-malati-di-covid-19-asintomatici") %>%
  html_elements("div.entry-content.entry.clearfix p") %>%
  html_text2() %>% paste0(collapse = " ")






# IT download ####
data <- read.xls("ita_dff.xls",sheet = "links")
data[is.na(data)] = 0
df <- data[data$actor == "confapi",]
# del <- read.csv("delete_text.csv",sep=";",fileEncoding = "UTF-8-BOM")
# "%nin%" <- Negate("%in%")
# a <- df[!duplicated(df$link),]
# df <- df %>% filter(check_run != 1)
df <- df[,1:3]

df$check_run <- 1
df$type <- "NA"

df <- df[,c(1,2,3,9,7,8,4,5,6)]

# short survey 
# read_html(i) %>% html_element("ul.is-style-custom-ul-chevrons.is-style-iconPrimary") %>%
#   html_text2()

# dataset composition ####


df <- plyr::ldply (df, data.frame)
df <- rename(df, link = X..i..)


df$title <- lapply(df$link,title)
df$title <- unlist(df$title)
df$text <- lapply(df$link,text)
df$text <-  unlist(df$text)
df$subtitle <- subtitle # lapply(df$link,subtitle)
df$subtitle <- unlist(df$subtitle)
df$date <- lapply(df$link,date)
df$date <- unlist(df$date)


str_match(df$text,del_t)
df$text <- str_replace_all(df$text,del_t,"")
df <- apply(df,2,as.character)




temp <- list.files(pattern = "*.csv")

df <- list()
for (i in temp) {
  
  d <- read.csv(i,sep = ";")
  df[[i]] = d
  
}
df

df <- bind_rows(df)

write.csv2(df,"ita_compiled/fiom.csv",row.names = F)





write.csv2(df,"ita_compiled/confapi.csv",row.names = F) # other 2 articles to add


# ITA work flow ####
# 
# dfa <- df
# df <- dfa[c(1:37,39:92),]
# 
# df$title <- lapply(df$link,title)
# df$title <- unlist(df$title)
# 
# df$text <- lapply(df$link,text)
# df$text <- unlist(df$text)
# 
# df$date <- lapply(df$link,date)
# df$date <- unlist(df$date)
# 
# df$subtitle <- lapply(df$link,subtitle)
# df$subtitle <- unlist(df$subtitle)
# 
# df$actor <- "confesercenti"
# df$policy <- "fse"
# df$type <- "NA"
# df$check_run <- "NA"
# 
# df <- df[,c(6,7,1,8,4,9,2,3,5)]
# 
# df <- df[!duplicated(df$link),]
# write.csv2(df,"ita_compiled/confesercenti/confsrct_fse.csv",row.names = F)
# 
# 
# df1 <- read.csv("ita_compiled/confesercenti/confsrct_agosto.csv",sep=";")
# df2 <- read.csv("ita_compiled/confesercenti/confsrct_curaitalia.csv",sep=";")
# df3 <- read.csv("ita_compiled/confesercenti/confsrct_fse.csv",sep=";")
# df4 <- read.csv("ita_compiled/confesercenti/confsrct_liquidita.csv",sep=";")
# df5 <- read.csv("ita_compiled/confesercenti/confsrct_nextgeneration.csv",sep=";")
# df6 <- read.csv("ita_compiled/confesercenti/confsrct_pnrr.csv",sep=";")
# df7 <- read.csv("ita_compiled/confesercenti/confsrct_rilancio.csv",sep=";")
# df8 <- read.csv("ita_compiled/confesercenti/confsrct_ristori.csv",sep=";")
# df9 <- read.csv("ita_compiled/confesercenti/confsrct_sostegni.csv",sep=";")
# 
# 
# 
# df <- rbind(df1,df2,df3,df4,df5,df6,df7,df8,df9)
# 
# write.csv2(df,"ita_compiled/confesercenti.csv",row.names = F)
# df <- read.csv("ita_compiled/fim.csv",sep = ";")


# DATA SELECTION #######
# bvmw_pressemitteilungen
# dfrev <- read.csv("deu_compiled/final/bvmw_pressemitteilungen.csv",sep=",") 
dfrev$actor <- "BVMW"
df$ID <- paste0(df$actor,"_",df$date,"_",rownames(df))
df$organization <- "TA"
df$selected = 1
df$note = NA
df$date <- substr(df$date,13,22)
df <- df[,c(8,7,9,1,2,3,4,6,5,10,11)]

# igmetall_presse
df <- read.csv("deu_compiled/final/igmetall_presse.csv",sep=",") 
df$actor <- "IGMETALL"
df$ID <- paste0(df$actor,"_",df$date,"_",rownames(df))
df$organization <- "TU"
df$selected = 1
df$note = NA
df$content <- paste(df$title,df$subtitle,df$text)
df <- df[,-1]
df <- df[,c(7,6,8,1,2,3,4,11,5,9,10)]

# write.csv(df,"deu_compiled/final/igmetall_presse.csv",row.names = F)

# verdi landespressemitteilung
# igmetall_presse
df <- read.csv("deu_compiled/verdi_landespressemitteilung.csv",sep=";") 
df$actor <- "VERDI"
df$subtitle <- " "
df$ID <- paste0(df$actor,"_",df$date,"_",rownames(df))
df$organization <- "TU"
df$selected = 1
df$note = NA
df$content <- paste(df$title,df$subtitle,df$text)
df <- df[,-1]
df <- df[,c(7,6,8,1,2,3,4,11,5,9,10)]

# write.csv(df,"deu_compiled/final/verdi_landespressemitteilung.csv",row.names = F)

# verdi pressemitteilung

df <- read.csv("deu_compiled/final/verdi_pressemitteilung.csv",sep=",") 
df$actor <- "VERDI"
df$subtitle <- " "
df$ID <- paste0(df$actor,"prmt","_",df$date,"_",rownames(df))
df$organization <- "TU"
df$selected = 1
df$note = NA
df$content <- paste(df$title,df$subtitle,df$text)
df <- df[,-1]
df <- df[,c(7,6,8,1,2,3,4,11,5,9,10)]

# write.csv(df,"deu_compiled/final/verdi_pressemitteilung.csv",row.names = F)

# dgb presse

df <- read.csv("deu_compiled/dgb_presse.csv",sep=";")
df$actor <- "DGB"
df$subtitle <- " "
df$ID <- paste0(df$actor,"_","presse",df$date,"_",rownames(df))
df$organization <- "TU"
df$selected = 1
df$note = NA
df$content <- paste(df$title,df$subtitle,df$text)
df <- df[,-1]
df <- df[,c(7,6,8,1,2,3,4,11,5,9,10)]

write.csv(df,"deu_compiled/final/dgb_presse.csv",row.names = F)

# combining sample ####

setwd("C:/Users/rocpa/OneDrive/Desktop/CNT/press_release/deu_compiled/final/bkp/")
list.files()

for (data in list.files()){
  
  # Create the first data if no data exist yet
  if (!exists("dataset")){
    dataset <- read.csv(data, header=TRUE)
  }
  
  # if data already exist, then append it together
  if (exists("dataset")){
    tempory <-read.csv(data, header=TRUE)
    dataset <-unique(rbind(dataset, tempory))
    rm(tempory)
  }
}

dataset$content <- tolower(dataset$content)
dataset$content <- str_replace_all(dataset$content,"u¨","ü")
dataset$content <- str_replace_all(dataset$content,"\n"," ")


# bvmw <- read.csv("bvmw_pressemitteilungen.csv",sep=",") 
# # bvmw$source <- "pressemitteilungen"
#  # bvmw$ID <- paste0(bvmw$actor,"_",bvmw$source,"_",bvmw$date,"_",rownames(bvmw))
#  # bvmw <- bvmw[,c(1,2,4,3,5:11)]
#  # write.csv(bvmw,"deu_compiled/final/bvmw_pressemitteilungen.csv",row.names = F)
#  
# dgb_presse <- read.csv("dgb_presse.csv",sep=",") 
# # dgb_presse$ID <- paste0(dgb_presse$actor,"_",dgb_presse$source,"_",dgb_presse$date,"_",rownames(dgb_presse))
# # dgb_presse <- dgb_presse[,c(1:3,12,4:11)]
# # # dgb_presse$source <- "presse"
# #  write.csv(dgb_presse,"deu_compiled/final/dgb_presse.csv",row.names = F)
# ig_presse <- read.csv("igmetall_presse.csv",sep=",") 
# # ig_presse$ID <- paste0(ig_presse$actor,"_",ig_presse$source,"_",ig_presse$date,"_",rownames(ig_presse))
# # ig_presse <- ig_presse[,c(1:3,12,4:11)]
# # # ig_presse$source <- "presse"
# #  write.csv(ig_presse,"deu_compiled/final/igmetall_presse.csv",row.names = F)
# verdi_landes <- read.csv("verdi_landespressemitteilung.csv",sep=",") 
# # verdi_landes$ID <- paste0(verdi_landes$actor,"_",verdi_landes$source,"_",verdi_landes$date,"_",rownames(verdi_landes))
# # verdi_landes <- verdi_landes[,c(1:3,12,4:11)]
# # # verdi_landes$source <- "landespressemitteilung"
# #  write.csv(verdi_landes,"deu_compiled/final/verdi_landespressemitteilung.csv",row.names = F)
# verdi_pressemitteilung <- read.csv("verdi_pressemitteilung.csv",sep=",")
# verdi_pressemitteilung$ID <- paste0(verdi_pressemitteilung$actor,"_",verdi_pressemitteilung$source,"_",verdi_pressemitteilung$date,"_",rownames(verdi_pressemitteilung))
# verdi_pressemitteilung <- verdi_pressemitteilung[,c(1:3,12,4:11)]
# # verdi_pressemitteilung$source <- "pressemitteilung"
#  write.csv(verdi_pressemitteilung,"deu_compiled/final/verdi_pressemitteilung.csv",row.names = F)






# df <- rbind(bvmw,dgb_presse, ig_presse,verdi_landes,verdi_pressemitteilung)


# with -
df_word <- unique(stringr::str_extract_all(dataset$content, 
                                            regex("\\b[:alnum:]*\\-?[:alnum:]*\\-?[:alnum:]*kredit\\-?[:alnum:]*\\-?[:alnum:]*", 
                                                  ignore_case = TRUE)))

# without - 
df_word <- unique(stringr::str_extract_all(dataset$content, 
                                           regex("\\b[:alnum:]*\\ ?[:alnum:]*\\ ?[:alnum:]* kredit\\ ?[:alnum:]*\\ ?[:alnum:]*", 
                                                 ignore_case = TRUE)))

df_word


# convert to date annd filter
dataset$date <- as.Date(dataset$date,format = "%d.%m.%Y")

dataset <- dataset %>% filter(dataset$date >= "2020-01-01" & dataset$date <= "2021-12-31")

deu_key <- read.xls("keywords_pr.xls",sheet = "DEU")[,1]
deu_key <- paste0("\\b",deu_key,"\\b",collapse="|")

dataset_key <- dataset %>% filter(str_detect(content, regex(deu_key, ignore_case=TRUE)))

deu_xtr <- read.xls("keywords_pr.xls",sheet = "DEU_EXTRA")[,1]
deu_xtr <- paste0("\\b",deu_xtr,"\\b",collapse="|")

dataset_xtr <- dataset %>% filter(str_detect(content, regex(deu_xtr, ignore_case=TRUE)))

cvd_xtr <- read.xls("keywords_pr.xls",sheet = "COVIDXTR")[,1]
cvd_xtr <- paste0("\\b",cvd_xtr,"\\b",collapse="|")

dataset_xtr <- dataset_xtr %>% filter(str_detect(content, regex(cvd_xtr,ignore_case = TRUE)))
dataset_xtr <- dataset_xtr %>% filter(!(link %in% dataset_key$link))

write.csv2(dataset_key, file = "deu_compiled/final/dataset_de.csv",row.names = F)
write.csv2(dataset_xtr, file = "deu_compiled/final/dataset_xtr.csv",row.names = F)


# dfss <- data.frame(team=c("Mavs", "Heat", "Pacers", "Cavs", "Mavs HEAT"),
#                  points=c(99, 90, 86, 103, 22))	
# 
# # dfss[str_detect(dfss$team, "avs|ea"), ]
#  dfss %>% filter(str_detect(team,regex("\\bMavs\\b|\\bea\\b", ignore_case = T)))





