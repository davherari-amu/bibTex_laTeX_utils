# Libraries {{{
import sys
import getopt
from pybtex.database import parse_file
from pybtex.database import parse_string
from pybtex.database import BibliographyData as bbd
from pybtex.database import Entry
from unidecode import unidecode
from pdb import set_trace
from string import ascii_lowercase
from doi2bib import doi2bib
from unifyBib import AddDoiAsNote
from unifyBib import ReplaceInitialSpecialCharaters
from unifyBib import UnifiedEntryName
from unifyBib import GetUnifiedEntryName
# }}}

# Functions {{{
# Get bib from dois {{{
def GetBibFromDois(doilist, lenAutName, doiNote, dummURL):
    # Initialisation of entries and bibTeX
    entries = []
    bibTeX = ""
    # Add bib for each doi
    for doi in doilist:
        # Get doi as bib entry
        bibEntry = doi2bib(doi.strip())
        bibLines = bibEntry.splitlines(0)
        # Set entry name {{{
        # Get default entry name, usually: @name_year
        entryName = bibLines[0]
        str0 = entryName.find('{') + 1
        str1 = entryName.find(',')
        entryName = entryName[str0 : str1]
        if not entryName in entries:
            # Keep entry name if it has not been used yet
            entries.append(entryName)
        else:
            # Modify it using an extra letter if the name already exists
            # Something like: @name_yeara
            for letter in ascii_lowercase:
                if not entryName + letter in entries:
                    entries.append(entryName + letter)
                    bibLines[0] = bibLines[0][:str0] + entryName + letter + ','
                    bibEntry = ''
                    for line in bibLines:
                        bibEntry += line + '\n'
                    break
        # }}}
        # Correction of ampersand symbols
        bibEntry = bibEntry.replace(r'{\&}amp$\mathsemicolon$', '&')
        # Add URL as dummy if necessary
        if dummURL:
            bibEntry = bibEntry.replace(r'url = {', 'dummURL = {')
        # Add entry
        bibTeX += "\n{}".format(bibEntry)
    return bibTeX
# }}}

# Add by doi {{{
def AddByDoi(inFile, iniBib, lenAutName, doiNote, dummURL):
    # Get initial bibTex {{{
    # Initial bib tex object
    old_bib = parse_file(iniBib)
    # Get entries and dois
    old_entries = []
    old_dois    = []
    for entryName, entry in old_bib.entries.items():
        old_entries.append(entryName)
        if "doi" in entry.fields:
            doi = entry.fields["doi"]
            old_dois.append(doi.lower())
    # }}}
    # Bib file from dois {{{
    with open(inFile, 'r') as File:
        dois = File.readlines()
    # Lower dois without special characters
    dois = [doi.strip().lower() for doi in dois]
    dois = list(filter(("").__ne__, dois))
    # Check whether dois are new
    newDois = []
    for doi in dois:
        if not doi in old_dois:
            newDois.append(doi)
    print(newDois)
    # Get new entries
    if len(newDois) == 0:
        message = "The doi list does not contain any new entry"
        raise ValueError(message)
    newBib_text = GetBibFromDois(newDois, lenAutName, doiNote, dummURL)
    # }}}
    # Unify new entry names {{{
    newBib = parse_string(newBib_text, "bibtex")
    entryNames = old_entries[:]
    # Map entry name with default entry name of the new dois
    keyMap = {}
    for entryName, entry in newBib.entries.items():
        newName = GetUnifiedEntryName(entry, entryNames,
                                      maxNumAutLets = lenAutName)
        keyMap[newName] = entryName
        entryNames.append(entryName)
    # Make unified new bib
    uniNewBib = bbd()
    for newName, name in keyMap.items():
        type_   = newBib.entries[name].type
        fields  = newBib.entries[name].fields
        persons = newBib.entries[name].persons
        entry = Entry(type_, fields, persons)
        uniNewBib.entries[unidecode(newName)] = entry
    # }}}
    return uniNewBib
# }}}
# }}}

# __main__ {{{
if __name__ == '__main__':
    # Input and output files {{{
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:b:l:du')
        if len(args)>0:
            raise getopt.GetoptError('Too many arguments!')
    except getopt.GetoptError:
        print('Wrong call! The excecution can have the following arguments:')
        print('To indicate the input file name with new dois: -i "fileName.txt"')
        print('To indicate the input of the current bib file: -b "fileName.bib"')
        print('To indicate the length of the author last-name letters: -l length (optional)')
        print('To indicate adding doi as note: -d (optional)')
        print('To indicate adding url as dummy: -u (optional)')
        raise
    # Initialisation
    doiNote = False
    dummURL = False
    inFile  = None
    iniBib = None
    lenAutName = 3
    for opt, arg in opts:
        # File name
        if opt in ['-i']:
            inFile = arg
        if opt in ['-b']:
            iniBib = arg
        if opt in ['-l']:
            lenAutName = eval(arg)
        if opt in ['-d']:
            doiNote = True
        if opt in ['-u']:
            dummURL = True
    if inFile is None:
        raise("Wrong call! The input file is not present. Use -i 'fileName.txt'")
    if iniBib is None:
        raise("Wrong call! The input file is not present. Use -i 'fileName.bib'")
    if not inFile[-4:] == '.txt':
        raise("Error: the input file must be a .txt file")
    # }}}
    # Append new dois
    newBib = AddByDoi(inFile, iniBib, lenAutName, doiNote, dummURL)
    # Append
    # Load bibTex as text
    with open(iniBib, 'a') as fle:
        fle.write("\n")
        fle.write(newBib.to_string("bibtex"))
# }}}
