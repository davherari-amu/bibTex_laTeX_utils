# bibTex_laTeX_utils
This repository contains some utilities to manage bibTex files.

## unifyBib.py
Add DOIs as notes so that LaTeX can generate a hyperlink in the
reference section.
Unify the entry name as {#1}author{#2}year:
        #1 refers to the first -l letters of the last name of the first
           author in lowercase and
        #2 refers to the last two digits of the year.

Script options -i, -o and -l
        -i: the name of the existing bibtex file (.bib) (mandatory),
        -o: the name of the out bibtex file (.bib) (optional, if not
            present the input file is overwritten), and
        -l: the number of author-last-name letters that should be
            included in each entry name (optinal, default: 3).

Necessary python libraries:
sys
getopt
pybtex
