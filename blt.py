import re
import sys
import nltk
import inflect

from nltk.stem.wordnet import WordNetLemmatizer


eng = inflect.engine()
lemmatizer = WordNetLemmatizer()


class BatchDefs(object):
    def __init__(self):
        self.sets = dict()
        
    def get(self, key, default=None):
        return self.sets.get(key, default)
        
    def add(self, key, value, prefix=''):
        self.sets[(prefix + '.' if prefix else '') + key] = value
            
    def add_all(self, all, prefix=''):
        for k, v in all.items():
            self.sets[(prefix + '.' if prefix else '') + k] = v
            
    def export(self, echo_off=False):
        res = ""
        
        if echo_off:
            res += "@echo off\n"
        
        for i, (k, v) in enumerate(self.sets.items()):
            # sys.stdout.write(k + (", " if i < len(self.sets) - 1 else ""))
            res += 'SET "{}={}"\n'.format(self.escape_batch(k), self.escape_batch(v))
            
        return res
        
    def unescape_batch(self, s, replace_vars=True, default_replace='(?)'):
        s = s.replace('^>', '>').replace('^<', '<').replace('^^', '^').replace('^=', '=')
        
        if replace_vars:
            for k, v in self.sets.items():
                s = s.replace('%{}%'.format(self.escape_batch(k)), v)
            
            if default_replace is not None:
                sr = re.search(r'(?<!\%)\%(.+?)\%(?!%)', s)
                
                if sr:
                    for g in sr.groups():
                        print("WARNING: Not found: {}".format(g))
            
                s = re.sub(r'(?<!\%)\%.+?\%(?!%)', default_replace, s)
                
        return s.replace('%%', '%')
        
    def escape_batch(self, s):
        return s.replace('^', '^^')
        
    def load(self, string):
        for l in string.split('\n'):
            line = l
        
            if l.upper()[:4] == 'SET ':
                l = l[4:]
                
                if l.upper()[0] == '/':
                    continue
                    
                l = re.split(r'(?<!\^)[\&\>\<\|]', l)[0]
                    
                if l.startswith('"') and l.endswith('"'):
                    l = l[1:-1]
                    
                match = re.match(r'(.+?[^\^])=(.+)', l)
                
                if match:
                    self.sets[self.unescape_batch(match.group(1))] = self.unescape_batch(match.group(2))
                    
                else:
                    print(line)

class BLTVerb(object):
    def __init__(self, radicals, person='third', kind='indicative', passive=False, plural=False, negated=False, tense=None):
        self.radicals = radicals
        self.conjugation = '{}.{}'.format(person, ('plural' if plural else 'singular'))
        self.kind = kind
        self.passive = passive
        self.negated = negated
            
        self.time = tense
        
    def synthesize(self, defs):
        return defs.unescape_batch(('%negation.verbal%' if self.negated else '') + '{}%conjugation.{}%{}{}%conjugation.{}%'.format('%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals), self.conjugation, '%conjugation.{}%'.format(self.kind) if self.kind != 'indicative' else '', '%time.{}%'.format(self.time) if self.time else '', 'passive' if self.passive else 'active'))

class BLTAdjective(object):
    def __init__(self, radicals, genitivity=None, relativity=None, negated=False):
        self.radicals = radicals
        self.genitivity = genitivity
        self.relativity = relativity
        self.negated = negated
        
        if genitivity not in (None, 'genitive', 'ingenitive'):
            raise ValueError("Invalid adjective genitivity value: " + repr(genitivity))
        
        if relativity not in (None, 'comparative', 'superlative'):
            raise ValueError("Invalid adjective relativity value: " + repr(relativity))
        
    def synthesize(self, defs):
        return defs.unescape_batch(('%negation.adjective%' if self.negated else '') + '%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals) + (' ' if defs.sets['negation.type'] == 'adverb' else '') + ('%ending.adjective.{}%'.format(self.genitivity) if self.genitivity else '') + ('%ending.adjective.{}%'.format(self.relativity) if self.relativity else ''))

class BLTNoun(object):
    def __init__(self, radicals, gender='male', degree=None, plural=False, convert=False, possessive=False):
        self.radicals = radicals
        self.gender = gender
        self.degree = degree
        self.plural = plural
        self.convert = convert
        self.possessive = possessive
        
    def synthesize(self, defs):
        return defs.unescape_batch('%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals) + ('%ending.nominal%' if self.convert else '') + '%ending.nominal.gender.{}%'.format(self.gender) + ('%ending.nominal.degree.{}%'.format(self.degree) if self.degree else '') + ('%ending.nominal.plural%' if self.plural else '') + ('%ending.nominal.genitive%' if self.possessive else ''))
        
class BLTGeneric(object):
    def __init__(self, radical, plural=False, possessive=False):
        self.rad = radical
        self.plural = plural
        self.possessive = possessive
        
        if isinstance(self.rad, str):
            self.rad = (radical,)
        
    def synthesize(self, defs):
        return defs.unescape_batch('%ligation%'.join('%rad.{}%'.format(r) for r in self.rad) + ('%ending.plural%' if self.plural else '') + ('%ending.nominal.genitive%' if self.possessive else ''))
     
class BLTAdverb(object):
    def __init__(self, radicals, adjective_adverb):
        self.radicals = radicals
        self.adj = adjective_adverb
        
    def synthesize(self, defs):
        return defs.unescape_batch('%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals) + ('%adverb.adjective%' if self.adj else '%adverb.verbal%'))
 
class BLTRaw(object):
    def __init__(self, text, spacing=True, plural=False, possessive=False):
        self.text = text
        self.spacing = spacing
        self.plural = plural
        self.possessive = possessive
        
    def synthesize(self, defs):
        return defs.unescape_batch(self.text + ('%ending.plural%' if self.plural else '') + ('%ending.nominal.genitive%' if self.possessive else ''))
 
class BLTDefinitePronoun(object):
    def __init__(self, kind="nominal", person="third", plural=False):
        self.kind = kind
        self.person = person
        self.plurality = ("plural" if plural else "singular")
        
    def synthesize(self, defs):
        return defs.unescape_batch('%pronoun.{}.{}.{}%'.format(self.kind, self.person, self.plurality))
 
class BLTIndefinitePronoun(object):
    def __init__(self, kind="pointer", subtype="internal", plural=False): # only 'pointer' atm
        self.kind = kind
        self.subtype = subtype
        self.plurality = ("plural" if plural else "singular")
        
    def synthesize(self, defs):
        return defs.unescape_batch('%pronoun.indefinite.{}.{}%%pronoun.indefinite.{}%'.format(self.kind, self.subtype, self.plurality))
        
tobe_people = {
    "BE": None,
    "AM": "first",
    "IS": "third",
    "ARE": None,
}  
   
tobe_plurality = {
    "BE": None,
    "AM": False,
    "IS": False,
    "ARE": True,
}
        
pronoun_people = {
    "I": 'first',
    "ME": 'first',
    "WE": 'first',
    "YOU": 'second',
    "THOU": 'second',
    "THEE": 'second',
    "YE": 'second',
    "HIM": 'third',
    "HE": 'third',
    "SHE": 'third',
    "IT": 'third',
    "THEY": 'third',
    "THEM": 'third',
}

genitive_pronoun_people = {
    "MY": 'first',
    "OUR": 'first',
    "YOUR": 'second',
    "THY": 'second',
    "THINE": 'second',
    "YER": 'second',
    "HIS": 'third',
    "HER": 'third',
    "ITS": 'third',
    "THEIR": 'third',
}

remove_y = "AEIOUDLT"

pronoun_plurality = {
    "I": False,
    "ME": False,
    "WE": True,
    "YOU": False,
    "THOU": False,
    "THEE": True,
    "YE": False,
    "HIM": False,
    "HE": False,
    "SHE": False,
    "IT": False,
    "THEY": True,
    "THEM": True,
}

genitive_pronoun_plurality = {
    "MY": False,
    "OUR": True,
    "YOUR": False,
    "THY": False,
    "THINE": True,
    "YER": False,
    "HIS": False,
    "HER": False,
    "ITS": False,
    "THEIR": True,
}

verbal_tenses = {
    "VBP": None, # present
    "VBZ": None, # present
    "VBG": None,
    "VB": None,
    "VBN": "perfect",
    "VBD": "perfect",
}

auxiliary_tenses = {
    "WILL": "future",
    "WOULD": "subfuture",
    "HAVE": "subpresent",
    "HAS": "subpresent",
    "HAD": "preteritous",
    "USED TO": "pluperfect",
    "HAVE BEEN": "pseudopast",
    "WOULD HAVE": "subpast",
}
        
class BLTLanguage(object):
    def __init__(self, definitions='', extra_composites=()):
        self._defs = BatchDefs()
        self.composites = dict(extra_composites)
        
        if definitions:
            self._defs.load(definitions)
            
        for k, v in self._defs.sets.items():
            if k.startswith('composite.'):
                key = k[10:]
                values = re.split(r';\s?', v)
                self.composites[key] = tuple(values)
            
    def add_composite(self, word, *radicals):
        self._defs.add('composite.' + word, '; '.join(radicals))
        self.composites[word] = tuple(radicals)
        
    def add_radical(self, key, value):
        self._defs.add(key, value, 'rad')
        
    def supports(self, key):
        return self._defs.get('rad.' + key) is not None or key in self.composites
        
    def dumps(self):
        return self._defs.export(True)
        
    def radicals_for(self, word):
        c = list(self.composites.get(word, [word,]))
        cd = []
        changed = True
        
        while changed:
            changed = False
        
            for r in c:
                if r in self.composites:
                    cd.extend(self.composites[r])
                    changed = True
                    
                else:
                    cd.append(r)
                    
            c = cd
            cd = []
            
        return tuple(c)
            
    def synthesize(self, words):
        synth = tuple(((w, w.synthesize(self._defs)) if not isinstance(w, str) else (w, None)) for w in words)
        res = ''.join((' ' + sn[1] if (not (isinstance(sn[0], BLTRaw) and not sn[0].spacing) and i > 0) else sn[1]) for i, sn in enumerate(synth))
        res = res[0].upper() + res[1:]
        
        for i, l in enumerate(res):
            if l in '.!?':
                i2 = i
                
                while i2 < len(res) and res[i2] in '.!? ':
                    i2 += 1
                    
                if i2 < len(res):
                    res = res[:i2] + res[i2].upper() + res[i2 + 1:]
                
        return res
        
    def translate(self, english_text):
        for i, l in enumerate(english_text):
            if l in '.!?':
                i2 = i
                
                while i2 < len(english_text) and english_text[i2] in '.!? ':
                    i2 += 1
                    
                if i2 < len(english_text):
                    english_text = english_text[:i2] + english_text[i2].lower() + english_text[i2 + 1:]
    
        text = nltk.word_tokenize(english_text[0].lower() + english_text[1:])
        tags = [tag for tag in nltk.pos_tag(text)]
        puncts = []
        
        c = '.'
        for t in tags[::-1]:    
            if t[1] == '.':
                c = t[0]
                
            puncts.insert(0, c)
        
        words = []
        historic = []
        prev = None
        
        for index, (word, tag) in enumerate(tags):
            if word.upper() == 'THIS':
                words.append(BLTIndefinitePronoun())
                
            elif word.upper() == 'THESE':
                words.append(BLTIndefinitePronoun(plural=True))
            
            elif word.upper() == 'THAT':
                words.append(BLTIndefinitePronoun(subtype="external"))
                
            elif word.upper() == 'THOSE':
                words.append(BLTIndefinitePronoun(subtype="external", plural=True))
        
            elif word.upper() in ('NO', 'NOT') and len(tags) > index + 1 and tags[index + 1][1][:2] == 'JJ':
                prev = (word, tag, (historic[index - 1] if index > 0 else None))                    
                historic.append((word, tag))
                continue
                
            elif word.upper() == 'THE':
                continue
                
            elif word.upper() in ('WILL', 'HAVE', 'HAD', 'WOULD', 'HAS') and len(tags) > index + 1 and tags[index + 1][1][:2] == 'VB':
                prev = (word, tag, (historic[index - 1] if index > 0 else None))                    
                historic.append((word, tag))
                continue
        
            elif tag == 'POS':
                continue
                
            elif tag in ('NN', 'NNS'):
                convert = False
            
                if word.lower().endswith('ness'): 
                    w = re.sub('i$', 'y', re.sub(r'ness$', '', word[:-4]))
                    
                    if nltk.pos_tag((w,))[0][1][:2] in ('JJ', 'RB'):
                        word = w
                        convert = True
            
                elif word.lower().endswith('y'):
                    w = word[:-1]
                    
                    if nltk.pos_tag((w,))[0][1][:2] in ('JJ', 'RB'):
                        word = w
                        convert = True
            
                words.append(BLTNoun(self.radicals_for((eng.singular_noun(word) or word).lower()),
                    plural=(tag == 'NNS'),
                    possessive=(index < len(tags) - 1 and tags[index + 1][1] == 'POS'),
                    convert=convert
                ))
                        
            elif tag in ('NNP', 'NNPS'):
                words.append(BLTRaw(word,
                    plural=(tag == 'NNPS'),
                    possessive=index < len(tags) - 1 and tags[index + 1][1] == 'POS'
                ))
                
            elif tag[:2] == ('JJ'):
                genit = None
                neg = False
            
                for d in ('in', 'un', 'non-', 'non', 'de'):
                    if word.lower().startswith(d):
                        neg = True
                        word = word[len(d):]
                        break
                    
                if word.lower().startswith('en') and word.lower().endswith('d'):
                    word = word[2:-1].lower()
                    genit = 'genitive'
                    
                elif word.lower().endswith('ful'):
                    word = re.sub(r'iful$', 'y', word)
                    genit = 'genitive'
                    
                elif word.lower().endswith('y'):
                    if word.upper()[-2] in remove_y:
                        word = re.sub(r'y$', '', word)
                    
                    else:
                        word = re.sub(r'y$', 'e', word)
                        
                    genit = 'genitive'
                    
                if tag == 'JJR':
                    word = re.sub(r'i$', 'y', word[:-2])
                
                if tag == 'JJS':
                    word = re.sub(r'i$', 'y', word[:-3])
            
                words.append(BLTAdjective(self.radicals_for(re.sub(r'(?:ful|less)+$', '', word.lower())),
                    genitivity=(genit or ('genitive' if word.lower().endswith('ful') else ('ingenitive' if word.lower().endswith('less') else None))),
                    relativity=('comparative' if tag == 'JJR' else ('superlative' if tag == 'JJS' else None)),
                    negated=neg or (prev is not None and prev[0].upper() in ('NO', 'NOT'))
                ))
                
            elif tag == 'PRP':
                words.append(BLTDefinitePronoun(person=pronoun_people[re.sub('SELF$', '', word.upper())], plural=pronoun_plurality[re.sub('SELF$', '', word.upper())]))
                     
            elif tag == 'PRP$':
                words.append(BLTDefinitePronoun('genitive', person=genitive_pronoun_people[word.upper()], plural=genitive_pronoun_plurality[word.upper()]))
                
            elif tag in (',', '.', ':'):
                words.append(BLTRaw(word, False))
                
            elif tag[:2] == 'VB':
                if index + 1 < len(tags) and tags[index + 1][1][:2] == 'VB' and word.upper() in tobe_people:
                    prev = (word, tag, (historic[index - 1] if index > 0 else None))                    
                    historic.append((word, tag))
                    continue
            
                passive = tag in ('VBN', 'VBG') and prev[1][2:] == 'VB'
                negate = prev is not None and len({prev[0].lower(), (prev[2] or ('',))[0].lower()} & {'no', 'not'}) == 1
                tense = None
                person = 'third'
                plural = False
                kind = 'indicative'
            
                if index == 0:
                    kind = 'imperative'
                
                elif puncts[index] == '?':
                    kind = 'subjunctive'
                    
                elif tag[2:] == 'G':
                    kind = 'gerund'
                    
                elif prev != None and prev[1] == 'TO':
                    kind = 'infinitive'
                 
                pointer = timeout = index
                pperson = None
                
                while pointer > 0 and timeout > 0:
                    pointer -= 1
                    timeout -= 1
                    
                    (pword, ptag) = tags[pointer]
                    
                    # print(pointer, timeout, pword, ptag)
                    
                    if ptag in '.,:':
                        timeout += 1
                        continue
                    
                    elif ptag[:2] == 'VB':
                        if pword.upper() in tobe_people:
                            pperson = tobe_people[pword.upper()]
                            person = pperson or person
                            plural = tobe_plurality[pword.upper()]
                            passive = True
                            
                        if not pperson:
                            if ptag[:2] == 'NN':
                                person = "third"
                                plural = eng.plural(pword.lower()) == pword.lower()
                                timeout = 1
                            
                            elif ptag == 'PRP':
                                person = pronoun_people[pword.upper()]
                                plural = pronoun_plurality[pword.upper()]
                                break
                    
                if prev != None and tag[2:] == 'N' and prev != None:    
                    if prev[0].upper() in auxiliary_tenses:
                        tense = auxiliary_tenses[prev[0].upper()]
                        
                    elif (prev[2][0].upper() + ' ' + prev[0].upper()) in auxiliary_tenses:
                        tense = auxiliary_tenses[(prev[2][0].upper() + ' ' + prev[0].upper())]
                        
                    elif prev[1][:2] == 'VB':
                        tense = verbal_tenses[prev[1]]
                    
                else:
                    tense = verbal_tenses.get(tag, None)
                
                words.append(BLTVerb(self.radicals_for(lemmatizer.lemmatize(word.lower(), 'v')), person, kind, passive, plural, negate, tense))
            
            elif tag in ('WRB', 'RB', 'MD', 'DT', 'CC', 'IN', 'TO'):
                adverb = False
                w = None
            
                if tag == 'RB' and word.lower().endswith('ly'):
                    w = word[:-2]
                    
                    if nltk.pos_tag((w,))[0][1][:2] in ('NN', 'JJ'):
                        adverb = True
            
                if adverb:
                    words.append(BLTAdverb(self.radicals_for(w.lower()), len(tags) > index + 1 and tags[index + 1][1][:2] == 'JJ'))
            
                elif word.upper() not in ('A', 'AN'):
                    words.append(BLTGeneric(self.radicals_for(word.lower())))
                    
                else:
                    continue
            
            else:
                words.append(BLTRaw(word.lower()))
                
            prev = (word, tag, (historic[-1] if len(historic) > 0 else None))
            historic.append((word, tag))
            
        return (self.synthesize(words), words)
        
def langfile(langname):
	return open('lang_{}.bat'.format(langname)).read()

def loadlang(langname):
    return BLTLanguage(langfile(langname))