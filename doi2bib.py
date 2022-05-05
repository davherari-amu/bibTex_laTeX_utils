"""Code copied from:
https://scipython.com/blog/doi-to-bibtex/
"""
# Libraries {{{
import sys
import urllib.request
from urllib.error import HTTPError
# }}}

# Parameters {{{
BASE_URL = 'http://dx.doi.org/'
# }}}

# Functions {{{
def doi2bib(doi):
    url = BASE_URL + doi
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/x-bibtex')
    try:
        with urllib.request.urlopen(req) as f:
            bibtex = f.read().decode()
    except HTTPError as e:
        if e.code == 404:
            print('DOI not found.')
        else:
            print('Service unavailable.')
        sys.exit(1)
    return bibtex
# }}}

# Test {{{
if __name__ == '__main__':
    print('Example with 10.1177/1470593113512323')
    doi = '10.1177/1470593113512323'
    print(doi2bib(doi))
# }}}
