# Libraries {{{
import sys
import getopt
from pybtex.database import parse_file
from pybtex.database import BibliographyData as bbd
from pybtex.database import Entry
from unidecode import unidecode
from pdb import set_trace
from string import ascii_lowercase
# }}}

# Functions {{{
# Add DOI as a note {{{
def AddDoiAsNote(bibData, message = 'DOI:'):
    """This makes bibtex generate a hyperlink to the document DOI."""
    bib = bibData
    for key in bib.entries:
        try:
            doi = bib.entries[key].fields['doi']
            bib.entries[key].fields['note'] = message + r' \href{https://doi.org/' + doi + '}' + '{' + doi + '}'
        except KeyError:
            print('Warnig: the entry "' + key + '" does not have doi.')
        except:
            raise
    return bib
# }}}

# Replace special characters of all initial letters in the name {{{
def ReplaceInitialSpecialCharaters(bibData):
    # Loop over bib entries
    for key in bibData.entries:
        # Loop over article authors
        authors = bibData.entries[key].persons["author"]
        for author in authors:
            # Loop over author first names
            first_names = author.first_names
            for k1 in range(len(first_names)):
                name = first_names[k1]
                author.first_names[k1] = unidecode(name[0]) + name[1:].lower()
            # Loop over author last names
            last_names = author.last_names
            for k1 in range(len(last_names)):
                name = last_names[k1]
                author.last_names[k1] = unidecode(name[0]) + name[1:].lower()
    return bibData
# }}}

# Get unified entry name {{{
def GetUnifiedEntryName(entry, entryNames, maxNumAutLets = 3):
    # Set default entry name {{{
    # First author last name
    name = entry.persons["author"][0].last_names[0]
    # Year
    try:
        year = entry.fields["year"]
    except KeyError:
        year = entry.fields["EarlyAccessDate"]
        year = year.split()[1]
    except:
        raise
    # Make name, for example abc12 when maxNumAutLets = 3
    lenName = min(len(name), maxNumAutLets)
    newEntry = name[:lenName].lower() + year[2:]
    newEntry = unidecode(newEntry)
    # }}}
    # If the default entry name has already been used try to change it
    # adding an extra letter, as in abc12a
    if newEntry in entryNames:
        fail = True
        for letter in ascii_lowercase:
            if not newEntry + letter in entryNames:
                newEntry += letter
                fail = False
                break
        if fail:
            message = "Error: too many entries have the same name and year."
            raise ValueError(message)
    # If the default entry has not been used yet
    return newEntry
# }}}

# Set unified entry name {{{
def UnifiedEntryName(bibData, maxNumAutLets = 3):
    # Get keys and names {{{
    keys = {}
    for key in bibData.entries:
        name = bibData.entries[key].persons["author"][0].last_names[0]
        try:
            year = bibData.entries[key].fields["year"]
        except KeyError:
            year = bibData.entries[key].fields["EarlyAccessDate"]
            year = year.split()[1]
        except:
            raise
        lenName = min(len(name), maxNumAutLets)
        newKey = name[:lenName].lower() + year[2:]
        newKey = unidecode(newKey)
        if not newKey in keys:
            keys[newKey] = key
        else:
            fail = True
            for letter in ascii_lowercase:
                if not newKey + letter in keys:
                    keys[newKey + letter] = key
                    fail = False
                    break
            if fail:
                raise("Error: too many entries have the same name and year.")
    # }}}
    # New data {{{
    newBib = bbd()
    for newKey in keys:
        oldKey = keys[newKey]
        type_   = bibData.entries[oldKey].type
        fields  = bibData.entries[oldKey].fields
        persons = bibData.entries[oldKey].persons
        entry = Entry(type_, fields, persons)
        newBib.entries[unidecode(newKey)] = entry
    # }}}
    return newBib
# }}}

# Uni_Doi_and_name
def Uni_Doi_and_name(inFile, outFile, lenAutName = 3, doiNote = True):
    bib = parse_file(inFile)
    if doiNote:
        bib = AddDoiAsNote(bib)
    bib = ReplaceInitialSpecialCharaters(bib)
    bib = UnifiedEntryName(bib, maxNumAutLets = lenAutName)
    with open(outFile, 'w') as File:
        File.write(bib.to_string("bibtex"))
# }}}

# As executable script {{{
if __name__ == '__main__':
    # Input and output files {{{
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:l:')
        if len(args)>0:
            raise getopt.GetoptError('Too many arguments!')
    except getopt.GetoptError:
        print('Wrong call! The excecution can have the following arguments:')
        print('To indicate the input file name: -i "fileName.bib"')
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
    if outFile == None:
        outFile = inFile
    if not inFile[-4:] == '.bib':
        raise("Error: the input file must be a .bib file")
    if not outFile[-4:] == '.bib':
        raise("Error: the output file must be a .bib file")
    # }}}
    Uni_Doi_and_name(inFile, outFile, lenAutName)
# }}}
