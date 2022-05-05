# Libraries {{{
import sys
import getopt
from pybtex.database import parse_file
from pybtex.database import BibliographyData as bbd
from pybtex.database import Entry
# }}}

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

# Set unified entry name {{{
def UnifiedEntryName(bibData, maxNumAutLets = 3):
    # Get keys and names {{{
    from string import ascii_lowercase
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
        type_ = bib.entries[oldKey].type
        fields = bib.entries[oldKey].fields
        persons = bib.entries[oldKey].persons
        entry = Entry(type_, fields, persons)
        newBib.entries[newKey] = entry
    # }}}
    return newBib
# }}}
# }}}


bib = parse_file(inFile)
bib = AddDoiAsNote(bib)
bib = UnifiedEntryName(bib, maxNumAutLets = lenAutName)
with open(outFile, 'w') as File:
    File.write(bib.to_string("bibtex"))
