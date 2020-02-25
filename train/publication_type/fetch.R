library(httr)
library(xml2)

PUBMED_STUDY_SEARCH_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_STUDY_FETCH_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

parse_search_result_pmids <- function(response) {
  
}

execute_search <- function(term, step_size=1e4, max_results = 5e5) {
  
  current_index <- 0
  search_complete <- FALSE
  
  all_pmids <- c()
  
  while (!search_complete && len(all_pmids) < max_results) {
    url <- paste0(
      PUBMED_STUDY_SEARCH_ENDPOINT,
      '?',
      'db=pubmed',
      '&sort=pub+date', # TODO, random order would be best?
      '&term=', URLencode(term),
      '&retmax=', step_size,
      '&retstart=', len(all_pmids) # TODO check off by one
    )
    
    step_results <- parse_search_result_pmids(GET(url))
    all_pmids <- c(all_pmids, step_results) 
    if (len(step_results) < step_size) {
      search_complete <- TRUE
    }
  }
  
  return(all_pmids)
}

ts_results <- execute_search('"twin Study" [Publication Type]')
