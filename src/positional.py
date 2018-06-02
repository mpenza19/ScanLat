# -*- coding: utf-8 -*-
import sys, re, clean
reload(sys)
sys.setdefaultencoding('utf-8')

##############################################################################
#  Categorized letters and digraphs                                          #
##############################################################################

alphabet = 'abcdefghiklmnopqrstuvxyz' + u'āēīōūȳ'
vowels = 'aeiouy'                               # Single vowels
lower_long_vowels = u'āēīōūȳ'                   # Single lowercase long vowels
upper_long_vowels = u'ĀĒĪŌŪȲ'                   # Single uppercase long vowels
all_lower_vowels = lower_long_vowels + vowels
little_i = ('i', 'ī')
diphthongs = ('ae', 'au', 'ei', 'eu', 'oe')     # Diphthongs
consonants = 'bcdfghklmnpqrstv'                 # Single consonants
plosives = 'pbtdcg'                             # Plosive-liquid combinations (treated as single cons.)
liquids = 'rl'
single_cons_digraphs = ('qu', 'ch', 'ph', 'th') # Digraphs treated as single consonants
qu = 'qu'
double_cons_letters = ('x', 'z')                # Letters counted as two consonants
punctuation = '.,?!/()|\\[]–;—:-`\'\"'          # Punctuation marks

##############################################################################
#  Text representation and analysis                                          #
##############################################################################

def tokenize(data):
    """ Cleans and tokenizes whole-document input """

    wholelines = data.decode('utf-8').splitlines()
    tokenized_lines = []
    for wholeline in wholelines:
        tokens = re.findall(r"[\w']+|[.,!?();:]", wholeline, flags=re.UNICODE)
        tokens = [Word(t) for t in tokens if not t.isdigit()]
        tokenized_lines.append(tokens)

    return tokenized_lines

class Word:
    """ Representation of a word as plaintext and a list of syllables """
    def __init__(self, word):
        self.word = word                                      # Plaintext whole word
        self.syllables = self.syllabify(word)                 # List of constituent Syllables

    # Breaks word into Syllables
    def syllabify(self, word):
        if word in punctuation: return [Syllable(word)]
        if word.startswith("ERROR_"): return [Syllable(str(word))]
        wordc = word.lower()

        # Special case: rare diphthong 'ui'
        if wordc in ('huic', 'hui', 'cui'): return [Syllable(word)]
        
        # Special case: rare long first syllable of words with consonantal 'i' between vowels
        if wordc in ('huius', 'cuius', 'maior', 'peior'): return [Syllable(word[0:3]), Syllable(word[3:])]

        ext = "_____"
        wordc += ext # underscore-extended copy of word for analysis
        seps = [False] * len(word) # True: letter marks start of new noninitial syllable; False: otherwise

        i = 0
        while i < len(wordc):
            if i == 0 and wordc[i] in little_i and wordc[i+1] in all_lower_vowels: i += 1 # Skip initial consonantal 'I' preceding vowel/diphthong
            elif wordc[i:i+2] == qu: i += 2 # Skip 'qu' as single consonant
            elif wordc[i] not in all_lower_vowels: i += 1 # Skip single consonants
            else:
                rules = {
                    "VIV"             : (wordc[i:i+2] not in diphthongs and wordc[i+1] in little_i and wordc[i+2] in all_lower_vowels,                                                                                  1, 2),
                    "DDIV_or_DDIDD"   : (wordc[i:i+2] in diphthongs and wordc[i+2] in little_i and wordc[i+3] in all_lower_vowels,                                                                                      2, 3),
                    "VV"              : (wordc[i:i+2] not in diphthongs and wordc[i+1] in all_lower_vowels,                                                                                                             1, 1),
                    "VDD"             : (wordc[i:i+2] not in diphthongs and wordc[i+1:i+3] in diphthongs,                                                                                                               1, 2),
                    "DDV"             : (wordc[i:i+2] in diphthongs and wordc[i+2] in all_lower_vowels,                                                                                                                 2, 2),
                    "VXV"             : (wordc[i+1] in double_cons_letters and wordc[i+2] in all_lower_vowels,                                                                                                          2, 2),
                    "VXPLV"           : (wordc[i+1] in double_cons_letters and wordc[i+2] in plosives and wordc[i+3] in liquids and wordc[i+4] in all_lower_vowels,                                                     2, 4),
                    "VXCV"            : (wordc[i+1] in double_cons_letters and wordc[i+2] in consonants and wordc[i+3] in all_lower_vowels and wordc[i+2:i+4] != qu,                                                    2, 3),
                    "VXCCV"           : (wordc[i+1] in double_cons_letters and wordc[i+2] in consonants and wordc[i+3] in consonants and wordc[i+4] in all_lower_vowels and wordc[i+3:i+5] != qu,                       2, 4),
                    "VCV"             : (wordc[i+1] in consonants and wordc[i+2] in all_lower_vowels and wordc[i+1:i+3] != qu,                                                                                          1, 2),
                    "VPLV"            : (wordc[i+1] in plosives and wordc[i+2] in liquids and wordc[i+3] in all_lower_vowels,                                                                                           1, 3),
                    "VCPLV"           : (wordc[i+1] in consonants and wordc[i+2] in plosives and wordc[i+3] in liquids and wordc[i+4] in all_lower_vowels,                                                              2, 4),
                    "VSSV"            : (wordc[i+1:i+3] in single_cons_digraphs and wordc[i+3] in all_lower_vowels,                                                                                                     1, 3),
                    "VCSSV"           : (wordc[i+1] in consonants and wordc[i+2:i+4] in single_cons_digraphs and wordc[i+4] in all_lower_vowels,                                                                        2, 4),
                    "VCCV"            : (wordc[i+1] in consonants and wordc[i+2] in consonants and wordc[i+3] in all_lower_vowels and wordc[i+2:i+4] != qu,                                                             2, 3),
                    "VCQUV"           : (wordc[i+1] in consonants and wordc[i+2:i+4] == qu and wordc[i+4] in all_lower_vowels,                                                                                          2, 4),
                    "VCCCV"           : (wordc[i+1] in consonants and wordc[i+2] in consonants and wordc[i+3] in consonants and wordc[i+4] in all_lower_vowels and wordc[i+3:i+5] != qu,                                3, 4),
                    "VCCQUV"          : (wordc[i+1] in consonants and wordc[i+2] in consonants and wordc[i+3:i+5] == qu and wordc[i+5] in all_lower_vowels,                                                             3, 5),
                    "VCCCCV"          : (wordc[i+1] in consonants and wordc[i+2] in consonants and wordc[i+3] in consonants and wordc[i+4] in consonants and word[i+5] in all_lower_vowels and wordc[i+4:i+6] != qu,    4, 5)
                }

                for key in rules.keys():
                    is_this_rule, seps_incr, i_incr = rules[key]
                    if is_this_rule:
                        seps[i + seps_incr] = True
                        i += i_incr
                        break
                else: i += 1

        syllables = []
        syl = ''
        for i in range(len(word)):
            if seps[i]:
                syllables.append(Syllable(syl))
                syl = ''
            syl = syl + word[i]
        syllables.append(Syllable(syl))

        return syllables

    def get_word(self):         return self.word
    def get_syllables(self):    return self.syllables
    def __str__(self):          return self.word

class Syllable:
    """ Representation of a syllable parsed into its onset, nucleus, and coda
    """

    def __init__(self, syl):
        self.syl = syl.decode('utf-8')                          # Plaintext whole syllable
        self.is_syl = True                                      # Assume not empty or punct. unless parse() finds otherwise
        self.iserror = False
        self.onset, self.nucleus, self.coda = self.parse()      # Plaintext syllable components

        self.fnucleus = None                                    # Formatted nucleus (diphthongs not macronized)
        self.next = None                                        # The next syllable ***in the LINE***
        self.brevisinlongo = False
        

    def parse(self):
        """ Breaks plaintext whole syllable into onset, nucleus, and coda """
        onset, nucleus, coda = '', '', ''

        if self.syl.startswith("ERROR_") or self.syl.startswith("error_"):
            self.iserror = True
            return onset, nucleus, coda

        sylc = self.syl.lower() # Lowercased syllable for analysis ('c' for 'comparison')

        if len(sylc) == 0 or self.syl in (' ', '\n') or (len(sylc) == 1 and sylc in punctuation):
            self.is_syl = False
            return onset, nucleus, coda

        has_onset = sylc[0] in consonants or sylc[0] in double_cons_letters
        if len(sylc) > 1: has_onset = has_onset or (sylc[0] in little_i and sylc[1] in all_lower_vowels)
        has_coda = sylc[-1] in consonants or sylc[-1] in double_cons_letters

        # Find start of nucleus
        i = 0
        while i < len(sylc):
            if sylc[i:i+2] == qu:
                i += 2
                continue

            if i == 0 and sylc[i] in little_i and i+1 < len(sylc) and sylc[i+1] in all_lower_vowels:
                i += 1
                continue

            if sylc[i] in all_lower_vowels:
                first_vowel_index = i
                break

            i += 1

        # Find end of nucleus
        for i in reversed(range(len(sylc))):
            if sylc[i] in all_lower_vowels:
                last_vowel_index = i
                break

        # Determine and return onset, nucleus, and coda
        if has_onset:
            onset = self.syl[0:first_vowel_index]
            #print "onset:", onset

        nucleus = self.syl[first_vowel_index:last_vowel_index+1]
        #print "nucleus:", nucleus

        if has_coda:
            coda = self.syl[last_vowel_index+1:]
            #print "coda:", coda

        if len(nucleus) > 2:
            sys.stderr.write("ERROR: TOO MANY CHARACTERS IN NUCLEUS: %s\n" % nucleus)
            return

        return onset, nucleus, coda

    def get_onset(self):    return self.onset
    def get_nucleus(self):  return self.nucleus
    def get_coda(self):     return self.coda
    def get_next(self):     return self.next
    def set_next(self, next): self.next = next

    def macronize(self):
        if self.nucleus == '': return
        
        should_macronize = self.get_brevisinlongo() # Brevis in longo
        should_macronize = should_macronize or len(self.coda) == 2 or self.coda in double_cons_letters # Ends in double consonant
        should_macronize = should_macronize or (self.coda != '' and self.next is not None and self.next.get_onset() != '')
        
        if should_macronize: 
            if len(self.nucleus) == 1:
                if self.nucleus == self.nucleus.lower():
                    if self.nucleus in lower_long_vowels.decode('utf-8'):
                        self.fnucleus = self.nucleus
                    else:
                        self.fnucleus = lower_long_vowels[vowels.index(self.nucleus)]

                elif self.nucleus == self.nucleus.upper():
                    if self.nucleus in upper_long_vowels.decode('utf-8'):
                        self.fnucleus = self.nucleus
                    else:
                        self.fnucleus = upper_long_vowels[vowels.index(self.nucleus.lower())]

            else:
                self.fnucleus = self.nucleus

    def get_brevisinlongo(self):
        return self.brevisinlongo

    def set_brevisinlongo(self, is_brevis):
        self.brevisinlongo = is_brevis

    def __str__(self):
        if self.syl in punctuation: return self.syl
        if not self.is_syl: return ''
        if self.syl.startswith("ERROR_"): return self.syl

        o = self.onset if self.onset != '' else ''
        n = self.fnucleus if self.fnucleus is not None else self.nucleus
        c = self.coda if self.coda != '' else ''
        return o+n+c

    def verbose(self):
        if self.syl in punctuation: return self.syl
        if not self.is_syl: return ''

        o = self.onset if self.onset != '' else '_'
        n = self.fnucleus if self.fnucleus is not None else self.nucleus
        c = self.coda if self.coda != '' else '_'
        return '[%s-%s-%s]' % (o, n, c)

def print_syllabified(data):
    for line in tokenize(data):
        sys.stdout.write("ORIGINAL:\t")
        for word in line:
            sys.stdout.write("%s " % word)
        sys.stdout.write('\n')

        sys.stdout.write("SYLLABIFIED:\t")
        for w in range(len(line)):
            for syl in line[w].get_syllables():
                sys.stdout.write(syl.verbose())
            sys.stdout.write('  ')
        sys.stdout.write('\n\n')


def print_document(data):
    output = ""
    tokenized_data = tokenize(data)
    for l in range(len(tokenized_data)):
        line = tokenized_data[l]


        for word_index in range(len(line)):
            word = line[word_index]
            syllables = word.get_syllables()
            
            index = 0
            if word_index == 0:
                prev_syl = syllables[0]
                index = 1

            

            for syl_in_word in range(index-1, len(syllables)-1):
                syl_in_word += 1
                
                if word_index == len(line)-1 and syl_in_word == len(syllables)-1 and not syllables[-1].is_syl:
                    prev_syl.set_brevisinlongo(True)

                this_syl = syllables[syl_in_word] 

                jump_punct = not this_syl.is_syl
                jump_punct = jump_punct and word_index+1 < len(line)-1
                if jump_punct:
                    nextwordsyls = line[word_index+1].get_syllables()
                    jump_punct = nextwordsyls[0].is_syl
                    
                if this_syl.is_syl:
                    prev_syl.set_next(this_syl)
                    prev_syl.macronize()

                elif jump_punct:
                    prev_syl.set_next(nextwordsyls[0])
                    prev_syl.macronize()

                prev_syl.macronize()

                if word_index != 0 and syl_in_word == 1: output += ' '
                output += str(prev_syl)
                prev_syl = this_syl
                if len(syllables) == 1: output += ' '
            
        this_syl.set_brevisinlongo(True)
        this_syl.macronize()
        
        if l != len(tokenized_data)-1: output += str(this_syl) + '\n'

    split_output = output.split('\n')
    for l in range(len(split_output)): 
        line_num = str(l+1) if (l+1) % 5 == 0 else ''
        line = split_output[l]
        sys.stdout.write("%s\t%s\n" % (line_num, line.strip()))

def main():
    data = clean.clean_lines(sys.stdin.read())
    print_document(data)

main()