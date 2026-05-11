import re
from urllib.parse import urlparse

IMPORTANT_PATHS = [
    "about",
    "team",
    "people",
    "portfolio",
    "contact",
    "apply",
    "pitch",
    "faq",
    "founders",
    "companies",
    "investments",
    "investment"
]

def discover_links(markdown, base_url):

    base_domain = urlparse(base_url).netloc

    links = re.findall(
        r'\[.*?\]\((.*?)\)',
        markdown
    )

    internal_links = []

    for link in links:     
        
        link_domain = urlparse(link).netloc

        if base_domain in link_domain or link_domain in base_domain:
            internal_links.append(link)

    important_links = []

    for link in internal_links:
        lower_link = link.lower()

        for keyword in IMPORTANT_PATHS:
            if keyword in lower_link:
                important_links.append(link)
                break

    important_links = list(set(important_links))
    
    return important_links