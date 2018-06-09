# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

""" Did you ever read the documentation of os.popen() the Hackish?
I thought not. It's not a technique COS 333 would teach you.
It's a StackOverflow legend.... """
from os import popen

noun_declensions = (0, 1, 2, 3, 4, 5)
adj_declensions = (1, 3)
verb_conjugations = (0, 1, 2, 3, 4)
long_vowels = 'āēīōūȳ'.decode('utf-8')
vowels = 'aeiouy'

# remember to set 'cherub' POS to Noun
class Word:
    def __init__(self, form, lemma, feats_str):
        self.feats_str = feats_str
        self.form, self.lemma = form, lemma
        self.feats = (dict([f.split('=') for f in feats_str.split('|')])) if feats_str not in ["", "_"] else dict()
        self.inflection = None
        self.macronized = None
        self.latmor = None
        self.initcap = form[0] == form[0].upper()

    def find_inflection(self): return None
    def macronize(self): return None
    
    def macronize_default(self, flipped=False):
        lines = list()
        with popen("echo '%s' | fst-mor LatMor/latmor.a" % self.form) as f:
            for line in f: lines.append(line.strip().decode('utf-8')) 
        
        latmors = lines[2:]
        default_latmor = latmors[0]
        default_macronized = "ERROR_"+self.form

        macronization_latmor_pairs = list()
        for lm in latmors:
            macronizations = list()
            with popen("echo '%s' | fst-mor LatMor/latmor-gen.a" % default_latmor) as f:
                for line in f:
                    sys.stderr.write("GETTING: %s %s\n" % (line.strip(), lm))
                    macronizations.append(line.strip().decode('utf-8'))
            
            for m in macronizations[2:]:
                if self.demacronize(m) == self.form and (m, lm) not in macronization_latmor_pairs:
                    macronization_latmor_pairs.append((m, lm))
                    sys.stderr.write("PAIR: %s %s\n" % (m, lm))

        sys.stderr.write("DEFAULT MACRONIZATIONS of form %s:\n" % self.form)
        for (m, lm) in macronization_latmor_pairs: sys.stderr.write("PAIR_PAIR %s --> %s\n" % (m, lm))
        sys.stderr.write('\n')

        if len(macronization_latmor_pairs) >= 1 and not macronization_latmor_pairs[0][0].startswith("no result"):
            return macronization_latmor_pairs[0]

        if not flipped:
            if not self.initcap:
                copy_form = self.form[0].upper() + self.form[1:]
                copy_lemma = self.lemma[0].upper() + self.lemma[1:]
                
            else:
                copy_form = self.form[0].lower() + self.form[1:]
                copy_lemma = self.lemma[0].lower() + self.lemma[1:]

            word_copy = Word(copy_form, copy_lemma, self.feats_str)
            copy_default_macronized, copy_default_latmor = word_copy.macronize_default(flipped=True)
            if copy_default_macronized is not None and not copy_default_macronized.startswith("no result"):
                return copy_default_macronized, copy_default_latmor


        return default_macronized, default_latmor
            

        


    def all_macronizations(self, string):
        lines = []
        with popen("echo '%s' | fst-mor LatMor/latmor-macronizer.a" % string) as f:
            for line in f: lines.append(line.strip().decode('utf-8')) 
        return lines[2:]

    def get_macronizations(self):
        lines = []
        with popen("echo '%s' | fst-mor LatMor/latmor-gen.a" % self.latmor) as f:
            for line in f: lines.append(line.strip())
        lines = [l for l in lines[2:] if self.demacronize(l) == self.form]
        if lines == []: sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'\n" % (self.form, self.lemma, self.inflection, self.latmor))
        return lines

    def demacronize(self, mac):
        demac = mac.replace('ā', 'a').replace('ē', 'e').replace('ī', 'i').replace('ō', 'o').replace('ū', 'u').replace('ȳ', 'y')
        demac = demac.replace('Ā', 'A').replace('Ē', 'E').replace('Ī', 'I').replace('Ō', 'O').replace('Ū', 'U').replace('Ȳ', 'Y')
        return demac


class Noun(Word):
    def __init__(self, form, lemma, feats_str):
        Word.__init__(self, form, lemma, feats_str)
        self.inflection = self.find_inflection()

        self.gender = self.feats["Gender"].lower() if "Gender" in self.feats else None
        self.case = self.feats["Case"].lower() if "Case" in self.feats else None
        self.number = None if "Number" not in self.feats else "sg" if self.feats["Number"] == "Sing" else "pl" if self.feats["Number"] == "Plur" else None
        self.latmor = "%s<N><%s><%s><%s>" % (self.lemma, self.gender, self.number, self.case)
        #print '\n', self.form, '-->', self.latmor

        self.macronized = self.macronize()
        
        demac = self.demacronize(self.macronized)
        if self.form != demac:
            sys.stderr.write("\nMACRONIZATION ERROR: form '%s', macronization '%s', demacronization '%s'\n\n" % (self.form, self.macronized, demac))

    def set_gender(self, newgender):
        if newgender not in ["Masc", "Fem", "Neut"]:
            sys.stderr.write("Invalid gender reset attempt: '%s'\n" % newgender)
            return

        old_latmor = self.latmor
        self.feats["Gender"] = newgender
        self.gender = newgender.lower()
        self.latmor = "%s<N><%s><%s><%s>" % (self.lemma, self.gender, self.number, self.case)
        #print 'RESET:', old_latmor, '-->', self.latmor

    def find_inflection(self):
        lemma, feats = self.lemma, self.feats
        
        if lemma in ['domus', 'locus', 'deus', 'balneus', 'bos', 'cherub', 'Iesus', 'Jesus']:
            return 0 # irregular

        if lemma in ['dies', 'meridies']:                               return 5
        if lemma == 'aer':                                              return 3
                
        if lemma[-1] == 'a':                                            return 1
        if "Gender" in feats:
            if lemma[-1] == 'e' and feats["Gender"] == "Fem":               return 1
            if lemma[-2:] in ['es', 'as'] and feats["Gender"] == "Masc":    return 1

            if lemma[-2:] == 'er' and feats["Gender"] == "Masc": return 2
            if lemma[-2:] == 'us' and feats["Gender"] == "Masc":
                if len(self.all_macronizations(lemma)) > 1: return 4
                return 2

            if lemma[-2:] == 'um' and feats["Gender"] == "Neut":            return 2
            if lemma[-2:] == 'os' and feats["Gender"] in ["Masc", "Fem"]:   return 2
            if 'y' in lemma and lemma[-2:] in ['us', 'os'] and feats["Gender"] in ["Masc", "Fem"]: return 2

            if lemma[-2:] == 'us' and feats["Gender"] in ["Masc", "Fem"]:   return 4
            if lemma[-1] == 'u' and feats["Gender"] == "Neut":              return 4
            if lemma[-1] == 'o' and feats["Gender"] == "Fem":               return 4
            
            if lemma[-2:] == 'es' and feats["Gender"] == "Fem":             return 5
        
        return 3

    def macronize_first(self):
        form, lemma, feats, declension = self.form, self.lemma, self.feats, self.inflection
        candidates = self.get_macronizations()

        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        # Handle Greek accusative singular variants
        if len(candidates) > 1:
            lastc = form[-1]
            for cand in candidates:
                if cand[-1] == lastc:
                    #print "returning:", cand
                    return cand
            sys.stderr.write("PROBLEM: 1st decl. noun '%s' has multiple macronizations but no suitable match:\t" % form)
            for cand in candidates: sys.stderr.write("%s\t" % cand)
            sys.stderr.write('\n')
            return "ERROR"

        # Handle normal forms
        #print "returning:", candidates[0]
        return candidates[0]

    def macronize_second(self):
        form, lemma, feats, declension = self.form, self.lemma, self.feats, self.inflection
        candidates = self.get_macronizations()
        
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        # Handle Greek variants: nominative singular m/f and neuter; accusative singular m/f/n; vocative neuter 
        if len(candidates) > 1:
            if self.number == "sg" and self.case in ["nom", "acc", "voc"] and form[-2:] in ['os', 'us', 'on', 'um']:
                lastcc = form[-2:]
                for cand in candidates:
                    if cand[-2:] == lastcc:
                        #print "returning:", cand
                        return cand
            
            sys.stderr.write("PROBLEM: 2nd decl. noun '%s' has multiple macronizations but no suitable match:\t" % form)
            for cand in candidates: sys.stderr.write("%s\t" % cand)
            sys.stderr.write('\n')
            return "ERROR"

        #print "returning:", candidates[0]
        return candidates[0]

    def macronize_third(self):
        form, lemma, feats, declension = self.form, self.lemma, self.feats, self.inflection
        candidates = self.get_macronizations()
        
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        if len(candidates) > 1:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: Multiple macronizations for 3-rd declension Noun '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        return candidates[0]

    def macronize_fourth_fifth(self):
        form, lemma, feats, declension = self.form, self.lemma, self.feats, self.inflection
        candidates = self.get_macronizations()
        
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        # Handle variants (there should be none)
        if len(candidates) > 1:
            sys.stderr.write("PROBLEM: 4th decl. noun '%s' has multiple macronizations (should not be possible):\t" % form)
            for c in candidates: sys.stderr.write("%s " % c)
            sys.stderr.write('\n')
            return "ERROR"
            
        #print "returning:", candidates[0]
        return candidates[0]

    def macronize_irreg(self):
        form, lemma, feats, declension = self.form, self.lemma, self.feats, self.inflection
        case, number = feats["Case"], feats["Number"]
        
        #'āēīōūȳ'.decode('utf-8')

        """
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized
        """

        if lemma == "domus":
            if number == "Sing":
                if case in ["Nom", "Voc"]: return "domus"

                if case == "Gen":
                    if form == "domus": return "domūs".decode('utf-8')
                    if form == "domi": return "domī".decode('utf-8')
                    sys.stderr.write("Invalid gen. sg. form '%s' of lemma '%s'.\n" % (form, lemma))
                    return "ERROR"

                if case == "Dat":
                    if form == "domui": return "domuī".decode('utf-8')
                    if form == "domo": return "domō".decode('utf-8')
                    if form == "domu": return "domū".decode('utf-8')
                    sys.stderr.write("Invalid dat. sg. form '%s' of lemma '%s'.\n" % (form, lemma))
                    return "ERROR"

                if case == "Acc": return "domum"

                if case == "Abl":
                    if form == "domo": return "domō".decode('utf-8')
                    if form == "domu": return "domū".decode('utf-8')
                    sys.stderr.write("Invalid abl. sg. form '%s' of lemma '%s'.\n" % (form, lemma))
                    return "ERROR"

            else:
                if case in ["Nom", "Voc"]: return "domūs".decode('utf-8')

                if case == "Gen": 
                    if form == "domuum": return "domuum"
                    if form == "domorum": return "domōrum".decode('utf-8')
                    sys.stderr.write("Invalid gen. pl. form '%s' of lemma '%s'.\n" % (form, lemma))
                    return "ERROR"

                if case in ["Dat", "Abl"]: return "domibus"

                if case == "Acc":
                    if form == "domus": return "domūs".decode('utf-8')
                    if form == "domos": return "domōs".decode('utf-8')
                    sys.stderr.write("Invalid acc. pl. form '%s' of lemma '%s'.\n" % (form, lemma))
                    return "ERROR"

        if lemma == "locus":
            if form == "loca": return "loca"
            self.set_gender("Masc")
            return self.macronize_second()

        if lemma == "deus":
            retval = "RETVAL"
            lform = form.lower()

            if number == "Sing":
                if case != "Voc":
                    retval = self.macronize_second()
                
                else:
                    if lform == "deus": retval = "deus"
                    if lform == "dee": retval = "dee"

            else:
                if case in ["Nom", "Voc"]:
                    if lform == "di": retval = "dī"
                    if lform == "dii": retval = "diī"
                    if lform == "dei": retval = "deī"
                
                if case == "Gen":
                    if lform == "deorum": retval = "deōrum"
                    if lform == "deum": retval = "deum"

                if case in ["Dat", "Abl"]:
                    if lform == "dis": retval = "dīs"
                    if lform == "diis": retval = "diīs"
                    if lform == "deis": retval = "deīs"
                
                if case == "Acc":
                    retval = "deōs"

            retval = retval.decode('utf-8')
            if form[0] == 'd': 
                #print "returning2:", retval
                return retval
            if form[0] == 'D': 
                #print "returning2:", 'D' + retval[1:]
                return 'D' + retval[1:]

        if lemma == "balneus":
            if form == "balneum": return "balneum"
            return self.macronize_second()

        if lemma == "bos":
            if form == "bos": return "bōs".decode('utf-8')
            if form == "bobus": return "bōbus".decode('utf-8')
            if form == "bubus": return "būbus".decode('utf-8')
            return self.macronize_third()
        
        # Remember to coerce "cherub" to be a noun
        if lemma == "cherub":
            return form

        if lemma in ["Iesus", "Jesus"]:
            if case == "Nom": return "Iēsus"
            if case == "Acc": return "Iēsum"
            return "Iēsū"

    def macronize(self):
        form, lemma, feats, declension = self.form, self.lemma, self.feats, self.inflection

        if declension not in noun_declensions or self.gender is None or self.case is None or self.number is None:
            sys.stderr.write("ERROR: Does not have valid declension or gender or case or number\tform: %s\tlemma: %s\tdeclension: %s\tgender: %s\tcase: %s\tnumber: %s\n" % (form, lemma, declension, self.gender, self.case, self.number))
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        if declension == 0:
            mac = self.macronize_irreg()
            #print "returning:", mac
            return mac

        if declension == 1: return self.macronize_first()
        if declension == 2: return self.macronize_second()
        if declension == 3: return self.macronize_third()
        if declension in [4, 5]: return self.macronize_fourth_fifth()

class Adj(Word):
    def __init__(self, form, lemma, feats_str):
        Word.__init__(self, form, lemma, feats_str)
    
        self.gender = self.feats["Gender"].lower() if "Gender" in self.feats else None
        self.gender = self.gender[:self.gender.index(',')] if self.gender is not None and ',' in self.gender else self.gender
        self.case = self.feats["Case"].lower()
        self.number = "sg" if self.feats["Number"] == "Sing" else "pl" if self.feats["Number"] == "Plur" else "ERROR"
        self.degree = None if "Degree" not in self.feats else "positive" if self.feats["Degree"] == "Pos" else "comparative" if self.feats["Degree"] == "Cmp" else "superlative" if self.feats["Degree"] == "Sup" else "ERROR"
        self.latmor = "%s<ADJ><%s><%s><%s><%s>" % (self.lemma, self.degree, self.gender, self.number, self.case) if self.gender is not None else "%s<ADJ><%s><%s><%s>" % (self.lemma, self.degree, self.number, self.case)

        self.inflection = self.find_inflection()
        self.macronized = self.macronize()

    def find_inflection(self):
        lemma, feats = self.lemma, self.feats

        if lemma in ('bonus', 'magnus', 'malus', 'parvus', 'multus') or self.degree is None: return 0 # irregular
        if feats["Degree"] == "Pos":  
            if lemma[-2:] == 'us': return 1
            return 3
        if feats["Degree"] == "Cmp": return 3
        if feats["Degree"] == "Sup": return 1

    def macronize(self):
        candidates = self.get_macronizations()
        
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        if len(candidates) > 1:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: Multiple macronizations for Adjective '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        return candidates[0]

class Adv(Word):
    def __init__(self, form, lemma, feats_str):
        Word.__init__(self, form, lemma, feats_str)
        if self.lemma == "pessime": self.lemma = "malus"

        self.degree = "NA" if "Degree" not in self.feats else "positive" if self.feats["Degree"] == "Pos" else "comparative" if self.feats["Degree"] == "Cmp" else "superlative" if self.feats["Degree"] == "Sup" else "ERROR"
        self.latmor = self.get_latmor()

        self.inflection = None
        self.macronized = self.macronize()

    def get_latmor(self):
        latmor = "%s<ADV><%s>" % (self.lemma, self.degree) if self.degree != "NA" else "%s<ADV>" % self.lemma

        if self.lemma in ["bonus", "malus"]:
            latmor = "%s<ADJ><%s><ADV>" % (self.lemma, self.degree)

        return latmor

    def macronize(self):
        candidates = self.get_macronizations()
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        if len(candidates) == 1:
            #print "returning:", candidates[0]
            return candidates[0]
        
        #print "too many candidates; returning first:", candidates[0]
        return candidates[0]

class Verb(Word):
    def __init__(self, form, lemma, feats_str):
        Word.__init__(self, form, lemma, feats_str)
        self.inf, self.deponent = None, None
        self.inflection = self.find_inflection()
        self.tense = self.get_tense()
        self.voice = self.get_voice()
        
    def find_infinitive(self):
        form, lemma, feats, deponent = self.form, self.lemma, self.feats, self.deponent
        
        if self.form.startswith("repuli"):
            self.form = "repp" + self.form[3:]
            self.lemma = "repello"
            return "repellere"

        lines = []
        with popen("echo '%s' | fst-mor LatMor/latmor.a" % lemma) as f:
            for line in f: lines.append(line)

        if len(lines[2:]) == 1 and lines[2].startswith("no result"):
            sys.stderr.write("Invalid lemma (cannot find infinitive): %s\n" % lemma)
            return "ERROR"

        lines = [l.strip().replace('>', '').split('<') for l in lines[2:]]
        for line in lines:
            if not deponent and line[1] == 'V':                       return line[0]
            if deponent and line[1] == 'V' and len(line) >= 5 and line[4] == 'deponens': return line[0]

        sys.stderr.write("form: %s\tlemma: %s\tCould not determine infinitive\n" % (form, lemma))
        return "ERROR"

    def find_inflection(self):
        form, lemma, feats = self.form, self.lemma, self.feats

        self.deponent = False
        self.inf = self.find_infinitive()
        inf = self.inf

        if lemma in ['sum', 'possum', 'volo', 'nolo', 'fero', 'eo', 'malo']: return 0 # irregular

        if lemma[-2:] == 'eo': return 2

        if lemma[-2:] == 'io':
            if inf[-3:] == 'ere': return 3
            if inf[-3:] == 'ire': return 4
            
            sys.stderr.write("ERROR: S/b 4th or 3rd-io conj, but reads as neither\tform: %s\tlemma: %s\tinf: %s\n" % (form, lemma, inf))
            return -1

        if lemma[-1] == 'o':
            if inf[-3:] == 'are': return 1
            if inf[-3:] == 'ere': return 3
            
            sys.stderr.write("ERROR: S/b 1st or 3rd-io conjugation, but reads as neither\tform: %s\tlemma: %s\tinf: %s\n" % (form, lemma, inf))
            return -1

        self.deponent = True
        self.inf = self.find_infinitive()
        inf = self.inf
        
        if lemma[-3:] == 'eor': return 2
        
        if lemma[-3:] == 'ior':
            if inf[-3:] == 'iri': return 4
            if inf[-1] == 'i': return 3
            
            sys.stderr.write("ERROR: S/b 4th or 3rd-io conjugation deponent, but reads as neither\tform: %s\tlemma: %s\tinf: %s\n" % (form, lemma, inf))
            return -1

        if lemma[-2:] == 'or':
            if inf[-3:] == 'ari': return 1
            if inf[-1] == 'i': return 3
            
            sys.stderr.write("ERROR: S/b 1st or 3rd conjugation deponent, but reads as neither\tform: %s\tlemma: %s\tinf: %s\n" % (form, lemma, inf))
            return -1

        self.deponent = False
        sys.stderr.write("ERROR: Could not determine conjugation\tform: %s\tlemma: %s\tinf: %s\n" % (form, lemma, inf))
        return -1

    def get_tense(self):
        f = self.feats
        tense = f["Tense"]

        if "Aspect" in f and f["Aspect"] == "Perf":
            if tense == "Past": return "perf"       # perfect
            if tense == "Fut":  return "futureII"   # future perfect

        if "Aspect" in f and f["Aspect"] == "Imp":
            if tense == "Past": return "imperf"     # imperfect
        
        if "Aspect" not in f:
            if tense == "Pres": return "pres"       # present
            if tense == "Pqp":  return "pqperf"     # pluperfect
            if tense == "Fut":  return "futureI"    # future

        return "INVALID_TENSE"

    def get_voice(self):
        if self.deponent: return "deponens"
        
        voice = self.feats["Voice"] if "Voice" in self.feats else "ERROR"
        if voice == "ERROR":
            sys.stderr.write("Unable to find voice of '%s'\n" % self.form)
            return "ERROR"
        
        if voice == "Act":  return "active"
        if voice == "Pass": return "passive"

        return "INVALID_VOICE"

    def macronize(self):
        return self.macronize_recur(0)

    def macronize_recur(self, attempts):
        form, lemma, feats, conjugation = self.form, self.lemma, self.feats, self.inflection

        candidates = self.get_macronizations()

        if conjugation not in verb_conjugations or (len(candidates) == 0 and attempts >= 3):
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("ERROR: Does not have valid conjugation\tform: %s\tlemma: %s\tconjugation: %s\n. Returning default macronization '%s' for LatMor form '%s'.\n" % (form, lemma, conjugation, default_macronized, default_latmor))
            return default_macronized

        
        if len(candidates) == 0:
            if not isinstance(self, VerbFin):
                default_macronized, default_latmor = self.macronize_default()
                sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
                return default_macronized

            if self.mood == "imp":
                self.mood = "ind"
                self.latmor = self.get_latmor()
                return self.macronize_recur(attempts+1)
            elif self.mood == "ind":
                self.mood = "subj"
                self.latmor = self.get_latmor()
                return self.macronize_recur(attempts+1)
            elif self.mood == "subj":
                self.mood = "imp"
                self.latmor = self.get_latmor()
                return self.macronize_recur(attempts+1)

            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized


        if len(candidates) == 1:
            #print "returning:", candidates[0]
            return candidates[0]
        
        #print "too many candidates; returning first:", candidates[0]
        return candidates[0]

class VerbFin(Verb):
    def __init__(self, form, lemma, feats_str):
        Verb.__init__(self, form, lemma, feats_str)
        self.mood = self.get_mood()
        self.number = self.get_number()
        self.person = self.get_person()

        # cantabo --> cantare<V><futureI><ind><active><sg><1>
        self.latmor = self.get_latmor()

        self.macronized = self.macronize()

    def get_mood(self):
        mood = self.feats["Mood"] if "Mood" in self.feats else "ERROR"
        if mood == "ERROR":
            sys.stderr.write("Unable to find mood of '%s'\n" % self.form)
            return "ERROR"

        if mood == "Ind": return "ind"
        if mood == "Sub": return "subj"
        if mood == "Imp": return "imp"
        
        return "INVALID_MOOD"

    def get_number(self):
        number = self.feats["Number"] if "Number" in self.feats else "ERROR"
        if number == "ERROR":
            sys.stderr.write("Unable to find number of '%s'\n" % self.form)
            return "ERROR"
        
        if number == "Sing": return "sg"
        if number == "Plur": return "pl"

        return "INVALID_NUMBER"

    def get_person(self):
        person = int(self.feats["Person"]) if "Person" in self.feats else 0
        if person == 0:
            sys.stderr.write("Unable to find person of '%s'\n" % self.form)
            return 0

        if person in (1, 2, 3): return person
        
        return 0

    def get_latmor(self):
        return "%s<V><%s><%s><%s><%s><%d>" % (self.inf, self.tense, self.mood, self.voice, self.number, self.person)

class VerbPart(Verb):
    def __init__(self, form, lemma, feats_str):
        Verb.__init__(self, form, lemma, feats_str)
        self.tense = "future" if self.tense in ["futureI", "futureII"] else self.tense
        self.gender = self.feats["Gender"].lower() if "Gender" in self.feats else None
        self.case   = self.feats["Case"].lower()
        self.number = "sg" if self.feats["Number"] == "Sing" else "pl" if self.feats["Number"] == "Plur" else "ERROR"

        # delectans --> delectare<V><part><pres><active><masc><sg><acc>
        self.latmor = "%s<V><part><%s><%s><%s><%s><%s>" % (self.inf, self.tense, self.voice, self.gender, self.number, self.case) if self.gender is not None else "%s<V><part><%s><%s><%s><%s>" % (self.inf, self.tense, self.voice, self.number, self.case)
        self.macronized = self.macronize()

class VerbInf(Verb):
    def __init__(self, form, lemma, feats_str):
        Verb.__init__(self, form, lemma, feats_str)

        # delectare --> delectare<V><pres><inf><active>
        self.latmor = "%s<V><%s><inf><%s>" % (self.inf, self.tense, self.voice)
        self.macronized = self.macronize()

class Indecl(Word):
    def __init__(self, form, lemma, feats_str):
        Word.__init__(self, form, lemma, feats_str)
        self.latmor = self.macronize_default()[1]
        self.macronized = self.macronize()

    def macronize(self):
        candidates = self.get_macronizations()
        
        if len(candidates) == 0:
            default_macronized, default_latmor = self.macronize_default()
            sys.stderr.write("PROBLEM: No macronizations for '%s' (lemma: '%s'; inflection: '%s') as LatMor form '%s'. Returning default macronization '%s' for LatMor form '%s'.\n" % (self.form, self.lemma, self.inflection, self.latmor, default_macronized, default_latmor))
            return default_macronized

        sys.stderr.write("This word '%s' is a Word of type Indecl. Using default macronization '%s' for LatMor form '%s'.\n" % (self.form, candidates[0], self.latmor))
        return candidates[0]
        
        

def print_tests(tests, include_feats):
    print "\n\n%-15s%-15s%-15s%-9s%-9s%-40s%-s" % ("Plain Form", "Macronized", "Lemma", "POS", "Infl.", "LatMor Form", "UDPipe Features")
    print "----------------------------------------------------------------------------------------------------------------------------------------------------------"
    
    for t in tests:
        macronized = t.macronized.decode('utf-8') if t.macronized is not None else None
        sys.stdout.write("%-15s%-15s%-15s%-9s%-9s%-40s" % (t.form, macronized, t.lemma, t.__class__.__name__, t.inflection, t.latmor))
        if include_feats: sys.stdout.write("%-s" % t.feats)
        sys.stdout.write('\n')
        
def test_nouns():
    puella = Noun("puellis", "puella", "Case=Dat|Degree=Pos|Gender=Fem|Number=Plur")
    xiphias = Noun("xiphian", "xiphias", "Case=Acc|Degree=Pos|Gender=Masc|Number=Sing")

    servus = Noun("serve", "servus", "Case=Voc|Degree=Pos|Gender=Masc|Number=Sing")
    filius = Noun("fili", "filius", "Case=Voc|Degree=Pos|Gender=Masc|Number=Sing")
    ager = Noun("agri", "ager", "Case=Gen|Degree=Pos|Gender=Masc|Number=Sing")
    locus = Noun("locorum", "locus", "Case=Gen|Degree=Pos|Gender=Neut|Number=Plur")
    deus = Noun("Deis", "deus", "Case=Dat|Degree=Pos|Gender=Masc|Number=Plur")

    corpus = Noun("corpore", "corpus", "Case=Abl|Degree=Pos|Gender=Neut|Number=Sing")
    tigris = Noun("tigridis", "tigris", "Case=Gen|Degree=Pos|Gender=Masc|Number=Sing")
    turris = Noun("turres", "turris", "Case=Acc|Degree=Pos|Gender=Fem|Number=Plur")
    aer = Noun("aeres", "aer", "Case=Acc|Degree=Pos|Gender=Masc|Number=Plur")
    #Dido = Noun("Dido", "Dido", "Case=Nom|Degree=Pos|Gender=Fem|Number=Sing") #PROPER NOUN

    spiritus = Noun("spiritus", "spiritus", "Case=Gen|Degree=Pos|Gender=Masc|Number=Sing")
    cornu = Noun("cornus", "cornu", "Case=Gen|Degree=Pos|Gender=Neut|Number=Sing")
    
    dies = Noun("diebus", "dies", "Case=Dat|Degree=Pos|Gender=Masc|Number=Plur")
    fides = Noun("fides", "fides", "Case=Voc|Degree=Pos|Gender=Fem|Number=Plur")

    domus = Noun("domus", "domus", "Case=Nom|Degree=Pos|Gender=Fem|Number=Sing")
    
    
    nouns = [puella, xiphias, servus, filius, ager, locus, deus, corpus, tigris, turris, aer, spiritus, cornu, dies, fides, domus]
    print_tests(nouns, True)

def test_adjectives():
    bonus_pos = Adj("optimum", "bonus", "Case=Acc|Degree=Sup|Gender=Neut|Number=Sing")
    bonus_cmp = Adj("meliora", "bonus", "Case=Nom|Degree=Cmp|Gender=Neut|Number=Plur")
    bonus_sup = Adj("optimis", "bonus", "Case=Abl|Degree=Sup|Gender=Fem|Number=Plur")
    activus = Adj("activum", "activus", "Case=Nom|Degree=Pos|Gender=Neut|Number=Sing")
    beatus = Adj("beatis", "beatus", "Case=Abl|Degree=Pos|Number=Plur")
    beatus2 = Adj("beatas", "beatus", "Case=Acc|Degree=Pos|Gender=Fem|Number=Plur")
    mirabilis = Adj("mirabilia", "mirabilis", "Case=Nom|Degree=Pos|Gender=Neut|Number=Plur")

    # MAKE MORE TEST CASES

    adjs = [bonus_pos, bonus_cmp, bonus_sup, activus, beatus, beatus2, mirabilis]
    print_tests(adjs, True)

def test_verbs_finite():
    eo = VerbFin("ivi", "eo", "Aspect=Perf|Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|Voice=Act")
    esse = VerbFin("sum", "esse", "Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act")

    amo = VerbFin("amarem", "amo", "Aspect=Imp|Mood=Sub|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|Voice=Act")
    moneo = VerbFin("monebo", "moneo", "Mood=Ind|Number=Sing|Person=1|Tense=Fut|VerbForm=Fin|Voice=Act")
    tego = VerbFin("tegam", "tego", "Mood=Ind|Number=Sing|Person=1|Tense=Fut|VerbForm=Fin|Voice=Act")
    capio = VerbFin("capiebam", "capio", "Aspect=Imp|Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|Voice=Act")
    audio = VerbFin("audiam", "audio", "Mood=Ind|Number=Sing|Person=1|Tense=Fut|VerbForm=Fin|Voice=Act")

    miror = VerbFin("mirarer", "miro", "Aspect=Imp|Mood=Sub|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|Voice=Pass")
    polliceor = VerbFin("polliceris", "polliceor", "Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Pass")
    loquor = VerbFin("loquor", "loquor", "Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin|Voice=Pass")
    gradior = VerbFin("gradiebar", "gradior", "Aspect=Imp|Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin|Voice=Pass")
    mentior = VerbFin("mentiar", "mentior", "Mood=Ind|Number=Sing|Person=1|Tense=Fut|VerbForm=Fin|Voice=Pass")

    verbs = [eo, esse, amo, moneo, tego, capio, audio, miror, polliceor, loquor, gradior, mentior]
    print_tests(verbs, False)

def test_verbs_participles():
    delecto = VerbPart("delectantibus", "delecto", "Case=Abl|Gender=Masc|Number=Plur|Tense=Pres|VerbForm=Part|Voice=Act")
    delecto2 = VerbPart("delectaturus", "delecto", "Case=Nom|Gender=Masc|Number=Sing|Tense=Fut|VerbForm=Part|Voice=Act")
    delecto3 = VerbPart("delectatus", "delecto", "Aspect=Perf|Case=Nom|Gender=Masc|Number=Sing|Tense=Past|VerbForm=Part|Voice=Pass")

    parts = [delecto, delecto2, delecto3]
    print_tests(parts, False)

def test_verbs_infinitives():
    delecto = VerbInf("delectare", "delecto", "Tense=Pres|VerbForm=Inf|Voice=Act")
    delecto2 = VerbInf("delectari", "delecto", "Tense=Pres|VerbForm=Inf|Voice=Pass")
    delecto3 = VerbInf("delectavisse", "delecto", "Aspect=Perf|Tense=Past|VerbForm=Inf|Voice=Act")

    infs = [delecto, delecto2, delecto3]
    print_tests(infs, True)

def main():
    test_nouns()
    test_adjectives()
    test_verbs_finite()
    test_verbs_participles()
    test_verbs_infinitives()