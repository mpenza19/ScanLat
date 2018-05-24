# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def clean_text(txt):
    chars = [t.replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('\'', '').replace('`', '') for t in txt if not t.isdigit()]
    text = ""
    for c in chars: text = text + c
    text = text.replace('æ', 'ae').replace('œ', 'oe').replace('ǽ', 'ae').replace('Æ', 'Ae').replace('Ǽ', 'Ae').replace('Œ', 'Oe').replace('j', 'i').replace('J', 'I')
    text = text.replace('ä', 'a').replace('Ä', 'A').replace('ë', 'e').replace('Ë', 'E').replace('ï', 'i').replace('Ï', 'I').replace('ö', 'o').replace('Ö', "O").replace('ü', 'u').replace('Ü', 'U').replace('ÿ', 'y').replace('Ÿ', 'Y')
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ý', 'y')
    while '  ' in text: text = text.replace('  ', ' ')
    while '\n ' in text: text = text.replace('\n ', '\n')
    while ' \n' in text: text = text.replace(' \n', '\n')
    while '\n\n' in text: text = text.replace('\n\n', '\n')
    text = text.replace('\n', ' \n ')


    return text

def clean_lines(txt):
    txt = clean_text(txt)
    text = ""
    for line in txt.split('\n'):
        line = line.strip().replace(',', ' , ').replace('.', ' . ').replace('?', ' ? ').replace('!', ' ! ').replace(':', ' : ').replace(';', ' ; ').replace('–', ' – ').replace('—', ' — ').replace('-', ' - ')
        text += line + '\n'

    return text

def demacronized_lines(txt):
    mac = clean_lines(txt)
    demac = mac.replace('ā', 'a').replace('ē', 'e').replace('ī', 'i').replace('ō', 'o').replace('ū', 'u').replace('ȳ', 'y').replace('ӯ'.decode('utf-8'), 'y')
    demac = demac.replace('Ā', 'A').replace('Ē', 'E').replace('Ī', 'I').replace('Ō', 'O').replace('Ū', 'U').replace('Ȳ', 'Y')
    return demac

def newline_locs(txt):
    locs = []
    for i in range(len(txt)):
        if txt[i] == '\n': locs.append(i)
    return locs

def main():
    with open("john.txt", 'r') as f: txt = f.read()
    
    print txt
    print '---------------------------------------------------------------'
    cleantxt = clean_text(txt)
    print cleantxt
    print newline_locs(cleantxt)
    print '---------------------------------------------------------------'
    print clean_lines(txt)
    print '---------------------------------------------------------------'

#main()