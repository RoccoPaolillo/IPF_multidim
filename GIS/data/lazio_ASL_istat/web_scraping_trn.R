library(tidyverse)
library(rvest)
# Kasper Welbers github
# https://github.com/ccs-amsterdam/r-course-material/blob/master/tutorials/rvest.md#what-is-web-scraping-and-why-learn-it
# Kasper Welbers video
# https://www.youtube.com/watch?v=9GR26Y4z_v4

# Training #####
url = "https://raw.githack.com/ccs-amsterdam/r-course-material/master/miscellaneous/simple_html.html"

read_html(url) %>%
 # html_element("#steve") %>% # id
 # html_element(".someTable") %>% # class, first element
  html_elements(".someTable") %>% # class, all elements
  html_table()

# Links from webpage

'https://en.wikipedia.org/wiki/Hyperlink' %>%
  read_html() %>%
  html_elements('a') %>%
  length()

html = 'https://bit.ly/3lz6ZRe' %>% read_html # text unpolished \n
html %>% html_element('.leftColumn') %>% html_text()

html = 'https://bit.ly/3lz6ZRe' %>% read_html
html %>% html_element('.leftColumn') %>% html_text2() # polished text

html %>% html_elements('#exampleTable') %>% html_attrs() # attributes

html %>% html_elements('a') %>% html_attr('href') # to get the links of hyperlinks

# if id


html = read_html('https://www.imdb.com/name/nm0000195/')

name_overview = html %>% 
  html_element('#name-overview-widget')

html_text2(name_overview)  

name = name_overview %>%             # take an exact name within span h1 >. itemprop
  html_element('h1 .itemprop') %>% 
  html_text2()

job_categories = name_overview %>% 
  html_elements('#name-job-categories .itemprop') %>%
  html_text2()

born_date = name_overview %>%
  html_element('#name-born-info time') %>% 
  html_attr('datetime')

born_date

born_location = name_overview %>%             # to pick a direct child. Here #name-born-info is a div
  html_element('#name-born-info > a') %>% 
  html_text2()

born_location

html = read_html('https://www.imdb.com/name/nm0000195/')

name_overview = html %>% html_element('#name-overview-widget')
name = name_overview %>% html_element('h1 .itemprop') %>% html_text2()
job_categories = name_overview %>% html_elements('#name-job-categories .itemprop') %>% html_text2()
bio = name_overview %>% html_element('#name-bio-text') %>% html_text2()
born_date = name_overview %>% html_element('#name-born-info time') %>% html_attr('datetime')
born_location = name_overview %>% html_element('#name-born-info > a') %>% html_text2()


tb <- tibble(name, born_date, born_location, bio,
       job_categories = paste(job_categories, collapse=' | '))

html = read_html('https://www.imdb.com/title/tt0362270/fullcredits?ref_=tt_cl_sm')
html %>% html_element('.cast_list') %>% html_table()

# for a nested class e.g. table, here to pick url to scrape later

bio_urls = html %>% html_elements('.cast_list .primary_photo a') %>% html_attr('href')
head(bio_urls, 5)  # show just first 5 

bio_urls = paste('https://imdb.com', bio_urls, sep='')
head(bio_urls, 5)  # show just first 5 

# loop over item or url

top3_bio_urls = head(bio_urls, 3)

results = list()
for (bio_url in top3_bio_urls) {
  bio_tibble = tibble(name = 'name goes here', born_date = "date goes here")
  results[[bio_url]] = bio_tibble
}

results

bind_rows(results, .id = 'url')

# put all together

## the URL for the cast page of a movie
movie_cast_url = 'https://www.imdb.com/title/tt0362270/fullcredits?ref_=tt_cl_sm'

## get URLs for every cast member
bio_urls = read_html(movie_cast_url) %>%
  html_elements('.cast_list .primary_photo a') %>% 
  html_attr('href')
bio_urls = paste('https://imdb.com', bio_urls, sep='')

## take just first 5 cast members for demo
top5_bio_urls = head(bio_urls, 5)

## loop over cast member bio_urls
results = list()
for (bio_url in top5_bio_urls) {
  message('Scraping URL: ', bio_url)
  
  ## read the html for the bio page
  bio_html = read_html(bio_url) 
  
  ## parse the bio page
  name_overview = bio_html %>% html_element('#name-overview-widget')
  name = name_overview %>% html_element('h1 .itemprop') %>% html_text2()
  job_categories = name_overview %>% html_elements('#name-job-categories .itemprop') %>% html_text2()
  bio = name_overview %>% html_element('#name-bio-text') %>% html_text2()
  born_date = name_overview %>% html_element('#name-born-info time') %>% html_attr('datetime')
  born_location = name_overview %>% html_element('#name-born-info > a') %>% html_text2()
  
  ## save results
  bio_tibble = tibble(name, born_date, born_location, bio,
                      job_categories = paste(job_categories, collapse=' | '))
  results[[bio_url]] = bio_tibble # add one line to list
}

d = bind_rows(results, .id = 'url')
d

# redo scraping with functions
parse_bio_page <- function(bio_url) {
  message('Scraping URL: ', bio_url)
  
  html = read_html(bio_url) 
  name_overview = html %>% html_element('#name-overview-widget')
  name = name_overview %>% html_element('h1 .itemprop') %>% html_text2()
  job_categories = name_overview %>% html_elements('#name-job-categories .itemprop') %>% html_text2()
  bio = name_overview %>% html_element('#name-bio-text') %>% html_text2()
  born_date = name_overview %>% html_element('#name-born-info time') %>% html_attr('datetime')
  born_location = name_overview %>% html_element('#name-born-info > a') %>% html_text2()
  
  ## return tibble
  tibble(name, born_date, born_location, bio, job_categories = paste(job_categories, collapse=' | '))
}

get_bio_urls <- function(cast_url, max_urls=Inf) {
  bio_urls = read_html(cast_url) %>%
    html_elements('.cast_list .primary_photo a') %>% 
    html_attr('href') %>%
    head(max_urls)
  
  paste('https://imdb.com', bio_urls, sep='')
} 

movie_cast_url = 'https://www.imdb.com/title/tt0362270/fullcredits?ref_=tt_cl_sm'
bio_urls = get_bio_urls(movie_cast_url, max_urls=5)

results = list()
for (bio_url in bio_urls) {
  results[[bio_url]] = parse_bio_page(bio_url)
}

bind_rows(results, .id = 'url')










































