import re
import sys
import nltk
import inflect
import random
import logging

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import names
from nltk.corpus import wordnet as wn

labeled_names = ([(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
random.shuffle(labeled_names)

gerund_no_e = "DLR"

def gender_features(word):
    res = {
        'last-letter': word[-1].lower(),
        'first-letter': word[0].lower(),
    }
    
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        res['count: ' + letter] = word.lower().count(letter)
        res['has: ' + letter] = (letter in word.lower())
        
    encounters = []
    encounters2 = []
    enc = ''
    vowels = "aeiou"
    
    for l in word.lower():
        if l.lower() in vowels:
            enc += l
            
        elif len(enc) > 1:
            encounters.append(enc)
            enc = ''
        
    enc = ''
        
    for l in word.lower():
        if l.lower() not in vowels:
            enc += l
            
        elif len(enc) > 1:
            encounters2.append(enc)
            enc = ''
        
    for i, e in enumerate(encounters):
            res['vowel encounter #{}'.format(i)] = e
            
    for i, e in enumerate(encounters2):
        res['consonant encounter #{}'.format(i)] = e
    
    return res

featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
train_set, test_set = featuresets[500:], featuresets[:500]
genderifier = nltk.NaiveBayesClassifier.train(train_set)

#=============
# Credits to bogs @ https://stackoverflow.com/a/16752477/5129091
# This is a modified version of their code.
def nounify(adjective_word):
    """ Transform a verb to the closest noun: die -> death """
    adjective_synsets = wn.synsets(adjective_word, pos=wn.ADJ)

    # Word not found
    if not adjective_synsets:
        return []

    # Get all adjective lemmas of the word
    adjective_lemmas = [l for s in adjective_synsets \
                   for l in s.lemmas() if s.name().split('.')[1] == wn.ADJ]

    # Get related forms
    derivationally_related_forms = [(l, l.derivationally_related_forms()) \
                                    for l in    adjective_lemmas]

    # filter only the nouns
    related_noun_lemmas = [l for drf in derivationally_related_forms \
                           for l in drf[1] if l.synset().name().split('.')[1] == 'n']

    # Extract the words from the lemmas
    words = [l.name() for l in related_noun_lemmas]
    len_words = len(words)

    # Build the result in the form of a list containing tuples (word, probability)
    result = [(w, float(words.count(w))/len_words) for w in set(words)]
    result.sort(key=lambda w: -w[1])

    # return all the possibilities sorted by probability
    return result

#=============

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
        
    def unescape_batch(self, s, replace_vars=True, default_replace='(\\1?)'):
        s = s.replace('^>', '>').replace('^<', '<').replace('^^', '^').replace('^=', '=')
        
        if replace_vars:
            for k, v in self.sets.items():
                s = s.replace('%{}%'.format(self.escape_batch(k)), v)
            
            if default_replace is not None:
                sr = re.search(r'(?<!\%)\%(.+?)\%(?!%)', s)
                
                if sr:
                    for g in sr.groups():
                        logging.info("WARNING: Not found: {}".format(g))
            
                s = re.sub(r'(?<!\%)\%(.+?)\%(?!%)', default_replace, s)
                
        return s.replace('%%', '%')
        
    def escape_batch(self, s):
        return s.replace('^', '^^')
        
    def load(self, string):
        for i, l in enumerate(string.split('\n')):
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
                    logging.info("WARNING: Batch SET line {} not comprehended: ".format(i) + line)

class BLTWord(object):
    def get_pos_tag(self):
        return self.tag
                    
class BLTVerb(BLTWord):
    def __init__(self, radicals, person='third', kind='indicative', passive=False, plural=False, negated=False, tense=None):
        self.radicals = radicals
        self.conjugation = '{}.{}'.format(person, ('plural' if plural else 'singular'))
        self.kind = kind
        self.passive = passive
        self.negated = negated
        self.spacing = True
            
        self.time = tense
        
    def synthesize(self, defs):
        return defs.unescape_batch(('%negation.verbal%' if self.negated else '') + '{}%conjugation.{}%{}{}%conjugation.{}%'.format('%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals), self.conjugation, '%conjugation.{}%'.format(self.kind) if self.kind != 'indicative' else '', '%time.{}%'.format(self.time) if self.time else '', 'passive' if self.passive else 'active'))

class BLTAdjective(BLTWord):
    def __init__(self, radicals, genitivity=None, relativity=None, negated=False):
        self.radicals = radicals
        self.genitivity = genitivity
        self.relativity = relativity
        self.negated = negated
        self.spacing = True
        
        if genitivity not in (None, 'genitive', 'ingenitive'):
            raise ValueError("Invalid adjective genitivity value: " + repr(genitivity))
        
        if relativity not in (None, 'comparative', 'superlative'):
            raise ValueError("Invalid adjective relativity value: " + repr(relativity))
        
    def synthesize(self, defs):
        return defs.unescape_batch(('%negation.adjective%' if self.negated else '') + (' ' if defs.sets['negation.type'] == 'adverb' else '') + '%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals) + ('%ending.adjective.{}%'.format(self.genitivity) if self.genitivity else '') + ('%ending.adjective.{}%'.format(self.relativity) if self.relativity else ''))

class BLTNoun(BLTWord):
    def __init__(self, radicals, gender='male', degree=None, plural=False, convert=False, possessive=False, genitivity=None, negate=False):
        self.radicals = radicals
        self.gender = gender
        self.degree = degree
        self.negate = negate
        self.plural = plural
        self.convert = convert
        self.possessive = possessive
        self.genitivity = None
        self.spacing = True
        
    def synthesize(self, defs):
        return defs.unescape_batch(('%negation.nominal%' if self.negate else '') + '%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals) + ('%ending.nominal%' if self.convert else '') + '%ending.nominal.gender.{}%'.format(self.gender) + ('%ending.nominal.degree.{}%'.format(self.degree) if self.degree else '') + ('%ending.plural%' if self.plural else '') + ('%ending.nominal.genitive%' if self.possessive else '') + ('%ending.adjective.{}%'.format(self.genitivity) if self.genitivity else ''))
        
class BLTGeneric(BLTWord):
    def __init__(self, radical, plural=False, possessive=False):
        self.rad = radical
        self.plural = plural
        self.possessive = possessive
        self.spacing = True
        
        if isinstance(self.rad, str):
            self.rad = (radical,)
        
    def synthesize(self, defs):
        return defs.unescape_batch('%ligation%'.join('%rad.{}%'.format(r) for r in self.rad) + ('%ending.plural%' if self.plural else '') + ('%ending.nominal.genitive%' if self.possessive else ''))
     
class BLTAdverb(BLTWord):
    def __init__(self, radicals, adjective_adverb):
        self.radicals = radicals
        self.adj = adjective_adverb
        self.spacing = True
        
    def synthesize(self, defs):
        return defs.unescape_batch('%ligation%'.join('%rad.{}%'.format(r) for r in self.radicals) + ('%adverb.adjective%' if self.adj else '%adverb.verbal%'))
 
class BLTRaw(BLTWord):
    def __init__(self, text, spacing=True, plural=False, possessive=False, gender=None, genitivity=None):
        self.text = text
        self.spacing = spacing
        self.plural = plural
        self.possessive = possessive
        self.gender = gender
        self.genitive = genitivity
        
    def synthesize(self, defs):
        return defs.unescape_batch(self.text + ('%ending.plural%' if self.plural else '') + ('%ending.nominal.genitive%' if self.possessive else '') + ('-%ending.nominal.gender.{}%'.format(self.gender) if self.gender is not None else '') + ('%ending.adjective.genitivity%' if self.genitive else ''))
        
    def get_pos_tag(self):
        if self.text == ',':
            return ','
            
        if self.text == '.?!':
            return '.'
            
        if self.text in ':;':
            return ':'
            
        if self.text in '([{':
            return "("
            
        if self.text in ')]}':
            return ")"
            
        return super(BLTRaw, self).get_pos_tag()
 
class BLTDefinitePronoun(BLTWord):
    def __init__(self, kind="nominal", person="third", plural=False):
        self.kind = kind
        self.person = person
        self.plurality = ("plural" if plural else "singular")
        self.spacing = True
        
    def synthesize(self, defs):
        return defs.unescape_batch('%pronoun.{}.{}.{}%'.format(self.kind, self.person, self.plurality))
 
class BLTIndefinitePronoun(BLTWord):
    def __init__(self, kind="pointer", subtype="internal", plural=False): # only 'pointer' atm
        self.kind = kind
        self.subtype = subtype
        self.plurality = ("plural" if plural else "singular")
        self.spacing = True
        
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
    "ONE": 'third',
    "I": 'first',
    "ME": 'first',
    "MY": 'first',
    "WE": 'first',
    "OUR": 'first',
    "US": 'first',
    "YOU": 'second',
    "YOUR": 'second',
    "THOU": 'second',
    "THEE": 'second',
    "THY": 'second',
    "THINE": 'second',
    "YE": 'second',
    "HIM": 'third',
    "HE": 'third',
    "SHE": 'third',
    "HER": 'third',
    "IT": 'third',
    "THEY": 'third',
    "THEM": 'third',
    "THEIRS": 'third',
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
    "THEIRS": 'third',
}

remove_y = "AEIOUDLTR"
remove_ous = "AEIOUDLTR"
remove_en = "AEIOUDLTR"
superlative_no_e = "DLTR"
superlative_with_eh = "G"

pronoun_plurality = {
    "ONE": True,
    "I": False,
    "ME": False,
    "WE": True,
    "US": True,
    "YOU": False,
    "THOU": False,
    "THEE": True,
    "YE": False,
    "HIM": False,
    "HE": False,
    "HER": False,
    "SHE": False,
    "IT": False,
    "THEY": True,
    "THEM": True,
    "MY": False,
    "OUR": True,
    "THY": False,
    "THINE": True,
    "YOUR": False,
    "THEM": True,
    "THEIR": 'True',
    "THEIRS": 'True',
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
    "THEIRS": True,
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
    "WAS": "transpast",
    "WERE": "transpast",
    "WILL": "future",
    "WOULD": "subfuture",
    "HAVE": "subpresent",
    "HAS": "subpresent",
    "HAD": "preteritous",
    "USED TO": "pluperfect",
    "HAVE BEEN": "pseudopast",
    "WOULD HAVE": "subpast",
    "WILL HAVE": "pseudofuture",
}
        
class BLTLanguage(object):
    def __init__(self, definitions='', extra_composites=()):
        self._defs = BatchDefs()
        self.composites = dict(extra_composites)
        
        if definitions:
            self._defs.load(definitions)
            
        self.name = self._defs.sets['langname']
            
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
        res = ''.join(
            (
                (sn[1] + ' ' if sn[0].spacing == 'post' else ' ' + sn[1]
            ) if sn[0].spacing is not False and (
                (i > 0 if sn[0].spacing != 'post' else i + 1 < len(synth))
            ) else sn[1]
        )
        for i, sn in enumerate(synth))
        
        if len(res) > 0:
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
            if l in '.!?' or i == 0:
                i2 = i
                
                while i2 < len(english_text) and english_text[i2] in '.!? ':
                    i2 += 1
                    
                if i2 < len(english_text) and not (english_text[i2] == 'I' and (len(english_text) == i2 + 1 or english_text[i2 + 1] == ' ') and (i2 == 0 or english_text[i2 - 1] == ' ')):
                    english_text = english_text[:i2] + english_text[i2].lower() + english_text[i2 + 1:]
                    # print(english_text[i2] == 'I', (len(english_text) == i2 + 1 or english_text[i2 + 1] == ' '), (i2 == 0 or english_text[i2 - 1] == ' '))
    
        text = nltk.word_tokenize(english_text)
        tags = [tag for tag in nltk.pos_tag(text)]
        puncts = []
        
        c = '.'
        for t in tags[::-1]:    
            if t[1] == '.':
                c = t[0]
                
            puncts.insert(0, c)
        
        words = []
        historic = []
        prev = lprev = None
        past_bracket = False
                
        for index, (word, tag) in enumerate(tags):
            def add_blt_word(w, _tag=None):
                setattr(w, 'tag', (_tag if _tag is not None else tag))
                
                words.append(w)
            
            # print("'" + word + "':", tag)
            if re.match(r"^[\(\[\{\\\/]+$", word):
                add_blt_word(BLTRaw(word, True))
                past_bracket = True
                continue
                
            elif re.match(r"^[\)\]\}]+$", word):
                add_blt_word(BLTRaw(word, "post"))
                past_bracket = True
                continue
                
            elif re.match(r"^[\=\-\_\*]+$", word):
                add_blt_word(BLTRaw(word, True))
                continue
                
            elif word.upper() == "'S":
                word = 'is'
                
            elif word.upper() == "N'T":
                continue
           
            elif word.upper() == 'THIS':
                add_blt_word(BLTIndefinitePronoun())
                
            elif word.upper() == 'THESE':
                add_blt_word(BLTIndefinitePronoun(plural=True))
            
            elif word.upper() == 'THAT':
                add_blt_word(BLTIndefinitePronoun(subtype="external"))
                
            elif word.upper() == 'THOSE':
                add_blt_word(BLTIndefinitePronoun(subtype="external", plural=True))
        
            elif word.upper() in ('NO', 'NOT') and len(tags) > index + 1 and tags[index + 1][1][:2] == 'JJ':
                prev = (word, tag, (historic[index - 1] if index > 0 and len(historic) > index - 1 else None))                    
                historic.append((word, tag))
                continue
                
            elif word.upper() == 'THE':
                continue
                
            elif word.upper() in ('WILL', 'HAVE', "'VE", 'HAD', 'WOULD', 'HAS') and len(tags) > index + 1 and tags[index + 1][1][:2] == 'VB':
                prev = (word, tag, (historic[index - 1] if index > 0 and len(historic) > index - 1 else None))                    
                historic.append((word, tag))
                continue
        
            elif tag == 'POS':
                continue
                                
            elif word.upper() in pronoun_people and (tag == 'PRP' or (((word.lower().endswith('selves') and len(word) > 6) or (word.lower().endswith('self') and len(word) > 4)) and nltk.pos_tag((word[:-4],))[0][1][:3] == 'PRP')):
                if word.upper().endswith('SELF'):
                    word = word[:-4]
                
                if word.upper().endswith('SELVES'):
                    word = word[:-6]
                
                word = word.lower().replace("'em", "them")
                
                add_blt_word(BLTDefinitePronoun(person=pronoun_people[word.upper()], plural=pronoun_plurality[re.sub('SELF$', '', word.upper())]))
                     
            elif tag in ('NN', 'NNS'):
                convert = False
                neg = False
                genit = False
                
                for d in ('dis', 'un', 'non-', 'non', 'dis'):
                    if word.lower().startswith(d) and len(word) > len(d):
                        if nltk.pos_tag((word[len(d):],))[0][1][:2] in ('JJ', 'NN', 'RB'):
                            neg = True
                            word = word[len(d):]
                            break
                            
                        elif len(word) > len(d) + 2 and nltk.pos_tag((word[len(d):],))[0][1][:2] == 'VB' and word.lower().endswith('ed'):
                            neg = True
                            word = word[len(d):-1]
                            break
                            
                if len(word) > 1 and nltk.pos_tag((word[:-1],))[0][1][:2] == 'VB' and word.lower().endswith('ed'):
                    neg = True
                    word = word[:-1]
                    break
                
                if '-' in word and word.lower() not in self.composites:
                    # Add implicit composite word.
                    self.add_composite((eng.singular_noun(word) or word), *(eng.singular_noun(word) or word).split('-'))
                    
                if word.lower().endswith('ness'): 
                    w = re.sub('i$', 'y', re.sub(r'ness$', '', word[:-4]))
                    
                    if nltk.pos_tag((w,))[0][1][:2] in ('JJ', 'NN', 'RB'):
                        word = w
                        convert = True
                        
                        if word[-2:] == 'ly':
                            genit = 'genitive'
                            word = word[:-2]
            
                add_blt_word(BLTNoun(self.radicals_for((eng.singular_noun(word) or word).lower()),
                    gender=genderifier.classify(gender_features((eng.singular_noun(word) or word).lower())),
                    plural=(tag == 'NNS' or bool(eng.singular_noun(word))),
                    possessive=(index < len(tags) - 1 and tags[index + 1][1] == 'POS'),
                    convert=convert,
                    negate=neg
                ))
                        
            elif tag in ('NNP', 'NNPS'):
                add_blt_word(BLTRaw(word,
                    gender=genderifier.classify(gender_features((eng.singular_noun(word) or word).lower())),
                    plural=(tag == 'NNPS'),
                    possessive=index < len(tags) - 1 and tags[index + 1][1] == 'POS'
                ))
                
            elif tag[:2] == 'JJ':
                genit = None
                neg = False
                i = 0
            
                for d in ('dis', 'un', 'non-', 'non'):
                    if word.lower().startswith(d) and len(word) > len(d):
                        if nltk.pos_tag((word[len(d):],))[0][1][:2] in ('JJ', 'RB'):
                            neg = True
                            word = word[len(d):]
                            break
                            
                        elif len(word) > len(d) + 2 and word.lower().endswith('ed') and nltk.pos_tag((word[len(d):],))[0][1][:2] in ('VB', 'NN'):
                            neg = True
                            word = word[len(d):-2]
                            break
                    
                    
                if len(word) > 2 and word.lower().startswith('en') and word.lower().endswith('d') and nltk.pos_tag((word.lower()[:-1],))[0][1][2:-1] in ('VB', 'JJ', 'NN', 'RB'):
                    word = word[2:-1].lower()
                    
                    if word[-1].upper() in remove_en.upper():
                        word = word[:-1]
                    
                    genit = 'genitive'
                    
                elif len(word) > 3 and word.lower().endswith('ful') and nltk.pos_tag((word.lower()[:-3],))[0][1][:2] in ('VB', 'JJ', 'NN', 'RB'):
                    word = re.sub(r'ful$', '', word)
                    word = re.sub(r'i$', 'y', word)
                    genit = 'genitive'
                    
                elif len(word) > 4 and word.lower().endswith('less') and nltk.pos_tag((word.lower()[:-4],))[0][1][:2] in ('VB', 'JJ', 'NN', 'RB'):
                    word = re.sub(r'less$', '', word)
                    word = re.sub(r'i$', 'y', word)
                    genit = 'ingenitive'
                    
                elif len(word) > 3 and word.lower().endswith('ous') and nltk.pos_tag((word.lower()[:-3],))[0][1][:2] in ('VB', 'JJ', 'NN', 'RB'):
                    if word[-2].upper() in remove_ous.upper():
                        word = re.sub(r'ous$', '', word)
                        
                    else:
                        word = re.sub(r'ous$', 'e', word)
                        
                    word = re.sub(r'i$', 'y', word)
                    word = re.sub(r'cy$', 'sh', word)
                    genit = 'genitive'
                    
                elif len(word) > 1 and word.lower().endswith('y') and nltk.pos_tag((word.lower()[:-1],))[0][1] in ('JJ', 'JJC', 'JJR', 'RB'):
                    if word[-2].upper() in remove_y.upper():
                        word = re.sub(r'y$', '', word)
                    
                    else:
                        word = re.sub(r'y$', 'e', word)
                        
                    genit = 'genitive'
                    
                else:
                    for d in ('in',):
                        if len(word) > len(d) and word.lower().startswith(d) and nltk.pos_tag((word[len(d):],))[0][1][:2] in ('JJ', 'NN'):
                            neg = True
                            word = word[len(d):]
                            break
                    
                if tag == 'JJR':
                    word = re.sub(r'i$', 'y', word[:-2])
                
                if tag == 'JJS':
                    word = re.sub(r'i$', 'y', word[:-3])
                    
                    if len(word) > 1 and (word[-2].upper() in superlative_no_e or (word[-2].upper() not in superlative_with_eh and word[-1].upper() == 'H')):
                        word += 'e'
            
                # base = nounify(word)
                
                # if len(base) < 1:
                #     base = word
                    
                # else:
                #     base = base[0][0]
                    
                # print(word, base)
            
                add_blt_word(BLTAdjective(self.radicals_for(word),
                    genitivity=genit,
                    relativity=('comparative' if tag == 'JJR' else ('superlative' if tag == 'JJS' else None)),
                    negated=neg or (prev is not None and prev[0].upper() in ('NO', 'NOT'))
                ))
                
            elif tag == 'PRP$' and word.upper() in genitive_pronoun_people:
                add_blt_word(BLTDefinitePronoun('genitive', person=genitive_pronoun_people[word.upper()], plural=genitive_pronoun_plurality[word.upper()]))
                
            elif tag in ',.:':
                add_blt_word(BLTRaw(word, False))
                prev = None
                past_bracket = False
                lprev = None
                continue
                
            elif tag[:2] == 'VB':
                if index + 1 < len(tags) and tags[index + 1][1][:2] == 'VB' and word.upper() in tobe_people:
                    prev = (word, tag, (historic[index - 1] if index > 0 and len(historic) > index - 1 else None))                    
                    historic.append((word, tag))
                    continue
            
                if tag == 'VBG' and len(word) > 3:
                    word = word[:-3]
                    
                    if word[-1].upper() in gerund_no_e:
                        word += 'e'
            
                passive = tag in ('VBN', 'VBG') and prev != None and prev[1][2:] == 'VB'
                negate = prev is not None and len({prev[0].lower(), (prev[2] or ('',))[0].lower()} & {'no', 'not'}) == 1 or (len(tags) > index + 1 and tags[index + 1][0] == "n't")
                
                tense = None
                person = 'third'
                plural = False
                kind = 'indicative'
                
                for pref in ('dis', 'un', 'de', 'non', 'non-'):
                    w = word[len(pref):]
                
                    if len(word) > len(pref) + 1 and word.startswith(pref) and nltk.pos_tag((w,))[0][1][:2] in ('VB', 'NN', 'RB'):
                        negate = True
                        word = w
                        break
            
                if index == 0:
                    kind = 'imperative'
                
                elif puncts[index] == '?':
                    kind = 'subjunctive'
                    
                elif tag[2:] == 'G':
                    kind = 'gerund'
                    
                elif prev != None and prev[1] == 'TO':
                    kind = 'infinitive'
                 
                pointer = timeout = min(index + 1, len(tags) - 1)
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
                            passive = tag != 'VBG'
                            
                        if not pperson:
                            if ptag[:2] == 'NN':
                                person = "third"
                                plural = eng.plural(pword.lower()) == pword.lower()
                                timeout = 1
                            
                            elif ptag == 'PRP' and (pointer < index + 1 or len(tags) < 3 or historic[-1][1] in '.:'):
                                person = pronoun_people[pword.upper()]
                                plural = pronoun_plurality[pword.upper()]
                                break
                    
                if prev is not None:
                    if prev[2] is not None and (prev[2][0].upper() + ' ' + prev[0].upper()) in auxiliary_tenses:
                        tense = auxiliary_tenses[prev[2][0].upper() + ' ' + prev[0].upper()]
                        
                    elif prev[0].upper() in auxiliary_tenses:
                        tense = auxiliary_tenses[prev[0].upper()]
                        
                    elif prev[1][:2] == 'VB':
                        tense = verbal_tenses[prev[1]]
                    
                else:
                    tense = verbal_tenses.get(tag, None)
                
                past_bracket = False
                add_blt_word(BLTVerb(self.radicals_for(lemmatizer.lemmatize(word.lower(), 'v')), person, kind, passive, plural, negate, tense))
            
            elif tag in ('WRB', 'RB', 'MD', 'DT', 'CC', 'IN', 'TO', 'UH'):
                adverb = False
                w = None
            
                if tag == 'RB' and word.lower().endswith('ly'):
                    w = word[:-2]
                    
                    if nltk.pos_tag((w,))[0][1][:2] in ('NN', 'JJ'):
                        adverb = True
            
                if adverb:
                    add_blt_word(BLTAdverb(self.radicals_for(w.lower()), len(tags) > index + 1 and tags[index + 1][1][:2] == 'JJ'))
            
                elif word.upper() not in ('A', 'AN'):
                    add_blt_word(BLTGeneric(self.radicals_for(word.lower())))
                    
                else:
                    continue
            
            else:
                add_blt_word(BLTRaw(word.lower()))
                
            prev = (word, tag, (historic[-1] if len(historic) > 0 else None))
            historic.append((word, tag))
            
            words[-1].spacing = prev != lprev and not past_bracket
                
            past_bracket = False
            lprev = prev
            
        return (self.synthesize(words), words)
        
def langfile(langname):
	return open('lang_{}.bat'.format(langname)).read()

def loadlang(langname):
    return BLTLanguage(langfile(langname))