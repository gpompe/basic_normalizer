import os
import re
import logging as log
import logging.config


def repreclean():
    log.debug("Entry point")
    re1 = re.compile('\+',flags=re.IGNORECASE)
    re2 = re.compile('\t',flags=re.IGNORECASE)
    re3 = re.compile('\s+',flags=re.IGNORECASE)
    re4 = re.compile('(’|‘)',flags=re.IGNORECASE)
    re5 = re.compile('(“|”)',flags=re.IGNORECASE)
    re6 = re.compile('(–|—)',flags=re.IGNORECASE)
    re7 = re.compile('[^\x00-\x7F]',flags=re.IGNORECASE)
    return ((re1,"<plus>"),(re2," "),(re3," "),(re4,"'"),(re5,'"'),(re6,"-"),(re7,""))


def repostclean():
    log.debug("Entry point")
    re8 = re.compile('[\+]{1}',flags=re.IGNORECASE)
    re9 = re.compile('<plus>',flags=re.IGNORECASE)
    re10 =re.compile('(?<=\d),(?=\d)',flags=re.IGNORECASE)
    #re11 =re.compile('_')
    return ((re8," "),(re9,"+"),(re10,""))

def clean(text,cleanerTuple):
    log.debug("Params: %s - %s",text,cleanerTuple)
    for rex,r in cleanerTuple:
        text = rex.sub(r, text)
    return text

def applysubstitutes(text):
    for fv in reSet.values():
        #print(fv)
        for t in fv.values():
            for r in t:
                text = re.sub(r['re'] , r['r'] , text,flags=re.IGNORECASE)
    return text


def normalize(text):
    return clean(applysubstitutes(clean(text, precleaning)),postcleaning).strip()

def quotemeta(text):
    unsafe = r'\\.+*?[^]$(){}=!<>|:'
    for t in unsafe:
        rea = re.compile("\\"+t)
        text = rea.sub( "\\"+t,text)

    return text

def lineHandle(filekey, rekey, replacer):
    # log.debug("lineHandle: "+str(filekey) + " - rekey: " + str(rekey) + " - replacer: "+str(replacer))

    startM = False
    endM = False
    lookup = rekey

    lineRgxs = []

    if rekey[0] == '<':
        startM = True
        lookup = lookup[1:]

    if rekey.endswith('>'):
        endM = True
        lookup = lookup[:-1]

    qm = quotemeta(re.sub('_',' ',lookup,flags=re.IGNORECASE))

    if startM and endM:
        lineRgxs.append({'re': "^" + qm + "$", 'r': replacer })
    elif startM:
        lineRgxs.append({'re': "^" + qm + "(\\W+|$)", 'r': replacer + r'\g<1>'})
    elif endM:
        lineRgxs.append({'re': "(\\W+|^)" + qm + "$", 'r': r'\g<1>' + replacer })
        if filekey == "_sys":
            lineRgxs.append({'re': qm + "$", 'r': replacer })
    else:
        lineRgxs.append({'re': "(\\W+|^)" + qm + "(\\W+|$)", 'r': r'\g<1>' + replacer + r'\g<2>' })

    # log.debug("lineRgxs: %s",lineRgxs)
    return lineRgxs


def readSubstitutes(filekey,file):
    ''' Read the file and created the dict entry with the content '''
    log.debug("parameters: filekey->%s  -   file->%s",filekey,file)
    entrydict = {}
    p = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data",file)
    try:
        with open(p, "r") as data:
            for line in data:
                # Remove newline and spaces
                nline = line.strip()
                # Ignore empty lines
                if len(nline)>0:
                    # Lets allow comments with '#'
                    pos = nline.find('#')
                    if pos >= 0:
                        nline = nline[0:pos-1]

                    parts = nline.split(" ")

                    if len(parts) <= 1:
                        entrydict[parts[0]] = lineHandle(filekey,parts[0], "")
                    else:
                        entrydict[parts[0]] = lineHandle(filekey,parts[0], parts[1])
    except FileNotFoundError as err:
        log.error("{0}".format(err))
        raise

    return entrydict


def loadData(forced=False):

    log.debug("loadData Request: Forced= %s -- Loaded: %s",forced,is_loaded())
    global reSet

    if not(is_loaded()) or forced:
        log.debug("Loading data...")
        tasks = [
            {'key':'_sys','file':'systemessentials.txt'},
            {'key':'_extra','file':'substitutes.txt'},
            {'key':'_contractions','file':'contractions.txt'},
            {'key':'_interjections','file':'interjections.txt'},
            {'key':'_britsh','file':'british.txt'},
            {'key':'_spellfix','file':'spellfix.txt'},
            {'key':'_texting','file':'texting.txt'}
            ]


        for d in tasks:
            reSet[d['key']] = readSubstitutes(d['key'], d['file'])

    #print(reSet)
    return

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

def is_loaded():
    log.debug("reSet Entries: %s",len(reSet))
    return not(is_empty(reSet))

def clearData():
    global reSet
    reSet.clear()

# Main body

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.realpath(__file__)),'logging.conf'))

precleaning = repreclean()
postcleaning = repostclean()
reSet = dict()

