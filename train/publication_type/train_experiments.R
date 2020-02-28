library(dplyr)
library(tidytext)
library(xgboost)

abstracts <- read.csv('./abstracts.csv', stringsAsFactors = FALSE)
publication_types <- read.csv('./publications.csv', stringsAsFactors = FALSE)

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