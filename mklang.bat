@echo OFF

ECHO Welcome to the ELSKIES Semi-Automatic Language Generator.
ECHO (c)2018 Gustavo R. Rehermann. CC0.
ECHO. 
ECHO [STEP 1. METADATA]
SET /P langname=Desired language name:
SET viewed=n
ECHO @echo off>lang_%langname%.bat
ECHO SET langname=%langname%>>lang_%langname%.bat
ECHO.
ECHO [STEP 2. RADICALS] - required: 'be', 'good', 'name'
GOTO :MKRADS

:MORE
ECHO Add more %1? (y for yes, anything else for no)
SET /P answer=:
IF %answer%==Y GOTO :%2
IF %answer%==y GOTO :%2
GOTO :%3

:MKRADS
ECHO Radical in English (e.g. 'beaut' for 'beauty', also some whole
SET /P radname=nouns and adj. like 'good'):
SET /P rad.%radname%=Radical in desired language:
CALL ECHO SET rad.%radname%=%%rad.%radname%%%>>lang_%langname%.bat

CALL :MORE radicals MKRADS MKLIGATION
EXIT /B

:MKLIGATION
ECHO.
ECHO [STEP 3. LIGATIONS]
SET /P ligation=Ligation syllable (e.g. ge[o]graphy): 
ECHO SET ligation=%ligation%>>lang_%langname%.bat
GOTO :MKNEGATION

:MKNEGATION
ECHO.
ECHO [STEP 4. NEGATION]
SET /P negation.type=Adjective negation type ('prefix' or 'adverb', MUST be lowercase): 
IF %negation.type%==prefix GOTO :MKNEG.OK
IF %negation.type%==adverb GOTO :MKNEG.OK 

EXIT /B
ECHO Bad answer!
GOTO :MKNEGATION

:MKNEG.OK
SET /P negation.adjective=Adjective negation prefix/adverb ([not] big): 
SET /P negation.verbal=Verbal negation prefix ([not] walking): 
SET /P negation.nominal=Nominal negation prefix ([un]intelligent): 

ECHO SET negation.type=%negation.type%>>lang_%langname%.bat
ECHO SET negation.adjective=%negation.adjective%>>lang_%langname%.bat
ECHO SET negation.nominal=%negation.nominal%>>lang_%langname%.bat
ECHO SET negation.verbal=%negation.verbal%>>lang_%langname%.bat

GOTO :MKENDING

:MKENDING
ECHO.
ECHO [STEP 5. ENDINGS]
SET /P ending.adjective.superlative=Superlative adjective ending (i.e. beautiful[est]): 
SET /P ending.adjective.comparative=Comparative adjective ending (i.e. beautiful[ler]): 
SET /P ending.adjective.genitive=Genitive adjective ending (i.e. beauti[ful]): 
SET /P ending.adjective.ingenitive=Ingenitive adjective ending (i.e. reck[less]): 
SET /P ending.nominal=Nominal conversion ending (i.e. beaut[y]): 
SET /P ending.plural=Nominal ending of plurality (i.e. bee[s]): 
SET /P ending.nominal.genitive=Nominal ending of genitivity (i.e. Andy['s] toy): 
SET /P ending.nominal.degree.small=Degree nominal ending of plurality, for small (i.e. [little] spark - except as a suffix): 
SET /P ending.nominal.degree.large=Degree nominal ending of plurality, for large (i.e. [big] car - except as a suffix): 
SET /P ending.nominal.gender.male=Degree nominal ending of gender, for male nouns: 
SET /P ending.nominal.gender.female=Degree nominal ending of gender, for female nouns: 

ECHO SET ending.adjective.superlative=%ending.adjective.superlative%>>lang_%langname%.bat
ECHO SET ending.adjective.comparative=%ending.adjective.comparative%>>lang_%langname%.bat
ECHO SET ending.adjective.genitive=%ending.adjective.genitive%>>lang_%langname%.bat
ECHO SET ending.adjective.ingenitive=%ending.adjective.ingenitive%>>lang_%langname%.bat
ECHO SET ending.nominal=%ending.nominal%>>lang_%langname%.bat
ECHO SET ending.plural=%ending.plural%>>lang_%langname%.bat
ECHO SET ending.nominal.genitive=%ending.nominal.genitive%>>lang_%langname%.bat
ECHO SET ending.nominal.degree.small=%ending.nominal.degree.small%>>lang_%langname%.bat
ECHO SET ending.nominal.degree.large=%ending.nominal.degree.large%>>lang_%langname%.bat
ECHO SET ending.nominal.gender.male=%ending.nominal.gender.male%>>lang_%langname%.bat
ECHO SET ending.nominal.gender.female=%ending.nominal.gender.female%>>lang_%langname%.bat

GOTO :MKPRONOUN

:MKPRONOUN
ECHO.
ECHO [STEP 6. PRONOUNS]

SET /P pronoun.nominal.first.singular=nominal first-person singular pronoun (I, me): 
SET /P pronoun.nominal.second.singular=nominal second-person singular pronoun (thou, you): 
SET /P pronoun.nominal.third.singular=nominal third-person singular pronoun (he, she, him, her): 
SET /P pronoun.nominal.first.plural=nominal first-person plural pronoun (we, us): 
SET /P pronoun.nominal.second.plural=nominal second-person plural pronoun (you, ye): 
SET /P pronoun.nominal.third.plural=nominal third-person plural pronoun (they): 

SET /P pronoun.genitive.first.singular=Genitive first-person singular pronoun (my): 
SET /P pronoun.genitive.second.singular=Genitive second-person singular pronoun (thy, your): 
SET /P pronoun.genitive.third.singular=Genitive third-person singular pronoun (his, her, its): 
SET /P pronoun.genitive.first.plural=Genitive first-person plural pronoun (our): 
SET /P pronoun.genitive.second.plural=Genitive second-person plural pronoun (your): 
SET /P pronoun.genitive.third.plural=Genitive third-person plural pronoun (their): 

SET /P pronoun.indefinite.singular=Singular indefinite pronoun (it): 
SET /P pronoun.indefinite.plural=Plural indefinite pronoun (it - except plural): 
SET /P pronoun.indefinite.pointer.external=External pointer indefinite pronoun (that)
SET /P pronoun.indefinite.pointer.internal=Internal pointer indefinite pronoun (this)

ECHO SET pronoun.nominal.first.singular=%pronoun.nominal.first.singular%>>lang_%langname%.bat
ECHO SET pronoun.nominal.second.singular=%pronoun.nominal.second.singular%>>lang_%langname%.bat
ECHO SET pronoun.nominal.third.singular=%pronoun.nominal.third.singular%>>lang_%langname%.bat
ECHO SET pronoun.nominal.first.plural=%pronoun.nominal.first.plural%>>lang_%langname%.bat
ECHO SET pronoun.nominal.second.plural=%pronoun.nominal.second.plural%>>lang_%langname%.bat
ECHO SET pronoun.nominal.third.plural=%pronoun.nominal.third.plural%>>lang_%langname%.bat

ECHO SET pronoun.genitive.first.singular=%pronoun.genitive.first.singular%>>lang_%langname%.bat
ECHO SET pronoun.genitive.second.singular=%pronoun.genitive.second.singular%>>lang_%langname%.bat
ECHO SET pronoun.genitive.third.singular=%pronoun.genitive.third.singular%>>lang_%langname%.bat
ECHO SET pronoun.genitive.first.plural=%pronoun.genitive.first.plural%>>lang_%langname%.bat
ECHO SET pronoun.genitive.second.plural=%pronoun.genitive.second.plural%>>lang_%langname%.bat
ECHO SET pronoun.genitive.third.plural=%pronoun.genitive.third.plural%>>lang_%langname%.bat

ECHO SET pronoun.indefinite.singular=%pronoun.indefinite.singular%>>lang_%langname%.bat
ECHO SET pronoun.indefinite.plural=%pronoun.indefinite.plural%>>lang_%langname%.bat
ECHO SET pronoun.indefinite.pointer.external=%pronoun.indefinite.pointer.external%>>lang_%langname%.bat
ECHO SET pronoun.indefinite.pointer.internal=%pronoun.indefinite.pointer.internal%>>lang_%langname%.bat

ECHO.
GOTO :MKADVERB

:MKADVERB
ECHO.
ECHO [STEP 7. ADVERBS]

SET /P adverb.adjective=Adjective adverbial suffix (great[ly]):
SET /P adverb.verbal=Verbal adverbial suffix (dy[ingly] poisoning monster):

ECHO SET adverb.adjective=%adverb.adjective%>>lang_%langname%.bat
ECHO SET adverb.verbal=%adverb.verbal%>>lang_%langname%.bat

GOTO MKCONJUG

:MKCONJUG
IF %viewed%==y GOTO :STOP
ECHO.
ECHO [STEP 8. CONJUGATIONS]

SET /P conjugation.first.singular=Singular first-person conjugation (verbal radical suffix): 
SET /P conjugation.second.singular=Singular second-person conjugation (verbal radical suffix): 
SET /P conjugation.third.singular=Singular third-person conjugation (verbal radical suffix): 
SET /P conjugation.first.plural=Plural first-person conjugation (verbal radical suffix): 
SET /P conjugation.second.plural=Plural second-person conjugation (verbal radical suffix): 
SET /P conjugation.third.plural=Plural third-person conjugation (verbal radical suffix):
SET /P conjugation.imperative=Imperative conjugation suffix (verbal addition): 
SET /P conjugation.subjunctive=Subjunctive conjugation suffix (verbal addition): 
SET /P conjugation.infinitive=Infinitive conjugation suffix (verbal addition): 
SET /P conjugation.gerund=Gerund conjugation suffix (verbal addition): 
SET /P conjugation.active=Active conjugation suffix (verbal addition): 
SET /P conjugation.passive=Passive conjugation suffix (verbal addition): 

ECHO SET conjugation.indictaifirst.singular=%conjugation.first.singular%>>lang_%langname%.bat
ECHO SET conjugation.second.singular=%conjugation.second.singular%>>lang_%langname%.bat
ECHO SET conjugation.third.singular=%conjugation.third.singular%>>lang_%langname%.bat
ECHO SET conjugation.first.plural=%conjugation.first.plural%>>lang_%langname%.bat
ECHO SET conjugation.second.plural=%conjugation.second.plural%>>lang_%langname%.bat
ECHO SET conjugation.third.plural=%conjugation.third.plural%>>lang_%langname%.bat
ECHO SET conjugation.imperative=%conjugation.imperative%>>lang_%langname%.bat
ECHO SET conjugation.subjunctive=%conjugation.subjunctive%>>lang_%langname%.bat
ECHO SET conjugation.infinitive=%conjugation.infinitive%>>lang_%langname%.bat
ECHO SET conjugation.gerund=%conjugation.gerund%>>lang_%langname%.bat
ECHO SET conjugation.active=%conjugation.active%>>lang_%langname%.bat
ECHO SET conjugation.passive=%conjugation.passive%>>lang_%langname%.bat

GOTO :MKTIMES

:MKTIMES
ECHO.
ECHO [STEP 9. VERBAL TIMES]
ECHO Remember, present verbs have NO time suffix.
ECHO.

SET /P time.perfect=Simple past verbal time suffix (made instead of make, but suffix): 
SET /P time.transpast=Transpast verbal time suffix (was making): 
SET /P time.pluperfect=Pluperfect past verbal time suffix (used to make): 
SET /P time.preteritous=Preteritous past verbal time suffix (had made): 
SET /P time.pseudopast=Pseudopast/continuous verbal time suffix (have been making): 
SET /P time.subpast=Subpast verbal time suffix (would have maken): 
SET /P time.subpresent=Simple subpresent verbal time suffix (have made): 
SET /P time.future=Simple future verbal time suffix (will make): 
SET /P time.subfuture=Subfuture verbal time suffix (would make): 
SET /P time.pseudofuture=Pseudofuture verbal time suffix (will have made): 

ECHO SET time.perfect=%time.perfect%>>lang_%langname%.bat
ECHO SET time.pluperfect=%time.pluperfect%>>lang_%langname%.bat
ECHO SET time.preteritous=%time.preteritous%>>lang_%langname%.bat
ECHO SET time.pseudopast=%time.pseudopast%>>lang_%langname%.bat
ECHO SET time.subpast=%time.subpast%>>lang_%langname%.bat
ECHO SET time.subpresent=%time.subpast%>>lang_%langname%.bat
ECHO SET time.future=%time.future%>>lang_%langname%.bat
ECHO SET time.subfuture=%time.subfuture%>>lang_%langname%.bat

GOTO :MKCOMPOSITES

:MKCOMPOSITES
ECHO.
ECHO [STEP 10. COMPOSITE WORDS]
SET /P "key=Word in English (e.g. 'weapon'): "
ECHO Semicolon-separated list of radicals with which
SET /P "values=to form the word (e.g. 'death; tool'): "
ECHO SET composite.%key%=%values%>>lang_%langname%.bat

CALL :MORE composites MKCOMPOSITES END
EXIT /B

:END
IF %viewed%==y GOTO :STOP
ECHO.
ECHO.
ECHO.
ECHO Done! Viewing:
ECHO.
IF %negation.type%==prefix (
    ECHO.'My name is Olster. It is good and not big, but weird. I speak Latko.' = '%pronoun.genitive.first.singular% %rad.name% %rad.be%%conjugation.third.singular% Olster. %pronoun.nominal.third.singular% %rad.be%%conjugation.third.singular% %rad.good% %conjunction.and% %negation.adjective%%rad.big%, %conjunction.but% %rad.weird%. %pronoun.nominal.first.singular% %rad.speak% %langname%.'
) ELSE (
    ECHO.'My name is Olster. It is good and not big, but weird. I speak Latko.' = '%pronoun.genitive.first.singular% %rad.name% %rad.be%%conjugation.third.singular% Olster. %pronoun.nominal.third.singular% %rad.be%%conjugation.third.singular% %rad.good% %conjunction.and% %negation.adjective% %rad.big%, %conjunction.but% %rad.weird%.. %pronoun.nominal.first.singular% %rad.speak% %langname%.'
)
SET viewed=y
GOTO :STOP

:STOP