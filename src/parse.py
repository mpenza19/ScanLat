import os, sys, clean
from ufal.udpipe import Model, Pipeline, ProcessingError
from natural import Noun, Adj, Adv, Verb, VerbFin, VerbInf, VerbPart, Indecl
import natural

def config():
    # In Python2, wrap sys.stdin and sys.stdout to work with unicode.
    if sys.version_info[0] < 3:
        import codecs, locale
        global encoding
        encoding = locale.getpreferredencoding()
        sys.stdin = codecs.getreader(encoding)(sys.stdin)
        sys.stdout = codecs.getwriter(encoding)(sys.stdout)

def get_pipeline():
    # Load model, handle errors
    global model
    sys.stderr.write('Loading model... ')
    model_fp = os.getenv("UD_MODEL_PATH")
    model = Model.load(model_fp)
    if not model:
        sys.stderr.write("Cannot load model from file '%s'\n" % model_fp)
        sys.exit(1)
    sys.stderr.write('Done.\n')

    # Create model pipeline
    pipeline = Pipeline(model, "horizontal", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
    error = ProcessingError()

    return pipeline, error

def process_text(txt, pipeline, error):
    # Process input text
    processed = pipeline.process(txt, error)

    if error.occurred():
        sys.stderr.write("An error occurred when running run_udpipe: ")
        sys.stderr.write(error.message)
        sys.stderr.write("\n")
        sys.exit(1)

    return processed

def main():
    # Read command-line args
    rawparse_filepath = sys.argv[1]

    # Read input text
    txt = clean.demacronized_lines(sys.stdin.read())

    config()
    pipeline, error = get_pipeline()
    processed = process_text(txt, pipeline, error)

    rawparse = processed.split('\n')[2:-2]

    with open(rawparse_filepath, 'w') as f:
        f.write("RAWPARSE:\n")
        for line in rawparse: f.write(line + '\n')

    for line in rawparse:
        if line.startswith("# sent_id =") or line.startswith("# newpar"): continue

        if line in ['', '\n', ' \n ', ' \n', '\n ']:
            sys.stdout.write('\n')
            continue

        line = line.split('\t')[1:]
        form, lemma, pos, feats_str = line[0], line[1], line[2], line[4]
        form_lower = form.lower()
        sys.stderr.write("%s\t%s\t%s\t%s\n\n" % (form, lemma, pos, feats_str))

        # A few irregular cases
        if form_lower == "amen":
            word = natural.Word(form, lemma, feats_str)
            word.macronized = "āmēn" if form == form_lower else "Āmēn"
        elif form_lower in ["quot", "quotquot"]:
            word = natural.Word(form, lemma, feats_str)
            word.macronized = form
        elif form_lower in ["iesus", "iesum", "iesu"]:
            word = natural.Word(form, lemma, feats_str)
            if "Case=Nom" in feats_str: word.macronized = form[0] + "ēsus"
            elif "Case=Acc" in feats_str: word.macronized = form[0] + "ēsum"
            else: word.macronized = form[0] + "ēsū"

        # Normal cases
        elif pos == "PUNCT":
            word = natural.Word(form, lemma, feats_str)
            word.macronized = form
        elif pos == "PROPN":
            word = Indecl(form, lemma, feats_str)
        elif pos == "NOUN":
            word = Noun(form, lemma, feats_str)
        elif pos == "ADJ" and "Poss=Yes" not in feats_str:
            word = Adj(form, lemma, feats_str)
        elif pos == "ADV":
            word = Adv(form, lemma, feats_str)
        elif pos in ["VERB", "AUX"]:
            if "VerbForm=Fin" in feats_str: word = VerbFin(form, lemma, feats_str)
            elif "VerbForm=Fin" in feats_str: word = VerbInf(form, lemma, feats_str)
            elif "VerbForm=Part" in feats_str: word = VerbPart(form, lemma, feats_str)
            else: word = VerbFin(form, lemma, feats_str)

        # Default cases
        else:
            word = Indecl(form, lemma, feats_str)

        sys.stdout.write(word.macronized)
        if word.macronized != '\n': sys.stdout.write(' ')

main()
