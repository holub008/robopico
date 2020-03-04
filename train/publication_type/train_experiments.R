library(dplyr)
library(tidytext)
library(xgboost)
library(readr)
library(tidyr)

intersects <- function(a, b) {
  length(intersect(a, b)) > 0
}

resolve_publication_type <- function(pubs) {
  pubs %>%
    group_by(pmid) %>%
    summarize(
      # these categories are sort-of-reasonably mutually exclusive. 
      # note that pub type tagging is super questionable for a lot of things (e.g. comparative studies are often also clinical studies)
      publication_type = ifelse(
        intersects(publication_type, c('Case Reports')), 'Case Report',
        ifelse(intersects(publication_type, c('Systematic Review', 'Meta-Analysis')), 'Systematic Review',
               ifelse(intersects(publication_type, c('Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III', 
                                              'Clinical Trial, Phase IV', 'Randomized Controlled Trial', 'Controlled Clinical Trial')), 
                      'RCT',
                      'other'
               )
        )
      )
    )
}

# note, r read.csv & read.table are incapable of reading files that they wrote (without fiddling with who knows what arguments) :(
# read_delim finds a very small number problems in the csv, but seems really good (good enough)
abstracts <-  read_delim(file="abstracts_all.csv", delim=',', escape_double=FALSE, escape_backslash=TRUE, quote="\"")
publication_types <-  read_delim(file="publications_all.csv", delim=',', escape_double=FALSE, escape_backslash=TRUE, quote="\"")

final_abstracts <- abstracts %>%
  filter(!is.na(abstract)) %>%
  filter(!is.na(term) & startsWith(term, "\"")) %>% # on my dataset, this clears out 4 (apparently) incorrectly parsed rows
  sample_frac(.1)

# downsampled_abstracts %>% write.table('abstracts_downsampled.csv', row.names=F, col.names = T, sep=',')
final_publications <- downsampled_abstracts %>%
  select(pmid) %>%
  inner_join(publication_types, on='pmid') %>%
  resolve_publication_type()

abstracts_parsed <- final_abstracts %>%
  unnest_tokens(bigram, abstract, token = "ngrams", n = 2) %>%
  separate(bigram, c('word1', 'word2'), sep=" ") %>%
  filter(!word1 %in% stop_words$word) %>%
  filter(!word2 %in% stop_words$word) %>%
  unite(bigram, word1, word2) %>%
  group_by(bigram) %>%
  filter(n() > 100)
abstracts_sparse <- abstracts_parsed %>%
  cast_sparse(pmid, bigram)

titles_parsed <- final_abstracts %>%
  unnest_tokens(bigram, title, token = "ngrams", n = 2) %>%
  separate(bigram, c('word1', 'word2'), sep=" ") %>%
  filter(!word1 %in% stop_words$word) %>%
  filter(!word2 %in% stop_words$word) %>%
  unite(bigram, word1, word2) %>%
  group_by(bigram) %>%
  filter(n() > 50) 
titles_sparse <- titles_parsed %>%
  cast_sparse(pmid, bigram)

  
train_data <- rBind.fill(titles_sparse, abstracts_sparse)



