library(httr)
library(xml2)
library(dplyr)

# avoid http2 errors with libcurl / entrez
httr::set_config(httr::config(http_version = 0))

PUBMED_STUDY_SEARCH_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_STUDY_FETCH_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

parse_search_result_pmids <- function(response) {
  read_xml(response$content) %>%
    xml_find_first('//IdList') %>% 
    xml_find_all('//Id') %>% 
    xml_text() %>% 
    as.numeric()
}

execute_search <- function(term, step_size=1e4, max_results = 5e5) {
  
  current_index <- 0
  search_complete <- FALSE
  
  all_pmids <- c()
  
  while (!search_complete && length(all_pmids) < max_results) {
    url <- paste0(
      PUBMED_STUDY_SEARCH_ENDPOINT,
      '?',
      'db=pubmed',
      '&sort=pub+date', # TODO, random order would be best?
      '&term=', URLencode(term),
      '&retmax=', step_size,
      '&retstart=', length(all_pmids)
    )
    

    step_results <- parse_search_result_pmids(RETRY("GET", url, times=5))
    
    Sys.sleep(.5)
    
    all_pmids <- c(all_pmids, step_results) 
    if (length(step_results) < step_size) {
      search_complete <- TRUE
    }
  }
  
  return(all_pmids)
}

extract_data <- function(response) {
  articles <- read_xml(response$content) %>%
    xml_find_all('//PubmedArticle')
  abstract_list <- articles %>%
    lapply(function(article) {
      pmid <- article %>%
        xml_find_first('.//PMID') %>% 
        xml_text() %>% 
        as.numeric()
      abstract <- article %>%
        xml_find_all('.//AbstractText') %>%
        xml_text() %>%
        paste(collapse=' ')
      title <- article %>%
        xml_find_first('.//ArticleTitle') %>%
        xml_text()
      
      list(pmid = pmid,
           abstract = abstract,
           title = title)
    })
  abstracts <- do.call(rbind.data.frame, c(abstract_list, list(stringsAsFactors=FALSE)))
  
  pubtype_list <- articles %>%
    lapply(function(article) {
      pmid <- article %>%
        xml_find_first('.//PMID') %>% 
        xml_text() %>% 
        as.numeric()
      publication_types <- article %>%
        xml_find_all('.//PublicationType') %>%
        xml_text()
      
      data.frame(
        pmid = pmid,
        publication_type = publication_types,
        stringsAsFactors = FALSE
      )
    })
    publication_types <- do.call(rbind, c(pubtype_list, list(stringsAsFactors=FALSE)))
  
  list(abstracts = abstracts, publication_types = publication_types)
}


fetch_abstracts_and_types <- function(pmids, search_term) {
  abstracts <- data.frame()
  publication_types <- data.frame()
  
  step_size <- 100
  for (lower_ix in seq(1, length(pmids), by=step_size)) {
    
    print(paste0(search_term, ': ', as.character(lower_ix), ' / ', as.character(length(pmids))))
    
    upper_ix <- min(length(pmids), (lower_ix + step_size - 1))
    
    url <- paste0(
      PUBMED_STUDY_FETCH_ENDPOINT,
      '?',
      'db=pubmed',
      '&id=', paste(pmids[lower_ix:upper_ix], collapse=','),
      '&rettype=xml'
    )
    
    response <- RETRY("GET", url, times=5)

    Sys.sleep(.5)
    
    results <- extract_data(response)

    abstracts <- rbind(abstracts, results$abstracts, stringsAsFactors=FALSE)
    publication_types <- rbind(publication_types, results$publication_types, stringsAsFactors=FALSE)
  }
  
  abstracts$term <- search_term
  
  list(
    abstracts = abstracts,
    publication_types = publication_types
  )
}

fetch_all_studies <- function(publication_types=c(
    'Case Reports', # note these are all "Study Characteristics" in the nlm hierarchy
    'Clinical Conference',
    'Clinical Study',
    'Comparative Study',
    'Consensus Development Conference',
    'Evaluation Study',
    'Meta-Analysis',
    'Multicenter Study',
    'Scientific Integrity Review',
    'Systematic Review',
    'Twin Study',
    'Validation Study'
  )) {
  abstracts <- data.frame()
  publications <- data.frame()
  
  tryCatch({
    for (publication_type in publication_types) {
      search_term <- paste0('"', publication_type, '" [Publication Type]') 
      search_results <- execute_search(search_term, step_size = 1e3, max_results = 5e5) # TODO, this should really be weighted according to freauency, to keep class priors accurate
      studies <- fetch_abstracts_and_types(search_results, search_term)
      
      abstracts <- rbind(abstracts, studies$abstracts, stringsAsFactors=FALSE)
      publications <- rbind(publications, studies$publication_types, stringsAsFactors=FALSE)
    }
  }, error=function(e){
    print(paste0('Error, catching to write out intermediate results'))
    print(e)
  })

  
  list(
    abstracts = abstracts %>% distinct(pmid, .keep_all = TRUE),
    publications = publications %>% distinct(pmid, publication_type, .keep_all = TRUE)
  )
}

all_studies <- fetch_all_studies()

write.table(all_studies$abstracts, 'abstracts.csv',
            sep=',', col.names = TRUE, row.names=FALSE)
write.table(all_studies$publications, 'publications.csv',
            sep=',', col.names = TRUE, row.names=FALSE)


#############
"
search_results <- execute_search('\"case reports\" [Publication Type]', step_size = 1e3, max_results = 2e3)
studies <- fetch_abstracts_and_types(search_results, 'blah')

studies$publication_types %>%
  group_by(pmid) %>%
  summarize(
    study_types = paste(publication_type, collapse = ', ')
  ) %>%
  group_by(study_types) %>%
  count(sort = T)
"

