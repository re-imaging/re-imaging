# cleans the image creator tag and counts them; its rough

library(RSQLite)
library(tidyverse)
library(knitr)

conn  <- dbConnect(RSQLite::SQLite(), 'data/arxiv_db_images.sqlite3')
q  <-  'select creator, count(creator) as n from images group by creator order by n desc'
res  <-  dbGetQuery(conn, q)

res %>% select(creator) %>%  group_by(creator) %>% count(creator) %>%  arrange(desc(n)) %>% head()
res %>% mutate(creator_clean = str_extract(str_replace_all(tolower(str_trim(creator)), pattern = '(\\d+(\\.\\d*)*)|(version)|wolfram|adobe|gpl|gnu |microsoft|the |v\\.|[:punct:]|www|http', ''), pattern = '([:alpha:]+ )?'))  %>%
    count(creator_clean) %>%
    slice_max(n=31, order_by = n ) %>%
    kable('html')

