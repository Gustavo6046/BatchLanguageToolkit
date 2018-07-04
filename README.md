# Batch Language Toolkit
**Galactic languages, as close from your tongue as your computer is from your chair.**

The Batch Language Toolkit is a simplistic attempt to do a flexible language superset, upon which many
similarly-structured languages can be created, fixed, and translated into, using the Python and
Batch interfaces.

## But... I don't know Latko!

It is simple to translate. Just replace Latko by the language of your choice, in these examples, and
you're good to go! No easiness scale is big enough to measure the practicity level of this.
 
**Batch:** _(manual, requires Windows)_

    $ call lang_Latko.bat
    $ echo %rad.good% %rad.morning%%ending.nominal.gender.male%!
    Wlo piiodrumzou!
    
**Python:** _(automatic, but requires NLTK and inflect)_

    >>> import blt
    >>> latko = blt.loadlang('Latko')
    >>> latko.translate("Good morning, afternoon and evening, friend world! And goodbye, huge space.")[0]
    'Wlo piiodrumzou, snodrumzou iet dikodrumzou, wloaijohkoslonenpa kijucloailibadixzou! Iet widjikzou, lingigno exanduailibadixzou.'
    
## Ooh, how does it works?

BLT is, at its root, a bunch of small words, called **radicals**, that can form everything, from nouns, verbs,
adjectives, and even other grammatical features. As a very modular system, BLT will attempt to form more
lexically complex words using multiple radicals, with **ligations** in between.

- Verbs support **conjugation**
(*"I did, you did, he did"*, but as a suffix), **tense** (*"I did, I do, I will do"*, also as a suffix!),
**purpose** (*"You did; did I? (Please) do. To do, doing."*, another suffix!), and **activity versus passivity**
(*"I painted, I'm being painted"*).

- Adjectives support genitivity (*beauti**ful***), *in*genitivity (*reck**less***), comparativity (*bigg**er***),
superlativity (*bigg**est***), and negation, which can be either as a prefix (like in Greek), or as an adverb
(like in English).

- Nouns support possessivity (*Andy**'s** toys*), gender (***she-**wolf*), degree (***big** car*), plurality (*boy**s***),
and even a way to convert other words into nouns (*beaut**y***)!

## That all sounds nice, but are there reasons I should _NOT_ use the BLT?

Well, to begin with, the manual translation is slow and boring, and the Python-based translation is inaccurate, because
English (the source language) is quite lackluster in word details like gender. For example, "doll" does not suggest if
it's a doll of a man or of a woman. The BLT will, as usual, default to male suffix.

Also, the BLT isn't an universal language toolkit. It's just a weird, but fun, word blender. I hope you have fun with
it as well, if you decide to try it out, though :)
