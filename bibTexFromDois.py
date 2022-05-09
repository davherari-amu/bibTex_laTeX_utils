# Libraries {{{
import sys
import getopt
from doi2bib import doi2bib
from unifyBib import Uni_Doi_and_name
# }}}

# Input and output files {{{
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:o:l:')
    if len(args)>0:
        raise getopt.GetoptError('Too many arguments!')
except getopt.GetoptError:
    print('Wrong call! The excecution can have the following arguments:')
    print('To indicate the input file name: -i "fileName.txt"')
    print('To indicate the output file name: -o "fileName.bib" (optional)')
    print('To indicate the length of the author last-name letters: -l length (optional)')
    raise
# Initialisation
inFile  = None
outFile = None
lenAutName = 3
for opt, arg in opts:
    # File name
    if opt in ['-i']:
        inFile = arg
    if opt in ['-o']:
        outFile = arg
    if opt in ['-l']:
        lenAutName = eval(arg)
if inFile == None:
    raise("Wrong call! The input file is not present. Use -i 'fileName.json'")
if not inFile[-4:] == '.txt':
    raise("Error: the input file must be a .txt file")
if outFile == None:
    outFile = inFile[:-4] + '.bib'
if not outFile[-4:] == '.bib':
    raise("Error: the output file must be a .bib file")
# }}}

# Get initial bibTex {{{
""" The initial bibTex is built based only on the information present in
websites (DOIs)"""
# Get a list with the DOIs
with open(inFile, 'r') as File:
    dois = File.readlines()
# Write initial bibTex
with open(outFile, 'w') as File:
    for doi in dois:
        bibtex = doi2bib(doi[:-1])
        File.write(bibtex)
        File.write('\n')
# }}}

# Get unified bibTex {{{
Uni_Doi_and_name(outFile, outFile, lenAutName)
# }}}