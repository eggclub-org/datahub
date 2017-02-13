from url_fetcher import UrlFetcher
from extractor import Extractor

def extract_url (url, depth):
    fetcher = UrlFetcher()
    domain = fetcher.get_domain(url)
    links = fetcher.getFullLinks(url, depth)
    extractor = Extractor()
    for url in links:
        std_url = fetcher.standardize_url(url)
        if (fetcher.check_url_in_blacklist(domain,url) is False):
            doc = fetcher.get_domain(url)
            if (doc):
                article = extractor.extract_content(doc,domain,std_url)
