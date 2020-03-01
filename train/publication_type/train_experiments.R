library(dplyr)
library(tidytext)
library(xgboost)
library(readr)

# note, r read.csv & read.table are incapable of reading files that they wrote (without fiddling with who knows what arguments) :(
# read_delim finds a very small number problems in the csv, but seems really good (good enough)
abstracts <-  read_delim(file="abstracts_all.csv", delim=',', escape_double=FALSE, escape_backslash=TRUE, quote="\"")
publication_types <-  read_delim(file="publications_all.csv", delim=',', escape_double=FALSE, escape_backslash=TRUE, quote="\"")

downsampled_abstracts <- abstracts %>%
  sample_frac(.1)

# downsampled_abstracts %>% write.table('abstracts_downsampled.csv', row.names=F, col.names = T, sep=',')
downsampled_publications <- downsampled_abstracts %>%
  select(pmid) %>%
  inner_join(publication_types, on='pmid')

resolve_publication_type <- function(pubs) {
  pubs %>%
    group_by(pmid)
    summarize(
      # these categories are sort-of-reasonably mutually exclusive. 
      # note that pub type tagging is super questionable for a lot of things (e.g. comparative studies are often also clinical studies)
      publication_type = ifelse(
        publication_type %in% c('Case Reports'), 'Case Report',
        ifelse(publication_type %in% c('Systematic Review', 'Meta-Analysis'), 'Systematic Review',
               ifelse(publication_type %in% c('Clinical Trial, Phase I', 'Clinical Trial, Phase II', 'Clinical Trial, Phase III', 
                                              'Clinical Trial, Phase IV', 'Randomized Controlled Trial', 'Controlled Clinical Trial'), 'RCT',
                      ifelse(publication_type %in% c('Observational Study',), 'Observational Study', 'other')
                      )
               )
      )
    )
}
